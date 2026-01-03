"""MCP tools for BPA form operations.

This module provides tools for reading and manipulating Form.io forms in BPA services.
Forms include: applicant forms, guide forms, send file forms, and payment forms.

BPA uses a read-modify-write pattern for forms:
1. GET the complete form schema
2. Modify the components array
3. PUT the entire updated schema

Write operations follow the audit-before-write pattern:
1. Validate parameters (pre-flight, no audit record if validation fails)
2. Create PENDING audit record
3. Execute BPA API call
4. Update audit record to SUCCESS or FAILED

API Endpoints used:
- GET /service/{id}/applicant-form?reusable=false - Get applicant form
- GET /service/{id}/guide-form?reusable=false - Get guide form
- GET /service/{id}/send-file-form?reusable=false - Get send file form
- GET /service/{id}/payment-form?reusable=false - Get payment form
- PUT /applicant-form/{form_id} - Update applicant form
- PUT /guide-form/{form_id} - Update guide form
- PUT /send-file-form/{form_id} - Update send file form
- PUT /payment-form/{form_id} - Update payment form
"""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp.exceptions import ToolError

from mcp_eregistrations_bpa.audit.context import (
    NotAuthenticatedError,
    get_current_user_email,
)
from mcp_eregistrations_bpa.audit.logger import AuditLogger
from mcp_eregistrations_bpa.bpa_client import BPAClient
from mcp_eregistrations_bpa.bpa_client.errors import (
    BPAClientError,
    BPANotFoundError,
    translate_error,
)
from mcp_eregistrations_bpa.tools.form_errors import FormErrorCode
from mcp_eregistrations_bpa.tools.formio_helpers import (
    CONTAINER_TYPES,
    find_component,
    get_all_component_keys,
    insert_component,
    move_component,
    remove_component,
    update_component,
    validate_component,
    validate_component_key_unique,
)

__all__ = [
    "form_get",
    "form_component_get",
    "form_component_add",
    "form_component_update",
    "form_component_remove",
    "form_component_move",
    "form_update",
    "register_form_tools",
]


# Form type to endpoint mapping
FORM_TYPES = {
    "applicant": {
        "get_endpoint": "/service/{id}/applicant-form",
        "put_endpoint": "/applicant-form/{form_id}",
        "name": "Applicant Form",
    },
    "guide": {
        "get_endpoint": "/service/{id}/guide-form",
        "put_endpoint": "/guide-form/{form_id}",
        "name": "Guide Form",
    },
    "send_file": {
        "get_endpoint": "/service/{id}/send-file-form",
        "put_endpoint": "/send-file-form/{form_id}",
        "name": "Send File Form",
    },
    "payment": {
        "get_endpoint": "/service/{id}/payment-form",
        "put_endpoint": "/payment-form/{form_id}",
        "name": "Payment Form",
    },
}


def _validate_form_type(form_type: str) -> dict[str, str]:
    """Validate form type and return endpoint config.

    Args:
        form_type: Form type to validate.

    Returns:
        Endpoint configuration dict.

    Raises:
        ToolError: If form type is invalid.
    """
    if form_type not in FORM_TYPES:
        valid_types = ", ".join(sorted(FORM_TYPES.keys()))
        raise ToolError(
            f"[{FormErrorCode.INVALID_FORM_TYPE}] Invalid form type '{form_type}'. "
            f"Valid types: {valid_types}"
        )
    return FORM_TYPES[form_type]


def _parse_form_schema(form_data: dict[str, Any]) -> dict[str, Any]:
    """Parse formSchema from form data, handling string JSON.

    Args:
        form_data: Form data from BPA API.

    Returns:
        Parsed form schema dict.
    """
    form_schema = form_data.get("formSchema", {})
    if isinstance(form_schema, str):
        try:
            parsed = json.loads(form_schema)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}
    return form_schema if isinstance(form_schema, dict) else {}


def _simplify_components(
    components: list[dict[str, Any]],
    path: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Simplify components for display.

    Args:
        components: Raw Form.io components.
        path: Current nesting path.

    Returns:
        Simplified component list.
    """
    if path is None:
        path = []

    result = []
    for comp in components:
        if not isinstance(comp, dict):
            continue

        key = comp.get("key")
        if not key:
            continue

        comp_type = comp.get("type", "unknown")
        simplified: dict[str, Any] = {
            "key": key,
            "type": comp_type,
        }

        if comp.get("label"):
            simplified["label"] = comp["label"]

        if path:
            simplified["path"] = path

        # Add validation info
        validate = comp.get("validate", {})
        if isinstance(validate, dict) and validate.get("required"):
            simplified["required"] = True

        # Add is_container flag for container types
        if comp_type in CONTAINER_TYPES:
            simplified["is_container"] = True

        # Handle nested components (panels, fieldsets, editgrids, datagrids, etc.)
        children_count = 0
        nested = comp.get("components", [])
        if nested:
            children_count += len(nested)
            result.extend(_simplify_components(nested, path + [key]))

        # Handle columns (2-level: columns > cells > components)
        columns = comp.get("columns", [])
        if columns:
            for col in columns:
                if isinstance(col, dict):
                    col_comps = col.get("components", [])
                    children_count += len(col_comps)
                    result.extend(_simplify_components(col_comps, path + [key]))

        # Handle table rows (rows[][] structure)
        rows = comp.get("rows", [])
        if rows:
            for row in rows:
                if isinstance(row, list):
                    for cell in row:
                        if isinstance(cell, dict):
                            cell_comps = cell.get("components", [])
                            children_count += len(cell_comps)
                            result.extend(
                                _simplify_components(cell_comps, path + [key])
                            )

        # Add children_count for containers
        if children_count > 0:
            simplified["children_count"] = children_count

        result.append(simplified)

    return result


async def _get_form_data(
    client: BPAClient,
    service_id: str | int,
    form_type: str,
) -> dict[str, Any]:
    """Get raw form data from BPA.

    Args:
        client: BPA client instance.
        service_id: Service ID.
        form_type: Type of form.

    Returns:
        Raw form data from API.

    Raises:
        ToolError: If form not found.
    """
    config = _validate_form_type(form_type)

    try:
        form_data = await client.get(
            config["get_endpoint"],
            path_params={"id": service_id},
            params={"reusable": "false"},
            resource_type="form",
            resource_id=f"{service_id}/{form_type}",
        )
    except BPANotFoundError:
        raise ToolError(
            f"[{FormErrorCode.SERVICE_NOT_FOUND}] {config['name']} not found for "
            f"service '{service_id}'. The service may not have this form type "
            "configured."
        )

    return form_data


async def _update_form_data(
    client: BPAClient,
    form_data: dict[str, Any],
    form_type: str,
) -> None:
    """Update form data in BPA.

    Args:
        client: BPA client instance.
        form_data: Complete form data to PUT.
        form_type: Type of form.
    """
    config = _validate_form_type(form_type)
    form_id = form_data.get("id")

    await client.put(
        config["put_endpoint"],
        path_params={"form_id": form_id},
        json=form_data,
        resource_type="form",
        resource_id=form_id,
    )


# =============================================================================
# Read Operations
# =============================================================================


async def form_get(
    service_id: str | int,
    form_type: str = "applicant",
) -> dict[str, Any]:
    """Get form schema with simplified component list.

    Args:
        service_id: BPA service UUID.
        form_type: "applicant" (default), "guide", "send_file", or "payment".

    Returns:
        dict with id, form_type, active, components, component_count, component_keys,
        raw_schema.
    """
    config = _validate_form_type(form_type)

    try:
        async with BPAClient() as client:
            form_data = await _get_form_data(client, service_id, form_type)
    except ToolError:
        raise
    except BPAClientError as e:
        raise translate_error(e, resource_type="form", resource_id=service_id)

    # Extract form schema
    form_schema = _parse_form_schema(form_data)
    components = form_schema.get("components", [])
    all_keys = get_all_component_keys(components)
    simplified = _simplify_components(components)

    return {
        "id": form_data.get("id"),
        "form_type": form_type,
        "form_name": config["name"],
        "service_id": service_id,
        "active": form_data.get("active", True),
        "components": simplified,
        "component_count": len(all_keys),
        "component_keys": sorted(all_keys),
        "raw_schema": form_schema,
    }


async def form_component_get(
    service_id: str | int,
    component_key: str,
    form_type: str = "applicant",
) -> dict[str, Any]:
    """Get details of a form component, including nested components.

    Args:
        service_id: BPA service UUID.
        component_key: Component's key property.
        form_type: "applicant" (default), "guide", "send_file", or "payment".

    Returns:
        dict with key, type, label, validate, data, determinant_ids, path, raw.
        See docs/mcp-tools-guide.md for path hierarchy examples.
    """
    config = _validate_form_type(form_type)

    try:
        async with BPAClient() as client:
            form_data = await _get_form_data(client, service_id, form_type)
    except ToolError:
        raise
    except BPAClientError as e:
        raise translate_error(e, resource_type="form", resource_id=service_id)

    # Extract form schema
    form_schema = _parse_form_schema(form_data)
    components = form_schema.get("components", [])

    # Find component
    result = find_component(components, component_key)
    if result is None:
        all_keys = get_all_component_keys(components)
        key_preview = list(sorted(all_keys))[:10]
        raise ToolError(
            f"[{FormErrorCode.COMPONENT_NOT_FOUND}] Component '{component_key}' not "
            f"found in {config['name']}. Available keys include: "
            f"{', '.join(key_preview)}... Use form_get to see all "
            f"{len(all_keys)} components."
        )

    comp, path = result

    # Build detailed response
    response: dict[str, Any] = {
        "key": comp.get("key"),
        "type": comp.get("type"),
        "label": comp.get("label"),
        "form_type": form_type,
        "service_id": service_id,
        "path": path,
    }

    # Add validation info
    validate = comp.get("validate", {})
    if validate:
        response["validate"] = validate

    # Add data source info (for selects)
    data = comp.get("data", {})
    if data:
        response["data"] = data

    # Add BPA-specific properties
    if comp.get("determinantIds"):
        response["determinant_ids"] = comp["determinantIds"]
    if comp.get("registrations"):
        response["registrations"] = comp["registrations"]
    if comp.get("componentActionId"):
        response["component_action_id"] = comp["componentActionId"]
    if comp.get("componentFormulaId"):
        response["component_formula_id"] = comp["componentFormulaId"]

    # Add common properties
    if comp.get("hidden"):
        response["hidden"] = True
    if comp.get("disabled"):
        response["disabled"] = True
    if comp.get("defaultValue") is not None:
        response["default_value"] = comp["defaultValue"]

    # Include raw component for advanced use
    response["raw"] = comp

    return response


# =============================================================================
# Write Operations
# =============================================================================


def _validate_component_add_params(
    component: dict[str, Any],
) -> list[str]:
    """Validate component for add operation.

    Args:
        component: Component to validate.

    Returns:
        List of validation errors (empty if valid).
    """
    return validate_component(component)


async def form_component_add(
    service_id: str | int,
    component: dict[str, Any],
    form_type: str = "applicant",
    parent_key: str | None = None,
    position: int | None = None,
) -> dict[str, Any]:
    """Add component to form. Audited write operation.

    Args:
        service_id: BPA service UUID.
        component: Form.io component with key, type, label.
        form_type: "applicant" (default), "guide", "send_file", "payment".
        parent_key: Parent container key for nesting, or None for root.
        position: Insert position (0-indexed), or None for end.

    Returns:
        dict with added, component_key, position, audit_id.
        See docs/mcp-tools-guide.md for parent_key nesting examples.
    """
    config = _validate_form_type(form_type)

    # Pre-flight validation
    errors = _validate_component_add_params(component)
    if errors:
        raise ToolError(
            f"[{FormErrorCode.MISSING_REQUIRED_PROPERTY}] Invalid component: "
            f"{'; '.join(errors)}. Ensure 'key', 'type', and 'label' are provided."
        )

    component_key = str(component.get("key", ""))

    # Get authenticated user
    try:
        user_email = get_current_user_email()
    except NotAuthenticatedError as e:
        raise ToolError(str(e))

    try:
        async with BPAClient() as client:
            # Get current form
            form_data = await _get_form_data(client, service_id, form_type)

            # Parse form schema
            form_schema = _parse_form_schema(form_data)
            components = form_schema.get("components", [])

            # Check key uniqueness
            if not validate_component_key_unique(components, component_key):
                raise ToolError(
                    f"[{FormErrorCode.DUPLICATE_KEY}] Component key '{component_key}' "
                    "already exists in form. Use a unique key or use "
                    "form_component_update to modify existing."
                )

            # Validate parent if specified
            if parent_key:
                parent_result = find_component(components, parent_key)
                if parent_result is None:
                    raise ToolError(
                        f"[{FormErrorCode.INVALID_PARENT}] Parent component "
                        f"'{parent_key}' not found. Use form_get to see "
                        "available components."
                    )

            # Create audit record BEFORE modification
            audit_logger = AuditLogger()
            audit_id = await audit_logger.record_pending(
                user_email=user_email,
                operation_type="create",
                object_type="form_component",
                params={
                    "service_id": str(service_id),
                    "form_type": form_type,
                    "form_id": form_data.get("id"),
                    "component_key": component_key,
                    "parent_key": parent_key,
                    "position": position,
                },
            )

            # Save rollback state (entire form before modification)
            await audit_logger.save_rollback_state(
                audit_id=audit_id,
                object_type="form",
                object_id=str(form_data.get("id")),
                previous_state=form_data,
            )

            operation_error: Exception | None = None
            try:
                # Insert component
                new_components = insert_component(
                    components, component, parent_key, position
                )

                # Update form schema
                form_schema["components"] = new_components
                form_data["formSchema"] = form_schema

                # PUT updated form
                await _update_form_data(client, form_data, form_type)

            except ValueError as e:
                operation_error = ToolError(f"[{FormErrorCode.INVALID_POSITION}] {e}")
            except BPAClientError as e:
                operation_error = translate_error(e, resource_type="form")
            finally:
                # Always update audit status, even if this fails
                try:
                    if operation_error:
                        await audit_logger.mark_failed(audit_id, str(operation_error))
                    else:
                        await audit_logger.mark_success(
                            audit_id,
                            result={
                                "component_key": component_key,
                                "parent_key": parent_key,
                                "position": position,
                            },
                        )
                except Exception:
                    pass  # Don't mask the original error

            if operation_error:
                raise operation_error

    except ToolError:
        raise
    except BPAClientError as e:
        raise translate_error(e, resource_type="form", resource_id=service_id)

    return {
        "added": True,
        "component_key": component_key,
        "component_type": component.get("type"),
        "form_type": form_type,
        "form_name": config["name"],
        "service_id": service_id,
        "parent_key": parent_key,
        "position": position,
        "audit_id": audit_id,
    }


async def form_component_update(
    service_id: str | int,
    component_key: str,
    updates: dict[str, Any],
    form_type: str = "applicant",
) -> dict[str, Any]:
    """Update component properties. Audited write operation.

    Args:
        service_id: BPA service UUID.
        component_key: Component to update.
        updates: Properties to merge (e.g., {"label": "New", "hidden": True}).
        form_type: "applicant" (default), "guide", "send_file", or "payment".

    Returns:
        dict with updated, component_key, updates_applied, previous_state, audit_id.
    """
    config = _validate_form_type(form_type)

    if not updates:
        raise ToolError(
            f"[{FormErrorCode.NO_UPDATES_PROVIDED}] No updates provided. "
            "Specify properties to update."
        )

    # Prevent key changes
    if "key" in updates and updates["key"] != component_key:
        raise ToolError(
            f"[{FormErrorCode.KEY_CHANGE_NOT_ALLOWED}] Cannot change component key. "
            "To rename, remove and re-add the component."
        )

    # Get authenticated user
    try:
        user_email = get_current_user_email()
    except NotAuthenticatedError as e:
        raise ToolError(str(e))

    try:
        async with BPAClient() as client:
            # Get current form
            form_data = await _get_form_data(client, service_id, form_type)

            # Parse form schema
            form_schema = _parse_form_schema(form_data)
            components = form_schema.get("components", [])

            # Check component exists
            found = find_component(components, component_key)
            if found is None:
                all_keys = get_all_component_keys(components)
                raise ToolError(
                    f"[{FormErrorCode.COMPONENT_NOT_FOUND}] Component "
                    f"'{component_key}' not found. Use form_get to see "
                    f"{len(all_keys)} available components."
                )

            # Create audit record
            audit_logger = AuditLogger()
            audit_id = await audit_logger.record_pending(
                user_email=user_email,
                operation_type="update",
                object_type="form_component",
                params={
                    "service_id": str(service_id),
                    "form_type": form_type,
                    "form_id": form_data.get("id"),
                    "component_key": component_key,
                    "updates": updates,
                },
            )

            # Save rollback state
            await audit_logger.save_rollback_state(
                audit_id=audit_id,
                object_type="form",
                object_id=str(form_data.get("id")),
                previous_state=form_data,
            )

            operation_error: Exception | None = None
            try:
                # Update component
                new_components, previous_state = update_component(
                    components, component_key, updates
                )

                # Update form schema
                form_schema["components"] = new_components
                form_data["formSchema"] = form_schema

                # PUT updated form
                await _update_form_data(client, form_data, form_type)

            except ValueError as e:
                operation_error = ToolError(
                    f"[{FormErrorCode.COMPONENT_NOT_FOUND}] {e}"
                )
            except BPAClientError as e:
                operation_error = translate_error(e, resource_type="form")
            finally:
                # Always update audit status, even if this fails
                try:
                    if operation_error:
                        await audit_logger.mark_failed(audit_id, str(operation_error))
                    else:
                        await audit_logger.mark_success(
                            audit_id,
                            result={
                                "component_key": component_key,
                                "updates_applied": list(updates.keys()),
                            },
                        )
                except Exception:
                    pass  # Don't mask the original error

            if operation_error:
                raise operation_error

    except ToolError:
        raise
    except BPAClientError as e:
        raise translate_error(e, resource_type="form", resource_id=service_id)

    # Simplify previous state for response
    prev_summary = {
        "label": previous_state.get("label"),
        "type": previous_state.get("type"),
    }
    if previous_state.get("validate"):
        prev_summary["validate"] = previous_state["validate"]
    if previous_state.get("hidden"):
        prev_summary["hidden"] = previous_state["hidden"]
    if previous_state.get("disabled"):
        prev_summary["disabled"] = previous_state["disabled"]

    return {
        "updated": True,
        "component_key": component_key,
        "form_type": form_type,
        "form_name": config["name"],
        "service_id": service_id,
        "updates_applied": list(updates.keys()),
        "previous_state": prev_summary,
        "audit_id": audit_id,
    }


async def form_component_remove(
    service_id: str | int,
    component_key: str,
    form_type: str = "applicant",
) -> dict[str, Any]:
    """Remove component from form. Audited write operation.

    Warning: May break determinant references. Check determinant_list first.

    Args:
        service_id: BPA service UUID.
        component_key: Component to remove.
        form_type: "applicant" (default), "guide", "send_file", or "payment".

    Returns:
        dict with removed, component_key, deleted_component, audit_id.
    """
    config = _validate_form_type(form_type)

    # Get authenticated user
    try:
        user_email = get_current_user_email()
    except NotAuthenticatedError as e:
        raise ToolError(str(e))

    try:
        async with BPAClient() as client:
            # Get current form
            form_data = await _get_form_data(client, service_id, form_type)

            # Parse form schema
            form_schema = _parse_form_schema(form_data)
            components = form_schema.get("components", [])

            # Check component exists
            found = find_component(components, component_key)
            if found is None:
                all_keys = get_all_component_keys(components)
                raise ToolError(
                    f"[{FormErrorCode.COMPONENT_NOT_FOUND}] Component "
                    f"'{component_key}' not found. Use form_get to see "
                    f"{len(all_keys)} available components."
                )

            # Create audit record
            audit_logger = AuditLogger()
            audit_id = await audit_logger.record_pending(
                user_email=user_email,
                operation_type="delete",
                object_type="form_component",
                params={
                    "service_id": str(service_id),
                    "form_type": form_type,
                    "form_id": form_data.get("id"),
                    "component_key": component_key,
                },
            )

            # Save rollback state
            await audit_logger.save_rollback_state(
                audit_id=audit_id,
                object_type="form",
                object_id=str(form_data.get("id")),
                previous_state=form_data,
            )

            operation_error: Exception | None = None
            try:
                # Remove component
                new_components, removed = remove_component(components, component_key)

                # Update form schema
                form_schema["components"] = new_components
                form_data["formSchema"] = form_schema

                # PUT updated form
                await _update_form_data(client, form_data, form_type)

            except ValueError as e:
                operation_error = ToolError(
                    f"[{FormErrorCode.COMPONENT_NOT_FOUND}] {e}"
                )
            except BPAClientError as e:
                operation_error = translate_error(e, resource_type="form")
            finally:
                # Always update audit status, even if this fails
                try:
                    if operation_error:
                        await audit_logger.mark_failed(audit_id, str(operation_error))
                    else:
                        await audit_logger.mark_success(
                            audit_id,
                            result={
                                "component_key": component_key,
                                "component_type": removed.get("type"),
                            },
                        )
                except Exception:
                    pass  # Don't mask the original error

            if operation_error:
                raise operation_error

    except ToolError:
        raise
    except BPAClientError as e:
        raise translate_error(e, resource_type="form", resource_id=service_id)

    # Simplify removed component for response
    removed_summary = {
        "key": removed.get("key"),
        "type": removed.get("type"),
        "label": removed.get("label"),
    }

    return {
        "removed": True,
        "component_key": component_key,
        "form_type": form_type,
        "form_name": config["name"],
        "service_id": service_id,
        "deleted_component": removed_summary,
        "audit_id": audit_id,
    }


async def form_component_move(
    service_id: str | int,
    component_key: str,
    new_parent_key: str | None = None,
    new_position: int | None = None,
    form_type: str = "applicant",
) -> dict[str, Any]:
    """Move component to new position. Audited write operation.

    Args:
        service_id: BPA service UUID.
        component_key: Component to move.
        new_parent_key: Target parent container, or None for root.
        new_position: Position in target, or None for end.
        form_type: "applicant" (default), "guide", "send_file", or "payment".

    Returns:
        dict with moved, old_parent, old_position, new_parent, new_position, audit_id.
    """
    config = _validate_form_type(form_type)

    # Get authenticated user
    try:
        user_email = get_current_user_email()
    except NotAuthenticatedError as e:
        raise ToolError(str(e))

    try:
        async with BPAClient() as client:
            # Get current form
            form_data = await _get_form_data(client, service_id, form_type)

            # Parse form schema
            form_schema = _parse_form_schema(form_data)
            components = form_schema.get("components", [])

            # Check component exists
            found = find_component(components, component_key)
            if found is None:
                raise ToolError(
                    f"[{FormErrorCode.COMPONENT_NOT_FOUND}] Component "
                    f"'{component_key}' not found. Use form_get to see "
                    "available components."
                )

            # Validate new parent if specified
            if new_parent_key:
                parent_result = find_component(components, new_parent_key)
                if parent_result is None:
                    raise ToolError(
                        f"[{FormErrorCode.INVALID_PARENT}] Target parent "
                        f"'{new_parent_key}' not found. Use form_get to see "
                        "available components."
                    )

            # Create audit record
            audit_logger = AuditLogger()
            audit_id = await audit_logger.record_pending(
                user_email=user_email,
                operation_type="update",
                object_type="form_component",
                params={
                    "service_id": str(service_id),
                    "form_type": form_type,
                    "form_id": form_data.get("id"),
                    "component_key": component_key,
                    "new_parent_key": new_parent_key,
                    "new_position": new_position,
                    "operation": "move",
                },
            )

            # Save rollback state
            await audit_logger.save_rollback_state(
                audit_id=audit_id,
                object_type="form",
                object_id=str(form_data.get("id")),
                previous_state=form_data,
            )

            operation_error: Exception | None = None
            try:
                # Move component
                new_components, move_info = move_component(
                    components, component_key, new_parent_key, new_position
                )

                # Update form schema
                form_schema["components"] = new_components
                form_data["formSchema"] = form_schema

                # PUT updated form
                await _update_form_data(client, form_data, form_type)

            except ValueError as e:
                operation_error = ToolError(f"[{FormErrorCode.INVALID_PARENT}] {e}")
            except BPAClientError as e:
                operation_error = translate_error(e, resource_type="form")
            finally:
                # Always update audit status, even if this fails
                try:
                    if operation_error:
                        await audit_logger.mark_failed(audit_id, str(operation_error))
                    else:
                        await audit_logger.mark_success(
                            audit_id,
                            result={
                                "component_key": component_key,
                                "move_info": move_info,
                            },
                        )
                except Exception:
                    pass  # Don't mask the original error

            if operation_error:
                raise operation_error

    except ToolError:
        raise
    except BPAClientError as e:
        raise translate_error(e, resource_type="form", resource_id=service_id)

    return {
        "moved": True,
        "component_key": component_key,
        "form_type": form_type,
        "form_name": config["name"],
        "service_id": service_id,
        "old_parent": move_info.get("old_parent"),
        "old_position": move_info.get("old_position"),
        "new_parent": move_info.get("new_parent"),
        "new_position": move_info.get("new_position"),
        "audit_id": audit_id,
    }


async def form_update(
    service_id: str | int,
    form_type: str = "applicant",
    components: list[dict[str, Any]] | None = None,
    active: bool | None = None,
    tutorials: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Update form schema. Audited write operation.

    Warning: components replaces ALL existing. Use form_component_* for targeted
    changes.

    Args:
        service_id: BPA service UUID.
        form_type: "applicant" (default), "guide", "send_file", or "payment".
        components: New components array (replaces existing).
        active: Set active status.
        tutorials: Update tutorials.

    Returns:
        dict with updated, form_id, components_replaced, active_updated, audit_id.
    """
    config = _validate_form_type(form_type)

    if components is None and active is None and tutorials is None:
        raise ToolError(
            f"[{FormErrorCode.NO_UPDATES_PROVIDED}] No updates provided. "
            "Specify components, active, or tutorials to update."
        )

    # Get authenticated user
    try:
        user_email = get_current_user_email()
    except NotAuthenticatedError as e:
        raise ToolError(str(e))

    try:
        async with BPAClient() as client:
            # Get current form
            form_data = await _get_form_data(client, service_id, form_type)

            # Create audit record
            audit_logger = AuditLogger()
            audit_id = await audit_logger.record_pending(
                user_email=user_email,
                operation_type="update",
                object_type="form",
                params={
                    "service_id": str(service_id),
                    "form_type": form_type,
                    "form_id": form_data.get("id"),
                    "updates": {
                        "components": components is not None,
                        "active": active,
                        "tutorials": tutorials is not None,
                    },
                },
            )

            # Save rollback state
            await audit_logger.save_rollback_state(
                audit_id=audit_id,
                object_type="form",
                object_id=str(form_data.get("id")),
                previous_state=form_data,
            )

            try:
                # Apply updates
                if components is not None:
                    form_schema = _parse_form_schema(form_data)
                    form_schema["components"] = components
                    form_data["formSchema"] = form_schema

                if active is not None:
                    form_data["active"] = active

                if tutorials is not None:
                    form_data["tutorials"] = tutorials

                # PUT updated form
                await _update_form_data(client, form_data, form_type)

                # Mark audit as success
                await audit_logger.mark_success(
                    audit_id,
                    result={
                        "form_id": form_data.get("id"),
                        "form_type": form_type,
                    },
                )

            except BPAClientError as e:
                await audit_logger.mark_failed(audit_id, str(e))
                raise translate_error(e, resource_type="form")

    except ToolError:
        raise
    except BPAClientError as e:
        raise translate_error(e, resource_type="form", resource_id=service_id)

    return {
        "updated": True,
        "form_id": form_data.get("id"),
        "form_type": form_type,
        "form_name": config["name"],
        "service_id": service_id,
        "components_replaced": components is not None,
        "active_updated": active is not None,
        "tutorials_updated": tutorials is not None,
        "audit_id": audit_id,
    }


# =============================================================================
# Registration
# =============================================================================


def register_form_tools(mcp: Any) -> None:
    """Register form tools with the MCP server.

    Args:
        mcp: The FastMCP server instance.
    """
    # Read operations
    mcp.tool()(form_get)
    mcp.tool()(form_component_get)
    # Write operations (audit-before-write pattern)
    mcp.tool()(form_component_add)
    mcp.tool()(form_component_update)
    mcp.tool()(form_component_remove)
    mcp.tool()(form_component_move)
    mcp.tool()(form_update)

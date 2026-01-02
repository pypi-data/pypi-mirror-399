"""MCP tools for BPA registration operations.

This module provides tools for listing, retrieving, creating, deleting,
activating, and linking BPA registrations.

Write operations follow the audit-before-write pattern:
1. Validate parameters (pre-flight, no audit record if validation fails)
2. Create PENDING audit record
3. Execute BPA API call
4. Update audit record to SUCCESS or FAILED

API Endpoints used:
- GET /registration - List all registrations
- GET /registration/{id} - Get registration by ID
- POST /registration - Create registration (with serviceId in body)
- DELETE /registration/{registration_id} - Delete registration
- POST /service_registration/{service_id}/{registration_id} - Link to service
- PUT /service/{service_id}/registration - Activate/deactivate registration

Note: The BPA API is service-centric. To get fields/determinants, use
the service-level endpoints (field_list, determinant_list with service_id).

Important: After creating a registration, you need TWO operations:
1. serviceregistration_link - Links registration to service AND activates it
2. registrationinstitution_create - Assigns institution (required for publishing)

Design principle: Elements are active by default upon creation/linking.
Use registration_activate with active=False to deactivate if needed.
"""

from __future__ import annotations

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

__all__ = [
    "registration_list",
    "registration_get",
    "registration_create",
    "registration_delete",
    "registration_activate",
    "serviceregistration_link",
    "register_registration_tools",
]


async def registration_list(service_id: str | int | None = None) -> dict[str, Any]:
    """List all BPA registrations.

    Returns registrations with optional service_id filter.
    Each registration includes id, name, and service_id.

    Note: The BPA API does not support server-side filtering by service_id.
    When service_id is provided, registrations are extracted from the service
    response (embedded in the service object).

    Args:
        service_id: Optional service ID to filter registrations by.

    Returns:
        dict: List of registrations with total count.
            - registrations: List of registration objects
            - total: Total number of registrations
    """
    try:
        async with BPAClient() as client:
            if service_id is not None:
                # BPA API embeds registrations in service response
                # Note: These are registration references (id, name only)
                try:
                    service_data = await client.get(
                        "/service/{id}",
                        path_params={"id": service_id},
                        resource_type="service",
                        resource_id=service_id,
                    )
                    registrations_data = service_data.get("registrations", [])
                except BPANotFoundError:
                    raise ToolError(
                        f"Service '{service_id}' not found. "
                        "Use 'service_list' to see available services."
                    )
            else:
                # Use global registration list
                registrations_data = await client.get_list(
                    "/registration",
                    resource_type="registration",
                )
    except ToolError:
        raise
    except BPAClientError as e:
        raise translate_error(e, resource_type="registration")

    # Transform to consistent output format
    registrations = []
    for reg in registrations_data:
        registrations.append(
            {
                "id": reg.get("id"),
                "name": reg.get("name"),
                "service_id": reg.get("serviceId")
                if service_id is None
                else service_id,
            }
        )

    return {
        "registrations": registrations,
        "total": len(registrations),
    }


async def registration_get(registration_id: str | int) -> dict[str, Any]:
    """Get details of a BPA registration by ID.

    Returns registration details including linked service info.
    Note: To get fields/determinants, use field_list(service_id) and
    determinant_list(service_id) with the service_id from this registration.

    Args:
        registration_id: The unique identifier of the registration.

    Returns:
        dict: Registration details including:
            - id, name, description, status
            - service_id: The parent service ID
            - service: Linked service summary (id, name)
    """
    try:
        async with BPAClient() as client:
            # Get registration details
            try:
                registration_data = await client.get(
                    "/registration/{id}",
                    path_params={"id": registration_id},
                    resource_type="registration",
                    resource_id=registration_id,
                )
            except BPANotFoundError:
                raise ToolError(
                    f"Registration '{registration_id}' not found. "
                    "Use 'registration_list' to see available registrations."
                )

            # Get linked service info (if exists)
            service_id = registration_data.get("serviceId")
            service_data: dict[str, Any] = {}
            if service_id:
                try:
                    service_data = await client.get(
                        "/service/{id}",
                        path_params={"id": service_id},
                        resource_type="service",
                        resource_id=service_id,
                    )
                except BPANotFoundError:
                    pass
    except ToolError:
        raise
    except BPAClientError as e:
        raise translate_error(
            e, resource_type="registration", resource_id=registration_id
        )

    service = {}
    if service_data:
        service = {
            "id": service_data.get("id"),
            "name": service_data.get("name"),
        }

    return {
        "id": registration_data.get("id"),
        "name": registration_data.get("name"),
        "description": registration_data.get("description"),
        "status": registration_data.get("status"),
        "service_id": service_id,
        "service": service,
    }


def _validate_registration_create_params(
    service_id: str | int,
    name: str,
    short_name: str,
    key: str,
    description: str | None,
) -> dict[str, Any]:
    """Validate registration_create parameters (pre-flight).

    Returns validated params dict or raises ToolError if invalid.
    No audit record is created for validation failures.

    Args:
        service_id: Parent service ID (required).
        name: Registration name (required).
        short_name: Short name for the registration (required).
        key: Unique key identifier for the registration (required).
        description: Registration description (optional).

    Returns:
        dict: Validated parameters ready for API call.

    Raises:
        ToolError: If validation fails.
    """
    errors = []

    if not service_id:
        errors.append("'service_id' is required")

    if not name or not name.strip():
        errors.append("'name' is required and cannot be empty")

    if name and len(name.strip()) > 255:
        errors.append("'name' must be 255 characters or less")

    if not short_name or not short_name.strip():
        errors.append("'short_name' is required and cannot be empty")

    if short_name and len(short_name.strip()) > 50:
        errors.append("'short_name' must be 50 characters or less")

    if not key or not key.strip():
        errors.append("'key' is required and cannot be empty")

    if key and len(key.strip()) > 100:
        errors.append("'key' must be 100 characters or less")

    if errors:
        error_msg = "; ".join(errors)
        raise ToolError(
            f"Cannot create registration: {error_msg}. "
            "Provide valid 'service_id', 'name', 'short_name', and 'key' parameters."
        )

    params: dict[str, Any] = {
        "name": name.strip(),
        "shortName": short_name.strip(),
        "key": key.strip(),
        "serviceId": str(service_id),
        "active": True,  # Elements are active by default
        "mandatorySelectedDefault": True,
    }
    if description:
        params["description"] = description.strip()

    return params


def _validate_registration_delete_params(
    registration_id: str | int,
) -> None:
    """Validate registration_delete parameters (pre-flight).

    Raises ToolError if validation fails.

    Args:
        registration_id: Registration ID to delete (required).

    Raises:
        ToolError: If validation fails.
    """
    if not registration_id:
        raise ToolError(
            "Cannot delete registration: 'registration_id' is required. "
            "Use 'registration_list' to find valid registration IDs."
        )


async def registration_create(
    service_id: str | int,
    name: str,
    short_name: str,
    key: str,
    description: str | None = None,
) -> dict[str, Any]:
    """Create a new BPA registration within a service.

    This operation follows the audit-before-write pattern:
    1. Validate parameters (pre-flight, no audit if validation fails)
    2. Verify parent service exists (no audit if service not found)
    3. Create PENDING audit record
    4. Execute POST /registration API call
    5. Update audit record to SUCCESS or FAILED

    Note: After creating a registration, you must assign an institution using
    registrationinstitution_create() for it to appear in "Registrations in
    the service" section of the BPA frontend.

    Design principle: Registrations are created as active by default.
    Use registration_activate with active=False to deactivate if needed.

    Args:
        service_id: ID of the parent service (required).
        name: Name of the registration (required).
        short_name: Short name for the registration (required).
        key: Unique key identifier for the registration (required).
        description: Description of the registration (optional).

    Returns:
        dict: Created registration details including:
            - id: The new registration ID
            - name, short_name, key, description, status
            - active: True (registrations are active by default)
            - service_id: The parent service ID
            - audit_id: The audit record ID

    Raises:
        ToolError: If validation fails, service not found, not authenticated,
            or API error.
    """
    # Pre-flight validation (no audit record for validation failures)
    validated_params = _validate_registration_create_params(
        service_id, name, short_name, key, description
    )

    # Get authenticated user for audit (before any API calls)
    try:
        user_email = get_current_user_email()
    except NotAuthenticatedError as e:
        raise ToolError(str(e))

    # Use single BPAClient connection for all operations
    try:
        async with BPAClient() as client:
            # Verify parent service exists before creating audit record
            try:
                await client.get(
                    "/service/{id}",
                    path_params={"id": service_id},
                    resource_type="service",
                    resource_id=service_id,
                )
            except BPANotFoundError:
                raise ToolError(
                    f"Cannot create registration: Service '{service_id}' not found. "
                    "Use 'service_list' to see available services."
                )

            # Create audit record BEFORE API call (audit-before-write pattern)
            audit_logger = AuditLogger()
            audit_id = await audit_logger.record_pending(
                user_email=user_email,
                operation_type="create",
                object_type="registration",
                params={
                    "service_id": str(service_id),
                    **validated_params,
                },
            )

            try:
                registration_data = await client.post(
                    "/registration",
                    json=validated_params,
                    resource_type="registration",
                )

                # Save rollback state (for create, save ID to enable deletion)
                created_id = registration_data.get("id")
                await audit_logger.save_rollback_state(
                    audit_id=audit_id,
                    object_type="registration",
                    object_id=str(created_id),
                    previous_state={
                        "id": created_id,
                        "name": registration_data.get("name"),
                        "shortName": registration_data.get("shortName"),
                        "key": registration_data.get("key"),
                        "description": registration_data.get("description"),
                        "serviceId": str(service_id),
                        "_operation": "create",  # Marker for rollback to DELETE
                    },
                )

                # Mark audit as success
                await audit_logger.mark_success(
                    audit_id,
                    result={
                        "registration_id": created_id,
                        "name": registration_data.get("name"),
                        "service_id": str(service_id),
                    },
                )

                return {
                    "id": created_id,
                    "name": registration_data.get("name"),
                    "short_name": registration_data.get("shortName"),
                    "key": registration_data.get("key"),
                    "description": registration_data.get("description"),
                    "status": registration_data.get("status"),
                    "active": registration_data.get("active", True),
                    "service_id": service_id,
                    "audit_id": audit_id,
                }

            except BPAClientError as e:
                # Mark audit as failed
                await audit_logger.mark_failed(audit_id, str(e))
                raise translate_error(e, resource_type="registration")

    except ToolError:
        raise
    except BPAClientError as e:
        raise translate_error(e, resource_type="service", resource_id=service_id)


async def registration_delete(
    registration_id: str | int,
) -> dict[str, Any]:
    """Delete a BPA registration.

    This operation follows the audit-before-write pattern:
    1. Validate parameters (pre-flight, no audit if validation fails)
    2. Capture current registration state for rollback
    3. Create PENDING audit record with previous_state
    4. Execute DELETE /registration/{registration_id} API call
    5. Update audit record to SUCCESS or FAILED

    Known Issue: The BPA server may return "Permission denied" errors even for
    authenticated users with appropriate roles. This is a server-side issue
    related to workflow permissions that cannot be resolved in the MCP client.
    If you encounter this error, contact your BPA administrator.

    Args:
        registration_id: ID of the registration to delete (required).

    Returns:
        dict: Deletion confirmation including:
            - deleted: True
            - registration_id: The deleted registration ID
            - deleted_registration: Summary of deleted registration (for rollback)
            - audit_id: The audit record ID

    Raises:
        ToolError: If validation fails, registration not found, not authenticated,
            permission denied (server-side), or API error.
    """
    # Pre-flight validation (no audit record for validation failures)
    _validate_registration_delete_params(registration_id)

    # Get authenticated user for audit
    try:
        user_email = get_current_user_email()
    except NotAuthenticatedError as e:
        raise ToolError(str(e))

    # Capture current state for rollback BEFORE making changes
    try:
        async with BPAClient() as client:
            try:
                previous_state = await client.get(
                    "/registration/{id}",
                    path_params={"id": registration_id},
                    resource_type="registration",
                    resource_id=registration_id,
                )
            except BPANotFoundError:
                raise ToolError(
                    f"Registration '{registration_id}' not found. "
                    "Use 'registration_list' to see available registrations."
                )

            # BPA API doesn't return serviceId in registration GET response
            # We need to find the parent service by checking all services
            service_id = previous_state.get("serviceId")
            if not service_id:
                # Search for the service containing this registration
                services = await client.get_list("/service", resource_type="service")
                for svc in services:
                    svc_id = svc.get("id")
                    try:
                        svc_detail = await client.get(
                            "/service/{id}",
                            path_params={"id": svc_id},
                            resource_type="service",
                            resource_id=svc_id,
                        )
                        for reg in svc_detail.get("registrations", []):
                            if str(reg.get("id")) == str(registration_id):
                                service_id = svc_id
                                break
                    except BPANotFoundError:
                        continue
                    if service_id:
                        break

    except ToolError:
        raise
    except BPAClientError as e:
        raise translate_error(
            e, resource_type="registration", resource_id=registration_id
        )

    # Build complete previous state for rollback (includes service_id)
    rollback_previous_state = {
        "id": previous_state.get("id"),
        "name": previous_state.get("name"),
        "shortName": previous_state.get("shortName"),
        "key": previous_state.get("key"),
        "description": previous_state.get("description"),
        "serviceId": service_id,  # Now we have the service_id
    }

    # Normalize previous_state to snake_case for response
    normalized_previous_state = {
        "id": previous_state.get("id"),
        "name": previous_state.get("name"),
        "description": previous_state.get("description"),
        "service_id": service_id,
        "status": previous_state.get("status"),
    }

    # Create audit record BEFORE API call (audit-before-write pattern)
    audit_logger = AuditLogger()
    audit_id = await audit_logger.record_pending(
        user_email=user_email,
        operation_type="delete",
        object_type="registration",
        object_id=str(registration_id),
        params={"service_id": service_id},  # Include service_id for rollback
    )

    # Save rollback state for undo capability (recreate on rollback)
    await audit_logger.save_rollback_state(
        audit_id=audit_id,
        object_type="registration",
        object_id=str(registration_id),
        previous_state=rollback_previous_state,
    )

    try:
        async with BPAClient() as client:
            await client.delete(
                "/registration/{id}",
                path_params={"id": registration_id},
                resource_type="registration",
                resource_id=registration_id,
            )

        # Mark audit as success
        await audit_logger.mark_success(
            audit_id,
            result={
                "deleted": True,
                "registration_id": str(registration_id),
            },
        )

        return {
            "deleted": True,
            "registration_id": registration_id,
            "deleted_registration": {
                "id": normalized_previous_state["id"],
                "name": normalized_previous_state["name"],
                "service_id": normalized_previous_state["service_id"],
            },
            "audit_id": audit_id,
        }

    except BPAClientError as e:
        # Mark audit as failed
        await audit_logger.mark_failed(audit_id, str(e))
        raise translate_error(
            e, resource_type="registration", resource_id=registration_id
        )


async def registration_activate(
    service_id: str | int,
    registration_id: str | int,
    active: bool = True,
) -> dict[str, Any]:
    """Activate or deactivate a registration within a service.

    This operation follows the audit-before-write pattern:
    1. Validate parameters (pre-flight, no audit if validation fails)
    2. Verify service and registration exist
    3. Create PENDING audit record
    4. Execute PUT /service/{service_id}/registration API call
    5. Update audit record to SUCCESS or FAILED

    Args:
        service_id: ID of the service containing the registration (required).
        registration_id: ID of the registration to activate/deactivate (required).
        active: True to activate, False to deactivate (default: True).

    Returns:
        dict: Activation result including:
            - service_id: The service ID
            - registration_id: The registration ID
            - registration_name: Name of the registration
            - active: The new active status
            - audit_id: The audit record ID

    Raises:
        ToolError: If validation fails, service/registration not found,
            not authenticated, or API error.
    """
    # Pre-flight validation
    errors = []
    if not service_id:
        errors.append("'service_id' is required")
    if not registration_id:
        errors.append("'registration_id' is required")
    if errors:
        error_msg = "; ".join(errors)
        raise ToolError(
            f"Cannot activate/deactivate registration: {error_msg}. "
            "Provide valid 'service_id' and 'registration_id' parameters."
        )

    # Get authenticated user for audit
    try:
        user_email = get_current_user_email()
    except NotAuthenticatedError as e:
        raise ToolError(str(e))

    try:
        async with BPAClient() as client:
            # Verify service exists
            try:
                await client.get(
                    "/service/{id}",
                    path_params={"id": service_id},
                    resource_type="service",
                    resource_id=service_id,
                )
            except BPANotFoundError:
                raise ToolError(
                    f"Cannot activate registration: Service '{service_id}' not found. "
                    "Use 'service_list' to see available services."
                )

            # Verify registration exists and get its details
            try:
                registration_data = await client.get(
                    "/registration/{id}",
                    path_params={"id": registration_id},
                    resource_type="registration",
                    resource_id=registration_id,
                )
            except BPANotFoundError:
                raise ToolError(
                    f"Registration '{registration_id}' not found. "
                    "Use 'registration_list' to see available registrations."
                )

            # Create audit record BEFORE API call
            audit_logger = AuditLogger()
            audit_id = await audit_logger.record_pending(
                user_email=user_email,
                operation_type="update",
                object_type="registration",
                object_id=str(registration_id),
                params={
                    "service_id": str(service_id),
                    "registration_id": str(registration_id),
                    "active": active,
                },
            )

            try:
                # Build payload - include registration data with active flag
                payload = {
                    "id": str(registration_id),
                    "name": registration_data.get("name"),
                    "shortName": registration_data.get("shortName"),
                    "key": registration_data.get("key"),
                    "active": active,
                }

                # PUT /service/{service_id}/registration
                await client.put(
                    "/service/{service_id}/registration",
                    path_params={"service_id": service_id},
                    json=payload,
                    resource_type="registration",
                )

                # Save rollback state
                await audit_logger.save_rollback_state(
                    audit_id=audit_id,
                    object_type="registration",
                    object_id=str(registration_id),
                    previous_state={
                        "service_id": str(service_id),
                        "registration_id": str(registration_id),
                        "active": not active,  # Previous state was opposite
                        "_operation": "activate",
                    },
                )

                # Mark audit as success
                await audit_logger.mark_success(
                    audit_id,
                    result={
                        "service_id": str(service_id),
                        "registration_id": str(registration_id),
                        "active": active,
                    },
                )

                return {
                    "service_id": str(service_id),
                    "registration_id": str(registration_id),
                    "registration_name": registration_data.get("name"),
                    "active": active,
                    "audit_id": audit_id,
                }

            except BPAClientError as e:
                await audit_logger.mark_failed(audit_id, str(e))
                raise translate_error(e, resource_type="registration")

    except ToolError:
        raise
    except BPAClientError as e:
        raise translate_error(e, resource_type="registration")


async def serviceregistration_link(
    service_id: str | int,
    registration_id: str | int,
) -> dict[str, Any]:
    """Link an existing registration to a service and activate it.

    This operation adds a registration to a service's "Registrations in the service"
    section in the BPA frontend and activates it by default. Without this linking,
    registrations appear in "Other registrations" and cannot be used with the service.

    This operation follows the audit-before-write pattern:
    1. Validate parameters (pre-flight, no audit if validation fails)
    2. Verify both service and registration exist
    3. Create PENDING audit record
    4. Execute POST /service_registration/{service_id}/{registration_id} API call
    5. Activate the registration via PUT /service/{service_id}/registration
    6. Update audit record to SUCCESS or FAILED

    Note: This is different from registrationinstitution_create which assigns
    an institution to a registration. Both operations may be needed:
    - serviceregistration_link: Links registration to service (appears in UI, activates)
    - registrationinstitution_create: Assigns institution (required for publishing)

    Args:
        service_id: ID of the service to link the registration to (required).
        registration_id: ID of the registration to link (required).

    Returns:
        dict: Link result including:
            - service_id: The service ID
            - registration_id: The registration ID
            - service_name: Name of the service
            - registration_name: Name of the registration
            - linked: True if successful
            - active: True (registration is activated after linking)
            - audit_id: The audit record ID

    Raises:
        ToolError: If validation fails, service/registration not found,
            not authenticated, or API error.
    """
    # Pre-flight validation
    errors = []
    if not service_id:
        errors.append("'service_id' is required")
    if not registration_id:
        errors.append("'registration_id' is required")
    if errors:
        error_msg = "; ".join(errors)
        raise ToolError(
            f"Cannot link registration to service: {error_msg}. "
            "Provide valid 'service_id' and 'registration_id' parameters."
        )

    # Get authenticated user for audit
    try:
        user_email = get_current_user_email()
    except NotAuthenticatedError as e:
        raise ToolError(str(e))

    try:
        async with BPAClient() as client:
            # Verify service exists
            try:
                service_data = await client.get(
                    "/service/{id}",
                    path_params={"id": service_id},
                    resource_type="service",
                    resource_id=service_id,
                )
            except BPANotFoundError:
                raise ToolError(
                    f"Cannot link registration: Service '{service_id}' not found. "
                    "Use 'service_list' to see available services."
                )

            # Verify registration exists
            try:
                registration_data = await client.get(
                    "/registration/{id}",
                    path_params={"id": registration_id},
                    resource_type="registration",
                    resource_id=registration_id,
                )
            except BPANotFoundError:
                raise ToolError(
                    f"Registration '{registration_id}' not found. "
                    "Use 'registration_list' to see available registrations."
                )

            # Create audit record BEFORE API call
            audit_logger = AuditLogger()
            audit_id = await audit_logger.record_pending(
                user_email=user_email,
                operation_type="link",
                object_type="service_registration",
                params={
                    "service_id": str(service_id),
                    "registration_id": str(registration_id),
                },
            )

            try:
                # POST /service_registration/{service_id}/{registration_id}
                await client.post(
                    "/service_registration/{service_id}/{registration_id}",
                    path_params={
                        "service_id": service_id,
                        "registration_id": registration_id,
                    },
                    json={"responseType": "text"},
                    resource_type="service_registration",
                )

                # Save rollback state (for unlink capability)
                await audit_logger.save_rollback_state(
                    audit_id=audit_id,
                    object_type="service_registration",
                    object_id=f"{service_id}_{registration_id}",
                    previous_state={
                        "service_id": str(service_id),
                        "registration_id": str(registration_id),
                        "_operation": "link",
                    },
                )

                # Activate the registration by default after linking
                # Build payload for activation
                activate_payload = {
                    "id": str(registration_id),
                    "name": registration_data.get("name"),
                    "shortName": registration_data.get("shortName"),
                    "key": registration_data.get("key"),
                    "active": True,
                }

                # PUT /service/{service_id}/registration to activate
                await client.put(
                    "/service/{service_id}/registration",
                    path_params={"service_id": service_id},
                    json=activate_payload,
                    resource_type="registration",
                )

                # Mark audit as success
                await audit_logger.mark_success(
                    audit_id,
                    result={
                        "service_id": str(service_id),
                        "registration_id": str(registration_id),
                        "linked": True,
                        "active": True,
                    },
                )

                return {
                    "service_id": str(service_id),
                    "registration_id": str(registration_id),
                    "service_name": service_data.get("name"),
                    "registration_name": registration_data.get("name"),
                    "linked": True,
                    "active": True,
                    "audit_id": audit_id,
                }

            except BPAClientError as e:
                await audit_logger.mark_failed(audit_id, str(e))
                raise translate_error(e, resource_type="service_registration")

    except ToolError:
        raise
    except BPAClientError as e:
        raise translate_error(e, resource_type="service_registration")


def register_registration_tools(mcp: Any) -> None:
    """Register registration tools with the MCP server.

    Args:
        mcp: The FastMCP server instance.
    """
    # Read operations
    mcp.tool()(registration_list)
    mcp.tool()(registration_get)
    # Write operations (audit-before-write pattern)
    mcp.tool()(registration_create)
    mcp.tool()(registration_delete)
    mcp.tool()(registration_activate)
    mcp.tool()(serviceregistration_link)

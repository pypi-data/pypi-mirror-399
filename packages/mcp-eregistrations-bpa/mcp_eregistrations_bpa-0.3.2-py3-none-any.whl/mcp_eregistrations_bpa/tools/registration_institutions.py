"""MCP tools for BPA registration institution operations.

This module provides tools for listing, retrieving, creating, and deleting
registration institution assignments. Registration institutions link a
registration to an institution, which is required for publishing services.

Write operations follow the audit-before-write pattern:
1. Validate parameters (pre-flight, no audit record if validation fails)
2. Create PENDING audit record
3. Execute BPA API call
4. Update audit record to SUCCESS or FAILED

API Endpoints used:
- GET /registration/{registration_id}/registration_institution - List for registration
- POST /registration/{registration_id}/registration_institution - Create assignment
- GET /registration_institution/{registration_institution_id} - Get by ID
- DELETE /registration_institution/{registration_institution_id} - Delete assignment
- GET /registration_institution_by_institution/{institution_id} - List by institution
"""

from __future__ import annotations

import os
from typing import Any

import httpx
from mcp.server.fastmcp.exceptions import ToolError

from mcp_eregistrations_bpa.audit.context import (
    NotAuthenticatedError,
    get_current_user_email,
    get_token_manager,
)
from mcp_eregistrations_bpa.audit.logger import AuditLogger
from mcp_eregistrations_bpa.bpa_client import BPAClient
from mcp_eregistrations_bpa.bpa_client.errors import (
    BPAClientError,
    BPANotFoundError,
    translate_error,
)
from mcp_eregistrations_bpa.config import load_config

__all__ = [
    "registrationinstitution_list",
    "registrationinstitution_get",
    "registrationinstitution_create",
    "registrationinstitution_delete",
    "registrationinstitution_list_by_institution",
    "institution_discover",
    "institution_create",
    "register_registration_institution_tools",
]

# Default institutions parent group ID in Keycloak
# Can be overridden with KEYCLOAK_INSTITUTIONS_GROUP_ID env var
DEFAULT_INSTITUTIONS_PARENT_GROUP = "967d3d31-5114-4131-b7e1-f5c652227259"


def _transform_response(data: dict[str, Any]) -> dict[str, Any]:
    """Transform registration institution API response from camelCase to snake_case.

    Args:
        data: Raw API response with camelCase keys.

    Returns:
        dict: Transformed response with snake_case keys.
    """
    return {
        "id": data.get("id"),
        "registration_id": data.get("registrationId"),
        "institution_id": data.get("institutionId"),
    }


async def registrationinstitution_list(
    registration_id: str | int,
) -> dict[str, Any]:
    """List all institution assignments for a BPA registration.

    Returns institution assignments configured for the specified registration.
    Each assignment links the registration to an institution.

    Args:
        registration_id: The registration ID to list institutions for (required).

    Returns:
        dict: List of institution assignments with total count.
            - assignments: List of registration institution objects
            - registration_id: The queried registration ID
            - total: Total number of assignments
    """
    if not registration_id:
        raise ToolError(
            "Cannot list registration institutions: 'registration_id' is required. "
            "Use 'registration_list' to find valid registration IDs."
        )

    try:
        async with BPAClient() as client:
            try:
                data = await client.get_list(
                    "/registration/{registration_id}/registration_institution",
                    path_params={"registration_id": registration_id},
                    resource_type="registration_institution",
                )
            except BPANotFoundError:
                raise ToolError(
                    f"Registration '{registration_id}' not found. "
                    "Use 'registration_list' to see available registrations."
                )
    except ToolError:
        raise
    except BPAClientError as e:
        raise translate_error(e, resource_type="registration_institution")

    # Transform to consistent output format
    assignments = [_transform_response(item) for item in data]

    return {
        "assignments": assignments,
        "registration_id": registration_id,
        "total": len(assignments),
    }


async def registrationinstitution_get(
    registration_institution_id: str | int,
) -> dict[str, Any]:
    """Get details of a BPA registration institution assignment by ID.

    Returns the registration institution assignment details.

    Args:
        registration_institution_id: The unique identifier of the assignment.

    Returns:
        dict: Assignment details including:
            - id: Unique identifier
            - registration_id: The registration ID
            - institution_id: The institution ID
    """
    if not registration_institution_id:
        raise ToolError(
            "Cannot get registration institution: "
            "'registration_institution_id' is required."
        )

    try:
        async with BPAClient() as client:
            try:
                data = await client.get(
                    "/registration_institution/{registration_institution_id}",
                    path_params={
                        "registration_institution_id": registration_institution_id
                    },
                )
            except BPANotFoundError:
                raise ToolError(
                    f"Registration institution '{registration_institution_id}' "
                    "not found."
                )
    except ToolError:
        raise
    except BPAClientError as e:
        raise translate_error(e, resource_type="registration_institution")

    return _transform_response(data)


async def registrationinstitution_create(
    registration_id: str | int,
    institution_id: str,
) -> dict[str, Any]:
    """Assign an institution to a BPA registration.

    This operation follows the audit-before-write pattern:
    1. Validate parameters (pre-flight, no audit if validation fails)
    2. Verify parent registration exists (no audit if not found)
    3. Create PENDING audit record
    4. Execute POST /registration/{registration_id}/registration_institution API call
    5. Update audit record to SUCCESS or FAILED

    Institution assignment is required for publishing a service.

    Args:
        registration_id: ID of the registration to assign institution to (required).
        institution_id: ID of the institution to assign (required).

    Returns:
        dict: Created assignment details including:
            - id: The new assignment ID
            - registration_id: The registration ID
            - institution_id: The institution ID
            - audit_id: The audit record ID

    Raises:
        ToolError: If validation fails, registration not found, not authenticated,
            or API error.
    """
    # Pre-flight validation (no audit if these fail)
    if not registration_id:
        raise ToolError(
            "Cannot create registration institution: 'registration_id' is required. "
            "Use 'registration_list' to find valid registration IDs."
        )
    if not institution_id:
        raise ToolError(
            "Cannot create registration institution: 'institution_id' is required."
        )

    # Get user email for audit
    try:
        user_email = get_current_user_email()
    except NotAuthenticatedError:
        raise ToolError(
            "Authentication required to create registration institution assignment. "
            "Use 'auth_login' to authenticate first."
        )

    audit_logger = AuditLogger()

    try:
        async with BPAClient() as client:
            # Verify registration exists (no audit if not found)
            try:
                await client.get(
                    "/registration/{registration_id}",
                    path_params={"registration_id": registration_id},
                )
            except BPANotFoundError:
                raise ToolError(
                    f"Registration '{registration_id}' not found. "
                    "Use 'registration_list' to see available registrations."
                )

            # Create PENDING audit record
            audit_id = await audit_logger.record_pending(
                user_email=user_email,
                operation_type="create",
                object_type="registration_institution",
                params={
                    "registration_id": registration_id,
                    "institution_id": institution_id,
                },
            )

            # Execute API call - body is the raw institution_id string
            try:
                result = await client.post(
                    "/registration/{registration_id}/registration_institution",
                    path_params={"registration_id": registration_id},
                    content=institution_id,
                )

                # Mark audit success
                await audit_logger.mark_success(
                    audit_id=audit_id,
                    result=result,
                )

            except Exception as e:
                # Mark audit failed
                await audit_logger.mark_failed(
                    audit_id=audit_id,
                    error_message=str(e),
                )
                raise

    except ToolError:
        raise
    except BPAClientError as e:
        raise translate_error(e, resource_type="registration_institution")

    response = _transform_response(result)
    response["audit_id"] = audit_id
    return response


async def registrationinstitution_delete(
    registration_institution_id: str | int,
) -> dict[str, Any]:
    """Delete a BPA registration institution assignment.

    This operation follows the audit-before-write pattern:
    1. Validate parameters (pre-flight, no audit if validation fails)
    2. Capture current state for rollback
    3. Create PENDING audit record with previous_state
    4. Execute DELETE /registration_institution/{id} API call
    5. Update audit record to SUCCESS or FAILED

    Args:
        registration_institution_id: ID of the assignment to delete (required).

    Returns:
        dict: Deletion confirmation including:
            - deleted: True
            - registration_institution_id: The deleted assignment ID
            - deleted_assignment: Summary of deleted assignment (for rollback)
            - audit_id: The audit record ID

    Raises:
        ToolError: If validation fails, assignment not found, not authenticated,
            or API error.
    """
    # Pre-flight validation
    if not registration_institution_id:
        raise ToolError(
            "Cannot delete registration institution: "
            "'registration_institution_id' is required."
        )

    # Get user email for audit
    try:
        user_email = get_current_user_email()
    except NotAuthenticatedError:
        raise ToolError(
            "Authentication required to delete registration institution assignment. "
            "Use 'auth_login' to authenticate first."
        )

    audit_logger = AuditLogger()

    try:
        async with BPAClient() as client:
            # Capture current state for rollback
            try:
                current_state = await client.get(
                    "/registration_institution/{registration_institution_id}",
                    path_params={
                        "registration_institution_id": registration_institution_id
                    },
                )
            except BPANotFoundError:
                raise ToolError(
                    f"Registration institution '{registration_institution_id}' "
                    "not found."
                )

            # Create PENDING audit record
            audit_id = await audit_logger.record_pending(
                user_email=user_email,
                operation_type="delete",
                object_type="registration_institution",
                object_id=str(registration_institution_id),
                params={"registration_institution_id": registration_institution_id},
            )

            # Save rollback state separately
            await audit_logger.save_rollback_state(
                audit_id=audit_id,
                object_type="registration_institution",
                object_id=str(registration_institution_id),
                previous_state=current_state,
            )

            # Execute delete
            try:
                await client.delete(
                    "/registration_institution/{registration_institution_id}",
                    path_params={
                        "registration_institution_id": registration_institution_id
                    },
                )

                # Mark audit success
                await audit_logger.mark_success(
                    audit_id=audit_id,
                    result={"deleted": True},
                )

            except Exception as e:
                # Mark audit failed
                await audit_logger.mark_failed(
                    audit_id=audit_id,
                    error_message=str(e),
                )
                raise

    except ToolError:
        raise
    except BPAClientError as e:
        raise translate_error(e, resource_type="registration_institution")

    return {
        "deleted": True,
        "registration_institution_id": registration_institution_id,
        "deleted_assignment": _transform_response(current_state),
        "audit_id": audit_id,
    }


async def registrationinstitution_list_by_institution(
    institution_id: str,
) -> dict[str, Any]:
    """List all registration assignments for a specific institution.

    Returns all registrations that are assigned to the specified institution.

    Args:
        institution_id: The institution ID to list registrations for (required).

    Returns:
        dict: List of registration assignments with total count.
            - assignments: List of registration institution objects
            - institution_id: The queried institution ID
            - total: Total number of assignments
    """
    if not institution_id:
        raise ToolError("Cannot list by institution: 'institution_id' is required.")

    try:
        async with BPAClient() as client:
            try:
                data = await client.get_list(
                    "/registration_institution_by_institution/{institution_id}",
                    path_params={"institution_id": institution_id},
                    resource_type="registration_institution",
                )
            except BPANotFoundError:
                # Institution may have no assignments
                data = []
    except BPAClientError as e:
        raise translate_error(e, resource_type="registration_institution")

    # Transform to consistent output format
    assignments = [_transform_response(item) for item in data]

    return {
        "assignments": assignments,
        "institution_id": institution_id,
        "total": len(assignments),
    }


async def institution_discover(
    sample_size: int = 50,
) -> dict[str, Any]:
    """Discover available institution IDs by scanning existing registrations.

    Since BPA doesn't have a direct endpoint to list institutions, this tool
    scans existing registration-institution assignments to discover all
    unique institution IDs that are in use.

    This is useful for finding valid institution IDs to use when assigning
    institutions to new registrations.

    Args:
        sample_size: Number of registrations to sample (default 50).
            Larger values find more institutions but take longer.

    Returns:
        dict: Discovery results including:
            - institutions: List of unique institution IDs found
            - total: Number of unique institutions found
            - registrations_scanned: Number of registrations checked
            - registrations_with_institutions: Count of registrations with assignments
            - message: Human-readable summary

    Note:
        This tool queries multiple registrations, so it may take a few seconds.
        For quick testing, a single known institution ID can be used directly.
    """
    try:
        async with BPAClient() as client:
            # Get list of registrations
            try:
                registrations = await client.get_list(
                    "/registration",
                    resource_type="registration",
                )
            except BPANotFoundError:
                return {
                    "institutions": [],
                    "total": 0,
                    "registrations_scanned": 0,
                    "registrations_with_institutions": 0,
                    "message": "No registrations found in the system.",
                }

            # Limit to sample size
            sample = registrations[:sample_size]

            # Collect unique institution IDs
            institution_ids: set[str] = set()
            registrations_with_institutions = 0

            for reg in sample:
                reg_id = reg.get("id")
                if not reg_id:
                    continue

                try:
                    assignments = await client.get_list(
                        "/registration/{registration_id}/registration_institution",
                        path_params={"registration_id": reg_id},
                        resource_type="registration_institution",
                    )

                    if assignments:
                        registrations_with_institutions += 1
                        for assignment in assignments:
                            inst_id = assignment.get("institutionId")
                            if inst_id:
                                institution_ids.add(inst_id)
                except BPANotFoundError:
                    # Registration may have been deleted
                    continue
                except Exception:
                    # Skip problematic registrations
                    continue

            institutions_list = sorted(institution_ids)

            if not institutions_list:
                message = (
                    f"Scanned {len(sample)} registrations but found no institution "
                    "assignments. Institution IDs may need to be obtained from "
                    "your BPA administrator."
                )
            else:
                message = (
                    f"Found {len(institutions_list)} unique institution(s) from "
                    f"{registrations_with_institutions} assigned registrations. "
                    f"Use any of these IDs with registrationinstitution_create."
                )

            return {
                "institutions": institutions_list,
                "total": len(institutions_list),
                "registrations_scanned": len(sample),
                "registrations_with_institutions": registrations_with_institutions,
                "message": message,
            }

    except BPAClientError as e:
        raise translate_error(e, resource_type="institution")


async def institution_create(
    name: str,
    short_name: str,
    url: str | None = None,
) -> dict[str, Any]:
    """Create a new institution in Keycloak.

    Institutions in BPA are managed as Keycloak groups under a parent
    "institutions" group. This tool creates a new institution group
    in Keycloak that can then be assigned to registrations.

    This operation follows the audit-before-write pattern:
    1. Validate parameters (pre-flight, no audit if validation fails)
    2. Create PENDING audit record
    3. Execute POST to Keycloak Admin API
    4. Update audit record to SUCCESS or FAILED

    Args:
        name: Display name of the institution (required).
        short_name: Short name/abbreviation (required).
        url: Optional URL for the institution's website.

    Returns:
        dict: Created institution details including:
            - id: The new institution ID (Keycloak group ID)
            - name: The institution name
            - short_name: The short name
            - url: The URL if provided
            - path: Keycloak group path
            - audit_id: The audit record ID

    Raises:
        ToolError: If validation fails, not authenticated, or API error.

    Note:
        The parent group ID for institutions is configured via
        KEYCLOAK_INSTITUTIONS_GROUP_ID environment variable or defaults
        to the standard eRegistrations institutions group.
    """
    # Pre-flight validation
    if not name or not name.strip():
        raise ToolError("Cannot create institution: 'name' is required.")
    if not short_name or not short_name.strip():
        raise ToolError("Cannot create institution: 'short_name' is required.")

    name = name.strip()
    short_name = short_name.strip()

    # Get user email for audit
    try:
        user_email = get_current_user_email()
    except NotAuthenticatedError:
        raise ToolError(
            "Authentication required to create institution. "
            "Use 'auth_login' to authenticate first."
        )

    # Get token manager for Keycloak API calls
    token_manager = get_token_manager()

    # Load config to get Keycloak URL and realm
    config = load_config()
    if not config.keycloak_url or not config.keycloak_realm:
        raise ToolError(
            "Keycloak configuration required for institution management. "
            "Set KEYCLOAK_URL and KEYCLOAK_REALM environment variables."
        )

    # Get parent group ID from env or use default
    parent_group_id = os.environ.get(
        "KEYCLOAK_INSTITUTIONS_GROUP_ID", DEFAULT_INSTITUTIONS_PARENT_GROUP
    )

    audit_logger = AuditLogger()

    # Prepare request payload
    attributes: dict[str, list[str]] = {
        "shortName": [short_name],
    }
    if url:
        attributes["url"] = [url]

    payload = {
        "name": name,
        "attributes": attributes,
    }

    # Create PENDING audit record
    audit_id = await audit_logger.record_pending(
        user_email=user_email,
        operation_type="create",
        object_type="institution",
        params={
            "name": name,
            "short_name": short_name,
            "url": url,
            "parent_group_id": parent_group_id,
        },
    )

    try:
        # Get access token
        access_token = await token_manager.get_access_token()

        # Build Keycloak Admin API URL
        keycloak_url = (
            f"{config.keycloak_url}/admin/realms/{config.keycloak_realm}"
            f"/groups/{parent_group_id}/children"
        )

        # Make the request to Keycloak
        async with httpx.AsyncClient() as client:
            response = await client.post(
                keycloak_url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )

            if response.status_code == 409:
                await audit_logger.mark_failed(audit_id, "Institution already exists")
                raise ToolError(
                    f"Institution '{name}' already exists. "
                    "Use 'institution_discover' to find existing institutions."
                )

            if response.status_code == 403:
                await audit_logger.mark_failed(audit_id, "Permission denied")
                raise ToolError(
                    "Permission denied to create institution. "
                    "Ensure your account has Keycloak admin privileges."
                )

            if response.status_code == 404:
                await audit_logger.mark_failed(audit_id, "Parent group not found")
                raise ToolError(
                    f"Institutions parent group '{parent_group_id}' not found. "
                    "Check KEYCLOAK_INSTITUTIONS_GROUP_ID configuration."
                )

            response.raise_for_status()
            result = response.json()

        # Mark audit success
        await audit_logger.mark_success(
            audit_id=audit_id,
            result={"id": result.get("id"), **result},
        )

        # Return formatted response
        return {
            "id": result.get("id"),
            "name": result.get("name"),
            "short_name": short_name,
            "url": url,
            "path": result.get("path"),
            "audit_id": audit_id,
            "message": (
                f"Institution '{name}' created successfully. "
                "Use this ID with registrationinstitution_create to assign."
            ),
        }

    except ToolError:
        raise
    except httpx.HTTPStatusError as e:
        error_msg = f"Keycloak API error: {e.response.status_code}"
        try:
            error_detail = e.response.json()
            if "errorMessage" in error_detail:
                error_msg = f"Keycloak error: {error_detail['errorMessage']}"
        except Exception:
            pass
        await audit_logger.mark_failed(audit_id, error_msg)
        raise ToolError(error_msg)
    except httpx.RequestError as e:
        error_msg = f"Network error connecting to Keycloak: {e}"
        await audit_logger.mark_failed(audit_id, error_msg)
        raise ToolError(error_msg)
    except Exception as e:
        await audit_logger.mark_failed(audit_id, str(e))
        raise ToolError(f"Failed to create institution: {e}")


def register_registration_institution_tools(mcp_server: Any) -> None:
    """Register registration institution tools with the MCP server.

    Args:
        mcp_server: The FastMCP server instance.
    """
    mcp_server.tool()(registrationinstitution_list)
    mcp_server.tool()(registrationinstitution_get)
    mcp_server.tool()(registrationinstitution_create)
    mcp_server.tool()(registrationinstitution_delete)
    mcp_server.tool()(registrationinstitution_list_by_institution)
    mcp_server.tool()(institution_discover)
    mcp_server.tool()(institution_create)

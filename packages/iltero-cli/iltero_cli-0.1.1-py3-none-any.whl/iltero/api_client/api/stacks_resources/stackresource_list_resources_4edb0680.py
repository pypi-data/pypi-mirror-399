from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    stack_id: str,
    *,
    resource_type: None | str | Unset = UNSET,
    lifecycle_status: None | str | Unset = UNSET,
    drift_detected: bool | None | Unset = UNSET,
    active_only: bool | Unset = True,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_resource_type: None | str | Unset
    if isinstance(resource_type, Unset):
        json_resource_type = UNSET
    else:
        json_resource_type = resource_type
    params["resource_type"] = json_resource_type

    json_lifecycle_status: None | str | Unset
    if isinstance(lifecycle_status, Unset):
        json_lifecycle_status = UNSET
    else:
        json_lifecycle_status = lifecycle_status
    params["lifecycle_status"] = json_lifecycle_status

    json_drift_detected: bool | None | Unset
    if isinstance(drift_detected, Unset):
        json_drift_detected = UNSET
    else:
        json_drift_detected = drift_detected
    params["drift_detected"] = json_drift_detected

    params["active_only"] = active_only

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/stacks/{stack_id}/resources/",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> APIResponseModel | None:
    if response.status_code == 200:
        response_200 = APIResponseModel.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[APIResponseModel]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    stack_id: str,
    *,
    client: AuthenticatedClient,
    resource_type: None | str | Unset = UNSET,
    lifecycle_status: None | str | Unset = UNSET,
    drift_detected: bool | None | Unset = UNSET,
    active_only: bool | Unset = True,
) -> Response[APIResponseModel]:
    """List Resources

     List resources in a stack with optional filtering.

    Args:
        resource_type: Filter by resource type
        lifecycle_status: Filter by lifecycle status
        drift_detected: Filter by drift detection status
        active_only: Include only non-destroyed resources (default: True)

    Args:
        stack_id (str):
        resource_type (None | str | Unset):
        lifecycle_status (None | str | Unset):
        drift_detected (bool | None | Unset):
        active_only (bool | Unset):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        stack_id=stack_id,
        resource_type=resource_type,
        lifecycle_status=lifecycle_status,
        drift_detected=drift_detected,
        active_only=active_only,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    stack_id: str,
    *,
    client: AuthenticatedClient,
    resource_type: None | str | Unset = UNSET,
    lifecycle_status: None | str | Unset = UNSET,
    drift_detected: bool | None | Unset = UNSET,
    active_only: bool | Unset = True,
) -> APIResponseModel | None:
    """List Resources

     List resources in a stack with optional filtering.

    Args:
        resource_type: Filter by resource type
        lifecycle_status: Filter by lifecycle status
        drift_detected: Filter by drift detection status
        active_only: Include only non-destroyed resources (default: True)

    Args:
        stack_id (str):
        resource_type (None | str | Unset):
        lifecycle_status (None | str | Unset):
        drift_detected (bool | None | Unset):
        active_only (bool | Unset):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        stack_id=stack_id,
        client=client,
        resource_type=resource_type,
        lifecycle_status=lifecycle_status,
        drift_detected=drift_detected,
        active_only=active_only,
    ).parsed


async def asyncio_detailed(
    stack_id: str,
    *,
    client: AuthenticatedClient,
    resource_type: None | str | Unset = UNSET,
    lifecycle_status: None | str | Unset = UNSET,
    drift_detected: bool | None | Unset = UNSET,
    active_only: bool | Unset = True,
) -> Response[APIResponseModel]:
    """List Resources

     List resources in a stack with optional filtering.

    Args:
        resource_type: Filter by resource type
        lifecycle_status: Filter by lifecycle status
        drift_detected: Filter by drift detection status
        active_only: Include only non-destroyed resources (default: True)

    Args:
        stack_id (str):
        resource_type (None | str | Unset):
        lifecycle_status (None | str | Unset):
        drift_detected (bool | None | Unset):
        active_only (bool | Unset):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        stack_id=stack_id,
        resource_type=resource_type,
        lifecycle_status=lifecycle_status,
        drift_detected=drift_detected,
        active_only=active_only,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    stack_id: str,
    *,
    client: AuthenticatedClient,
    resource_type: None | str | Unset = UNSET,
    lifecycle_status: None | str | Unset = UNSET,
    drift_detected: bool | None | Unset = UNSET,
    active_only: bool | Unset = True,
) -> APIResponseModel | None:
    """List Resources

     List resources in a stack with optional filtering.

    Args:
        resource_type: Filter by resource type
        lifecycle_status: Filter by lifecycle status
        drift_detected: Filter by drift detection status
        active_only: Include only non-destroyed resources (default: True)

    Args:
        stack_id (str):
        resource_type (None | str | Unset):
        lifecycle_status (None | str | Unset):
        drift_detected (bool | None | Unset):
        active_only (bool | Unset):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            stack_id=stack_id,
            client=client,
            resource_type=resource_type,
            lifecycle_status=lifecycle_status,
            drift_detected=drift_detected,
            active_only=active_only,
        )
    ).parsed

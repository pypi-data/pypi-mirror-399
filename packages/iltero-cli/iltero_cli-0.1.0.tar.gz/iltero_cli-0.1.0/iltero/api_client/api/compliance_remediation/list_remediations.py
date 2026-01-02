from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    violation_id: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
    action_type: None | str | Unset = UNSET,
    limit: int | Unset = 100,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_violation_id: None | str | Unset
    if isinstance(violation_id, Unset):
        json_violation_id = UNSET
    else:
        json_violation_id = violation_id
    params["violation_id"] = json_violation_id

    json_status: None | str | Unset
    if isinstance(status, Unset):
        json_status = UNSET
    else:
        json_status = status
    params["status"] = json_status

    json_action_type: None | str | Unset
    if isinstance(action_type, Unset):
        json_action_type = UNSET
    else:
        json_action_type = action_type
    params["action_type"] = json_action_type

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/compliance/remediations/",
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
    *,
    client: AuthenticatedClient,
    violation_id: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
    action_type: None | str | Unset = UNSET,
    limit: int | Unset = 100,
) -> Response[APIResponseModel]:
    """List remediation actions


            Lists remediation actions with optional filtering.

            Use filters to find remediations by violation, status, or action type.
            Results include remediation details and associated violation information.


    Args:
        violation_id (None | str | Unset):
        status (None | str | Unset):
        action_type (None | str | Unset):
        limit (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        violation_id=violation_id,
        status=status,
        action_type=action_type,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    violation_id: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
    action_type: None | str | Unset = UNSET,
    limit: int | Unset = 100,
) -> APIResponseModel | None:
    """List remediation actions


            Lists remediation actions with optional filtering.

            Use filters to find remediations by violation, status, or action type.
            Results include remediation details and associated violation information.


    Args:
        violation_id (None | str | Unset):
        status (None | str | Unset):
        action_type (None | str | Unset):
        limit (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        client=client,
        violation_id=violation_id,
        status=status,
        action_type=action_type,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    violation_id: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
    action_type: None | str | Unset = UNSET,
    limit: int | Unset = 100,
) -> Response[APIResponseModel]:
    """List remediation actions


            Lists remediation actions with optional filtering.

            Use filters to find remediations by violation, status, or action type.
            Results include remediation details and associated violation information.


    Args:
        violation_id (None | str | Unset):
        status (None | str | Unset):
        action_type (None | str | Unset):
        limit (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        violation_id=violation_id,
        status=status,
        action_type=action_type,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    violation_id: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
    action_type: None | str | Unset = UNSET,
    limit: int | Unset = 100,
) -> APIResponseModel | None:
    """List remediation actions


            Lists remediation actions with optional filtering.

            Use filters to find remediations by violation, status, or action type.
            Results include remediation details and associated violation information.


    Args:
        violation_id (None | str | Unset):
        status (None | str | Unset):
        action_type (None | str | Unset):
        limit (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            client=client,
            violation_id=violation_id,
            status=status,
            action_type=action_type,
            limit=limit,
        )
    ).parsed

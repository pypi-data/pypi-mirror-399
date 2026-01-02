from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    approval_id: str,
    *,
    reason: str | Unset = "",
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["reason"] = reason

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": f"/v1/stacks/approvals/{approval_id}",
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
    approval_id: str,
    *,
    client: AuthenticatedClient,
    reason: str | Unset = "",
) -> Response[APIResponseModel]:
    """Cancel approval request


            Cancel a pending approval request.

            This endpoint allows the requester or an admin to cancel
            a pending approval request.


    Args:
        approval_id (str):
        reason (str | Unset):  Default: ''.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        approval_id=approval_id,
        reason=reason,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    approval_id: str,
    *,
    client: AuthenticatedClient,
    reason: str | Unset = "",
) -> APIResponseModel | None:
    """Cancel approval request


            Cancel a pending approval request.

            This endpoint allows the requester or an admin to cancel
            a pending approval request.


    Args:
        approval_id (str):
        reason (str | Unset):  Default: ''.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        approval_id=approval_id,
        client=client,
        reason=reason,
    ).parsed


async def asyncio_detailed(
    approval_id: str,
    *,
    client: AuthenticatedClient,
    reason: str | Unset = "",
) -> Response[APIResponseModel]:
    """Cancel approval request


            Cancel a pending approval request.

            This endpoint allows the requester or an admin to cancel
            a pending approval request.


    Args:
        approval_id (str):
        reason (str | Unset):  Default: ''.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        approval_id=approval_id,
        reason=reason,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    approval_id: str,
    *,
    client: AuthenticatedClient,
    reason: str | Unset = "",
) -> APIResponseModel | None:
    """Cancel approval request


            Cancel a pending approval request.

            This endpoint allows the requester or an admin to cancel
            a pending approval request.


    Args:
        approval_id (str):
        reason (str | Unset):  Default: ''.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            approval_id=approval_id,
            client=client,
            reason=reason,
        )
    ).parsed

from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...types import Response


def _get_kwargs(
    approval_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/stacks/approvals/{approval_id}",
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
) -> Response[APIResponseModel]:
    """Get approval details


            Get details of a specific approval request.

            Returns the full details of an approval request including
            its status, compliance analysis, and response history.


    Args:
        approval_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        approval_id=approval_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    approval_id: str,
    *,
    client: AuthenticatedClient,
) -> APIResponseModel | None:
    """Get approval details


            Get details of a specific approval request.

            Returns the full details of an approval request including
            its status, compliance analysis, and response history.


    Args:
        approval_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        approval_id=approval_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    approval_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[APIResponseModel]:
    """Get approval details


            Get details of a specific approval request.

            Returns the full details of an approval request including
            its status, compliance analysis, and response history.


    Args:
        approval_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        approval_id=approval_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    approval_id: str,
    *,
    client: AuthenticatedClient,
) -> APIResponseModel | None:
    """Get approval details


            Get details of a specific approval request.

            Returns the full details of an approval request including
            its status, compliance analysis, and response history.


    Args:
        approval_id (str):

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
        )
    ).parsed

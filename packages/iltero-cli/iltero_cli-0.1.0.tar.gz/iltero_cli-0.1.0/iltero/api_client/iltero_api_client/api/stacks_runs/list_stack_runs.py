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
    limit: int | Unset = 50,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/stacks/{stack_id}/runs",
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
    limit: int | Unset = 50,
) -> Response[APIResponseModel]:
    """List stack runs


            Lists recent runs for a stack.

            Use this endpoint to view deployment history and run status.
            Results are ordered by creation time, most recent first.


    Args:
        stack_id (str):
        limit (int | Unset):  Default: 50.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        stack_id=stack_id,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    stack_id: str,
    *,
    client: AuthenticatedClient,
    limit: int | Unset = 50,
) -> APIResponseModel | None:
    """List stack runs


            Lists recent runs for a stack.

            Use this endpoint to view deployment history and run status.
            Results are ordered by creation time, most recent first.


    Args:
        stack_id (str):
        limit (int | Unset):  Default: 50.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        stack_id=stack_id,
        client=client,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    stack_id: str,
    *,
    client: AuthenticatedClient,
    limit: int | Unset = 50,
) -> Response[APIResponseModel]:
    """List stack runs


            Lists recent runs for a stack.

            Use this endpoint to view deployment history and run status.
            Results are ordered by creation time, most recent first.


    Args:
        stack_id (str):
        limit (int | Unset):  Default: 50.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        stack_id=stack_id,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    stack_id: str,
    *,
    client: AuthenticatedClient,
    limit: int | Unset = 50,
) -> APIResponseModel | None:
    """List stack runs


            Lists recent runs for a stack.

            Use this endpoint to view deployment history and run status.
            Results are ordered by creation time, most recent first.


    Args:
        stack_id (str):
        limit (int | Unset):  Default: 50.

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
            limit=limit,
        )
    ).parsed

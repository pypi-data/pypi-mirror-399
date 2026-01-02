from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...types import Response


def _get_kwargs(
    stack_id: str,
    resource_type: str,
    resource_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": f"/v1/stacks/{stack_id}/resources/{resource_type}/{resource_id}",
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
    resource_type: str,
    resource_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[APIResponseModel]:
    """Mark Resource Destroyed

     Mark a resource as destroyed.

    Soft deletes the resource by setting its lifecycle status to 'destroyed'.

    Args:
        stack_id (str):
        resource_type (str):
        resource_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        stack_id=stack_id,
        resource_type=resource_type,
        resource_id=resource_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    stack_id: str,
    resource_type: str,
    resource_id: str,
    *,
    client: AuthenticatedClient,
) -> APIResponseModel | None:
    """Mark Resource Destroyed

     Mark a resource as destroyed.

    Soft deletes the resource by setting its lifecycle status to 'destroyed'.

    Args:
        stack_id (str):
        resource_type (str):
        resource_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        stack_id=stack_id,
        resource_type=resource_type,
        resource_id=resource_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    stack_id: str,
    resource_type: str,
    resource_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[APIResponseModel]:
    """Mark Resource Destroyed

     Mark a resource as destroyed.

    Soft deletes the resource by setting its lifecycle status to 'destroyed'.

    Args:
        stack_id (str):
        resource_type (str):
        resource_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        stack_id=stack_id,
        resource_type=resource_type,
        resource_id=resource_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    stack_id: str,
    resource_type: str,
    resource_id: str,
    *,
    client: AuthenticatedClient,
) -> APIResponseModel | None:
    """Mark Resource Destroyed

     Mark a resource as destroyed.

    Soft deletes the resource by setting its lifecycle status to 'destroyed'.

    Args:
        stack_id (str):
        resource_type (str):
        resource_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            stack_id=stack_id,
            resource_type=resource_type,
            resource_id=resource_id,
            client=client,
        )
    ).parsed

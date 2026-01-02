from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...types import UNSET, Response


def _get_kwargs(
    repository_id: str,
    *,
    path: str,
    branch: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["path"] = path

    params["branch"] = branch

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/git/{repository_id}/files",
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
    repository_id: str,
    *,
    client: AuthenticatedClient,
    path: str,
    branch: str,
) -> Response[APIResponseModel]:
    """List Files

     List files in repository.

    Args:
        repository_id (str):
        path (str): File path in repository
        branch (str): Branch name

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        repository_id=repository_id,
        path=path,
        branch=branch,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository_id: str,
    *,
    client: AuthenticatedClient,
    path: str,
    branch: str,
) -> APIResponseModel | None:
    """List Files

     List files in repository.

    Args:
        repository_id (str):
        path (str): File path in repository
        branch (str): Branch name

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        repository_id=repository_id,
        client=client,
        path=path,
        branch=branch,
    ).parsed


async def asyncio_detailed(
    repository_id: str,
    *,
    client: AuthenticatedClient,
    path: str,
    branch: str,
) -> Response[APIResponseModel]:
    """List Files

     List files in repository.

    Args:
        repository_id (str):
        path (str): File path in repository
        branch (str): Branch name

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        repository_id=repository_id,
        path=path,
        branch=branch,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository_id: str,
    *,
    client: AuthenticatedClient,
    path: str,
    branch: str,
) -> APIResponseModel | None:
    """List Files

     List files in repository.

    Args:
        repository_id (str):
        path (str): File path in repository
        branch (str): Branch name

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            repository_id=repository_id,
            client=client,
            path=path,
            branch=branch,
        )
    ).parsed

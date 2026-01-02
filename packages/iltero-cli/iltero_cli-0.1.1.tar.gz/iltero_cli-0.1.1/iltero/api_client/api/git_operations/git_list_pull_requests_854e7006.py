from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository_id: str,
    *,
    state: str | Unset = "all",
    base_branch: None | str | Unset = UNSET,
    head_branch: None | str | Unset = UNSET,
    sort: str | Unset = "created",
    direction: str | Unset = "desc",
    limit: int | Unset = 100,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["state"] = state

    json_base_branch: None | str | Unset
    if isinstance(base_branch, Unset):
        json_base_branch = UNSET
    else:
        json_base_branch = base_branch
    params["base_branch"] = json_base_branch

    json_head_branch: None | str | Unset
    if isinstance(head_branch, Unset):
        json_head_branch = UNSET
    else:
        json_head_branch = head_branch
    params["head_branch"] = json_head_branch

    params["sort"] = sort

    params["direction"] = direction

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/git/{repository_id}/pull-requests",
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
    state: str | Unset = "all",
    base_branch: None | str | Unset = UNSET,
    head_branch: None | str | Unset = UNSET,
    sort: str | Unset = "created",
    direction: str | Unset = "desc",
    limit: int | Unset = 100,
) -> Response[APIResponseModel]:
    """List Pull Requests

     List pull requests in a repository.

    Args:
        repository_id (str):
        state (str | Unset): PR state: open, closed, all Default: 'all'.
        base_branch (None | str | Unset): Base branch
        head_branch (None | str | Unset): Head branch
        sort (str | Unset): Sort by: created, updated, popularity Default: 'created'.
        direction (str | Unset): Sort direction: asc, desc Default: 'desc'.
        limit (int | Unset): Maximum number of PRs Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        repository_id=repository_id,
        state=state,
        base_branch=base_branch,
        head_branch=head_branch,
        sort=sort,
        direction=direction,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository_id: str,
    *,
    client: AuthenticatedClient,
    state: str | Unset = "all",
    base_branch: None | str | Unset = UNSET,
    head_branch: None | str | Unset = UNSET,
    sort: str | Unset = "created",
    direction: str | Unset = "desc",
    limit: int | Unset = 100,
) -> APIResponseModel | None:
    """List Pull Requests

     List pull requests in a repository.

    Args:
        repository_id (str):
        state (str | Unset): PR state: open, closed, all Default: 'all'.
        base_branch (None | str | Unset): Base branch
        head_branch (None | str | Unset): Head branch
        sort (str | Unset): Sort by: created, updated, popularity Default: 'created'.
        direction (str | Unset): Sort direction: asc, desc Default: 'desc'.
        limit (int | Unset): Maximum number of PRs Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        repository_id=repository_id,
        client=client,
        state=state,
        base_branch=base_branch,
        head_branch=head_branch,
        sort=sort,
        direction=direction,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    repository_id: str,
    *,
    client: AuthenticatedClient,
    state: str | Unset = "all",
    base_branch: None | str | Unset = UNSET,
    head_branch: None | str | Unset = UNSET,
    sort: str | Unset = "created",
    direction: str | Unset = "desc",
    limit: int | Unset = 100,
) -> Response[APIResponseModel]:
    """List Pull Requests

     List pull requests in a repository.

    Args:
        repository_id (str):
        state (str | Unset): PR state: open, closed, all Default: 'all'.
        base_branch (None | str | Unset): Base branch
        head_branch (None | str | Unset): Head branch
        sort (str | Unset): Sort by: created, updated, popularity Default: 'created'.
        direction (str | Unset): Sort direction: asc, desc Default: 'desc'.
        limit (int | Unset): Maximum number of PRs Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        repository_id=repository_id,
        state=state,
        base_branch=base_branch,
        head_branch=head_branch,
        sort=sort,
        direction=direction,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository_id: str,
    *,
    client: AuthenticatedClient,
    state: str | Unset = "all",
    base_branch: None | str | Unset = UNSET,
    head_branch: None | str | Unset = UNSET,
    sort: str | Unset = "created",
    direction: str | Unset = "desc",
    limit: int | Unset = 100,
) -> APIResponseModel | None:
    """List Pull Requests

     List pull requests in a repository.

    Args:
        repository_id (str):
        state (str | Unset): PR state: open, closed, all Default: 'all'.
        base_branch (None | str | Unset): Base branch
        head_branch (None | str | Unset): Head branch
        sort (str | Unset): Sort by: created, updated, popularity Default: 'created'.
        direction (str | Unset): Sort direction: asc, desc Default: 'desc'.
        limit (int | Unset): Maximum number of PRs Default: 100.

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
            state=state,
            base_branch=base_branch,
            head_branch=head_branch,
            sort=sort,
            direction=direction,
            limit=limit,
        )
    ).parsed

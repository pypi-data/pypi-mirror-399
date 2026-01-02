import datetime
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
    branch: str | Unset = "main",
    since: datetime.datetime | None | Unset = UNSET,
    until: datetime.datetime | None | Unset = UNSET,
    author: None | str | Unset = UNSET,
    limit: int | Unset = 100,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["branch"] = branch

    json_since: None | str | Unset
    if isinstance(since, Unset):
        json_since = UNSET
    elif isinstance(since, datetime.datetime):
        json_since = since.isoformat()
    else:
        json_since = since
    params["since"] = json_since

    json_until: None | str | Unset
    if isinstance(until, Unset):
        json_until = UNSET
    elif isinstance(until, datetime.datetime):
        json_until = until.isoformat()
    else:
        json_until = until
    params["until"] = json_until

    json_author: None | str | Unset
    if isinstance(author, Unset):
        json_author = UNSET
    else:
        json_author = author
    params["author"] = json_author

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/git/{repository_id}/commits",
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
    branch: str | Unset = "main",
    since: datetime.datetime | None | Unset = UNSET,
    until: datetime.datetime | None | Unset = UNSET,
    author: None | str | Unset = UNSET,
    limit: int | Unset = 100,
) -> Response[APIResponseModel]:
    """List Commits

     List commits in a repository.

    Args:
        repository_id (str):
        branch (str | Unset): Branch name Default: 'main'.
        since (datetime.datetime | None | Unset): Start date
        until (datetime.datetime | None | Unset): End date
        author (None | str | Unset): Author username or email
        limit (int | Unset): Maximum number of commits Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        repository_id=repository_id,
        branch=branch,
        since=since,
        until=until,
        author=author,
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
    branch: str | Unset = "main",
    since: datetime.datetime | None | Unset = UNSET,
    until: datetime.datetime | None | Unset = UNSET,
    author: None | str | Unset = UNSET,
    limit: int | Unset = 100,
) -> APIResponseModel | None:
    """List Commits

     List commits in a repository.

    Args:
        repository_id (str):
        branch (str | Unset): Branch name Default: 'main'.
        since (datetime.datetime | None | Unset): Start date
        until (datetime.datetime | None | Unset): End date
        author (None | str | Unset): Author username or email
        limit (int | Unset): Maximum number of commits Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        repository_id=repository_id,
        client=client,
        branch=branch,
        since=since,
        until=until,
        author=author,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    repository_id: str,
    *,
    client: AuthenticatedClient,
    branch: str | Unset = "main",
    since: datetime.datetime | None | Unset = UNSET,
    until: datetime.datetime | None | Unset = UNSET,
    author: None | str | Unset = UNSET,
    limit: int | Unset = 100,
) -> Response[APIResponseModel]:
    """List Commits

     List commits in a repository.

    Args:
        repository_id (str):
        branch (str | Unset): Branch name Default: 'main'.
        since (datetime.datetime | None | Unset): Start date
        until (datetime.datetime | None | Unset): End date
        author (None | str | Unset): Author username or email
        limit (int | Unset): Maximum number of commits Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        repository_id=repository_id,
        branch=branch,
        since=since,
        until=until,
        author=author,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository_id: str,
    *,
    client: AuthenticatedClient,
    branch: str | Unset = "main",
    since: datetime.datetime | None | Unset = UNSET,
    until: datetime.datetime | None | Unset = UNSET,
    author: None | str | Unset = UNSET,
    limit: int | Unset = 100,
) -> APIResponseModel | None:
    """List Commits

     List commits in a repository.

    Args:
        repository_id (str):
        branch (str | Unset): Branch name Default: 'main'.
        since (datetime.datetime | None | Unset): Start date
        until (datetime.datetime | None | Unset): End date
        author (None | str | Unset): Author username or email
        limit (int | Unset): Maximum number of commits Default: 100.

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
            branch=branch,
            since=since,
            until=until,
            author=author,
            limit=limit,
        )
    ).parsed

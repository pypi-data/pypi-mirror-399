from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    page: int | Unset = 1,
    limit: int | Unset = 10,
    search: None | str | Unset = UNSET,
    is_default: bool | None | Unset = UNSET,
    is_production: bool | None | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["limit"] = limit

    json_search: None | str | Unset
    if isinstance(search, Unset):
        json_search = UNSET
    else:
        json_search = search
    params["search"] = json_search

    json_is_default: bool | None | Unset
    if isinstance(is_default, Unset):
        json_is_default = UNSET
    else:
        json_is_default = is_default
    params["is_default"] = json_is_default

    json_is_production: bool | None | Unset
    if isinstance(is_production, Unset):
        json_is_production = UNSET
    else:
        json_is_production = is_production
    params["is_production"] = json_is_production

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/environments",
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
    page: int | Unset = 1,
    limit: int | Unset = 10,
    search: None | str | Unset = UNSET,
    is_default: bool | None | Unset = UNSET,
    is_production: bool | None | Unset = UNSET,
) -> Response[APIResponseModel]:
    """List environments


            Lists all environments in the organization.

            Returns paginated results with filtering options.


    Args:
        page (int | Unset):  Default: 1.
        limit (int | Unset):  Default: 10.
        search (None | str | Unset):
        is_default (bool | None | Unset):
        is_production (bool | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        page=page,
        limit=limit,
        search=search,
        is_default=is_default,
        is_production=is_production,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    page: int | Unset = 1,
    limit: int | Unset = 10,
    search: None | str | Unset = UNSET,
    is_default: bool | None | Unset = UNSET,
    is_production: bool | None | Unset = UNSET,
) -> APIResponseModel | None:
    """List environments


            Lists all environments in the organization.

            Returns paginated results with filtering options.


    Args:
        page (int | Unset):  Default: 1.
        limit (int | Unset):  Default: 10.
        search (None | str | Unset):
        is_default (bool | None | Unset):
        is_production (bool | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        client=client,
        page=page,
        limit=limit,
        search=search,
        is_default=is_default,
        is_production=is_production,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    page: int | Unset = 1,
    limit: int | Unset = 10,
    search: None | str | Unset = UNSET,
    is_default: bool | None | Unset = UNSET,
    is_production: bool | None | Unset = UNSET,
) -> Response[APIResponseModel]:
    """List environments


            Lists all environments in the organization.

            Returns paginated results with filtering options.


    Args:
        page (int | Unset):  Default: 1.
        limit (int | Unset):  Default: 10.
        search (None | str | Unset):
        is_default (bool | None | Unset):
        is_production (bool | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        page=page,
        limit=limit,
        search=search,
        is_default=is_default,
        is_production=is_production,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    page: int | Unset = 1,
    limit: int | Unset = 10,
    search: None | str | Unset = UNSET,
    is_default: bool | None | Unset = UNSET,
    is_production: bool | None | Unset = UNSET,
) -> APIResponseModel | None:
    """List environments


            Lists all environments in the organization.

            Returns paginated results with filtering options.


    Args:
        page (int | Unset):  Default: 1.
        limit (int | Unset):  Default: 10.
        search (None | str | Unset):
        is_default (bool | None | Unset):
        is_production (bool | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            client=client,
            page=page,
            limit=limit,
            search=search,
            is_default=is_default,
            is_production=is_production,
        )
    ).parsed

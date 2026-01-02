from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    tool: None | str | Unset = UNSET,
    namespace: None | str | Unset = UNSET,
    provider: None | str | Unset = UNSET,
    name: None | str | Unset = UNSET,
    active: bool | None | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_tool: None | str | Unset
    if isinstance(tool, Unset):
        json_tool = UNSET
    else:
        json_tool = tool
    params["tool"] = json_tool

    json_namespace: None | str | Unset
    if isinstance(namespace, Unset):
        json_namespace = UNSET
    else:
        json_namespace = namespace
    params["namespace"] = json_namespace

    json_provider: None | str | Unset
    if isinstance(provider, Unset):
        json_provider = UNSET
    else:
        json_provider = provider
    params["provider"] = json_provider

    json_name: None | str | Unset
    if isinstance(name, Unset):
        json_name = UNSET
    else:
        json_name = name
    params["name"] = json_name

    json_active: bool | None | Unset
    if isinstance(active, Unset):
        json_active = UNSET
    else:
        json_active = active
    params["active"] = json_active

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/registry/modules",
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
    tool: None | str | Unset = UNSET,
    namespace: None | str | Unset = UNSET,
    provider: None | str | Unset = UNSET,
    name: None | str | Unset = UNSET,
    active: bool | None | Unset = UNSET,
) -> Response[APIResponseModel]:
    """List registry modules


            Lists available modules in the registry.

            Use filters to find specific modules by tool, namespace,
            provider, or name. Returns both private and public modules.


    Args:
        tool (None | str | Unset):
        namespace (None | str | Unset):
        provider (None | str | Unset):
        name (None | str | Unset):
        active (bool | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        tool=tool,
        namespace=namespace,
        provider=provider,
        name=name,
        active=active,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    tool: None | str | Unset = UNSET,
    namespace: None | str | Unset = UNSET,
    provider: None | str | Unset = UNSET,
    name: None | str | Unset = UNSET,
    active: bool | None | Unset = UNSET,
) -> APIResponseModel | None:
    """List registry modules


            Lists available modules in the registry.

            Use filters to find specific modules by tool, namespace,
            provider, or name. Returns both private and public modules.


    Args:
        tool (None | str | Unset):
        namespace (None | str | Unset):
        provider (None | str | Unset):
        name (None | str | Unset):
        active (bool | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        client=client,
        tool=tool,
        namespace=namespace,
        provider=provider,
        name=name,
        active=active,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    tool: None | str | Unset = UNSET,
    namespace: None | str | Unset = UNSET,
    provider: None | str | Unset = UNSET,
    name: None | str | Unset = UNSET,
    active: bool | None | Unset = UNSET,
) -> Response[APIResponseModel]:
    """List registry modules


            Lists available modules in the registry.

            Use filters to find specific modules by tool, namespace,
            provider, or name. Returns both private and public modules.


    Args:
        tool (None | str | Unset):
        namespace (None | str | Unset):
        provider (None | str | Unset):
        name (None | str | Unset):
        active (bool | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        tool=tool,
        namespace=namespace,
        provider=provider,
        name=name,
        active=active,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    tool: None | str | Unset = UNSET,
    namespace: None | str | Unset = UNSET,
    provider: None | str | Unset = UNSET,
    name: None | str | Unset = UNSET,
    active: bool | None | Unset = UNSET,
) -> APIResponseModel | None:
    """List registry modules


            Lists available modules in the registry.

            Use filters to find specific modules by tool, namespace,
            provider, or name. Returns both private and public modules.


    Args:
        tool (None | str | Unset):
        namespace (None | str | Unset):
        provider (None | str | Unset):
        name (None | str | Unset):
        active (bool | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            client=client,
            tool=tool,
            namespace=namespace,
            provider=provider,
            name=name,
            active=active,
        )
    ).parsed

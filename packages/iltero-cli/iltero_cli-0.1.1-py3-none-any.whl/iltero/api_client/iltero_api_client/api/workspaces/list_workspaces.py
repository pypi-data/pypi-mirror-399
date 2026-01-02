from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    environment_id: None | str | Unset = UNSET,
    name: None | str | Unset = UNSET,
    active: bool | None | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_environment_id: None | str | Unset
    if isinstance(environment_id, Unset):
        json_environment_id = UNSET
    else:
        json_environment_id = environment_id
    params["environment_id"] = json_environment_id

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
        "url": "/v1/workspaces",
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
    environment_id: None | str | Unset = UNSET,
    name: None | str | Unset = UNSET,
    active: bool | None | Unset = UNSET,
) -> Response[APIResponseModel]:
    """List workspaces


            Lists all workspaces in the organization.

            Use filters to find workspaces by environment, name,
            or active status.


    Args:
        environment_id (None | str | Unset):
        name (None | str | Unset):
        active (bool | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        environment_id=environment_id,
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
    environment_id: None | str | Unset = UNSET,
    name: None | str | Unset = UNSET,
    active: bool | None | Unset = UNSET,
) -> APIResponseModel | None:
    """List workspaces


            Lists all workspaces in the organization.

            Use filters to find workspaces by environment, name,
            or active status.


    Args:
        environment_id (None | str | Unset):
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
        environment_id=environment_id,
        name=name,
        active=active,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    environment_id: None | str | Unset = UNSET,
    name: None | str | Unset = UNSET,
    active: bool | None | Unset = UNSET,
) -> Response[APIResponseModel]:
    """List workspaces


            Lists all workspaces in the organization.

            Use filters to find workspaces by environment, name,
            or active status.


    Args:
        environment_id (None | str | Unset):
        name (None | str | Unset):
        active (bool | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        environment_id=environment_id,
        name=name,
        active=active,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    environment_id: None | str | Unset = UNSET,
    name: None | str | Unset = UNSET,
    active: bool | None | Unset = UNSET,
) -> APIResponseModel | None:
    """List workspaces


            Lists all workspaces in the organization.

            Use filters to find workspaces by environment, name,
            or active status.


    Args:
        environment_id (None | str | Unset):
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
            environment_id=environment_id,
            name=name,
            active=active,
        )
    ).parsed

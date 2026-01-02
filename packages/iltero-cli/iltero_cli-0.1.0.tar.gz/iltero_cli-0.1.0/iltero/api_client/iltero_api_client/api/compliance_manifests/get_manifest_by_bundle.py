from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...types import Response


def _get_kwargs(
    bundle_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/compliance/manifests/{bundle_id}",
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
    bundle_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[APIResponseModel]:
    """Get compliance manifest for bundle


            Retrieves the compliance manifest for a specific template bundle.

            Returns manifest details including frameworks, controls, policies,
            and module profiles.


    Args:
        bundle_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        bundle_id=bundle_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    bundle_id: str,
    *,
    client: AuthenticatedClient,
) -> APIResponseModel | None:
    """Get compliance manifest for bundle


            Retrieves the compliance manifest for a specific template bundle.

            Returns manifest details including frameworks, controls, policies,
            and module profiles.


    Args:
        bundle_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        bundle_id=bundle_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    bundle_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[APIResponseModel]:
    """Get compliance manifest for bundle


            Retrieves the compliance manifest for a specific template bundle.

            Returns manifest details including frameworks, controls, policies,
            and module profiles.


    Args:
        bundle_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        bundle_id=bundle_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    bundle_id: str,
    *,
    client: AuthenticatedClient,
) -> APIResponseModel | None:
    """Get compliance manifest for bundle


            Retrieves the compliance manifest for a specific template bundle.

            Returns manifest details including frameworks, controls, policies,
            and module profiles.


    Args:
        bundle_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            bundle_id=bundle_id,
            client=client,
        )
    ).parsed

from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...types import Response


def _get_kwargs(
    manifest_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/compliance/manifests/{manifest_id}/verify",
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
    manifest_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[APIResponseModel]:
    """Verify compliance manifest


            Verifies the integrity and validity of a compliance manifest.

            Checks hash integrity and signature validity (if signed).


    Args:
        manifest_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        manifest_id=manifest_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    manifest_id: str,
    *,
    client: AuthenticatedClient,
) -> APIResponseModel | None:
    """Verify compliance manifest


            Verifies the integrity and validity of a compliance manifest.

            Checks hash integrity and signature validity (if signed).


    Args:
        manifest_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        manifest_id=manifest_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    manifest_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[APIResponseModel]:
    """Verify compliance manifest


            Verifies the integrity and validity of a compliance manifest.

            Checks hash integrity and signature validity (if signed).


    Args:
        manifest_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        manifest_id=manifest_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    manifest_id: str,
    *,
    client: AuthenticatedClient,
) -> APIResponseModel | None:
    """Verify compliance manifest


            Verifies the integrity and validity of a compliance manifest.

            Checks hash integrity and signature validity (if signed).


    Args:
        manifest_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            manifest_id=manifest_id,
            client=client,
        )
    ).parsed

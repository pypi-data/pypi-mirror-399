from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...types import Response


def _get_kwargs() -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/modules/publish",
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
) -> Response[APIResponseModel]:
    """Publish Module

     Publish a new module version with file upload.

    Requires registry create permission.
    This endpoint handles multipart/form-data uploads.

    Request form data:
    - tool: IaC tool type
    - namespace: Module namespace
    - name: Module name
    - provider: Cloud provider
    - version: Version string (SemVer format)
    - description: Optional module description
    - is_public: Optional public visibility flag
    - module_file: Uploaded module archive (.zip)

    Returns:
        API response with published version details

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
) -> APIResponseModel | None:
    """Publish Module

     Publish a new module version with file upload.

    Requires registry create permission.
    This endpoint handles multipart/form-data uploads.

    Request form data:
    - tool: IaC tool type
    - namespace: Module namespace
    - name: Module name
    - provider: Cloud provider
    - version: Version string (SemVer format)
    - description: Optional module description
    - is_public: Optional public visibility flag
    - module_file: Uploaded module archive (.zip)

    Returns:
        API response with published version details

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[APIResponseModel]:
    """Publish Module

     Publish a new module version with file upload.

    Requires registry create permission.
    This endpoint handles multipart/form-data uploads.

    Request form data:
    - tool: IaC tool type
    - namespace: Module namespace
    - name: Module name
    - provider: Cloud provider
    - version: Version string (SemVer format)
    - description: Optional module description
    - is_public: Optional public visibility flag
    - module_file: Uploaded module archive (.zip)

    Returns:
        API response with published version details

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
) -> APIResponseModel | None:
    """Publish Module

     Publish a new module version with file upload.

    Requires registry create permission.
    This endpoint handles multipart/form-data uploads.

    Request form data:
    - tool: IaC tool type
    - namespace: Module namespace
    - name: Module name
    - provider: Cloud provider
    - version: Version string (SemVer format)
    - description: Optional module description
    - is_public: Optional public visibility flag
    - module_file: Uploaded module archive (.zip)

    Returns:
        API response with published version details

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed

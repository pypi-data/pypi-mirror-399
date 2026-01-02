from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    industry: str,
    modules: None | str | Unset = UNSET,
    environment_type: str | Unset = "production",
    region: str | Unset = "us-east-1",
    expected_users: int | Unset = 1000,
    compliance_framework: None | str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["industry"] = industry

    json_modules: None | str | Unset
    if isinstance(modules, Unset):
        json_modules = UNSET
    else:
        json_modules = modules
    params["modules"] = json_modules

    params["environment_type"] = environment_type

    params["region"] = region

    params["expected_users"] = expected_users

    json_compliance_framework: None | str | Unset
    if isinstance(compliance_framework, Unset):
        json_compliance_framework = UNSET
    else:
        json_compliance_framework = compliance_framework
    params["compliance_framework"] = json_compliance_framework

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/onboarding/cost-calculator",
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
    industry: str,
    modules: None | str | Unset = UNSET,
    environment_type: str | Unset = "production",
    region: str | Unset = "us-east-1",
    expected_users: int | Unset = 1000,
    compliance_framework: None | str | Unset = UNSET,
) -> Response[APIResponseModel]:
    """Calculate Infrastructure Cost

     Calculate detailed infrastructure costs for specific modules.

    Provides detailed cost breakdown, scaling factors, and optimization tips
    for infrastructure planning and budgeting.

    Args:
        industry (str):
        modules (None | str | Unset):
        environment_type (str | Unset):  Default: 'production'.
        region (str | Unset):  Default: 'us-east-1'.
        expected_users (int | Unset):  Default: 1000.
        compliance_framework (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        industry=industry,
        modules=modules,
        environment_type=environment_type,
        region=region,
        expected_users=expected_users,
        compliance_framework=compliance_framework,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    industry: str,
    modules: None | str | Unset = UNSET,
    environment_type: str | Unset = "production",
    region: str | Unset = "us-east-1",
    expected_users: int | Unset = 1000,
    compliance_framework: None | str | Unset = UNSET,
) -> APIResponseModel | None:
    """Calculate Infrastructure Cost

     Calculate detailed infrastructure costs for specific modules.

    Provides detailed cost breakdown, scaling factors, and optimization tips
    for infrastructure planning and budgeting.

    Args:
        industry (str):
        modules (None | str | Unset):
        environment_type (str | Unset):  Default: 'production'.
        region (str | Unset):  Default: 'us-east-1'.
        expected_users (int | Unset):  Default: 1000.
        compliance_framework (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        client=client,
        industry=industry,
        modules=modules,
        environment_type=environment_type,
        region=region,
        expected_users=expected_users,
        compliance_framework=compliance_framework,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    industry: str,
    modules: None | str | Unset = UNSET,
    environment_type: str | Unset = "production",
    region: str | Unset = "us-east-1",
    expected_users: int | Unset = 1000,
    compliance_framework: None | str | Unset = UNSET,
) -> Response[APIResponseModel]:
    """Calculate Infrastructure Cost

     Calculate detailed infrastructure costs for specific modules.

    Provides detailed cost breakdown, scaling factors, and optimization tips
    for infrastructure planning and budgeting.

    Args:
        industry (str):
        modules (None | str | Unset):
        environment_type (str | Unset):  Default: 'production'.
        region (str | Unset):  Default: 'us-east-1'.
        expected_users (int | Unset):  Default: 1000.
        compliance_framework (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        industry=industry,
        modules=modules,
        environment_type=environment_type,
        region=region,
        expected_users=expected_users,
        compliance_framework=compliance_framework,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    industry: str,
    modules: None | str | Unset = UNSET,
    environment_type: str | Unset = "production",
    region: str | Unset = "us-east-1",
    expected_users: int | Unset = 1000,
    compliance_framework: None | str | Unset = UNSET,
) -> APIResponseModel | None:
    """Calculate Infrastructure Cost

     Calculate detailed infrastructure costs for specific modules.

    Provides detailed cost breakdown, scaling factors, and optimization tips
    for infrastructure planning and budgeting.

    Args:
        industry (str):
        modules (None | str | Unset):
        environment_type (str | Unset):  Default: 'production'.
        region (str | Unset):  Default: 'us-east-1'.
        expected_users (int | Unset):  Default: 1000.
        compliance_framework (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            client=client,
            industry=industry,
            modules=modules,
            environment_type=environment_type,
            region=region,
            expected_users=expected_users,
            compliance_framework=compliance_framework,
        )
    ).parsed

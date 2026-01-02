from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    industry: None | str | Unset = UNSET,
    compliance_frameworks: None | str | Unset = UNSET,
    provider: None | str | Unset = UNSET,
    tier: None | str | Unset = UNSET,
    business_use_case: None | str | Unset = UNSET,
    marketplace_category: None | str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_industry: None | str | Unset
    if isinstance(industry, Unset):
        json_industry = UNSET
    else:
        json_industry = industry
    params["industry"] = json_industry

    json_compliance_frameworks: None | str | Unset
    if isinstance(compliance_frameworks, Unset):
        json_compliance_frameworks = UNSET
    else:
        json_compliance_frameworks = compliance_frameworks
    params["compliance_frameworks"] = json_compliance_frameworks

    json_provider: None | str | Unset
    if isinstance(provider, Unset):
        json_provider = UNSET
    else:
        json_provider = provider
    params["provider"] = json_provider

    json_tier: None | str | Unset
    if isinstance(tier, Unset):
        json_tier = UNSET
    else:
        json_tier = tier
    params["tier"] = json_tier

    json_business_use_case: None | str | Unset
    if isinstance(business_use_case, Unset):
        json_business_use_case = UNSET
    else:
        json_business_use_case = business_use_case
    params["business_use_case"] = json_business_use_case

    json_marketplace_category: None | str | Unset
    if isinstance(marketplace_category, Unset):
        json_marketplace_category = UNSET
    else:
        json_marketplace_category = marketplace_category
    params["marketplace_category"] = json_marketplace_category

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/stacks/marketplace/template-bundles/discover",
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
    industry: None | str | Unset = UNSET,
    compliance_frameworks: None | str | Unset = UNSET,
    provider: None | str | Unset = UNSET,
    tier: None | str | Unset = UNSET,
    business_use_case: None | str | Unset = UNSET,
    marketplace_category: None | str | Unset = UNSET,
) -> Response[APIResponseModel]:
    """Discover Template Bundles Marketplace

     Discover Template Bundles from marketplace.

    Args:
        industry (None | str | Unset):
        compliance_frameworks (None | str | Unset):
        provider (None | str | Unset):
        tier (None | str | Unset):
        business_use_case (None | str | Unset):
        marketplace_category (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        industry=industry,
        compliance_frameworks=compliance_frameworks,
        provider=provider,
        tier=tier,
        business_use_case=business_use_case,
        marketplace_category=marketplace_category,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    industry: None | str | Unset = UNSET,
    compliance_frameworks: None | str | Unset = UNSET,
    provider: None | str | Unset = UNSET,
    tier: None | str | Unset = UNSET,
    business_use_case: None | str | Unset = UNSET,
    marketplace_category: None | str | Unset = UNSET,
) -> APIResponseModel | None:
    """Discover Template Bundles Marketplace

     Discover Template Bundles from marketplace.

    Args:
        industry (None | str | Unset):
        compliance_frameworks (None | str | Unset):
        provider (None | str | Unset):
        tier (None | str | Unset):
        business_use_case (None | str | Unset):
        marketplace_category (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        client=client,
        industry=industry,
        compliance_frameworks=compliance_frameworks,
        provider=provider,
        tier=tier,
        business_use_case=business_use_case,
        marketplace_category=marketplace_category,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    industry: None | str | Unset = UNSET,
    compliance_frameworks: None | str | Unset = UNSET,
    provider: None | str | Unset = UNSET,
    tier: None | str | Unset = UNSET,
    business_use_case: None | str | Unset = UNSET,
    marketplace_category: None | str | Unset = UNSET,
) -> Response[APIResponseModel]:
    """Discover Template Bundles Marketplace

     Discover Template Bundles from marketplace.

    Args:
        industry (None | str | Unset):
        compliance_frameworks (None | str | Unset):
        provider (None | str | Unset):
        tier (None | str | Unset):
        business_use_case (None | str | Unset):
        marketplace_category (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        industry=industry,
        compliance_frameworks=compliance_frameworks,
        provider=provider,
        tier=tier,
        business_use_case=business_use_case,
        marketplace_category=marketplace_category,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    industry: None | str | Unset = UNSET,
    compliance_frameworks: None | str | Unset = UNSET,
    provider: None | str | Unset = UNSET,
    tier: None | str | Unset = UNSET,
    business_use_case: None | str | Unset = UNSET,
    marketplace_category: None | str | Unset = UNSET,
) -> APIResponseModel | None:
    """Discover Template Bundles Marketplace

     Discover Template Bundles from marketplace.

    Args:
        industry (None | str | Unset):
        compliance_frameworks (None | str | Unset):
        provider (None | str | Unset):
        tier (None | str | Unset):
        business_use_case (None | str | Unset):
        marketplace_category (None | str | Unset):

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
            compliance_frameworks=compliance_frameworks,
            provider=provider,
            tier=tier,
            business_use_case=business_use_case,
            marketplace_category=marketplace_category,
        )
    ).parsed

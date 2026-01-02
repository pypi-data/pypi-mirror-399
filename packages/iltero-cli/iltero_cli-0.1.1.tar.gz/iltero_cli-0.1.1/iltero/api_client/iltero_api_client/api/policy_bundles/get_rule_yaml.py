from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.rule_content_response import RuleContentResponse
from ...types import UNSET, Response


def _get_kwargs(
    rule_id: str,
    *,
    bundle_key: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["bundle_key"] = bundle_key

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/policy-bundles/rules/{rule_id}/yaml",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> RuleContentResponse | None:
    if response.status_code == 200:
        response_200 = RuleContentResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[RuleContentResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    rule_id: str,
    *,
    client: AuthenticatedClient | Client,
    bundle_key: str,
) -> Response[RuleContentResponse]:
    """Get rule YAML content


            Get single rule's YAML content for Checkov graph checks.

            Fetches from S3 with 24-hour caching.

            Args:
                rule_id: Rule ID (e.g., 'CKV2_AWS_1')
                bundle_key: Bundle key (e.g., 'checkov_aws_latest')

            Returns:
                JSON with yaml_content field


    Args:
        rule_id (str):
        bundle_key (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RuleContentResponse]
    """

    kwargs = _get_kwargs(
        rule_id=rule_id,
        bundle_key=bundle_key,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    rule_id: str,
    *,
    client: AuthenticatedClient | Client,
    bundle_key: str,
) -> RuleContentResponse | None:
    """Get rule YAML content


            Get single rule's YAML content for Checkov graph checks.

            Fetches from S3 with 24-hour caching.

            Args:
                rule_id: Rule ID (e.g., 'CKV2_AWS_1')
                bundle_key: Bundle key (e.g., 'checkov_aws_latest')

            Returns:
                JSON with yaml_content field


    Args:
        rule_id (str):
        bundle_key (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RuleContentResponse
    """

    return sync_detailed(
        rule_id=rule_id,
        client=client,
        bundle_key=bundle_key,
    ).parsed


async def asyncio_detailed(
    rule_id: str,
    *,
    client: AuthenticatedClient | Client,
    bundle_key: str,
) -> Response[RuleContentResponse]:
    """Get rule YAML content


            Get single rule's YAML content for Checkov graph checks.

            Fetches from S3 with 24-hour caching.

            Args:
                rule_id: Rule ID (e.g., 'CKV2_AWS_1')
                bundle_key: Bundle key (e.g., 'checkov_aws_latest')

            Returns:
                JSON with yaml_content field


    Args:
        rule_id (str):
        bundle_key (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RuleContentResponse]
    """

    kwargs = _get_kwargs(
        rule_id=rule_id,
        bundle_key=bundle_key,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    rule_id: str,
    *,
    client: AuthenticatedClient | Client,
    bundle_key: str,
) -> RuleContentResponse | None:
    """Get rule YAML content


            Get single rule's YAML content for Checkov graph checks.

            Fetches from S3 with 24-hour caching.

            Args:
                rule_id: Rule ID (e.g., 'CKV2_AWS_1')
                bundle_key: Bundle key (e.g., 'checkov_aws_latest')

            Returns:
                JSON with yaml_content field


    Args:
        rule_id (str):
        bundle_key (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RuleContentResponse
    """

    return (
        await asyncio_detailed(
            rule_id=rule_id,
            client=client,
            bundle_key=bundle_key,
        )
    ).parsed

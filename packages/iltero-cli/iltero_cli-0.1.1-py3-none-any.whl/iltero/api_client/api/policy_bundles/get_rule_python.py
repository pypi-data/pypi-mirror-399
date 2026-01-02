from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
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
        "url": f"/v1/policy-bundles/rules/{rule_id}/python",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | None:
    if response.status_code == 200:
        return None

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any]:
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
) -> Response[Any]:
    """Get rule Python content


            Get single rule's Python content for Checkov resource checks.

            Fetches from S3 with 24-hour caching.

            Args:
                rule_id: Rule ID (e.g., 'CKV_AWS_18')
                bundle_key: Bundle key (e.g., 'checkov_aws_latest')

            Returns:
                JSON with python_content field


    Args:
        rule_id (str):
        bundle_key (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        rule_id=rule_id,
        bundle_key=bundle_key,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    rule_id: str,
    *,
    client: AuthenticatedClient | Client,
    bundle_key: str,
) -> Response[Any]:
    """Get rule Python content


            Get single rule's Python content for Checkov resource checks.

            Fetches from S3 with 24-hour caching.

            Args:
                rule_id: Rule ID (e.g., 'CKV_AWS_18')
                bundle_key: Bundle key (e.g., 'checkov_aws_latest')

            Returns:
                JSON with python_content field


    Args:
        rule_id (str):
        bundle_key (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        rule_id=rule_id,
        bundle_key=bundle_key,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)

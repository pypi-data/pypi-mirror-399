from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...types import Response


def _get_kwargs(
    bundle_key: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/policy-bundles/{bundle_key}/export/opa",
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
    bundle_key: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any]:
    r""" Export OPA-compatible policy bundle

     
            Export policy bundle as OPA-compatible .tar.gz.

            Downloads bundle from S3, extracts Rego files, repackages for OPA.
            Supports both versioned bundles (opa_aws_v1.0.2) and latest (opa_aws_latest).

            Usage:
            curl -o opa_aws_latest.tar.gz \
                http://localhost:8000/api/policy-bundles/opa_aws_latest/export/opa

            # Use with OPA
            opa eval -b opa_aws_latest.tar.gz -i input.json 'data.accurics'

            # Extract for Conftest
            tar -xzf opa_aws_latest.tar.gz
            conftest test tfplan.json -p policies/

            Returns:
                OPA-compatible tarball (application/gzip)


    Args:
        bundle_key (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """

    kwargs = _get_kwargs(
        bundle_key=bundle_key,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    bundle_key: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any]:
    r""" Export OPA-compatible policy bundle

     
            Export policy bundle as OPA-compatible .tar.gz.

            Downloads bundle from S3, extracts Rego files, repackages for OPA.
            Supports both versioned bundles (opa_aws_v1.0.2) and latest (opa_aws_latest).

            Usage:
            curl -o opa_aws_latest.tar.gz \
                http://localhost:8000/api/policy-bundles/opa_aws_latest/export/opa

            # Use with OPA
            opa eval -b opa_aws_latest.tar.gz -i input.json 'data.accurics'

            # Extract for Conftest
            tar -xzf opa_aws_latest.tar.gz
            conftest test tfplan.json -p policies/

            Returns:
                OPA-compatible tarball (application/gzip)


    Args:
        bundle_key (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """

    kwargs = _get_kwargs(
        bundle_key=bundle_key,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)

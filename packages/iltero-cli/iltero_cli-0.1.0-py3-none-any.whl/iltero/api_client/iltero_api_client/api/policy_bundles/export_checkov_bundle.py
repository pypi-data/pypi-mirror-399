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
        "url": f"/v1/policy-bundles/{bundle_key}/export/checkov",
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
    r""" Export Checkov policy bundle

     
            Export policy bundle as Checkov-compatible .tar.gz.

            Downloads bundle from S3, extracts YAML and Python checks, repackages.
            Supports both versioned bundles (checkov_aws_v2.3.4) and latest.

            Bundle Structure:
                - manifest.json: Bundle metadata
                - checks/graph/*.yaml: YAML graph checks (CKV2_*)
                - checks/resource/*.py: Python resource checks (CKV_*)

            Usage:
                curl -o checkov_aws_latest.tar.gz \
                    http://localhost:8000/api/policy-bundles/checkov_aws_latest/export/checkov

                # Extract and use with Checkov
                tar -xzf checkov_aws_latest.tar.gz
                checkov -f terraform.tf --external-checks-dir checks/

            Returns:
                Checkov-compatible tarball (application/gzip)


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
    r""" Export Checkov policy bundle

     
            Export policy bundle as Checkov-compatible .tar.gz.

            Downloads bundle from S3, extracts YAML and Python checks, repackages.
            Supports both versioned bundles (checkov_aws_v2.3.4) and latest.

            Bundle Structure:
                - manifest.json: Bundle metadata
                - checks/graph/*.yaml: YAML graph checks (CKV2_*)
                - checks/resource/*.py: Python resource checks (CKV_*)

            Usage:
                curl -o checkov_aws_latest.tar.gz \
                    http://localhost:8000/api/policy-bundles/checkov_aws_latest/export/checkov

                # Extract and use with Checkov
                tar -xzf checkov_aws_latest.tar.gz
                checkov -f terraform.tf --external-checks-dir checks/

            Returns:
                Checkov-compatible tarball (application/gzip)


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

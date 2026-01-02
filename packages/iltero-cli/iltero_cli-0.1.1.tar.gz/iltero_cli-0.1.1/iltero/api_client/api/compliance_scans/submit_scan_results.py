from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...models.scan_results_submission_schema import ScanResultsSubmissionSchema
from ...types import Response


def _get_kwargs(
    scan_id: str,
    *,
    body: ScanResultsSubmissionSchema,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/v1/compliance/{scan_id}/results/",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
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
    scan_id: str,
    *,
    client: AuthenticatedClient,
    body: ScanResultsSubmissionSchema,
) -> Response[APIResponseModel]:
    """Submit scan results from CI/CD pipeline


            Accepts scan results from CI/CD pipeline after scan execution.

            This endpoint is called by the CLI tool running in CI/CD pipelines
            after Checkov/OPA scanners complete. It processes the raw scan results,
            generates compliance evidence, calculates scores, and updates the scan status.

            The scan must already exist (created via create_static_scan or similar)
            and be in PENDING or IN_PROGRESS status.


    Args:
        scan_id (str):
        body (ScanResultsSubmissionSchema): Schema for submitting scan results from CI/CD
            pipeline.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        scan_id=scan_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    scan_id: str,
    *,
    client: AuthenticatedClient,
    body: ScanResultsSubmissionSchema,
) -> APIResponseModel | None:
    """Submit scan results from CI/CD pipeline


            Accepts scan results from CI/CD pipeline after scan execution.

            This endpoint is called by the CLI tool running in CI/CD pipelines
            after Checkov/OPA scanners complete. It processes the raw scan results,
            generates compliance evidence, calculates scores, and updates the scan status.

            The scan must already exist (created via create_static_scan or similar)
            and be in PENDING or IN_PROGRESS status.


    Args:
        scan_id (str):
        body (ScanResultsSubmissionSchema): Schema for submitting scan results from CI/CD
            pipeline.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        scan_id=scan_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    scan_id: str,
    *,
    client: AuthenticatedClient,
    body: ScanResultsSubmissionSchema,
) -> Response[APIResponseModel]:
    """Submit scan results from CI/CD pipeline


            Accepts scan results from CI/CD pipeline after scan execution.

            This endpoint is called by the CLI tool running in CI/CD pipelines
            after Checkov/OPA scanners complete. It processes the raw scan results,
            generates compliance evidence, calculates scores, and updates the scan status.

            The scan must already exist (created via create_static_scan or similar)
            and be in PENDING or IN_PROGRESS status.


    Args:
        scan_id (str):
        body (ScanResultsSubmissionSchema): Schema for submitting scan results from CI/CD
            pipeline.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        scan_id=scan_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    scan_id: str,
    *,
    client: AuthenticatedClient,
    body: ScanResultsSubmissionSchema,
) -> APIResponseModel | None:
    """Submit scan results from CI/CD pipeline


            Accepts scan results from CI/CD pipeline after scan execution.

            This endpoint is called by the CLI tool running in CI/CD pipelines
            after Checkov/OPA scanners complete. It processes the raw scan results,
            generates compliance evidence, calculates scores, and updates the scan status.

            The scan must already exist (created via create_static_scan or similar)
            and be in PENDING or IN_PROGRESS status.


    Args:
        scan_id (str):
        body (ScanResultsSubmissionSchema): Schema for submitting scan results from CI/CD
            pipeline.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            scan_id=scan_id,
            client=client,
            body=body,
        )
    ).parsed

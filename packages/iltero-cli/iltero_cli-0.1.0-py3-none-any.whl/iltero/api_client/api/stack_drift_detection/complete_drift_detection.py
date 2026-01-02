from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...models.drift_detection_result_schema import DriftDetectionResultSchema
from ...types import Response


def _get_kwargs(
    detection_id: str,
    *,
    body: DriftDetectionResultSchema,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/v1/stacks/drift/{detection_id}/complete",
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
    detection_id: str,
    *,
    client: AuthenticatedClient,
    body: DriftDetectionResultSchema,
) -> Response[APIResponseModel]:
    """Complete drift detection


            Complete a drift detection with results.

            This endpoint is called by the CI/CD system to report
            the results of the drift detection.


    Args:
        detection_id (str):
        body (DriftDetectionResultSchema): Schema for drift detection results.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        detection_id=detection_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    detection_id: str,
    *,
    client: AuthenticatedClient,
    body: DriftDetectionResultSchema,
) -> APIResponseModel | None:
    """Complete drift detection


            Complete a drift detection with results.

            This endpoint is called by the CI/CD system to report
            the results of the drift detection.


    Args:
        detection_id (str):
        body (DriftDetectionResultSchema): Schema for drift detection results.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        detection_id=detection_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    detection_id: str,
    *,
    client: AuthenticatedClient,
    body: DriftDetectionResultSchema,
) -> Response[APIResponseModel]:
    """Complete drift detection


            Complete a drift detection with results.

            This endpoint is called by the CI/CD system to report
            the results of the drift detection.


    Args:
        detection_id (str):
        body (DriftDetectionResultSchema): Schema for drift detection results.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        detection_id=detection_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    detection_id: str,
    *,
    client: AuthenticatedClient,
    body: DriftDetectionResultSchema,
) -> APIResponseModel | None:
    """Complete drift detection


            Complete a drift detection with results.

            This endpoint is called by the CI/CD system to report
            the results of the drift detection.


    Args:
        detection_id (str):
        body (DriftDetectionResultSchema): Schema for drift detection results.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            detection_id=detection_id,
            client=client,
            body=body,
        )
    ).parsed

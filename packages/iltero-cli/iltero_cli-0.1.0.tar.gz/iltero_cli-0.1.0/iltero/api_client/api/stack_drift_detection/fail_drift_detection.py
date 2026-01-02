from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...models.fail_drift_detection_error_details_type_0 import FailDriftDetectionErrorDetailsType0
from ...types import UNSET, Response, Unset


def _get_kwargs(
    detection_id: str,
    *,
    error_message: str,
    error_details: FailDriftDetectionErrorDetailsType0 | None | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["error_message"] = error_message

    json_error_details: dict[str, Any] | None | Unset
    if isinstance(error_details, Unset):
        json_error_details = UNSET
    elif isinstance(error_details, FailDriftDetectionErrorDetailsType0):
        json_error_details = error_details.to_dict()
    else:
        json_error_details = error_details
    params["error_details"] = json_error_details

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/v1/stacks/drift/{detection_id}/fail",
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
    detection_id: str,
    *,
    client: AuthenticatedClient,
    error_message: str,
    error_details: FailDriftDetectionErrorDetailsType0 | None | Unset = UNSET,
) -> Response[APIResponseModel]:
    """Mark drift detection as failed


            Mark a drift detection as failed.

            This endpoint is called when the drift detection fails
            due to an error.


    Args:
        detection_id (str):
        error_message (str):
        error_details (FailDriftDetectionErrorDetailsType0 | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        detection_id=detection_id,
        error_message=error_message,
        error_details=error_details,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    detection_id: str,
    *,
    client: AuthenticatedClient,
    error_message: str,
    error_details: FailDriftDetectionErrorDetailsType0 | None | Unset = UNSET,
) -> APIResponseModel | None:
    """Mark drift detection as failed


            Mark a drift detection as failed.

            This endpoint is called when the drift detection fails
            due to an error.


    Args:
        detection_id (str):
        error_message (str):
        error_details (FailDriftDetectionErrorDetailsType0 | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        detection_id=detection_id,
        client=client,
        error_message=error_message,
        error_details=error_details,
    ).parsed


async def asyncio_detailed(
    detection_id: str,
    *,
    client: AuthenticatedClient,
    error_message: str,
    error_details: FailDriftDetectionErrorDetailsType0 | None | Unset = UNSET,
) -> Response[APIResponseModel]:
    """Mark drift detection as failed


            Mark a drift detection as failed.

            This endpoint is called when the drift detection fails
            due to an error.


    Args:
        detection_id (str):
        error_message (str):
        error_details (FailDriftDetectionErrorDetailsType0 | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        detection_id=detection_id,
        error_message=error_message,
        error_details=error_details,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    detection_id: str,
    *,
    client: AuthenticatedClient,
    error_message: str,
    error_details: FailDriftDetectionErrorDetailsType0 | None | Unset = UNSET,
) -> APIResponseModel | None:
    """Mark drift detection as failed


            Mark a drift detection as failed.

            This endpoint is called when the drift detection fails
            due to an error.


    Args:
        detection_id (str):
        error_message (str):
        error_details (FailDriftDetectionErrorDetailsType0 | None | Unset):

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
            error_message=error_message,
            error_details=error_details,
        )
    ).parsed

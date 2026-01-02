from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...models.schedule_periodic_drift_detection_config_type_0 import SchedulePeriodicDriftDetectionConfigType0
from ...types import UNSET, Response, Unset


def _get_kwargs(
    stack_id: str,
    *,
    interval_hours: int | Unset = 24,
    detection_config: None | SchedulePeriodicDriftDetectionConfigType0 | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["interval_hours"] = interval_hours

    json_detection_config: dict[str, Any] | None | Unset
    if isinstance(detection_config, Unset):
        json_detection_config = UNSET
    elif isinstance(detection_config, SchedulePeriodicDriftDetectionConfigType0):
        json_detection_config = detection_config.to_dict()
    else:
        json_detection_config = detection_config
    params["detection_config"] = json_detection_config

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/v1/stacks/drift/stack/{stack_id}/schedule-periodic",
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
    stack_id: str,
    *,
    client: AuthenticatedClient,
    interval_hours: int | Unset = 24,
    detection_config: None | SchedulePeriodicDriftDetectionConfigType0 | Unset = UNSET,
) -> Response[APIResponseModel]:
    """Schedule periodic drift detection


            Schedule periodic drift detection for a stack.

            This endpoint configures automatic drift detection
            to run at specified intervals.


    Args:
        stack_id (str):
        interval_hours (int | Unset):  Default: 24.
        detection_config (None | SchedulePeriodicDriftDetectionConfigType0 | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        stack_id=stack_id,
        interval_hours=interval_hours,
        detection_config=detection_config,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    stack_id: str,
    *,
    client: AuthenticatedClient,
    interval_hours: int | Unset = 24,
    detection_config: None | SchedulePeriodicDriftDetectionConfigType0 | Unset = UNSET,
) -> APIResponseModel | None:
    """Schedule periodic drift detection


            Schedule periodic drift detection for a stack.

            This endpoint configures automatic drift detection
            to run at specified intervals.


    Args:
        stack_id (str):
        interval_hours (int | Unset):  Default: 24.
        detection_config (None | SchedulePeriodicDriftDetectionConfigType0 | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        stack_id=stack_id,
        client=client,
        interval_hours=interval_hours,
        detection_config=detection_config,
    ).parsed


async def asyncio_detailed(
    stack_id: str,
    *,
    client: AuthenticatedClient,
    interval_hours: int | Unset = 24,
    detection_config: None | SchedulePeriodicDriftDetectionConfigType0 | Unset = UNSET,
) -> Response[APIResponseModel]:
    """Schedule periodic drift detection


            Schedule periodic drift detection for a stack.

            This endpoint configures automatic drift detection
            to run at specified intervals.


    Args:
        stack_id (str):
        interval_hours (int | Unset):  Default: 24.
        detection_config (None | SchedulePeriodicDriftDetectionConfigType0 | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        stack_id=stack_id,
        interval_hours=interval_hours,
        detection_config=detection_config,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    stack_id: str,
    *,
    client: AuthenticatedClient,
    interval_hours: int | Unset = 24,
    detection_config: None | SchedulePeriodicDriftDetectionConfigType0 | Unset = UNSET,
) -> APIResponseModel | None:
    """Schedule periodic drift detection


            Schedule periodic drift detection for a stack.

            This endpoint configures automatic drift detection
            to run at specified intervals.


    Args:
        stack_id (str):
        interval_hours (int | Unset):  Default: 24.
        detection_config (None | SchedulePeriodicDriftDetectionConfigType0 | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            stack_id=stack_id,
            client=client,
            interval_hours=interval_hours,
            detection_config=detection_config,
        )
    ).parsed

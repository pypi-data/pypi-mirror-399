from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...models.monitoring_setup_request_schema import MonitoringSetupRequestSchema
from ...types import Response


def _get_kwargs(
    stack_id: str,
    *,
    body: MonitoringSetupRequestSchema,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/v1/compliance/stacks/{stack_id}/monitoring/setup",
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
    stack_id: str,
    *,
    client: AuthenticatedClient,
    body: MonitoringSetupRequestSchema,
) -> Response[APIResponseModel]:
    """Setup compliance monitoring


            Configures continuous compliance monitoring for a stack with
            customizable check intervals, alert thresholds, and notification channels.


    Args:
        stack_id (str):
        body (MonitoringSetupRequestSchema): Request schema for setting up compliance monitoring.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        stack_id=stack_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    stack_id: str,
    *,
    client: AuthenticatedClient,
    body: MonitoringSetupRequestSchema,
) -> APIResponseModel | None:
    """Setup compliance monitoring


            Configures continuous compliance monitoring for a stack with
            customizable check intervals, alert thresholds, and notification channels.


    Args:
        stack_id (str):
        body (MonitoringSetupRequestSchema): Request schema for setting up compliance monitoring.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        stack_id=stack_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    stack_id: str,
    *,
    client: AuthenticatedClient,
    body: MonitoringSetupRequestSchema,
) -> Response[APIResponseModel]:
    """Setup compliance monitoring


            Configures continuous compliance monitoring for a stack with
            customizable check intervals, alert thresholds, and notification channels.


    Args:
        stack_id (str):
        body (MonitoringSetupRequestSchema): Request schema for setting up compliance monitoring.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        stack_id=stack_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    stack_id: str,
    *,
    client: AuthenticatedClient,
    body: MonitoringSetupRequestSchema,
) -> APIResponseModel | None:
    """Setup compliance monitoring


            Configures continuous compliance monitoring for a stack with
            customizable check intervals, alert thresholds, and notification channels.


    Args:
        stack_id (str):
        body (MonitoringSetupRequestSchema): Request schema for setting up compliance monitoring.

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
            body=body,
        )
    ).parsed

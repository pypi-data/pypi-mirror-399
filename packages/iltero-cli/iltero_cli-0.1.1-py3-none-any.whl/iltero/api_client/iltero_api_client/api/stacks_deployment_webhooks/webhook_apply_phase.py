from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...models.apply_phase_schema import ApplyPhaseSchema
from ...types import Response


def _get_kwargs(
    *,
    body: ApplyPhaseSchema,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/stacks/webhooks/apply",
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
    *,
    client: AuthenticatedClient,
    body: ApplyPhaseSchema,
) -> Response[APIResponseModel]:
    """Apply phase webhook


            Receives apply results from CI/CD pipeline.

            This webhook is called after terraform apply completes.
            Records deployment results and optionally schedules drift detection
            based on environment policies or explicit request.

            Note: Requires internal API key authentication.


    Args:
        body (ApplyPhaseSchema): Schema for apply phase webhook.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: ApplyPhaseSchema,
) -> APIResponseModel | None:
    """Apply phase webhook


            Receives apply results from CI/CD pipeline.

            This webhook is called after terraform apply completes.
            Records deployment results and optionally schedules drift detection
            based on environment policies or explicit request.

            Note: Requires internal API key authentication.


    Args:
        body (ApplyPhaseSchema): Schema for apply phase webhook.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: ApplyPhaseSchema,
) -> Response[APIResponseModel]:
    """Apply phase webhook


            Receives apply results from CI/CD pipeline.

            This webhook is called after terraform apply completes.
            Records deployment results and optionally schedules drift detection
            based on environment policies or explicit request.

            Note: Requires internal API key authentication.


    Args:
        body (ApplyPhaseSchema): Schema for apply phase webhook.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: ApplyPhaseSchema,
) -> APIResponseModel | None:
    """Apply phase webhook


            Receives apply results from CI/CD pipeline.

            This webhook is called after terraform apply completes.
            Records deployment results and optionally schedules drift detection
            based on environment policies or explicit request.

            Note: Requires internal API key authentication.


    Args:
        body (ApplyPhaseSchema): Schema for apply phase webhook.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed

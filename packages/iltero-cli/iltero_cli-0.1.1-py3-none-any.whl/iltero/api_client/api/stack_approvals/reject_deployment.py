from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...models.reject_request_schema import RejectRequestSchema
from ...types import Response


def _get_kwargs(
    approval_id: str,
    *,
    body: RejectRequestSchema,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/v1/stacks/approvals/{approval_id}/reject",
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
    approval_id: str,
    *,
    client: AuthenticatedClient,
    body: RejectRequestSchema,
) -> Response[APIResponseModel]:
    """Reject deployment


            Reject a pending deployment request.

            This endpoint allows authorized users to reject a deployment
            with an optional comment explaining the rejection.


    Args:
        approval_id (str):
        body (RejectRequestSchema): Schema for rejecting a deployment.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        approval_id=approval_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    approval_id: str,
    *,
    client: AuthenticatedClient,
    body: RejectRequestSchema,
) -> APIResponseModel | None:
    """Reject deployment


            Reject a pending deployment request.

            This endpoint allows authorized users to reject a deployment
            with an optional comment explaining the rejection.


    Args:
        approval_id (str):
        body (RejectRequestSchema): Schema for rejecting a deployment.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        approval_id=approval_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    approval_id: str,
    *,
    client: AuthenticatedClient,
    body: RejectRequestSchema,
) -> Response[APIResponseModel]:
    """Reject deployment


            Reject a pending deployment request.

            This endpoint allows authorized users to reject a deployment
            with an optional comment explaining the rejection.


    Args:
        approval_id (str):
        body (RejectRequestSchema): Schema for rejecting a deployment.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        approval_id=approval_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    approval_id: str,
    *,
    client: AuthenticatedClient,
    body: RejectRequestSchema,
) -> APIResponseModel | None:
    """Reject deployment


            Reject a pending deployment request.

            This endpoint allows authorized users to reject a deployment
            with an optional comment explaining the rejection.


    Args:
        approval_id (str):
        body (RejectRequestSchema): Schema for rejecting a deployment.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            approval_id=approval_id,
            client=client,
            body=body,
        )
    ).parsed

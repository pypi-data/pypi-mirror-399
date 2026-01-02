from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...models.violation_update_schema import ViolationUpdateSchema
from ...types import Response


def _get_kwargs(
    violation_id: str,
    *,
    body: ViolationUpdateSchema,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": f"/v1/compliance/violations/{violation_id}",
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
    violation_id: str,
    *,
    client: AuthenticatedClient,
    body: ViolationUpdateSchema,
) -> Response[APIResponseModel]:
    """Update violation status


            Updates the status of a compliance violation.

            Use this endpoint to acknowledge violations, mark them as resolved,
            or flag them for remediation. Supports adding comments for audit trail.


    Args:
        violation_id (str):
        body (ViolationUpdateSchema): Schema for updating violation status.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        violation_id=violation_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    violation_id: str,
    *,
    client: AuthenticatedClient,
    body: ViolationUpdateSchema,
) -> APIResponseModel | None:
    """Update violation status


            Updates the status of a compliance violation.

            Use this endpoint to acknowledge violations, mark them as resolved,
            or flag them for remediation. Supports adding comments for audit trail.


    Args:
        violation_id (str):
        body (ViolationUpdateSchema): Schema for updating violation status.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        violation_id=violation_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    violation_id: str,
    *,
    client: AuthenticatedClient,
    body: ViolationUpdateSchema,
) -> Response[APIResponseModel]:
    """Update violation status


            Updates the status of a compliance violation.

            Use this endpoint to acknowledge violations, mark them as resolved,
            or flag them for remediation. Supports adding comments for audit trail.


    Args:
        violation_id (str):
        body (ViolationUpdateSchema): Schema for updating violation status.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        violation_id=violation_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    violation_id: str,
    *,
    client: AuthenticatedClient,
    body: ViolationUpdateSchema,
) -> APIResponseModel | None:
    """Update violation status


            Updates the status of a compliance violation.

            Use this endpoint to acknowledge violations, mark them as resolved,
            or flag them for remediation. Supports adding comments for audit trail.


    Args:
        violation_id (str):
        body (ViolationUpdateSchema): Schema for updating violation status.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            violation_id=violation_id,
            client=client,
            body=body,
        )
    ).parsed

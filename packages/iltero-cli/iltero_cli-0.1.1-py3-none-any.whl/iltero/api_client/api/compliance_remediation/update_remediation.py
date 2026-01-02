from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...models.remediation_update_schema import RemediationUpdateSchema
from ...types import Response


def _get_kwargs(
    remediation_id: str,
    *,
    body: RemediationUpdateSchema,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": f"/v1/compliance/remediations/{remediation_id}",
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
    remediation_id: str,
    *,
    client: AuthenticatedClient,
    body: RemediationUpdateSchema,
) -> Response[APIResponseModel]:
    """Update remediation status


            Updates the status of a remediation action.

            Use this endpoint to track remediation progress, mark as completed,
            or update with results of the remediation attempt.


    Args:
        remediation_id (str):
        body (RemediationUpdateSchema): Schema for updating a remediation action.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        remediation_id=remediation_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    remediation_id: str,
    *,
    client: AuthenticatedClient,
    body: RemediationUpdateSchema,
) -> APIResponseModel | None:
    """Update remediation status


            Updates the status of a remediation action.

            Use this endpoint to track remediation progress, mark as completed,
            or update with results of the remediation attempt.


    Args:
        remediation_id (str):
        body (RemediationUpdateSchema): Schema for updating a remediation action.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        remediation_id=remediation_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    remediation_id: str,
    *,
    client: AuthenticatedClient,
    body: RemediationUpdateSchema,
) -> Response[APIResponseModel]:
    """Update remediation status


            Updates the status of a remediation action.

            Use this endpoint to track remediation progress, mark as completed,
            or update with results of the remediation attempt.


    Args:
        remediation_id (str):
        body (RemediationUpdateSchema): Schema for updating a remediation action.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        remediation_id=remediation_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    remediation_id: str,
    *,
    client: AuthenticatedClient,
    body: RemediationUpdateSchema,
) -> APIResponseModel | None:
    """Update remediation status


            Updates the status of a remediation action.

            Use this endpoint to track remediation progress, mark as completed,
            or update with results of the remediation attempt.


    Args:
        remediation_id (str):
        body (RemediationUpdateSchema): Schema for updating a remediation action.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            remediation_id=remediation_id,
            client=client,
            body=body,
        )
    ).parsed

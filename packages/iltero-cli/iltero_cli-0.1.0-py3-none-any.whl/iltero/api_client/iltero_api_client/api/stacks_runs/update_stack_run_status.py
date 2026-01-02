from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...models.stack_run_update_schema import StackRunUpdateSchema
from ...types import Response


def _get_kwargs(
    stack_id: str,
    run_id: str,
    *,
    body: StackRunUpdateSchema,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": f"/v1/stacks/{stack_id}/runs/{run_id}/status",
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
    run_id: str,
    *,
    client: AuthenticatedClient,
    body: StackRunUpdateSchema,
) -> Response[APIResponseModel]:
    """Update run status


            Updates the status and output of a stack run.

            This endpoint is typically called by CI/CD systems to report
            run progress and results. Requires appropriate authentication.


    Args:
        stack_id (str):
        run_id (str):
        body (StackRunUpdateSchema): Schema used by internal processes (e.g., CI/CD webhook) to
            update run status.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        stack_id=stack_id,
        run_id=run_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    stack_id: str,
    run_id: str,
    *,
    client: AuthenticatedClient,
    body: StackRunUpdateSchema,
) -> APIResponseModel | None:
    """Update run status


            Updates the status and output of a stack run.

            This endpoint is typically called by CI/CD systems to report
            run progress and results. Requires appropriate authentication.


    Args:
        stack_id (str):
        run_id (str):
        body (StackRunUpdateSchema): Schema used by internal processes (e.g., CI/CD webhook) to
            update run status.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        stack_id=stack_id,
        run_id=run_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    stack_id: str,
    run_id: str,
    *,
    client: AuthenticatedClient,
    body: StackRunUpdateSchema,
) -> Response[APIResponseModel]:
    """Update run status


            Updates the status and output of a stack run.

            This endpoint is typically called by CI/CD systems to report
            run progress and results. Requires appropriate authentication.


    Args:
        stack_id (str):
        run_id (str):
        body (StackRunUpdateSchema): Schema used by internal processes (e.g., CI/CD webhook) to
            update run status.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        stack_id=stack_id,
        run_id=run_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    stack_id: str,
    run_id: str,
    *,
    client: AuthenticatedClient,
    body: StackRunUpdateSchema,
) -> APIResponseModel | None:
    """Update run status


            Updates the status and output of a stack run.

            This endpoint is typically called by CI/CD systems to report
            run progress and results. Requires appropriate authentication.


    Args:
        stack_id (str):
        run_id (str):
        body (StackRunUpdateSchema): Schema used by internal processes (e.g., CI/CD webhook) to
            update run status.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            stack_id=stack_id,
            run_id=run_id,
            client=client,
            body=body,
        )
    ).parsed

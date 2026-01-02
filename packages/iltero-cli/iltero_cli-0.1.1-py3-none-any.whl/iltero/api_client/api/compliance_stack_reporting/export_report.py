from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    stack_id: str,
    report_id: str,
    *,
    format_: str | Unset = "PDF",
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["format"] = format_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/v1/compliance/stacks/{stack_id}/reports/{report_id}/export",
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
    report_id: str,
    *,
    client: AuthenticatedClient,
    format_: str | Unset = "PDF",
) -> Response[APIResponseModel]:
    """Export report

     Exports a compliance report in specified format (PDF, JSON, CSV).

    Args:
        stack_id (str):
        report_id (str):
        format_ (str | Unset):  Default: 'PDF'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        stack_id=stack_id,
        report_id=report_id,
        format_=format_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    stack_id: str,
    report_id: str,
    *,
    client: AuthenticatedClient,
    format_: str | Unset = "PDF",
) -> APIResponseModel | None:
    """Export report

     Exports a compliance report in specified format (PDF, JSON, CSV).

    Args:
        stack_id (str):
        report_id (str):
        format_ (str | Unset):  Default: 'PDF'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        stack_id=stack_id,
        report_id=report_id,
        client=client,
        format_=format_,
    ).parsed


async def asyncio_detailed(
    stack_id: str,
    report_id: str,
    *,
    client: AuthenticatedClient,
    format_: str | Unset = "PDF",
) -> Response[APIResponseModel]:
    """Export report

     Exports a compliance report in specified format (PDF, JSON, CSV).

    Args:
        stack_id (str):
        report_id (str):
        format_ (str | Unset):  Default: 'PDF'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        stack_id=stack_id,
        report_id=report_id,
        format_=format_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    stack_id: str,
    report_id: str,
    *,
    client: AuthenticatedClient,
    format_: str | Unset = "PDF",
) -> APIResponseModel | None:
    """Export report

     Exports a compliance report in specified format (PDF, JSON, CSV).

    Args:
        stack_id (str):
        report_id (str):
        format_ (str | Unset):  Default: 'PDF'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            stack_id=stack_id,
            report_id=report_id,
            client=client,
            format_=format_,
        )
    ).parsed

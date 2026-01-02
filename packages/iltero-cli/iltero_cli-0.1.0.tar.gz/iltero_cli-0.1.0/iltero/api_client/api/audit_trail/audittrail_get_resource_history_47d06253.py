import datetime
from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    resource_type: str,
    resource_id: str,
    *,
    start_date: datetime.datetime | None | Unset = UNSET,
    end_date: datetime.datetime | None | Unset = UNSET,
    limit: int | Unset = 100,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_start_date: None | str | Unset
    if isinstance(start_date, Unset):
        json_start_date = UNSET
    elif isinstance(start_date, datetime.datetime):
        json_start_date = start_date.isoformat()
    else:
        json_start_date = start_date
    params["start_date"] = json_start_date

    json_end_date: None | str | Unset
    if isinstance(end_date, Unset):
        json_end_date = UNSET
    elif isinstance(end_date, datetime.datetime):
        json_end_date = end_date.isoformat()
    else:
        json_end_date = end_date
    params["end_date"] = json_end_date

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/audit/logs/resource/{resource_type}/{resource_id}",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> APIResponseModel | None:
    if response.status_code == 200:
        response_200 = APIResponseModel.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = APIResponseModel.from_dict(response.json())

        return response_400

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
    resource_type: str,
    resource_id: str,
    *,
    client: AuthenticatedClient,
    start_date: datetime.datetime | None | Unset = UNSET,
    end_date: datetime.datetime | None | Unset = UNSET,
    limit: int | Unset = 100,
) -> Response[APIResponseModel]:
    """Get Resource History

     Get audit history for specific resource.

    Args:
        request: HTTP request
        resource_type: Type of resource
        resource_id: Resource ID
        start_date: Optional start date filter
        end_date: Optional end date filter
        limit: Maximum number of logs

    Returns:
        API response with resource history

    Raises:
        400: If validation fails

    Args:
        resource_type (str):
        resource_id (str):
        start_date (datetime.datetime | None | Unset):
        end_date (datetime.datetime | None | Unset):
        limit (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        resource_type=resource_type,
        resource_id=resource_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    resource_type: str,
    resource_id: str,
    *,
    client: AuthenticatedClient,
    start_date: datetime.datetime | None | Unset = UNSET,
    end_date: datetime.datetime | None | Unset = UNSET,
    limit: int | Unset = 100,
) -> APIResponseModel | None:
    """Get Resource History

     Get audit history for specific resource.

    Args:
        request: HTTP request
        resource_type: Type of resource
        resource_id: Resource ID
        start_date: Optional start date filter
        end_date: Optional end date filter
        limit: Maximum number of logs

    Returns:
        API response with resource history

    Raises:
        400: If validation fails

    Args:
        resource_type (str):
        resource_id (str):
        start_date (datetime.datetime | None | Unset):
        end_date (datetime.datetime | None | Unset):
        limit (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        resource_type=resource_type,
        resource_id=resource_id,
        client=client,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    resource_type: str,
    resource_id: str,
    *,
    client: AuthenticatedClient,
    start_date: datetime.datetime | None | Unset = UNSET,
    end_date: datetime.datetime | None | Unset = UNSET,
    limit: int | Unset = 100,
) -> Response[APIResponseModel]:
    """Get Resource History

     Get audit history for specific resource.

    Args:
        request: HTTP request
        resource_type: Type of resource
        resource_id: Resource ID
        start_date: Optional start date filter
        end_date: Optional end date filter
        limit: Maximum number of logs

    Returns:
        API response with resource history

    Raises:
        400: If validation fails

    Args:
        resource_type (str):
        resource_id (str):
        start_date (datetime.datetime | None | Unset):
        end_date (datetime.datetime | None | Unset):
        limit (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        resource_type=resource_type,
        resource_id=resource_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    resource_type: str,
    resource_id: str,
    *,
    client: AuthenticatedClient,
    start_date: datetime.datetime | None | Unset = UNSET,
    end_date: datetime.datetime | None | Unset = UNSET,
    limit: int | Unset = 100,
) -> APIResponseModel | None:
    """Get Resource History

     Get audit history for specific resource.

    Args:
        request: HTTP request
        resource_type: Type of resource
        resource_id: Resource ID
        start_date: Optional start date filter
        end_date: Optional end date filter
        limit: Maximum number of logs

    Returns:
        API response with resource history

    Raises:
        400: If validation fails

    Args:
        resource_type (str):
        resource_id (str):
        start_date (datetime.datetime | None | Unset):
        end_date (datetime.datetime | None | Unset):
        limit (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            resource_type=resource_type,
            resource_id=resource_id,
            client=client,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )
    ).parsed

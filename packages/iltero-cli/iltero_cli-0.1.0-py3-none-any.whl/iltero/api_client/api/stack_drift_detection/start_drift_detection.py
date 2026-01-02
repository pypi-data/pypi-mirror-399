from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    detection_id: str,
    *,
    run_id: None | str | Unset = UNSET,
    external_scan_id: None | str | Unset = UNSET,
    external_scan_url: None | str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_run_id: None | str | Unset
    if isinstance(run_id, Unset):
        json_run_id = UNSET
    else:
        json_run_id = run_id
    params["run_id"] = json_run_id

    json_external_scan_id: None | str | Unset
    if isinstance(external_scan_id, Unset):
        json_external_scan_id = UNSET
    else:
        json_external_scan_id = external_scan_id
    params["external_scan_id"] = json_external_scan_id

    json_external_scan_url: None | str | Unset
    if isinstance(external_scan_url, Unset):
        json_external_scan_url = UNSET
    else:
        json_external_scan_url = external_scan_url
    params["external_scan_url"] = json_external_scan_url

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/v1/stacks/drift/{detection_id}/start",
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
    run_id: None | str | Unset = UNSET,
    external_scan_id: None | str | Unset = UNSET,
    external_scan_url: None | str | Unset = UNSET,
) -> Response[APIResponseModel]:
    """Start drift detection


            Mark a drift detection as started.

            This endpoint is typically called by the CI/CD system when
            it begins executing the drift detection.


    Args:
        detection_id (str):
        run_id (None | str | Unset):
        external_scan_id (None | str | Unset):
        external_scan_url (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        detection_id=detection_id,
        run_id=run_id,
        external_scan_id=external_scan_id,
        external_scan_url=external_scan_url,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    detection_id: str,
    *,
    client: AuthenticatedClient,
    run_id: None | str | Unset = UNSET,
    external_scan_id: None | str | Unset = UNSET,
    external_scan_url: None | str | Unset = UNSET,
) -> APIResponseModel | None:
    """Start drift detection


            Mark a drift detection as started.

            This endpoint is typically called by the CI/CD system when
            it begins executing the drift detection.


    Args:
        detection_id (str):
        run_id (None | str | Unset):
        external_scan_id (None | str | Unset):
        external_scan_url (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        detection_id=detection_id,
        client=client,
        run_id=run_id,
        external_scan_id=external_scan_id,
        external_scan_url=external_scan_url,
    ).parsed


async def asyncio_detailed(
    detection_id: str,
    *,
    client: AuthenticatedClient,
    run_id: None | str | Unset = UNSET,
    external_scan_id: None | str | Unset = UNSET,
    external_scan_url: None | str | Unset = UNSET,
) -> Response[APIResponseModel]:
    """Start drift detection


            Mark a drift detection as started.

            This endpoint is typically called by the CI/CD system when
            it begins executing the drift detection.


    Args:
        detection_id (str):
        run_id (None | str | Unset):
        external_scan_id (None | str | Unset):
        external_scan_url (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        detection_id=detection_id,
        run_id=run_id,
        external_scan_id=external_scan_id,
        external_scan_url=external_scan_url,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    detection_id: str,
    *,
    client: AuthenticatedClient,
    run_id: None | str | Unset = UNSET,
    external_scan_id: None | str | Unset = UNSET,
    external_scan_url: None | str | Unset = UNSET,
) -> APIResponseModel | None:
    """Start drift detection


            Mark a drift detection as started.

            This endpoint is typically called by the CI/CD system when
            it begins executing the drift detection.


    Args:
        detection_id (str):
        run_id (None | str | Unset):
        external_scan_id (None | str | Unset):
        external_scan_url (None | str | Unset):

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
            run_id=run_id,
            external_scan_id=external_scan_id,
            external_scan_url=external_scan_url,
        )
    ).parsed

from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    scan_id: None | str | Unset = UNSET,
    stack_id: None | str | Unset = UNSET,
    policy_id: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_scan_id: None | str | Unset
    if isinstance(scan_id, Unset):
        json_scan_id = UNSET
    else:
        json_scan_id = scan_id
    params["scan_id"] = json_scan_id

    json_stack_id: None | str | Unset
    if isinstance(stack_id, Unset):
        json_stack_id = UNSET
    else:
        json_stack_id = stack_id
    params["stack_id"] = json_stack_id

    json_policy_id: None | str | Unset
    if isinstance(policy_id, Unset):
        json_policy_id = UNSET
    else:
        json_policy_id = policy_id
    params["policy_id"] = json_policy_id

    json_status: None | str | Unset
    if isinstance(status, Unset):
        json_status = UNSET
    else:
        json_status = status
    params["status"] = json_status

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/compliance/violations/",
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
    *,
    client: AuthenticatedClient,
    scan_id: None | str | Unset = UNSET,
    stack_id: None | str | Unset = UNSET,
    policy_id: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
) -> Response[APIResponseModel]:
    """List compliance violations


            Retrieves violations found during compliance scans.

            Use filters to find specific violations by scan, stack, or policy.
            Results include severity, resource details, and remediation guidance.


    Args:
        scan_id (None | str | Unset):
        stack_id (None | str | Unset):
        policy_id (None | str | Unset):
        status (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        scan_id=scan_id,
        stack_id=stack_id,
        policy_id=policy_id,
        status=status,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    scan_id: None | str | Unset = UNSET,
    stack_id: None | str | Unset = UNSET,
    policy_id: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
) -> APIResponseModel | None:
    """List compliance violations


            Retrieves violations found during compliance scans.

            Use filters to find specific violations by scan, stack, or policy.
            Results include severity, resource details, and remediation guidance.


    Args:
        scan_id (None | str | Unset):
        stack_id (None | str | Unset):
        policy_id (None | str | Unset):
        status (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        client=client,
        scan_id=scan_id,
        stack_id=stack_id,
        policy_id=policy_id,
        status=status,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    scan_id: None | str | Unset = UNSET,
    stack_id: None | str | Unset = UNSET,
    policy_id: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
) -> Response[APIResponseModel]:
    """List compliance violations


            Retrieves violations found during compliance scans.

            Use filters to find specific violations by scan, stack, or policy.
            Results include severity, resource details, and remediation guidance.


    Args:
        scan_id (None | str | Unset):
        stack_id (None | str | Unset):
        policy_id (None | str | Unset):
        status (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        scan_id=scan_id,
        stack_id=stack_id,
        policy_id=policy_id,
        status=status,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    scan_id: None | str | Unset = UNSET,
    stack_id: None | str | Unset = UNSET,
    policy_id: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
) -> APIResponseModel | None:
    """List compliance violations


            Retrieves violations found during compliance scans.

            Use filters to find specific violations by scan, stack, or policy.
            Results include severity, resource details, and remediation guidance.


    Args:
        scan_id (None | str | Unset):
        stack_id (None | str | Unset):
        policy_id (None | str | Unset):
        status (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            client=client,
            scan_id=scan_id,
            stack_id=stack_id,
            policy_id=policy_id,
            status=status,
        )
    ).parsed

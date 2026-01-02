from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...types import Response


def _get_kwargs(
    policy_set_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": f"/v1/compliance/policies/sets/{policy_set_id}",
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
    policy_set_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[APIResponseModel]:
    """Delete policy set


            Deletes a policy set from the system.

            Use with caution as this permanently removes the policy set.
            Existing scans using this set will not be affected. Requires admin permissions.


    Args:
        policy_set_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        policy_set_id=policy_set_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    policy_set_id: str,
    *,
    client: AuthenticatedClient,
) -> APIResponseModel | None:
    """Delete policy set


            Deletes a policy set from the system.

            Use with caution as this permanently removes the policy set.
            Existing scans using this set will not be affected. Requires admin permissions.


    Args:
        policy_set_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        policy_set_id=policy_set_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    policy_set_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[APIResponseModel]:
    """Delete policy set


            Deletes a policy set from the system.

            Use with caution as this permanently removes the policy set.
            Existing scans using this set will not be affected. Requires admin permissions.


    Args:
        policy_set_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        policy_set_id=policy_set_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    policy_set_id: str,
    *,
    client: AuthenticatedClient,
) -> APIResponseModel | None:
    """Delete policy set


            Deletes a policy set from the system.

            Use with caution as this permanently removes the policy set.
            Existing scans using this set will not be affected. Requires admin permissions.


    Args:
        policy_set_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            policy_set_id=policy_set_id,
            client=client,
        )
    ).parsed

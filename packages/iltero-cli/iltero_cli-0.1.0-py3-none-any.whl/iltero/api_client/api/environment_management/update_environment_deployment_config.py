from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...models.deployment_policies_schema import DeploymentPoliciesSchema
from ...types import Response


def _get_kwargs(
    environment_id: str,
    *,
    body: DeploymentPoliciesSchema,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": f"/v1/environments/{environment_id}/policies/deployment",
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
    environment_id: str,
    *,
    client: AuthenticatedClient,
    body: DeploymentPoliciesSchema,
) -> Response[APIResponseModel]:
    """Update deployment policies


            Update deployment automation and pipeline policies for the environment.

            This controls deployment strategies, approval workflows, and automation
            settings for all workspaces in this environment.


    Args:
        environment_id (str):
        body (DeploymentPoliciesSchema): Schema for deployment policies API endpoints.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        environment_id=environment_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    environment_id: str,
    *,
    client: AuthenticatedClient,
    body: DeploymentPoliciesSchema,
) -> APIResponseModel | None:
    """Update deployment policies


            Update deployment automation and pipeline policies for the environment.

            This controls deployment strategies, approval workflows, and automation
            settings for all workspaces in this environment.


    Args:
        environment_id (str):
        body (DeploymentPoliciesSchema): Schema for deployment policies API endpoints.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        environment_id=environment_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    environment_id: str,
    *,
    client: AuthenticatedClient,
    body: DeploymentPoliciesSchema,
) -> Response[APIResponseModel]:
    """Update deployment policies


            Update deployment automation and pipeline policies for the environment.

            This controls deployment strategies, approval workflows, and automation
            settings for all workspaces in this environment.


    Args:
        environment_id (str):
        body (DeploymentPoliciesSchema): Schema for deployment policies API endpoints.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        environment_id=environment_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    environment_id: str,
    *,
    client: AuthenticatedClient,
    body: DeploymentPoliciesSchema,
) -> APIResponseModel | None:
    """Update deployment policies


            Update deployment automation and pipeline policies for the environment.

            This controls deployment strategies, approval workflows, and automation
            settings for all workspaces in this environment.


    Args:
        environment_id (str):
        body (DeploymentPoliciesSchema): Schema for deployment policies API endpoints.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            environment_id=environment_id,
            client=client,
            body=body,
        )
    ).parsed

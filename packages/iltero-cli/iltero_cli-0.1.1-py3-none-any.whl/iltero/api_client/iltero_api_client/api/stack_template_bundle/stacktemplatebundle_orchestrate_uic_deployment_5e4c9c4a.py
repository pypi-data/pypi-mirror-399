from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...models.stacktemplatebundle_orchestrate_uic_deployment_5e4c9c4a_deployment_config_type_0 import (
    StacktemplatebundleOrchestrateUicDeployment5E4C9C4ADeploymentConfigType0,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    stack_id: str,
    *,
    deployment_config: None | StacktemplatebundleOrchestrateUicDeployment5E4C9C4ADeploymentConfigType0 | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_deployment_config: dict[str, Any] | None | Unset
    if isinstance(deployment_config, Unset):
        json_deployment_config = UNSET
    elif isinstance(deployment_config, StacktemplatebundleOrchestrateUicDeployment5E4C9C4ADeploymentConfigType0):
        json_deployment_config = deployment_config.to_dict()
    else:
        json_deployment_config = deployment_config
    params["deployment_config"] = json_deployment_config

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/v1/stacks/{stack_id}/template-bundle/deploy",
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
    *,
    client: AuthenticatedClient,
    deployment_config: None | StacktemplatebundleOrchestrateUicDeployment5E4C9C4ADeploymentConfigType0 | Unset = UNSET,
) -> Response[APIResponseModel]:
    """Orchestrate Uic Deployment

     Orchestrate UIC-coordinated deployment.

    Handles deployment ordering, dependency resolution, and cross-unit
    data flows according to the Template Bundle UIC contracts.

    Args:
        stack_id (str):
        deployment_config (None |
            StacktemplatebundleOrchestrateUicDeployment5E4C9C4ADeploymentConfigType0 | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        stack_id=stack_id,
        deployment_config=deployment_config,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    stack_id: str,
    *,
    client: AuthenticatedClient,
    deployment_config: None | StacktemplatebundleOrchestrateUicDeployment5E4C9C4ADeploymentConfigType0 | Unset = UNSET,
) -> APIResponseModel | None:
    """Orchestrate Uic Deployment

     Orchestrate UIC-coordinated deployment.

    Handles deployment ordering, dependency resolution, and cross-unit
    data flows according to the Template Bundle UIC contracts.

    Args:
        stack_id (str):
        deployment_config (None |
            StacktemplatebundleOrchestrateUicDeployment5E4C9C4ADeploymentConfigType0 | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        stack_id=stack_id,
        client=client,
        deployment_config=deployment_config,
    ).parsed


async def asyncio_detailed(
    stack_id: str,
    *,
    client: AuthenticatedClient,
    deployment_config: None | StacktemplatebundleOrchestrateUicDeployment5E4C9C4ADeploymentConfigType0 | Unset = UNSET,
) -> Response[APIResponseModel]:
    """Orchestrate Uic Deployment

     Orchestrate UIC-coordinated deployment.

    Handles deployment ordering, dependency resolution, and cross-unit
    data flows according to the Template Bundle UIC contracts.

    Args:
        stack_id (str):
        deployment_config (None |
            StacktemplatebundleOrchestrateUicDeployment5E4C9C4ADeploymentConfigType0 | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        stack_id=stack_id,
        deployment_config=deployment_config,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    stack_id: str,
    *,
    client: AuthenticatedClient,
    deployment_config: None | StacktemplatebundleOrchestrateUicDeployment5E4C9C4ADeploymentConfigType0 | Unset = UNSET,
) -> APIResponseModel | None:
    """Orchestrate Uic Deployment

     Orchestrate UIC-coordinated deployment.

    Handles deployment ordering, dependency resolution, and cross-unit
    data flows according to the Template Bundle UIC contracts.

    Args:
        stack_id (str):
        deployment_config (None |
            StacktemplatebundleOrchestrateUicDeployment5E4C9C4ADeploymentConfigType0 | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            stack_id=stack_id,
            client=client,
            deployment_config=deployment_config,
        )
    ).parsed

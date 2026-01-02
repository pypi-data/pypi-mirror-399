from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...models.stack_resource_terraform_state_update_schema import StackResourceTerraformStateUpdateSchema
from ...types import Response


def _get_kwargs(
    stack_id: str,
    *,
    body: StackResourceTerraformStateUpdateSchema,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/v1/stacks/{stack_id}/resources/terraform-state",
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
    *,
    client: AuthenticatedClient,
    body: StackResourceTerraformStateUpdateSchema,
) -> Response[APIResponseModel]:
    """Update Terraform State

     Update Terraform state for a resource.

    Called after Terraform apply to update resource state.

    Args:
        stack_id (str):
        body (StackResourceTerraformStateUpdateSchema): Schema for updating Terraform state of a
            resource.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        stack_id=stack_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    stack_id: str,
    *,
    client: AuthenticatedClient,
    body: StackResourceTerraformStateUpdateSchema,
) -> APIResponseModel | None:
    """Update Terraform State

     Update Terraform state for a resource.

    Called after Terraform apply to update resource state.

    Args:
        stack_id (str):
        body (StackResourceTerraformStateUpdateSchema): Schema for updating Terraform state of a
            resource.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        stack_id=stack_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    stack_id: str,
    *,
    client: AuthenticatedClient,
    body: StackResourceTerraformStateUpdateSchema,
) -> Response[APIResponseModel]:
    """Update Terraform State

     Update Terraform state for a resource.

    Called after Terraform apply to update resource state.

    Args:
        stack_id (str):
        body (StackResourceTerraformStateUpdateSchema): Schema for updating Terraform state of a
            resource.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        stack_id=stack_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    stack_id: str,
    *,
    client: AuthenticatedClient,
    body: StackResourceTerraformStateUpdateSchema,
) -> APIResponseModel | None:
    """Update Terraform State

     Update Terraform state for a resource.

    Called after Terraform apply to update resource state.

    Args:
        stack_id (str):
        body (StackResourceTerraformStateUpdateSchema): Schema for updating Terraform state of a
            resource.

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
            body=body,
        )
    ).parsed

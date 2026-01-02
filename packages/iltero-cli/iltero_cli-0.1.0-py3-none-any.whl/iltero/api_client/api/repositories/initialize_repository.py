from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...models.repository_initialize_request_schema import RepositoryInitializeRequestSchema
from ...types import Response


def _get_kwargs(
    repository_id: str,
    *,
    body: None | RepositoryInitializeRequestSchema,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/v1/repositories/{repository_id}/initialize",
    }

    _kwargs["json"]: dict[str, Any] | None
    if isinstance(body, RepositoryInitializeRequestSchema):
        _kwargs["json"] = body.to_dict()
    else:
        _kwargs["json"] = body

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
    repository_id: str,
    *,
    client: AuthenticatedClient,
    body: None | RepositoryInitializeRequestSchema,
) -> Response[APIResponseModel]:
    """Initialize repository CI/CD


            Initialize repository with base CI/CD infrastructure.

            This creates the foundational workflows needed
            before any stacks can be bootstrapped into the repository.

            This is a one-time operation that:
            - Creates base workflows (iltero-base.yml, iltero-processor.yml)
            - Sets up repository secrets and variables

            Returns a PR URL that must be merged before stack bootstrapping.


    Args:
        repository_id (str):
        body (None | RepositoryInitializeRequestSchema):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        repository_id=repository_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository_id: str,
    *,
    client: AuthenticatedClient,
    body: None | RepositoryInitializeRequestSchema,
) -> APIResponseModel | None:
    """Initialize repository CI/CD


            Initialize repository with base CI/CD infrastructure.

            This creates the foundational workflows needed
            before any stacks can be bootstrapped into the repository.

            This is a one-time operation that:
            - Creates base workflows (iltero-base.yml, iltero-processor.yml)
            - Sets up repository secrets and variables

            Returns a PR URL that must be merged before stack bootstrapping.


    Args:
        repository_id (str):
        body (None | RepositoryInitializeRequestSchema):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        repository_id=repository_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    repository_id: str,
    *,
    client: AuthenticatedClient,
    body: None | RepositoryInitializeRequestSchema,
) -> Response[APIResponseModel]:
    """Initialize repository CI/CD


            Initialize repository with base CI/CD infrastructure.

            This creates the foundational workflows needed
            before any stacks can be bootstrapped into the repository.

            This is a one-time operation that:
            - Creates base workflows (iltero-base.yml, iltero-processor.yml)
            - Sets up repository secrets and variables

            Returns a PR URL that must be merged before stack bootstrapping.


    Args:
        repository_id (str):
        body (None | RepositoryInitializeRequestSchema):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        repository_id=repository_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository_id: str,
    *,
    client: AuthenticatedClient,
    body: None | RepositoryInitializeRequestSchema,
) -> APIResponseModel | None:
    """Initialize repository CI/CD


            Initialize repository with base CI/CD infrastructure.

            This creates the foundational workflows needed
            before any stacks can be bootstrapped into the repository.

            This is a one-time operation that:
            - Creates base workflows (iltero-base.yml, iltero-processor.yml)
            - Sets up repository secrets and variables

            Returns a PR URL that must be merged before stack bootstrapping.


    Args:
        repository_id (str):
        body (None | RepositoryInitializeRequestSchema):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            repository_id=repository_id,
            client=client,
            body=body,
        )
    ).parsed

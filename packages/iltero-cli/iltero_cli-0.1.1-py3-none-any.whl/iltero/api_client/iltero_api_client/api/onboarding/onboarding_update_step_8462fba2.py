from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...models.onboarding_step_update_schema import OnboardingStepUpdateSchema
from ...types import Response


def _get_kwargs(
    step_name: str,
    *,
    body: OnboardingStepUpdateSchema,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/v1/onboarding/steps/{step_name}",
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
    step_name: str,
    *,
    client: AuthenticatedClient,
    body: OnboardingStepUpdateSchema,
) -> Response[APIResponseModel]:
    """Update Step

     Update or skip a specific onboarding step.

    Allows updating step data or marking steps as skipped.

    Args:
        step_name (str):
        body (OnboardingStepUpdateSchema): Generic schema for updating onboarding step progress.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        step_name=step_name,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    step_name: str,
    *,
    client: AuthenticatedClient,
    body: OnboardingStepUpdateSchema,
) -> APIResponseModel | None:
    """Update Step

     Update or skip a specific onboarding step.

    Allows updating step data or marking steps as skipped.

    Args:
        step_name (str):
        body (OnboardingStepUpdateSchema): Generic schema for updating onboarding step progress.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        step_name=step_name,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    step_name: str,
    *,
    client: AuthenticatedClient,
    body: OnboardingStepUpdateSchema,
) -> Response[APIResponseModel]:
    """Update Step

     Update or skip a specific onboarding step.

    Allows updating step data or marking steps as skipped.

    Args:
        step_name (str):
        body (OnboardingStepUpdateSchema): Generic schema for updating onboarding step progress.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        step_name=step_name,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    step_name: str,
    *,
    client: AuthenticatedClient,
    body: OnboardingStepUpdateSchema,
) -> APIResponseModel | None:
    """Update Step

     Update or skip a specific onboarding step.

    Allows updating step data or marking steps as skipped.

    Args:
        step_name (str):
        body (OnboardingStepUpdateSchema): Generic schema for updating onboarding step progress.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            step_name=step_name,
            client=client,
            body=body,
        )
    ).parsed

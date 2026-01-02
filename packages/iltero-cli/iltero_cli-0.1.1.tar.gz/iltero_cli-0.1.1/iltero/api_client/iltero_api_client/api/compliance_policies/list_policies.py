from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_response_model import APIResponseModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    policy_set_id: None | str | Unset = UNSET,
    severity: None | str | Unset = UNSET,
    rule_id_pattern: None | str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_policy_set_id: None | str | Unset
    if isinstance(policy_set_id, Unset):
        json_policy_set_id = UNSET
    else:
        json_policy_set_id = policy_set_id
    params["policy_set_id"] = json_policy_set_id

    json_severity: None | str | Unset
    if isinstance(severity, Unset):
        json_severity = UNSET
    else:
        json_severity = severity
    params["severity"] = json_severity

    json_rule_id_pattern: None | str | Unset
    if isinstance(rule_id_pattern, Unset):
        json_rule_id_pattern = UNSET
    else:
        json_rule_id_pattern = rule_id_pattern
    params["rule_id_pattern"] = json_rule_id_pattern

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/compliance/policies/",
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
    policy_set_id: None | str | Unset = UNSET,
    severity: None | str | Unset = UNSET,
    rule_id_pattern: None | str | Unset = UNSET,
) -> Response[APIResponseModel]:
    """List compliance policies


            Retrieves individual compliance policies.

            Use filters to find policies by set, severity, or activation status.
            Each policy represents a specific compliance rule or check.


    Args:
        policy_set_id (None | str | Unset):
        severity (None | str | Unset):
        rule_id_pattern (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        policy_set_id=policy_set_id,
        severity=severity,
        rule_id_pattern=rule_id_pattern,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    policy_set_id: None | str | Unset = UNSET,
    severity: None | str | Unset = UNSET,
    rule_id_pattern: None | str | Unset = UNSET,
) -> APIResponseModel | None:
    """List compliance policies


            Retrieves individual compliance policies.

            Use filters to find policies by set, severity, or activation status.
            Each policy represents a specific compliance rule or check.


    Args:
        policy_set_id (None | str | Unset):
        severity (None | str | Unset):
        rule_id_pattern (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return sync_detailed(
        client=client,
        policy_set_id=policy_set_id,
        severity=severity,
        rule_id_pattern=rule_id_pattern,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    policy_set_id: None | str | Unset = UNSET,
    severity: None | str | Unset = UNSET,
    rule_id_pattern: None | str | Unset = UNSET,
) -> Response[APIResponseModel]:
    """List compliance policies


            Retrieves individual compliance policies.

            Use filters to find policies by set, severity, or activation status.
            Each policy represents a specific compliance rule or check.


    Args:
        policy_set_id (None | str | Unset):
        severity (None | str | Unset):
        rule_id_pattern (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIResponseModel]
    """

    kwargs = _get_kwargs(
        policy_set_id=policy_set_id,
        severity=severity,
        rule_id_pattern=rule_id_pattern,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    policy_set_id: None | str | Unset = UNSET,
    severity: None | str | Unset = UNSET,
    rule_id_pattern: None | str | Unset = UNSET,
) -> APIResponseModel | None:
    """List compliance policies


            Retrieves individual compliance policies.

            Use filters to find policies by set, severity, or activation status.
            Each policy represents a specific compliance rule or check.


    Args:
        policy_set_id (None | str | Unset):
        severity (None | str | Unset):
        rule_id_pattern (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIResponseModel
    """

    return (
        await asyncio_detailed(
            client=client,
            policy_set_id=policy_set_id,
            severity=severity,
            rule_id_pattern=rule_id_pattern,
        )
    ).parsed

from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.device_update_session_request import DeviceUpdateSessionRequest
from ...models.device_update_session_response import DeviceUpdateSessionResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: DeviceUpdateSessionRequest,
    authorization: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["Authorization"] = authorization

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/mcp-device/update-session",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DeviceUpdateSessionResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = DeviceUpdateSessionResponse.from_dict(response.json())

        return response_200

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[DeviceUpdateSessionResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: DeviceUpdateSessionRequest,
    authorization: None | str | Unset = UNSET,
) -> Response[DeviceUpdateSessionResponse | HTTPValidationError]:
    r"""Update Device Session

     Authorize and prepare a device session for CLI exchange.

    This is called by the CLI onboarding flow after the user completes:
    - Sign in / account creation
    - Organization setup
    - GitHub connection (optional)

    This endpoint:
    1. Authorizes the session (associates with user)
    2. Sets the organization ID
    3. Marks as \"ready\" for CLI exchange

    This is the ONLY authorization step needed - no separate device verification.

    Args:
        authorization (None | str | Unset):
        body (DeviceUpdateSessionRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeviceUpdateSessionResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        body=body,
        authorization=authorization,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: DeviceUpdateSessionRequest,
    authorization: None | str | Unset = UNSET,
) -> DeviceUpdateSessionResponse | HTTPValidationError | None:
    r"""Update Device Session

     Authorize and prepare a device session for CLI exchange.

    This is called by the CLI onboarding flow after the user completes:
    - Sign in / account creation
    - Organization setup
    - GitHub connection (optional)

    This endpoint:
    1. Authorizes the session (associates with user)
    2. Sets the organization ID
    3. Marks as \"ready\" for CLI exchange

    This is the ONLY authorization step needed - no separate device verification.

    Args:
        authorization (None | str | Unset):
        body (DeviceUpdateSessionRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeviceUpdateSessionResponse | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        body=body,
        authorization=authorization,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: DeviceUpdateSessionRequest,
    authorization: None | str | Unset = UNSET,
) -> Response[DeviceUpdateSessionResponse | HTTPValidationError]:
    r"""Update Device Session

     Authorize and prepare a device session for CLI exchange.

    This is called by the CLI onboarding flow after the user completes:
    - Sign in / account creation
    - Organization setup
    - GitHub connection (optional)

    This endpoint:
    1. Authorizes the session (associates with user)
    2. Sets the organization ID
    3. Marks as \"ready\" for CLI exchange

    This is the ONLY authorization step needed - no separate device verification.

    Args:
        authorization (None | str | Unset):
        body (DeviceUpdateSessionRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeviceUpdateSessionResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        body=body,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: DeviceUpdateSessionRequest,
    authorization: None | str | Unset = UNSET,
) -> DeviceUpdateSessionResponse | HTTPValidationError | None:
    r"""Update Device Session

     Authorize and prepare a device session for CLI exchange.

    This is called by the CLI onboarding flow after the user completes:
    - Sign in / account creation
    - Organization setup
    - GitHub connection (optional)

    This endpoint:
    1. Authorizes the session (associates with user)
    2. Sets the organization ID
    3. Marks as \"ready\" for CLI exchange

    This is the ONLY authorization step needed - no separate device verification.

    Args:
        authorization (None | str | Unset):
        body (DeviceUpdateSessionRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeviceUpdateSessionResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            authorization=authorization,
        )
    ).parsed

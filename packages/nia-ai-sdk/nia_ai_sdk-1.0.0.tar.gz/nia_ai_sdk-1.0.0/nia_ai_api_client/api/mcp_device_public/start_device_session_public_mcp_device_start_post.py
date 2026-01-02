from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.device_start_response import DeviceStartResponse
from ...types import Response


def _get_kwargs() -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/public/mcp-device/start",
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> DeviceStartResponse | None:
    if response.status_code == 200:
        response_200 = DeviceStartResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[DeviceStartResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[DeviceStartResponse]:
    """Start Device Session

     Initialize a new device authorization session.

    This is called by the CLI when no API key is provided. It generates:
    - A high-entropy authorization_session_id for the exchange step
    - A human-friendly user_code for the user to enter in the browser
    - A verification_url where the user should go to authorize

    The session expires after 15 minutes.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeviceStartResponse]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
) -> DeviceStartResponse | None:
    """Start Device Session

     Initialize a new device authorization session.

    This is called by the CLI when no API key is provided. It generates:
    - A high-entropy authorization_session_id for the exchange step
    - A human-friendly user_code for the user to enter in the browser
    - A verification_url where the user should go to authorize

    The session expires after 15 minutes.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeviceStartResponse
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[DeviceStartResponse]:
    """Start Device Session

     Initialize a new device authorization session.

    This is called by the CLI when no API key is provided. It generates:
    - A high-entropy authorization_session_id for the exchange step
    - A human-friendly user_code for the user to enter in the browser
    - A verification_url where the user should go to authorize

    The session expires after 15 minutes.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeviceStartResponse]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
) -> DeviceStartResponse | None:
    """Start Device Session

     Initialize a new device authorization session.

    This is called by the CLI when no API key is provided. It generates:
    - A high-entropy authorization_session_id for the exchange step
    - A human-friendly user_code for the user to enter in the browser
    - A verification_url where the user should go to authorize

    The session expires after 15 minutes.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeviceStartResponse
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed

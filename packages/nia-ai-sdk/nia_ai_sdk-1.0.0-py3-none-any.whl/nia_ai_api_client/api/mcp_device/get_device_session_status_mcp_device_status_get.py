from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.device_status_response import DeviceStatusResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    user_code: str,
    authorization: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["Authorization"] = authorization

    params: dict[str, Any] = {}

    params["user_code"] = user_code

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/mcp-device/status",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DeviceStatusResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = DeviceStatusResponse.from_dict(response.json())

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
) -> Response[DeviceStatusResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    user_code: str,
    authorization: None | str | Unset = UNSET,
) -> Response[DeviceStatusResponse | HTTPValidationError]:
    """Get Device Session Status

     Check the status of a device session.

    This is called by the browser UI to poll for when the CLI
    has completed the exchange and configured MCP.

    Only returns status if the session belongs to the authenticated user.

    Args:
        user_code (str): The user code to check status for
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeviceStatusResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        user_code=user_code,
        authorization=authorization,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    user_code: str,
    authorization: None | str | Unset = UNSET,
) -> DeviceStatusResponse | HTTPValidationError | None:
    """Get Device Session Status

     Check the status of a device session.

    This is called by the browser UI to poll for when the CLI
    has completed the exchange and configured MCP.

    Only returns status if the session belongs to the authenticated user.

    Args:
        user_code (str): The user code to check status for
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeviceStatusResponse | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        user_code=user_code,
        authorization=authorization,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    user_code: str,
    authorization: None | str | Unset = UNSET,
) -> Response[DeviceStatusResponse | HTTPValidationError]:
    """Get Device Session Status

     Check the status of a device session.

    This is called by the browser UI to poll for when the CLI
    has completed the exchange and configured MCP.

    Only returns status if the session belongs to the authenticated user.

    Args:
        user_code (str): The user code to check status for
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeviceStatusResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        user_code=user_code,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    user_code: str,
    authorization: None | str | Unset = UNSET,
) -> DeviceStatusResponse | HTTPValidationError | None:
    """Get Device Session Status

     Check the status of a device session.

    This is called by the browser UI to poll for when the CLI
    has completed the exchange and configured MCP.

    Only returns status if the session belongs to the authenticated user.

    Args:
        user_code (str): The user code to check status for
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeviceStatusResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            user_code=user_code,
            authorization=authorization,
        )
    ).parsed

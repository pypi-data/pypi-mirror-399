from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_usage_details_response import ApiUsageDetailsResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    user_id: str,
    authorization: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["Authorization"] = authorization

    params: dict[str, Any] = {}

    params["user_id"] = user_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/billing/api-usage-details",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ApiUsageDetailsResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = ApiUsageDetailsResponse.from_dict(response.json())

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
) -> Response[ApiUsageDetailsResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    user_id: str,
    authorization: None | str | Unset = UNSET,
) -> Response[ApiUsageDetailsResponse | HTTPValidationError]:
    """Get Api Usage Details

     Get basic API usage details for Pro users.
    Since Pro users have unlimited API access, this endpoint provides simplified information.

    Args:
        user_id: The ID of the user to get API usage details for
        authenticated_user_id: Authenticated user ID from token

    Returns:
        ApiUsageDetailsResponse: Basic API usage information

    Args:
        user_id (str):
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ApiUsageDetailsResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        authorization=authorization,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    user_id: str,
    authorization: None | str | Unset = UNSET,
) -> ApiUsageDetailsResponse | HTTPValidationError | None:
    """Get Api Usage Details

     Get basic API usage details for Pro users.
    Since Pro users have unlimited API access, this endpoint provides simplified information.

    Args:
        user_id: The ID of the user to get API usage details for
        authenticated_user_id: Authenticated user ID from token

    Returns:
        ApiUsageDetailsResponse: Basic API usage information

    Args:
        user_id (str):
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ApiUsageDetailsResponse | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        user_id=user_id,
        authorization=authorization,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    user_id: str,
    authorization: None | str | Unset = UNSET,
) -> Response[ApiUsageDetailsResponse | HTTPValidationError]:
    """Get Api Usage Details

     Get basic API usage details for Pro users.
    Since Pro users have unlimited API access, this endpoint provides simplified information.

    Args:
        user_id: The ID of the user to get API usage details for
        authenticated_user_id: Authenticated user ID from token

    Returns:
        ApiUsageDetailsResponse: Basic API usage information

    Args:
        user_id (str):
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ApiUsageDetailsResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    user_id: str,
    authorization: None | str | Unset = UNSET,
) -> ApiUsageDetailsResponse | HTTPValidationError | None:
    """Get Api Usage Details

     Get basic API usage details for Pro users.
    Since Pro users have unlimited API access, this endpoint provides simplified information.

    Args:
        user_id: The ID of the user to get API usage details for
        authenticated_user_id: Authenticated user ID from token

    Returns:
        ApiUsageDetailsResponse: Basic API usage information

    Args:
        user_id (str):
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ApiUsageDetailsResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            user_id=user_id,
            authorization=authorization,
        )
    ).parsed

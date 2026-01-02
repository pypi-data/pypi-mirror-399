from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_activity_summary_api_analytics_activity_summary_get_response_get_activity_summary_api_analytics_activity_summary_get import (
    GetActivitySummaryApiAnalyticsActivitySummaryGetResponseGetActivitySummaryApiAnalyticsActivitySummaryGet,
)
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    user_id: str,
    days: int | Unset = 30,
    authorization: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["Authorization"] = authorization

    params: dict[str, Any] = {}

    params["user_id"] = user_id

    params["days"] = days

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/analytics/activity-summary",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    GetActivitySummaryApiAnalyticsActivitySummaryGetResponseGetActivitySummaryApiAnalyticsActivitySummaryGet
    | HTTPValidationError
    | None
):
    if response.status_code == 200:
        response_200 = GetActivitySummaryApiAnalyticsActivitySummaryGetResponseGetActivitySummaryApiAnalyticsActivitySummaryGet.from_dict(
            response.json()
        )

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
) -> Response[
    GetActivitySummaryApiAnalyticsActivitySummaryGetResponseGetActivitySummaryApiAnalyticsActivitySummaryGet
    | HTTPValidationError
]:
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
    days: int | Unset = 30,
    authorization: None | str | Unset = UNSET,
) -> Response[
    GetActivitySummaryApiAnalyticsActivitySummaryGetResponseGetActivitySummaryApiAnalyticsActivitySummaryGet
    | HTTPValidationError
]:
    """Get Activity Summary

     Get a summary of user's API activity over a time period.

    Returns:
        Summary statistics including:
        - Total API calls
        - Breakdown by query type
        - Most queried repositories
        - Most queried data sources
        - Activity trends

    Args:
        user_id (str): User ID to fetch summary for
        days (int | Unset): Number of days to look back Default: 30.
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetActivitySummaryApiAnalyticsActivitySummaryGetResponseGetActivitySummaryApiAnalyticsActivitySummaryGet | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        days=days,
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
    days: int | Unset = 30,
    authorization: None | str | Unset = UNSET,
) -> (
    GetActivitySummaryApiAnalyticsActivitySummaryGetResponseGetActivitySummaryApiAnalyticsActivitySummaryGet
    | HTTPValidationError
    | None
):
    """Get Activity Summary

     Get a summary of user's API activity over a time period.

    Returns:
        Summary statistics including:
        - Total API calls
        - Breakdown by query type
        - Most queried repositories
        - Most queried data sources
        - Activity trends

    Args:
        user_id (str): User ID to fetch summary for
        days (int | Unset): Number of days to look back Default: 30.
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetActivitySummaryApiAnalyticsActivitySummaryGetResponseGetActivitySummaryApiAnalyticsActivitySummaryGet | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        user_id=user_id,
        days=days,
        authorization=authorization,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    user_id: str,
    days: int | Unset = 30,
    authorization: None | str | Unset = UNSET,
) -> Response[
    GetActivitySummaryApiAnalyticsActivitySummaryGetResponseGetActivitySummaryApiAnalyticsActivitySummaryGet
    | HTTPValidationError
]:
    """Get Activity Summary

     Get a summary of user's API activity over a time period.

    Returns:
        Summary statistics including:
        - Total API calls
        - Breakdown by query type
        - Most queried repositories
        - Most queried data sources
        - Activity trends

    Args:
        user_id (str): User ID to fetch summary for
        days (int | Unset): Number of days to look back Default: 30.
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetActivitySummaryApiAnalyticsActivitySummaryGetResponseGetActivitySummaryApiAnalyticsActivitySummaryGet | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        days=days,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    user_id: str,
    days: int | Unset = 30,
    authorization: None | str | Unset = UNSET,
) -> (
    GetActivitySummaryApiAnalyticsActivitySummaryGetResponseGetActivitySummaryApiAnalyticsActivitySummaryGet
    | HTTPValidationError
    | None
):
    """Get Activity Summary

     Get a summary of user's API activity over a time period.

    Returns:
        Summary statistics including:
        - Total API calls
        - Breakdown by query type
        - Most queried repositories
        - Most queried data sources
        - Activity trends

    Args:
        user_id (str): User ID to fetch summary for
        days (int | Unset): Number of days to look back Default: 30.
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetActivitySummaryApiAnalyticsActivitySummaryGetResponseGetActivitySummaryApiAnalyticsActivitySummaryGet | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            user_id=user_id,
            days=days,
            authorization=authorization,
        )
    ).parsed

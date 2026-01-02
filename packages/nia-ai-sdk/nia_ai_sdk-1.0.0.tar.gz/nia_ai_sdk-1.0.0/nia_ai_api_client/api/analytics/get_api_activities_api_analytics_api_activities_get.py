from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_api_activities_api_analytics_api_activities_get_response_get_api_activities_api_analytics_api_activities_get import (
    GetApiActivitiesApiAnalyticsApiActivitiesGetResponseGetApiActivitiesApiAnalyticsApiActivitiesGet,
)
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    user_id: str,
    query_type: None | str | Unset = UNSET,
    days: int | Unset = 7,
    limit: int | Unset = 100,
    cursor: None | str | Unset = UNSET,
    cursor_id: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["Authorization"] = authorization

    params: dict[str, Any] = {}

    params["user_id"] = user_id

    json_query_type: None | str | Unset
    if isinstance(query_type, Unset):
        json_query_type = UNSET
    else:
        json_query_type = query_type
    params["query_type"] = json_query_type

    params["days"] = days

    params["limit"] = limit

    json_cursor: None | str | Unset
    if isinstance(cursor, Unset):
        json_cursor = UNSET
    else:
        json_cursor = cursor
    params["cursor"] = json_cursor

    json_cursor_id: None | str | Unset
    if isinstance(cursor_id, Unset):
        json_cursor_id = UNSET
    else:
        json_cursor_id = cursor_id
    params["cursor_id"] = json_cursor_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/analytics/api-activities",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    GetApiActivitiesApiAnalyticsApiActivitiesGetResponseGetApiActivitiesApiAnalyticsApiActivitiesGet
    | HTTPValidationError
    | None
):
    if response.status_code == 200:
        response_200 = (
            GetApiActivitiesApiAnalyticsApiActivitiesGetResponseGetApiActivitiesApiAnalyticsApiActivitiesGet.from_dict(
                response.json()
            )
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
    GetApiActivitiesApiAnalyticsApiActivitiesGetResponseGetApiActivitiesApiAnalyticsApiActivitiesGet
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
    query_type: None | str | Unset = UNSET,
    days: int | Unset = 7,
    limit: int | Unset = 100,
    cursor: None | str | Unset = UNSET,
    cursor_id: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
) -> Response[
    GetApiActivitiesApiAnalyticsApiActivitiesGetResponseGetApiActivitiesApiAnalyticsApiActivitiesGet
    | HTTPValidationError
]:
    """Get Api Activities

     Fetch API activities for a user with optional filtering.

    Returns:
        Dictionary containing:
        - activities: List of API activity records
        - summary: Summary statistics

    Args:
        user_id (str): User ID to fetch activities for
        query_type (None | str | Unset): Filter by query type (unified, repositories, sources,
            web_search, deep_research)
        days (int | Unset): Number of days to look back Default: 7.
        limit (int | Unset): Maximum number of activities to return Default: 100.
        cursor (None | str | Unset): Pagination cursor timestamp (ISO8601)
        cursor_id (None | str | Unset): Pagination cursor tie-breaker id
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetApiActivitiesApiAnalyticsApiActivitiesGetResponseGetApiActivitiesApiAnalyticsApiActivitiesGet | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        query_type=query_type,
        days=days,
        limit=limit,
        cursor=cursor,
        cursor_id=cursor_id,
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
    query_type: None | str | Unset = UNSET,
    days: int | Unset = 7,
    limit: int | Unset = 100,
    cursor: None | str | Unset = UNSET,
    cursor_id: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
) -> (
    GetApiActivitiesApiAnalyticsApiActivitiesGetResponseGetApiActivitiesApiAnalyticsApiActivitiesGet
    | HTTPValidationError
    | None
):
    """Get Api Activities

     Fetch API activities for a user with optional filtering.

    Returns:
        Dictionary containing:
        - activities: List of API activity records
        - summary: Summary statistics

    Args:
        user_id (str): User ID to fetch activities for
        query_type (None | str | Unset): Filter by query type (unified, repositories, sources,
            web_search, deep_research)
        days (int | Unset): Number of days to look back Default: 7.
        limit (int | Unset): Maximum number of activities to return Default: 100.
        cursor (None | str | Unset): Pagination cursor timestamp (ISO8601)
        cursor_id (None | str | Unset): Pagination cursor tie-breaker id
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetApiActivitiesApiAnalyticsApiActivitiesGetResponseGetApiActivitiesApiAnalyticsApiActivitiesGet | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        user_id=user_id,
        query_type=query_type,
        days=days,
        limit=limit,
        cursor=cursor,
        cursor_id=cursor_id,
        authorization=authorization,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    user_id: str,
    query_type: None | str | Unset = UNSET,
    days: int | Unset = 7,
    limit: int | Unset = 100,
    cursor: None | str | Unset = UNSET,
    cursor_id: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
) -> Response[
    GetApiActivitiesApiAnalyticsApiActivitiesGetResponseGetApiActivitiesApiAnalyticsApiActivitiesGet
    | HTTPValidationError
]:
    """Get Api Activities

     Fetch API activities for a user with optional filtering.

    Returns:
        Dictionary containing:
        - activities: List of API activity records
        - summary: Summary statistics

    Args:
        user_id (str): User ID to fetch activities for
        query_type (None | str | Unset): Filter by query type (unified, repositories, sources,
            web_search, deep_research)
        days (int | Unset): Number of days to look back Default: 7.
        limit (int | Unset): Maximum number of activities to return Default: 100.
        cursor (None | str | Unset): Pagination cursor timestamp (ISO8601)
        cursor_id (None | str | Unset): Pagination cursor tie-breaker id
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetApiActivitiesApiAnalyticsApiActivitiesGetResponseGetApiActivitiesApiAnalyticsApiActivitiesGet | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        query_type=query_type,
        days=days,
        limit=limit,
        cursor=cursor,
        cursor_id=cursor_id,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    user_id: str,
    query_type: None | str | Unset = UNSET,
    days: int | Unset = 7,
    limit: int | Unset = 100,
    cursor: None | str | Unset = UNSET,
    cursor_id: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
) -> (
    GetApiActivitiesApiAnalyticsApiActivitiesGetResponseGetApiActivitiesApiAnalyticsApiActivitiesGet
    | HTTPValidationError
    | None
):
    """Get Api Activities

     Fetch API activities for a user with optional filtering.

    Returns:
        Dictionary containing:
        - activities: List of API activity records
        - summary: Summary statistics

    Args:
        user_id (str): User ID to fetch activities for
        query_type (None | str | Unset): Filter by query type (unified, repositories, sources,
            web_search, deep_research)
        days (int | Unset): Number of days to look back Default: 7.
        limit (int | Unset): Maximum number of activities to return Default: 100.
        cursor (None | str | Unset): Pagination cursor timestamp (ISO8601)
        cursor_id (None | str | Unset): Pagination cursor tie-breaker id
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetApiActivitiesApiAnalyticsApiActivitiesGetResponseGetApiActivitiesApiAnalyticsApiActivitiesGet | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            user_id=user_id,
            query_type=query_type,
            days=days,
            limit=limit,
            cursor=cursor,
            cursor_id=cursor_id,
            authorization=authorization,
        )
    ).parsed

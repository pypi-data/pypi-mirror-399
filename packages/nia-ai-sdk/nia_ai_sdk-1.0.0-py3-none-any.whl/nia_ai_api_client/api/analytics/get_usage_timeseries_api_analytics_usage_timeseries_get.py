from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_usage_timeseries_api_analytics_usage_timeseries_get_response_get_usage_timeseries_api_analytics_usage_timeseries_get import (
    GetUsageTimeseriesApiAnalyticsUsageTimeseriesGetResponseGetUsageTimeseriesApiAnalyticsUsageTimeseriesGet,
)
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    user_id: str,
    organization_id: None | str | Unset = UNSET,
    days: int | Unset = 7,
    authorization: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["Authorization"] = authorization

    params: dict[str, Any] = {}

    params["user_id"] = user_id

    json_organization_id: None | str | Unset
    if isinstance(organization_id, Unset):
        json_organization_id = UNSET
    else:
        json_organization_id = organization_id
    params["organization_id"] = json_organization_id

    params["days"] = days

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/analytics/usage-timeseries",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    GetUsageTimeseriesApiAnalyticsUsageTimeseriesGetResponseGetUsageTimeseriesApiAnalyticsUsageTimeseriesGet
    | HTTPValidationError
    | None
):
    if response.status_code == 200:
        response_200 = GetUsageTimeseriesApiAnalyticsUsageTimeseriesGetResponseGetUsageTimeseriesApiAnalyticsUsageTimeseriesGet.from_dict(
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
    GetUsageTimeseriesApiAnalyticsUsageTimeseriesGetResponseGetUsageTimeseriesApiAnalyticsUsageTimeseriesGet
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
    organization_id: None | str | Unset = UNSET,
    days: int | Unset = 7,
    authorization: None | str | Unset = UNSET,
) -> Response[
    GetUsageTimeseriesApiAnalyticsUsageTimeseriesGetResponseGetUsageTimeseriesApiAnalyticsUsageTimeseriesGet
    | HTTPValidationError
]:
    """Get Usage Timeseries

     Return daily usage totals for the last N days, derived from `api_activities`.

    This is designed for charts: it returns a dense daily series (missing days
    are returned with total=0) and also includes the current-period usage limits
    from `usage_tracking`.

    Args:
        user_id (str): User ID to fetch usage for
        organization_id (None | str | Unset): Optional organization context for usage limits
        days (int | Unset): Number of days to include Default: 7.
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetUsageTimeseriesApiAnalyticsUsageTimeseriesGetResponseGetUsageTimeseriesApiAnalyticsUsageTimeseriesGet | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        organization_id=organization_id,
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
    organization_id: None | str | Unset = UNSET,
    days: int | Unset = 7,
    authorization: None | str | Unset = UNSET,
) -> (
    GetUsageTimeseriesApiAnalyticsUsageTimeseriesGetResponseGetUsageTimeseriesApiAnalyticsUsageTimeseriesGet
    | HTTPValidationError
    | None
):
    """Get Usage Timeseries

     Return daily usage totals for the last N days, derived from `api_activities`.

    This is designed for charts: it returns a dense daily series (missing days
    are returned with total=0) and also includes the current-period usage limits
    from `usage_tracking`.

    Args:
        user_id (str): User ID to fetch usage for
        organization_id (None | str | Unset): Optional organization context for usage limits
        days (int | Unset): Number of days to include Default: 7.
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetUsageTimeseriesApiAnalyticsUsageTimeseriesGetResponseGetUsageTimeseriesApiAnalyticsUsageTimeseriesGet | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        user_id=user_id,
        organization_id=organization_id,
        days=days,
        authorization=authorization,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    user_id: str,
    organization_id: None | str | Unset = UNSET,
    days: int | Unset = 7,
    authorization: None | str | Unset = UNSET,
) -> Response[
    GetUsageTimeseriesApiAnalyticsUsageTimeseriesGetResponseGetUsageTimeseriesApiAnalyticsUsageTimeseriesGet
    | HTTPValidationError
]:
    """Get Usage Timeseries

     Return daily usage totals for the last N days, derived from `api_activities`.

    This is designed for charts: it returns a dense daily series (missing days
    are returned with total=0) and also includes the current-period usage limits
    from `usage_tracking`.

    Args:
        user_id (str): User ID to fetch usage for
        organization_id (None | str | Unset): Optional organization context for usage limits
        days (int | Unset): Number of days to include Default: 7.
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetUsageTimeseriesApiAnalyticsUsageTimeseriesGetResponseGetUsageTimeseriesApiAnalyticsUsageTimeseriesGet | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        organization_id=organization_id,
        days=days,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    user_id: str,
    organization_id: None | str | Unset = UNSET,
    days: int | Unset = 7,
    authorization: None | str | Unset = UNSET,
) -> (
    GetUsageTimeseriesApiAnalyticsUsageTimeseriesGetResponseGetUsageTimeseriesApiAnalyticsUsageTimeseriesGet
    | HTTPValidationError
    | None
):
    """Get Usage Timeseries

     Return daily usage totals for the last N days, derived from `api_activities`.

    This is designed for charts: it returns a dense daily series (missing days
    are returned with total=0) and also includes the current-period usage limits
    from `usage_tracking`.

    Args:
        user_id (str): User ID to fetch usage for
        organization_id (None | str | Unset): Optional organization context for usage limits
        days (int | Unset): Number of days to include Default: 7.
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetUsageTimeseriesApiAnalyticsUsageTimeseriesGetResponseGetUsageTimeseriesApiAnalyticsUsageTimeseriesGet | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            user_id=user_id,
            organization_id=organization_id,
            days=days,
            authorization=authorization,
        )
    ).parsed

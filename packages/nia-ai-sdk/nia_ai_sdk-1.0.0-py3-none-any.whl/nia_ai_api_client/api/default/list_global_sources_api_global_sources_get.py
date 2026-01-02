from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.global_source_list_response import GlobalSourceListResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    search: str | Unset = "",
    source_type: str | Unset = "",
    status: str | Unset = "indexed",
    sort: str | Unset = "recently_indexed",
    order: str | Unset = "desc",
    updated_within_days: int | None | Unset = UNSET,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["search"] = search

    params["source_type"] = source_type

    params["status"] = status

    params["sort"] = sort

    params["order"] = order

    json_updated_within_days: int | None | Unset
    if isinstance(updated_within_days, Unset):
        json_updated_within_days = UNSET
    else:
        json_updated_within_days = updated_within_days
    params["updated_within_days"] = json_updated_within_days

    params["limit"] = limit

    params["offset"] = offset

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/global-sources",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GlobalSourceListResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = GlobalSourceListResponse.from_dict(response.json())

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
) -> Response[GlobalSourceListResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    search: str | Unset = "",
    source_type: str | Unset = "",
    status: str | Unset = "indexed",
    sort: str | Unset = "recently_indexed",
    order: str | Unset = "desc",
    updated_within_days: int | None | Unset = UNSET,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
) -> Response[GlobalSourceListResponse | HTTPValidationError]:
    """List Global Sources

     List all globally indexed public sources.

    This endpoint allows users to discover what repositories and documentation
    are already indexed and available for instant access.

    Args:
        search (str | Unset): Search by URL or name Default: ''.
        source_type (str | Unset): Filter by type: repository | documentation | research_paper
            Default: ''.
        status (str | Unset): Filter by status Default: 'indexed'.
        sort (str | Unset): Sort order: recently_indexed | recently_updated | most_tokens |
            most_snippets | most_subscribed Default: 'recently_indexed'.
        order (str | Unset): Sort direction: asc | desc Default: 'desc'.
        updated_within_days (int | None | Unset): Only include sources updated/indexed within N
            days
        limit (int | Unset): Number of results Default: 50.
        offset (int | Unset): Pagination offset Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GlobalSourceListResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        search=search,
        source_type=source_type,
        status=status,
        sort=sort,
        order=order,
        updated_within_days=updated_within_days,
        limit=limit,
        offset=offset,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    search: str | Unset = "",
    source_type: str | Unset = "",
    status: str | Unset = "indexed",
    sort: str | Unset = "recently_indexed",
    order: str | Unset = "desc",
    updated_within_days: int | None | Unset = UNSET,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
) -> GlobalSourceListResponse | HTTPValidationError | None:
    """List Global Sources

     List all globally indexed public sources.

    This endpoint allows users to discover what repositories and documentation
    are already indexed and available for instant access.

    Args:
        search (str | Unset): Search by URL or name Default: ''.
        source_type (str | Unset): Filter by type: repository | documentation | research_paper
            Default: ''.
        status (str | Unset): Filter by status Default: 'indexed'.
        sort (str | Unset): Sort order: recently_indexed | recently_updated | most_tokens |
            most_snippets | most_subscribed Default: 'recently_indexed'.
        order (str | Unset): Sort direction: asc | desc Default: 'desc'.
        updated_within_days (int | None | Unset): Only include sources updated/indexed within N
            days
        limit (int | Unset): Number of results Default: 50.
        offset (int | Unset): Pagination offset Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GlobalSourceListResponse | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        search=search,
        source_type=source_type,
        status=status,
        sort=sort,
        order=order,
        updated_within_days=updated_within_days,
        limit=limit,
        offset=offset,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    search: str | Unset = "",
    source_type: str | Unset = "",
    status: str | Unset = "indexed",
    sort: str | Unset = "recently_indexed",
    order: str | Unset = "desc",
    updated_within_days: int | None | Unset = UNSET,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
) -> Response[GlobalSourceListResponse | HTTPValidationError]:
    """List Global Sources

     List all globally indexed public sources.

    This endpoint allows users to discover what repositories and documentation
    are already indexed and available for instant access.

    Args:
        search (str | Unset): Search by URL or name Default: ''.
        source_type (str | Unset): Filter by type: repository | documentation | research_paper
            Default: ''.
        status (str | Unset): Filter by status Default: 'indexed'.
        sort (str | Unset): Sort order: recently_indexed | recently_updated | most_tokens |
            most_snippets | most_subscribed Default: 'recently_indexed'.
        order (str | Unset): Sort direction: asc | desc Default: 'desc'.
        updated_within_days (int | None | Unset): Only include sources updated/indexed within N
            days
        limit (int | Unset): Number of results Default: 50.
        offset (int | Unset): Pagination offset Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GlobalSourceListResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        search=search,
        source_type=source_type,
        status=status,
        sort=sort,
        order=order,
        updated_within_days=updated_within_days,
        limit=limit,
        offset=offset,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    search: str | Unset = "",
    source_type: str | Unset = "",
    status: str | Unset = "indexed",
    sort: str | Unset = "recently_indexed",
    order: str | Unset = "desc",
    updated_within_days: int | None | Unset = UNSET,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
) -> GlobalSourceListResponse | HTTPValidationError | None:
    """List Global Sources

     List all globally indexed public sources.

    This endpoint allows users to discover what repositories and documentation
    are already indexed and available for instant access.

    Args:
        search (str | Unset): Search by URL or name Default: ''.
        source_type (str | Unset): Filter by type: repository | documentation | research_paper
            Default: ''.
        status (str | Unset): Filter by status Default: 'indexed'.
        sort (str | Unset): Sort order: recently_indexed | recently_updated | most_tokens |
            most_snippets | most_subscribed Default: 'recently_indexed'.
        order (str | Unset): Sort direction: asc | desc Default: 'desc'.
        updated_within_days (int | None | Unset): Only include sources updated/indexed within N
            days
        limit (int | Unset): Number of results Default: 50.
        offset (int | Unset): Pagination offset Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GlobalSourceListResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            search=search,
            source_type=source_type,
            status=status,
            sort=sort,
            order=order,
            updated_within_days=updated_within_days,
            limit=limit,
            offset=offset,
        )
    ).parsed

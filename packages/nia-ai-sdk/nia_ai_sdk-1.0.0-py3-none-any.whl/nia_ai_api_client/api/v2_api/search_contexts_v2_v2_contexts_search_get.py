from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.context_search_response import ContextSearchResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    q: str,
    limit: int | Unset = 20,
    tags: None | str | Unset = UNSET,
    agent_source: None | str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["q"] = q

    params["limit"] = limit

    json_tags: None | str | Unset
    if isinstance(tags, Unset):
        json_tags = UNSET
    else:
        json_tags = tags
    params["tags"] = json_tags

    json_agent_source: None | str | Unset
    if isinstance(agent_source, Unset):
        json_agent_source = UNSET
    else:
        json_agent_source = agent_source
    params["agent_source"] = json_agent_source

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/contexts/search",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ContextSearchResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = ContextSearchResponse.from_dict(response.json())

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
) -> Response[ContextSearchResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    q: str,
    limit: int | Unset = 20,
    tags: None | str | Unset = UNSET,
    agent_source: None | str | Unset = UNSET,
) -> Response[ContextSearchResponse | HTTPValidationError]:
    """Text search contexts

     Search contexts by content, title, summary, or tags using MongoDB text search.

    Args:
        q (str): Search query
        limit (int | Unset): Number of contexts to return Default: 20.
        tags (None | str | Unset): Comma-separated tags to filter by
        agent_source (None | str | Unset): Filter by agent source

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ContextSearchResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        q=q,
        limit=limit,
        tags=tags,
        agent_source=agent_source,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    q: str,
    limit: int | Unset = 20,
    tags: None | str | Unset = UNSET,
    agent_source: None | str | Unset = UNSET,
) -> ContextSearchResponse | HTTPValidationError | None:
    """Text search contexts

     Search contexts by content, title, summary, or tags using MongoDB text search.

    Args:
        q (str): Search query
        limit (int | Unset): Number of contexts to return Default: 20.
        tags (None | str | Unset): Comma-separated tags to filter by
        agent_source (None | str | Unset): Filter by agent source

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ContextSearchResponse | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        q=q,
        limit=limit,
        tags=tags,
        agent_source=agent_source,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    q: str,
    limit: int | Unset = 20,
    tags: None | str | Unset = UNSET,
    agent_source: None | str | Unset = UNSET,
) -> Response[ContextSearchResponse | HTTPValidationError]:
    """Text search contexts

     Search contexts by content, title, summary, or tags using MongoDB text search.

    Args:
        q (str): Search query
        limit (int | Unset): Number of contexts to return Default: 20.
        tags (None | str | Unset): Comma-separated tags to filter by
        agent_source (None | str | Unset): Filter by agent source

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ContextSearchResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        q=q,
        limit=limit,
        tags=tags,
        agent_source=agent_source,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    q: str,
    limit: int | Unset = 20,
    tags: None | str | Unset = UNSET,
    agent_source: None | str | Unset = UNSET,
) -> ContextSearchResponse | HTTPValidationError | None:
    """Text search contexts

     Search contexts by content, title, summary, or tags using MongoDB text search.

    Args:
        q (str): Search query
        limit (int | Unset): Number of contexts to return Default: 20.
        tags (None | str | Unset): Comma-separated tags to filter by
        agent_source (None | str | Unset): Filter by agent source

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ContextSearchResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            q=q,
            limit=limit,
            tags=tags,
            agent_source=agent_source,
        )
    ).parsed

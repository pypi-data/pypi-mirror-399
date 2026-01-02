from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    user_id: str,
    q: str,
    limit: int | Unset = 20,
    organization_id: None | str | Unset = UNSET,
    cwd: None | str | Unset = UNSET,
    include_highlights: bool | Unset = True,
    workspace_filter: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["Authorization"] = authorization

    params: dict[str, Any] = {}

    params["user_id"] = user_id

    params["q"] = q

    params["limit"] = limit

    json_organization_id: None | str | Unset
    if isinstance(organization_id, Unset):
        json_organization_id = UNSET
    else:
        json_organization_id = organization_id
    params["organization_id"] = json_organization_id

    json_cwd: None | str | Unset
    if isinstance(cwd, Unset):
        json_cwd = UNSET
    else:
        json_cwd = cwd
    params["cwd"] = json_cwd

    params["include_highlights"] = include_highlights

    json_workspace_filter: None | str | Unset
    if isinstance(workspace_filter, Unset):
        json_workspace_filter = UNSET
    else:
        json_workspace_filter = workspace_filter
    params["workspace_filter"] = json_workspace_filter

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/contexts/semantic-search",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = response.json()
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
) -> Response[Any | HTTPValidationError]:
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
    q: str,
    limit: int | Unset = 20,
    organization_id: None | str | Unset = UNSET,
    cwd: None | str | Unset = UNSET,
    include_highlights: bool | Unset = True,
    workspace_filter: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Semantic Search Contexts

     Semantic search with rich, structured output using Turbopuffer hybrid search.

    Args:
        user_id (str): User ID
        q (str): Search query
        limit (int | Unset): Number of contexts to return Default: 20.
        organization_id (None | str | Unset): Organization ID context filter
        cwd (None | str | Unset): Current working directory for workspace awareness
        include_highlights (bool | Unset): Include match highlights Default: True.
        workspace_filter (None | str | Unset): Filter by specific workspace name
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        q=q,
        limit=limit,
        organization_id=organization_id,
        cwd=cwd,
        include_highlights=include_highlights,
        workspace_filter=workspace_filter,
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
    q: str,
    limit: int | Unset = 20,
    organization_id: None | str | Unset = UNSET,
    cwd: None | str | Unset = UNSET,
    include_highlights: bool | Unset = True,
    workspace_filter: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Semantic Search Contexts

     Semantic search with rich, structured output using Turbopuffer hybrid search.

    Args:
        user_id (str): User ID
        q (str): Search query
        limit (int | Unset): Number of contexts to return Default: 20.
        organization_id (None | str | Unset): Organization ID context filter
        cwd (None | str | Unset): Current working directory for workspace awareness
        include_highlights (bool | Unset): Include match highlights Default: True.
        workspace_filter (None | str | Unset): Filter by specific workspace name
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        user_id=user_id,
        q=q,
        limit=limit,
        organization_id=organization_id,
        cwd=cwd,
        include_highlights=include_highlights,
        workspace_filter=workspace_filter,
        authorization=authorization,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    user_id: str,
    q: str,
    limit: int | Unset = 20,
    organization_id: None | str | Unset = UNSET,
    cwd: None | str | Unset = UNSET,
    include_highlights: bool | Unset = True,
    workspace_filter: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Semantic Search Contexts

     Semantic search with rich, structured output using Turbopuffer hybrid search.

    Args:
        user_id (str): User ID
        q (str): Search query
        limit (int | Unset): Number of contexts to return Default: 20.
        organization_id (None | str | Unset): Organization ID context filter
        cwd (None | str | Unset): Current working directory for workspace awareness
        include_highlights (bool | Unset): Include match highlights Default: True.
        workspace_filter (None | str | Unset): Filter by specific workspace name
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        q=q,
        limit=limit,
        organization_id=organization_id,
        cwd=cwd,
        include_highlights=include_highlights,
        workspace_filter=workspace_filter,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    user_id: str,
    q: str,
    limit: int | Unset = 20,
    organization_id: None | str | Unset = UNSET,
    cwd: None | str | Unset = UNSET,
    include_highlights: bool | Unset = True,
    workspace_filter: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Semantic Search Contexts

     Semantic search with rich, structured output using Turbopuffer hybrid search.

    Args:
        user_id (str): User ID
        q (str): Search query
        limit (int | Unset): Number of contexts to return Default: 20.
        organization_id (None | str | Unset): Organization ID context filter
        cwd (None | str | Unset): Current working directory for workspace awareness
        include_highlights (bool | Unset): Include match highlights Default: True.
        workspace_filter (None | str | Unset): Filter by specific workspace name
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            user_id=user_id,
            q=q,
            limit=limit,
            organization_id=organization_id,
            cwd=cwd,
            include_highlights=include_highlights,
            workspace_filter=workspace_filter,
            authorization=authorization,
        )
    ).parsed

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
    limit: int | Unset = 20,
    offset: int | Unset = 0,
    tags: None | str | Unset = UNSET,
    agent_source: None | str | Unset = UNSET,
    organization_id: None | str | Unset = UNSET,
    scope: None | str | Unset = UNSET,
    workspace: None | str | Unset = UNSET,
    directory: None | str | Unset = UNSET,
    file_overlap: None | str | Unset = UNSET,
    cwd: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["Authorization"] = authorization

    params: dict[str, Any] = {}

    params["user_id"] = user_id

    params["limit"] = limit

    params["offset"] = offset

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

    json_organization_id: None | str | Unset
    if isinstance(organization_id, Unset):
        json_organization_id = UNSET
    else:
        json_organization_id = organization_id
    params["organization_id"] = json_organization_id

    json_scope: None | str | Unset
    if isinstance(scope, Unset):
        json_scope = UNSET
    else:
        json_scope = scope
    params["scope"] = json_scope

    json_workspace: None | str | Unset
    if isinstance(workspace, Unset):
        json_workspace = UNSET
    else:
        json_workspace = workspace
    params["workspace"] = json_workspace

    json_directory: None | str | Unset
    if isinstance(directory, Unset):
        json_directory = UNSET
    else:
        json_directory = directory
    params["directory"] = json_directory

    json_file_overlap: None | str | Unset
    if isinstance(file_overlap, Unset):
        json_file_overlap = UNSET
    else:
        json_file_overlap = file_overlap
    params["file_overlap"] = json_file_overlap

    json_cwd: None | str | Unset
    if isinstance(cwd, Unset):
        json_cwd = UNSET
    else:
        json_cwd = cwd
    params["cwd"] = json_cwd

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/contexts",
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
    limit: int | Unset = 20,
    offset: int | Unset = 0,
    tags: None | str | Unset = UNSET,
    agent_source: None | str | Unset = UNSET,
    organization_id: None | str | Unset = UNSET,
    scope: None | str | Unset = UNSET,
    workspace: None | str | Unset = UNSET,
    directory: None | str | Unset = UNSET,
    file_overlap: None | str | Unset = UNSET,
    cwd: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """List Contexts

     List user's conversation contexts with pagination, filtering, and relevance scoring.

    Args:
        user_id (str): User ID
        limit (int | Unset): Number of contexts to return Default: 20.
        offset (int | Unset): Number of contexts to skip Default: 0.
        tags (None | str | Unset): Comma-separated tags to filter by
        agent_source (None | str | Unset): Filter by agent source
        organization_id (None | str | Unset): Organization ID context filter
        scope (None | str | Unset): Scope: 'auto', 'all', 'workspace', 'directory'
        workspace (None | str | Unset): Filter by workspace/project name
        directory (None | str | Unset): Filter by directory path
        file_overlap (None | str | Unset): Comma-separated file paths to find overlaps
        cwd (None | str | Unset): Current working directory for 'auto' scope
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        limit=limit,
        offset=offset,
        tags=tags,
        agent_source=agent_source,
        organization_id=organization_id,
        scope=scope,
        workspace=workspace,
        directory=directory,
        file_overlap=file_overlap,
        cwd=cwd,
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
    limit: int | Unset = 20,
    offset: int | Unset = 0,
    tags: None | str | Unset = UNSET,
    agent_source: None | str | Unset = UNSET,
    organization_id: None | str | Unset = UNSET,
    scope: None | str | Unset = UNSET,
    workspace: None | str | Unset = UNSET,
    directory: None | str | Unset = UNSET,
    file_overlap: None | str | Unset = UNSET,
    cwd: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """List Contexts

     List user's conversation contexts with pagination, filtering, and relevance scoring.

    Args:
        user_id (str): User ID
        limit (int | Unset): Number of contexts to return Default: 20.
        offset (int | Unset): Number of contexts to skip Default: 0.
        tags (None | str | Unset): Comma-separated tags to filter by
        agent_source (None | str | Unset): Filter by agent source
        organization_id (None | str | Unset): Organization ID context filter
        scope (None | str | Unset): Scope: 'auto', 'all', 'workspace', 'directory'
        workspace (None | str | Unset): Filter by workspace/project name
        directory (None | str | Unset): Filter by directory path
        file_overlap (None | str | Unset): Comma-separated file paths to find overlaps
        cwd (None | str | Unset): Current working directory for 'auto' scope
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
        limit=limit,
        offset=offset,
        tags=tags,
        agent_source=agent_source,
        organization_id=organization_id,
        scope=scope,
        workspace=workspace,
        directory=directory,
        file_overlap=file_overlap,
        cwd=cwd,
        authorization=authorization,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    user_id: str,
    limit: int | Unset = 20,
    offset: int | Unset = 0,
    tags: None | str | Unset = UNSET,
    agent_source: None | str | Unset = UNSET,
    organization_id: None | str | Unset = UNSET,
    scope: None | str | Unset = UNSET,
    workspace: None | str | Unset = UNSET,
    directory: None | str | Unset = UNSET,
    file_overlap: None | str | Unset = UNSET,
    cwd: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """List Contexts

     List user's conversation contexts with pagination, filtering, and relevance scoring.

    Args:
        user_id (str): User ID
        limit (int | Unset): Number of contexts to return Default: 20.
        offset (int | Unset): Number of contexts to skip Default: 0.
        tags (None | str | Unset): Comma-separated tags to filter by
        agent_source (None | str | Unset): Filter by agent source
        organization_id (None | str | Unset): Organization ID context filter
        scope (None | str | Unset): Scope: 'auto', 'all', 'workspace', 'directory'
        workspace (None | str | Unset): Filter by workspace/project name
        directory (None | str | Unset): Filter by directory path
        file_overlap (None | str | Unset): Comma-separated file paths to find overlaps
        cwd (None | str | Unset): Current working directory for 'auto' scope
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        limit=limit,
        offset=offset,
        tags=tags,
        agent_source=agent_source,
        organization_id=organization_id,
        scope=scope,
        workspace=workspace,
        directory=directory,
        file_overlap=file_overlap,
        cwd=cwd,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    user_id: str,
    limit: int | Unset = 20,
    offset: int | Unset = 0,
    tags: None | str | Unset = UNSET,
    agent_source: None | str | Unset = UNSET,
    organization_id: None | str | Unset = UNSET,
    scope: None | str | Unset = UNSET,
    workspace: None | str | Unset = UNSET,
    directory: None | str | Unset = UNSET,
    file_overlap: None | str | Unset = UNSET,
    cwd: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """List Contexts

     List user's conversation contexts with pagination, filtering, and relevance scoring.

    Args:
        user_id (str): User ID
        limit (int | Unset): Number of contexts to return Default: 20.
        offset (int | Unset): Number of contexts to skip Default: 0.
        tags (None | str | Unset): Comma-separated tags to filter by
        agent_source (None | str | Unset): Filter by agent source
        organization_id (None | str | Unset): Organization ID context filter
        scope (None | str | Unset): Scope: 'auto', 'all', 'workspace', 'directory'
        workspace (None | str | Unset): Filter by workspace/project name
        directory (None | str | Unset): Filter by directory path
        file_overlap (None | str | Unset): Comma-separated file paths to find overlaps
        cwd (None | str | Unset): Current working directory for 'auto' scope
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
            limit=limit,
            offset=offset,
            tags=tags,
            agent_source=agent_source,
            organization_id=organization_id,
            scope=scope,
            workspace=workspace,
            directory=directory,
            file_overlap=file_overlap,
            cwd=cwd,
            authorization=authorization,
        )
    ).parsed

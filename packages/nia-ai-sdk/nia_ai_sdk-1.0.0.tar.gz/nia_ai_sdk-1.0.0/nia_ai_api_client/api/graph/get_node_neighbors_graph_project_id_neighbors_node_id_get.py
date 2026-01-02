from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.graph_data import GraphData
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project_id: str,
    node_id: int,
    *,
    user_id: str,
    relationship_types: list[str] | None | Unset = UNSET,
    depth: int | Unset = 1,
    authorization: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["Authorization"] = authorization

    params: dict[str, Any] = {}

    params["user_id"] = user_id

    json_relationship_types: list[str] | None | Unset
    if isinstance(relationship_types, Unset):
        json_relationship_types = UNSET
    elif isinstance(relationship_types, list):
        json_relationship_types = relationship_types

    else:
        json_relationship_types = relationship_types
    params["relationship_types"] = json_relationship_types

    params["depth"] = depth

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/graph/{project_id}/neighbors/{node_id}".format(
            project_id=quote(str(project_id), safe=""),
            node_id=quote(str(node_id), safe=""),
        ),
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GraphData | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = GraphData.from_dict(response.json())

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
) -> Response[GraphData | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: str,
    node_id: int,
    *,
    client: AuthenticatedClient | Client,
    user_id: str,
    relationship_types: list[str] | None | Unset = UNSET,
    depth: int | Unset = 1,
    authorization: None | str | Unset = UNSET,
) -> Response[GraphData | HTTPValidationError]:
    """Get Node Neighbors

     Get neighbors of a specific node.

    Args:
        project_id: The project ID
        node_id: The node ID to expand
        user_id: User ID
        relationship_types: Optional filter for relationship types
        depth: Depth of traversal

    Returns:
        GraphData with expanded nodes and relationships

    Args:
        project_id (str):
        node_id (int):
        user_id (str): User ID
        relationship_types (list[str] | None | Unset): Filter by relationship types
        depth (int | Unset): Depth of traversal Default: 1.
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GraphData | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        node_id=node_id,
        user_id=user_id,
        relationship_types=relationship_types,
        depth=depth,
        authorization=authorization,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project_id: str,
    node_id: int,
    *,
    client: AuthenticatedClient | Client,
    user_id: str,
    relationship_types: list[str] | None | Unset = UNSET,
    depth: int | Unset = 1,
    authorization: None | str | Unset = UNSET,
) -> GraphData | HTTPValidationError | None:
    """Get Node Neighbors

     Get neighbors of a specific node.

    Args:
        project_id: The project ID
        node_id: The node ID to expand
        user_id: User ID
        relationship_types: Optional filter for relationship types
        depth: Depth of traversal

    Returns:
        GraphData with expanded nodes and relationships

    Args:
        project_id (str):
        node_id (int):
        user_id (str): User ID
        relationship_types (list[str] | None | Unset): Filter by relationship types
        depth (int | Unset): Depth of traversal Default: 1.
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GraphData | HTTPValidationError
    """

    return sync_detailed(
        project_id=project_id,
        node_id=node_id,
        client=client,
        user_id=user_id,
        relationship_types=relationship_types,
        depth=depth,
        authorization=authorization,
    ).parsed


async def asyncio_detailed(
    project_id: str,
    node_id: int,
    *,
    client: AuthenticatedClient | Client,
    user_id: str,
    relationship_types: list[str] | None | Unset = UNSET,
    depth: int | Unset = 1,
    authorization: None | str | Unset = UNSET,
) -> Response[GraphData | HTTPValidationError]:
    """Get Node Neighbors

     Get neighbors of a specific node.

    Args:
        project_id: The project ID
        node_id: The node ID to expand
        user_id: User ID
        relationship_types: Optional filter for relationship types
        depth: Depth of traversal

    Returns:
        GraphData with expanded nodes and relationships

    Args:
        project_id (str):
        node_id (int):
        user_id (str): User ID
        relationship_types (list[str] | None | Unset): Filter by relationship types
        depth (int | Unset): Depth of traversal Default: 1.
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GraphData | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        node_id=node_id,
        user_id=user_id,
        relationship_types=relationship_types,
        depth=depth,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_id: str,
    node_id: int,
    *,
    client: AuthenticatedClient | Client,
    user_id: str,
    relationship_types: list[str] | None | Unset = UNSET,
    depth: int | Unset = 1,
    authorization: None | str | Unset = UNSET,
) -> GraphData | HTTPValidationError | None:
    """Get Node Neighbors

     Get neighbors of a specific node.

    Args:
        project_id: The project ID
        node_id: The node ID to expand
        user_id: User ID
        relationship_types: Optional filter for relationship types
        depth: Depth of traversal

    Returns:
        GraphData with expanded nodes and relationships

    Args:
        project_id (str):
        node_id (int):
        user_id (str): User ID
        relationship_types (list[str] | None | Unset): Filter by relationship types
        depth (int | Unset): Depth of traversal Default: 1.
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GraphData | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            project_id=project_id,
            node_id=node_id,
            client=client,
            user_id=user_id,
            relationship_types=relationship_types,
            depth=depth,
            authorization=authorization,
        )
    ).parsed

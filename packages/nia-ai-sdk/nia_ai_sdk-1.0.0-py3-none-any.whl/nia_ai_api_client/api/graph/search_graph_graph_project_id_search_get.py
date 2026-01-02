from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.graph_node import GraphNode
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project_id: str,
    *,
    user_id: str,
    q: str,
    search_type: str | Unset = "name",
    authorization: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["Authorization"] = authorization

    params: dict[str, Any] = {}

    params["user_id"] = user_id

    params["q"] = q

    params["search_type"] = search_type

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/graph/{project_id}/search".format(
            project_id=quote(str(project_id), safe=""),
        ),
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | list[GraphNode] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = GraphNode.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[HTTPValidationError | list[GraphNode]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: str,
    *,
    client: AuthenticatedClient | Client,
    user_id: str,
    q: str,
    search_type: str | Unset = "name",
    authorization: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | list[GraphNode]]:
    """Search Graph

     Search for nodes in the graph.

    Args:
        project_id: The project ID
        user_id: User ID
        q: Search query
        search_type: Field to search in

    Returns:
        List of matching nodes

    Args:
        project_id (str):
        user_id (str): User ID
        q (str): Search query
        search_type (str | Unset): Search by 'name' or 'qualified_name' Default: 'name'.
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[GraphNode]]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        user_id=user_id,
        q=q,
        search_type=search_type,
        authorization=authorization,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project_id: str,
    *,
    client: AuthenticatedClient | Client,
    user_id: str,
    q: str,
    search_type: str | Unset = "name",
    authorization: None | str | Unset = UNSET,
) -> HTTPValidationError | list[GraphNode] | None:
    """Search Graph

     Search for nodes in the graph.

    Args:
        project_id: The project ID
        user_id: User ID
        q: Search query
        search_type: Field to search in

    Returns:
        List of matching nodes

    Args:
        project_id (str):
        user_id (str): User ID
        q (str): Search query
        search_type (str | Unset): Search by 'name' or 'qualified_name' Default: 'name'.
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[GraphNode]
    """

    return sync_detailed(
        project_id=project_id,
        client=client,
        user_id=user_id,
        q=q,
        search_type=search_type,
        authorization=authorization,
    ).parsed


async def asyncio_detailed(
    project_id: str,
    *,
    client: AuthenticatedClient | Client,
    user_id: str,
    q: str,
    search_type: str | Unset = "name",
    authorization: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | list[GraphNode]]:
    """Search Graph

     Search for nodes in the graph.

    Args:
        project_id: The project ID
        user_id: User ID
        q: Search query
        search_type: Field to search in

    Returns:
        List of matching nodes

    Args:
        project_id (str):
        user_id (str): User ID
        q (str): Search query
        search_type (str | Unset): Search by 'name' or 'qualified_name' Default: 'name'.
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[GraphNode]]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        user_id=user_id,
        q=q,
        search_type=search_type,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_id: str,
    *,
    client: AuthenticatedClient | Client,
    user_id: str,
    q: str,
    search_type: str | Unset = "name",
    authorization: None | str | Unset = UNSET,
) -> HTTPValidationError | list[GraphNode] | None:
    """Search Graph

     Search for nodes in the graph.

    Args:
        project_id: The project ID
        user_id: User ID
        q: Search query
        search_type: Field to search in

    Returns:
        List of matching nodes

    Args:
        project_id (str):
        user_id (str): User ID
        q (str): Search query
        search_type (str | Unset): Search by 'name' or 'qualified_name' Default: 'name'.
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[GraphNode]
    """

    return (
        await asyncio_detailed(
            project_id=project_id,
            client=client,
            user_id=user_id,
            q=q,
            search_type=search_type,
            authorization=authorization,
        )
    ).parsed

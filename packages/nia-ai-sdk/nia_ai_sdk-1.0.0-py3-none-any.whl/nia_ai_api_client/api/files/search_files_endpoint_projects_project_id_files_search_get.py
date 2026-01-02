from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.file_search_result import FileSearchResult
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project_id: str,
    *,
    query: str,
    user_id: str,
    top_k: int | Unset = 10,
    additional_project_ids: list[str] | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["Authorization"] = authorization

    params: dict[str, Any] = {}

    params["query"] = query

    params["user_id"] = user_id

    params["top_k"] = top_k

    json_additional_project_ids: list[str] | Unset = UNSET
    if not isinstance(additional_project_ids, Unset):
        json_additional_project_ids = additional_project_ids

    params["additional_project_ids"] = json_additional_project_ids

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/projects/{project_id}/files/search".format(
            project_id=quote(str(project_id), safe=""),
        ),
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | list[FileSearchResult] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = FileSearchResult.from_dict(response_200_item_data)

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
) -> Response[HTTPValidationError | list[FileSearchResult]]:
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
    query: str,
    user_id: str,
    top_k: int | Unset = 10,
    additional_project_ids: list[str] | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | list[FileSearchResult]]:
    """Search Files Endpoint

     Search for files using semantic search across multiple projects

    Args:
        project_id (str):
        query (str):
        user_id (str):
        top_k (int | Unset):  Default: 10.
        additional_project_ids (list[str] | Unset):
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[FileSearchResult]]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        query=query,
        user_id=user_id,
        top_k=top_k,
        additional_project_ids=additional_project_ids,
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
    query: str,
    user_id: str,
    top_k: int | Unset = 10,
    additional_project_ids: list[str] | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
) -> HTTPValidationError | list[FileSearchResult] | None:
    """Search Files Endpoint

     Search for files using semantic search across multiple projects

    Args:
        project_id (str):
        query (str):
        user_id (str):
        top_k (int | Unset):  Default: 10.
        additional_project_ids (list[str] | Unset):
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[FileSearchResult]
    """

    return sync_detailed(
        project_id=project_id,
        client=client,
        query=query,
        user_id=user_id,
        top_k=top_k,
        additional_project_ids=additional_project_ids,
        authorization=authorization,
    ).parsed


async def asyncio_detailed(
    project_id: str,
    *,
    client: AuthenticatedClient | Client,
    query: str,
    user_id: str,
    top_k: int | Unset = 10,
    additional_project_ids: list[str] | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | list[FileSearchResult]]:
    """Search Files Endpoint

     Search for files using semantic search across multiple projects

    Args:
        project_id (str):
        query (str):
        user_id (str):
        top_k (int | Unset):  Default: 10.
        additional_project_ids (list[str] | Unset):
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[FileSearchResult]]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        query=query,
        user_id=user_id,
        top_k=top_k,
        additional_project_ids=additional_project_ids,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_id: str,
    *,
    client: AuthenticatedClient | Client,
    query: str,
    user_id: str,
    top_k: int | Unset = 10,
    additional_project_ids: list[str] | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
) -> HTTPValidationError | list[FileSearchResult] | None:
    """Search Files Endpoint

     Search for files using semantic search across multiple projects

    Args:
        project_id (str):
        query (str):
        user_id (str):
        top_k (int | Unset):  Default: 10.
        additional_project_ids (list[str] | Unset):
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[FileSearchResult]
    """

    return (
        await asyncio_detailed(
            project_id=project_id,
            client=client,
            query=query,
            user_id=user_id,
            top_k=top_k,
            additional_project_ids=additional_project_ids,
            authorization=authorization,
        )
    ).parsed

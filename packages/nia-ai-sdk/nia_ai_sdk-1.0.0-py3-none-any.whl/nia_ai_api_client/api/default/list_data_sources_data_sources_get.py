from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.data_source_response import DataSourceResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    project_id: None | str | Unset = UNSET,
    q: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
    is_active: bool | None | Unset = UNSET,
    source_type: None | str | Unset = UNSET,
    user_id: None | str | Unset = UNSET,
    organization_id: None | str | Unset = UNSET,
    limit: int | Unset = 500,
    offset: int | Unset = 0,
    authorization: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["Authorization"] = authorization

    params: dict[str, Any] = {}

    json_project_id: None | str | Unset
    if isinstance(project_id, Unset):
        json_project_id = UNSET
    else:
        json_project_id = project_id
    params["project_id"] = json_project_id

    json_q: None | str | Unset
    if isinstance(q, Unset):
        json_q = UNSET
    else:
        json_q = q
    params["q"] = json_q

    json_status: None | str | Unset
    if isinstance(status, Unset):
        json_status = UNSET
    else:
        json_status = status
    params["status"] = json_status

    json_is_active: bool | None | Unset
    if isinstance(is_active, Unset):
        json_is_active = UNSET
    else:
        json_is_active = is_active
    params["is_active"] = json_is_active

    json_source_type: None | str | Unset
    if isinstance(source_type, Unset):
        json_source_type = UNSET
    else:
        json_source_type = source_type
    params["source_type"] = json_source_type

    json_user_id: None | str | Unset
    if isinstance(user_id, Unset):
        json_user_id = UNSET
    else:
        json_user_id = user_id
    params["user_id"] = json_user_id

    json_organization_id: None | str | Unset
    if isinstance(organization_id, Unset):
        json_organization_id = UNSET
    else:
        json_organization_id = organization_id
    params["organization_id"] = json_organization_id

    params["limit"] = limit

    params["offset"] = offset

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/data-sources",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | list[DataSourceResponse] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = DataSourceResponse.from_dict(response_200_item_data)

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
) -> Response[HTTPValidationError | list[DataSourceResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    project_id: None | str | Unset = UNSET,
    q: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
    is_active: bool | None | Unset = UNSET,
    source_type: None | str | Unset = UNSET,
    user_id: None | str | Unset = UNSET,
    organization_id: None | str | Unset = UNSET,
    limit: int | Unset = 500,
    offset: int | Unset = 0,
    authorization: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | list[DataSourceResponse]]:
    """List Data Sources

     List data sources for current context (personal or specific org).

    Args:
        project_id (None | str | Unset):
        q (None | str | Unset): Search by display name, URL, or file name
        status (None | str | Unset): Filter by indexing status
        is_active (bool | None | Unset): Filter by active/inactive
        source_type (None | str | Unset): Filter by source type
        user_id (None | str | Unset):
        organization_id (None | str | Unset): Active organization ID for context filtering
        limit (int | Unset): Maximum number of sources to return Default: 500.
        offset (int | Unset): Number of sources to skip Default: 0.
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[DataSourceResponse]]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        q=q,
        status=status,
        is_active=is_active,
        source_type=source_type,
        user_id=user_id,
        organization_id=organization_id,
        limit=limit,
        offset=offset,
        authorization=authorization,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    project_id: None | str | Unset = UNSET,
    q: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
    is_active: bool | None | Unset = UNSET,
    source_type: None | str | Unset = UNSET,
    user_id: None | str | Unset = UNSET,
    organization_id: None | str | Unset = UNSET,
    limit: int | Unset = 500,
    offset: int | Unset = 0,
    authorization: None | str | Unset = UNSET,
) -> HTTPValidationError | list[DataSourceResponse] | None:
    """List Data Sources

     List data sources for current context (personal or specific org).

    Args:
        project_id (None | str | Unset):
        q (None | str | Unset): Search by display name, URL, or file name
        status (None | str | Unset): Filter by indexing status
        is_active (bool | None | Unset): Filter by active/inactive
        source_type (None | str | Unset): Filter by source type
        user_id (None | str | Unset):
        organization_id (None | str | Unset): Active organization ID for context filtering
        limit (int | Unset): Maximum number of sources to return Default: 500.
        offset (int | Unset): Number of sources to skip Default: 0.
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[DataSourceResponse]
    """

    return sync_detailed(
        client=client,
        project_id=project_id,
        q=q,
        status=status,
        is_active=is_active,
        source_type=source_type,
        user_id=user_id,
        organization_id=organization_id,
        limit=limit,
        offset=offset,
        authorization=authorization,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    project_id: None | str | Unset = UNSET,
    q: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
    is_active: bool | None | Unset = UNSET,
    source_type: None | str | Unset = UNSET,
    user_id: None | str | Unset = UNSET,
    organization_id: None | str | Unset = UNSET,
    limit: int | Unset = 500,
    offset: int | Unset = 0,
    authorization: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | list[DataSourceResponse]]:
    """List Data Sources

     List data sources for current context (personal or specific org).

    Args:
        project_id (None | str | Unset):
        q (None | str | Unset): Search by display name, URL, or file name
        status (None | str | Unset): Filter by indexing status
        is_active (bool | None | Unset): Filter by active/inactive
        source_type (None | str | Unset): Filter by source type
        user_id (None | str | Unset):
        organization_id (None | str | Unset): Active organization ID for context filtering
        limit (int | Unset): Maximum number of sources to return Default: 500.
        offset (int | Unset): Number of sources to skip Default: 0.
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[DataSourceResponse]]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        q=q,
        status=status,
        is_active=is_active,
        source_type=source_type,
        user_id=user_id,
        organization_id=organization_id,
        limit=limit,
        offset=offset,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    project_id: None | str | Unset = UNSET,
    q: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
    is_active: bool | None | Unset = UNSET,
    source_type: None | str | Unset = UNSET,
    user_id: None | str | Unset = UNSET,
    organization_id: None | str | Unset = UNSET,
    limit: int | Unset = 500,
    offset: int | Unset = 0,
    authorization: None | str | Unset = UNSET,
) -> HTTPValidationError | list[DataSourceResponse] | None:
    """List Data Sources

     List data sources for current context (personal or specific org).

    Args:
        project_id (None | str | Unset):
        q (None | str | Unset): Search by display name, URL, or file name
        status (None | str | Unset): Filter by indexing status
        is_active (bool | None | Unset): Filter by active/inactive
        source_type (None | str | Unset): Filter by source type
        user_id (None | str | Unset):
        organization_id (None | str | Unset): Active organization ID for context filtering
        limit (int | Unset): Maximum number of sources to return Default: 500.
        offset (int | Unset): Number of sources to skip Default: 0.
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[DataSourceResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            project_id=project_id,
            q=q,
            status=status,
            is_active=is_active,
            source_type=source_type,
            user_id=user_id,
            organization_id=organization_id,
            limit=limit,
            offset=offset,
            authorization=authorization,
        )
    ).parsed

from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.doc_content_response import DocContentResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    source_id: str,
    *,
    path: None | str | Unset = UNSET,
    url_query: None | str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_path: None | str | Unset
    if isinstance(path, Unset):
        json_path = UNSET
    else:
        json_path = path
    params["path"] = json_path

    json_url_query: None | str | Unset
    if isinstance(url_query, Unset):
        json_url_query = UNSET
    else:
        json_url_query = url_query
    params["url"] = json_url_query

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/data-sources/{source_id}/content".format(
            source_id=quote(str(source_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DocContentResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = DocContentResponse.from_dict(response.json())

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
) -> Response[DocContentResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    source_id: str,
    *,
    client: AuthenticatedClient | Client,
    path: None | str | Unset = UNSET,
    url_query: None | str | Unset = UNSET,
) -> Response[DocContentResponse | HTTPValidationError]:
    """Get page content

     Retrieve full content of a documentation page.

    Args:
        source_id (str):
        path (None | str | Unset): Virtual path to the page
        url_query (None | str | Unset): Direct URL of the page

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DocContentResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        source_id=source_id,
        path=path,
        url_query=url_query,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    source_id: str,
    *,
    client: AuthenticatedClient | Client,
    path: None | str | Unset = UNSET,
    url_query: None | str | Unset = UNSET,
) -> DocContentResponse | HTTPValidationError | None:
    """Get page content

     Retrieve full content of a documentation page.

    Args:
        source_id (str):
        path (None | str | Unset): Virtual path to the page
        url_query (None | str | Unset): Direct URL of the page

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DocContentResponse | HTTPValidationError
    """

    return sync_detailed(
        source_id=source_id,
        client=client,
        path=path,
        url_query=url_query,
    ).parsed


async def asyncio_detailed(
    source_id: str,
    *,
    client: AuthenticatedClient | Client,
    path: None | str | Unset = UNSET,
    url_query: None | str | Unset = UNSET,
) -> Response[DocContentResponse | HTTPValidationError]:
    """Get page content

     Retrieve full content of a documentation page.

    Args:
        source_id (str):
        path (None | str | Unset): Virtual path to the page
        url_query (None | str | Unset): Direct URL of the page

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DocContentResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        source_id=source_id,
        path=path,
        url_query=url_query,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    source_id: str,
    *,
    client: AuthenticatedClient | Client,
    path: None | str | Unset = UNSET,
    url_query: None | str | Unset = UNSET,
) -> DocContentResponse | HTTPValidationError | None:
    """Get page content

     Retrieve full content of a documentation page.

    Args:
        source_id (str):
        path (None | str | Unset): Virtual path to the page
        url_query (None | str | Unset): Direct URL of the page

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DocContentResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            source_id=source_id,
            client=client,
            path=path,
            url_query=url_query,
        )
    ).parsed

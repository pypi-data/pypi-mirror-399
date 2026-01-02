from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    source_id: str,
    *,
    path: str,
    line_start: int | None | Unset = UNSET,
    line_end: int | None | Unset = UNSET,
    max_length: int | None | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["path"] = path

    json_line_start: int | None | Unset
    if isinstance(line_start, Unset):
        json_line_start = UNSET
    else:
        json_line_start = line_start
    params["line_start"] = json_line_start

    json_line_end: int | None | Unset
    if isinstance(line_end, Unset):
        json_line_end = UNSET
    else:
        json_line_end = line_end
    params["line_end"] = json_line_end

    json_max_length: int | None | Unset
    if isinstance(max_length, Unset):
        json_max_length = UNSET
    else:
        json_max_length = max_length
    params["max_length"] = json_max_length

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/data-sources/{source_id}/read".format(
            source_id=quote(str(source_id), safe=""),
        ),
        "params": params,
    }

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
    source_id: str,
    *,
    client: AuthenticatedClient | Client,
    path: str,
    line_start: int | None | Unset = UNSET,
    line_end: int | None | Unset = UNSET,
    max_length: int | None | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Read documentation page

     Read page content by virtual path. Supports line range and max_length truncation.

    Args:
        source_id (str):
        path (str):
        line_start (int | None | Unset): Start line (1-based, inclusive)
        line_end (int | None | Unset): End line (1-based, inclusive)
        max_length (int | None | Unset): Max characters to return

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        source_id=source_id,
        path=path,
        line_start=line_start,
        line_end=line_end,
        max_length=max_length,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    source_id: str,
    *,
    client: AuthenticatedClient | Client,
    path: str,
    line_start: int | None | Unset = UNSET,
    line_end: int | None | Unset = UNSET,
    max_length: int | None | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Read documentation page

     Read page content by virtual path. Supports line range and max_length truncation.

    Args:
        source_id (str):
        path (str):
        line_start (int | None | Unset): Start line (1-based, inclusive)
        line_end (int | None | Unset): End line (1-based, inclusive)
        max_length (int | None | Unset): Max characters to return

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        source_id=source_id,
        client=client,
        path=path,
        line_start=line_start,
        line_end=line_end,
        max_length=max_length,
    ).parsed


async def asyncio_detailed(
    source_id: str,
    *,
    client: AuthenticatedClient | Client,
    path: str,
    line_start: int | None | Unset = UNSET,
    line_end: int | None | Unset = UNSET,
    max_length: int | None | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Read documentation page

     Read page content by virtual path. Supports line range and max_length truncation.

    Args:
        source_id (str):
        path (str):
        line_start (int | None | Unset): Start line (1-based, inclusive)
        line_end (int | None | Unset): End line (1-based, inclusive)
        max_length (int | None | Unset): Max characters to return

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        source_id=source_id,
        path=path,
        line_start=line_start,
        line_end=line_end,
        max_length=max_length,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    source_id: str,
    *,
    client: AuthenticatedClient | Client,
    path: str,
    line_start: int | None | Unset = UNSET,
    line_end: int | None | Unset = UNSET,
    max_length: int | None | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Read documentation page

     Read page content by virtual path. Supports line range and max_length truncation.

    Args:
        source_id (str):
        path (str):
        line_start (int | None | Unset): Start line (1-based, inclusive)
        line_end (int | None | Unset): End line (1-based, inclusive)
        max_length (int | None | Unset): Max characters to return

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            source_id=source_id,
            client=client,
            path=path,
            line_start=line_start,
            line_end=line_end,
            max_length=max_length,
        )
    ).parsed

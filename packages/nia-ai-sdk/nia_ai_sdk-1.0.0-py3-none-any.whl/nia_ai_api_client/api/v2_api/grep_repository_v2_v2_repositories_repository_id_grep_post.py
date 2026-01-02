from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.code_grep_request import CodeGrepRequest
from ...models.code_grep_response import CodeGrepResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    repository_id: str,
    *,
    body: CodeGrepRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v2/repositories/{repository_id}/grep".format(
            repository_id=quote(str(repository_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CodeGrepResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = CodeGrepResponse.from_dict(response.json())

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
) -> Response[CodeGrepResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    repository_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: CodeGrepRequest,
) -> Response[CodeGrepResponse | HTTPValidationError]:
    """Grep repository code

     Regex search over indexed code. Exhaustive by default (searches all chunks). Supports context lines,
    case sensitivity, output modes.

    Args:
        repository_id (str):
        body (CodeGrepRequest): Request model for code grep search with advanced options.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CodeGrepResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        repository_id=repository_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: CodeGrepRequest,
) -> CodeGrepResponse | HTTPValidationError | None:
    """Grep repository code

     Regex search over indexed code. Exhaustive by default (searches all chunks). Supports context lines,
    case sensitivity, output modes.

    Args:
        repository_id (str):
        body (CodeGrepRequest): Request model for code grep search with advanced options.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CodeGrepResponse | HTTPValidationError
    """

    return sync_detailed(
        repository_id=repository_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    repository_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: CodeGrepRequest,
) -> Response[CodeGrepResponse | HTTPValidationError]:
    """Grep repository code

     Regex search over indexed code. Exhaustive by default (searches all chunks). Supports context lines,
    case sensitivity, output modes.

    Args:
        repository_id (str):
        body (CodeGrepRequest): Request model for code grep search with advanced options.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CodeGrepResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        repository_id=repository_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: CodeGrepRequest,
) -> CodeGrepResponse | HTTPValidationError | None:
    """Grep repository code

     Regex search over indexed code. Exhaustive by default (searches all chunks). Supports context lines,
    case sensitivity, output modes.

    Args:
        repository_id (str):
        body (CodeGrepRequest): Request model for code grep search with advanced options.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CodeGrepResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            repository_id=repository_id,
            client=client,
            body=body,
        )
    ).parsed

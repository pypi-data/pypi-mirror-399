from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.subscribe_request import SubscribeRequest
from ...models.subscribe_response import SubscribeResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: SubscribeRequest,
    authorization: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["Authorization"] = authorization

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/global-sources/subscribe",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | SubscribeResponse | None:
    if response.status_code == 200:
        response_200 = SubscribeResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | SubscribeResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: SubscribeRequest,
    authorization: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | SubscribeResponse]:
    """Subscribe To Global Source

     Subscribe to a global source or trigger indexing if not yet indexed.

    This endpoint:
    1. Checks if the source is already globally indexed
    2. If indexed (with data):
       - For REPOSITORIES: Creates a project entry pointing to global namespace
       - For DOCUMENTATION: Creates a data_source entry pointing to global namespace
    3. If indexed but no data OR needs indexing: triggers indexing workflow

    Requires authentication and the user must match the provided user_id.

    Args:
        authorization (None | str | Unset):
        body (SubscribeRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SubscribeResponse]
    """

    kwargs = _get_kwargs(
        body=body,
        authorization=authorization,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: SubscribeRequest,
    authorization: None | str | Unset = UNSET,
) -> HTTPValidationError | SubscribeResponse | None:
    """Subscribe To Global Source

     Subscribe to a global source or trigger indexing if not yet indexed.

    This endpoint:
    1. Checks if the source is already globally indexed
    2. If indexed (with data):
       - For REPOSITORIES: Creates a project entry pointing to global namespace
       - For DOCUMENTATION: Creates a data_source entry pointing to global namespace
    3. If indexed but no data OR needs indexing: triggers indexing workflow

    Requires authentication and the user must match the provided user_id.

    Args:
        authorization (None | str | Unset):
        body (SubscribeRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | SubscribeResponse
    """

    return sync_detailed(
        client=client,
        body=body,
        authorization=authorization,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: SubscribeRequest,
    authorization: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | SubscribeResponse]:
    """Subscribe To Global Source

     Subscribe to a global source or trigger indexing if not yet indexed.

    This endpoint:
    1. Checks if the source is already globally indexed
    2. If indexed (with data):
       - For REPOSITORIES: Creates a project entry pointing to global namespace
       - For DOCUMENTATION: Creates a data_source entry pointing to global namespace
    3. If indexed but no data OR needs indexing: triggers indexing workflow

    Requires authentication and the user must match the provided user_id.

    Args:
        authorization (None | str | Unset):
        body (SubscribeRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SubscribeResponse]
    """

    kwargs = _get_kwargs(
        body=body,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: SubscribeRequest,
    authorization: None | str | Unset = UNSET,
) -> HTTPValidationError | SubscribeResponse | None:
    """Subscribe To Global Source

     Subscribe to a global source or trigger indexing if not yet indexed.

    This endpoint:
    1. Checks if the source is already globally indexed
    2. If indexed (with data):
       - For REPOSITORIES: Creates a project entry pointing to global namespace
       - For DOCUMENTATION: Creates a data_source entry pointing to global namespace
    3. If indexed but no data OR needs indexing: triggers indexing workflow

    Requires authentication and the user must match the provided user_id.

    Args:
        authorization (None | str | Unset):
        body (SubscribeRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | SubscribeResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            authorization=authorization,
        )
    ).parsed

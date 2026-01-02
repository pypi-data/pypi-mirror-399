from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project_id: str,
    chat_id: str,
    *,
    body: str,
    user_id: str,
    authorization: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["Authorization"] = authorization

    params: dict[str, Any] = {}

    params["user_id"] = user_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/projects/{project_id}/chats/{chat_id}".format(
            project_id=quote(str(project_id), safe=""),
            chat_id=quote(str(chat_id), safe=""),
        ),
        "params": params,
    }

    _kwargs["json"] = body

    headers["Content-Type"] = "application/json"

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
    project_id: str,
    chat_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: str,
    user_id: str,
    authorization: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Update Chat Endpoint

     Update a chat's title.

    Args:
        project_id (str):
        chat_id (str):
        user_id (str):
        authorization (None | str | Unset):
        body (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        chat_id=chat_id,
        body=body,
        user_id=user_id,
        authorization=authorization,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project_id: str,
    chat_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: str,
    user_id: str,
    authorization: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Update Chat Endpoint

     Update a chat's title.

    Args:
        project_id (str):
        chat_id (str):
        user_id (str):
        authorization (None | str | Unset):
        body (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        project_id=project_id,
        chat_id=chat_id,
        client=client,
        body=body,
        user_id=user_id,
        authorization=authorization,
    ).parsed


async def asyncio_detailed(
    project_id: str,
    chat_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: str,
    user_id: str,
    authorization: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Update Chat Endpoint

     Update a chat's title.

    Args:
        project_id (str):
        chat_id (str):
        user_id (str):
        authorization (None | str | Unset):
        body (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        chat_id=chat_id,
        body=body,
        user_id=user_id,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_id: str,
    chat_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: str,
    user_id: str,
    authorization: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Update Chat Endpoint

     Update a chat's title.

    Args:
        project_id (str):
        chat_id (str):
        user_id (str):
        authorization (None | str | Unset):
        body (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            project_id=project_id,
            chat_id=chat_id,
            client=client,
            body=body,
            user_id=user_id,
            authorization=authorization,
        )
    ).parsed

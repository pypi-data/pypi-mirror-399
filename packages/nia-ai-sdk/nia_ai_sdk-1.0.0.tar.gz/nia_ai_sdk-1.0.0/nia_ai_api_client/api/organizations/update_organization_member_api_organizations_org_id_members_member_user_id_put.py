from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.update_member_request import UpdateMemberRequest
from ...types import UNSET, Response, Unset


def _get_kwargs(
    org_id: str,
    member_user_id: str,
    *,
    body: UpdateMemberRequest,
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
        "method": "put",
        "url": "/api/organizations/{org_id}/members/{member_user_id}".format(
            org_id=quote(str(org_id), safe=""),
            member_user_id=quote(str(member_user_id), safe=""),
        ),
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

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
    org_id: str,
    member_user_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateMemberRequest,
    user_id: str,
    authorization: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Update Organization Member

     Update organization member settings (e.g., toggle Pro).
    Only admins can update members.

    Args:
        org_id (str):
        member_user_id (str):
        user_id (str):
        authorization (None | str | Unset):
        body (UpdateMemberRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        member_user_id=member_user_id,
        body=body,
        user_id=user_id,
        authorization=authorization,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    org_id: str,
    member_user_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateMemberRequest,
    user_id: str,
    authorization: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Update Organization Member

     Update organization member settings (e.g., toggle Pro).
    Only admins can update members.

    Args:
        org_id (str):
        member_user_id (str):
        user_id (str):
        authorization (None | str | Unset):
        body (UpdateMemberRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        org_id=org_id,
        member_user_id=member_user_id,
        client=client,
        body=body,
        user_id=user_id,
        authorization=authorization,
    ).parsed


async def asyncio_detailed(
    org_id: str,
    member_user_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateMemberRequest,
    user_id: str,
    authorization: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Update Organization Member

     Update organization member settings (e.g., toggle Pro).
    Only admins can update members.

    Args:
        org_id (str):
        member_user_id (str):
        user_id (str):
        authorization (None | str | Unset):
        body (UpdateMemberRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        member_user_id=member_user_id,
        body=body,
        user_id=user_id,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    org_id: str,
    member_user_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateMemberRequest,
    user_id: str,
    authorization: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Update Organization Member

     Update organization member settings (e.g., toggle Pro).
    Only admins can update members.

    Args:
        org_id (str):
        member_user_id (str):
        user_id (str):
        authorization (None | str | Unset):
        body (UpdateMemberRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            member_user_id=member_user_id,
            client=client,
            body=body,
            user_id=user_id,
            authorization=authorization,
        )
    ).parsed

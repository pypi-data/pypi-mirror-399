from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.invoice_list_response import InvoiceListResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    org_id: str,
    *,
    user_id: str,
    limit: int | Unset = 10,
    authorization: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["Authorization"] = authorization

    params: dict[str, Any] = {}

    params["user_id"] = user_id

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/billing/organization/{org_id}/invoices".format(
            org_id=quote(str(org_id), safe=""),
        ),
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | InvoiceListResponse | None:
    if response.status_code == 200:
        response_200 = InvoiceListResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | InvoiceListResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    user_id: str,
    limit: int | Unset = 10,
    authorization: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | InvoiceListResponse]:
    """List Organization Invoices

     List invoices for an organization. User must be a member.

    Args:
        org_id (str):
        user_id (str):
        limit (int | Unset):  Default: 10.
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | InvoiceListResponse]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        user_id=user_id,
        limit=limit,
        authorization=authorization,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    user_id: str,
    limit: int | Unset = 10,
    authorization: None | str | Unset = UNSET,
) -> HTTPValidationError | InvoiceListResponse | None:
    """List Organization Invoices

     List invoices for an organization. User must be a member.

    Args:
        org_id (str):
        user_id (str):
        limit (int | Unset):  Default: 10.
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | InvoiceListResponse
    """

    return sync_detailed(
        org_id=org_id,
        client=client,
        user_id=user_id,
        limit=limit,
        authorization=authorization,
    ).parsed


async def asyncio_detailed(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    user_id: str,
    limit: int | Unset = 10,
    authorization: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | InvoiceListResponse]:
    """List Organization Invoices

     List invoices for an organization. User must be a member.

    Args:
        org_id (str):
        user_id (str):
        limit (int | Unset):  Default: 10.
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | InvoiceListResponse]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        user_id=user_id,
        limit=limit,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    user_id: str,
    limit: int | Unset = 10,
    authorization: None | str | Unset = UNSET,
) -> HTTPValidationError | InvoiceListResponse | None:
    """List Organization Invoices

     List invoices for an organization. User must be a member.

    Args:
        org_id (str):
        user_id (str):
        limit (int | Unset):  Default: 10.
        authorization (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | InvoiceListResponse
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            client=client,
            user_id=user_id,
            limit=limit,
            authorization=authorization,
        )
    ).parsed

from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.project_source_association_request import ProjectSourceAssociationRequest
from ...models.project_source_association_response import ProjectSourceAssociationResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: ProjectSourceAssociationRequest,
    authorization: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["Authorization"] = authorization

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/project-sources/associate",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | ProjectSourceAssociationResponse | None:
    if response.status_code == 200:
        response_200 = ProjectSourceAssociationResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | ProjectSourceAssociationResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ProjectSourceAssociationRequest,
    authorization: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ProjectSourceAssociationResponse]:
    """Associate Project Source

     Associate a data source with a project.

    Args:
        authorization (None | str | Unset):
        body (ProjectSourceAssociationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ProjectSourceAssociationResponse]
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
    body: ProjectSourceAssociationRequest,
    authorization: None | str | Unset = UNSET,
) -> HTTPValidationError | ProjectSourceAssociationResponse | None:
    """Associate Project Source

     Associate a data source with a project.

    Args:
        authorization (None | str | Unset):
        body (ProjectSourceAssociationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ProjectSourceAssociationResponse
    """

    return sync_detailed(
        client=client,
        body=body,
        authorization=authorization,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ProjectSourceAssociationRequest,
    authorization: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ProjectSourceAssociationResponse]:
    """Associate Project Source

     Associate a data source with a project.

    Args:
        authorization (None | str | Unset):
        body (ProjectSourceAssociationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ProjectSourceAssociationResponse]
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
    body: ProjectSourceAssociationRequest,
    authorization: None | str | Unset = UNSET,
) -> HTTPValidationError | ProjectSourceAssociationResponse | None:
    """Associate Project Source

     Associate a data source with a project.

    Args:
        authorization (None | str | Unset):
        body (ProjectSourceAssociationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ProjectSourceAssociationResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            authorization=authorization,
        )
    ).parsed

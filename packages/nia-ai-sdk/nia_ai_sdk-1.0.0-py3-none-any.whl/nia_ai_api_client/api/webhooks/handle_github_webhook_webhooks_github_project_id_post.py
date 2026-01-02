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
    *,
    x_github_event: None | str | Unset = UNSET,
    x_hub_signature_256: None | str | Unset = UNSET,
    x_github_delivery: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_github_event, Unset):
        headers["x-github-event"] = x_github_event

    if not isinstance(x_hub_signature_256, Unset):
        headers["x-hub-signature-256"] = x_hub_signature_256

    if not isinstance(x_github_delivery, Unset):
        headers["x-github-delivery"] = x_github_delivery

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/webhooks/github/{project_id}".format(
            project_id=quote(str(project_id), safe=""),
        ),
    }

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
    *,
    client: AuthenticatedClient | Client,
    x_github_event: None | str | Unset = UNSET,
    x_hub_signature_256: None | str | Unset = UNSET,
    x_github_delivery: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Handle Github Webhook

     Handle GitHub webhook events for a specific project.

    This endpoint receives webhook events from GitHub and triggers
    appropriate workflows for continuous indexing.

    Args:
        request: FastAPI request object
        project_id: The project ID
        x_github_event: GitHub event type header
        x_hub_signature_256: GitHub signature header
        x_github_delivery: GitHub delivery ID header

    Returns:
        Processing status

    Args:
        project_id (str):
        x_github_event (None | str | Unset):
        x_hub_signature_256 (None | str | Unset):
        x_github_delivery (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        x_github_event=x_github_event,
        x_hub_signature_256=x_hub_signature_256,
        x_github_delivery=x_github_delivery,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project_id: str,
    *,
    client: AuthenticatedClient | Client,
    x_github_event: None | str | Unset = UNSET,
    x_hub_signature_256: None | str | Unset = UNSET,
    x_github_delivery: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Handle Github Webhook

     Handle GitHub webhook events for a specific project.

    This endpoint receives webhook events from GitHub and triggers
    appropriate workflows for continuous indexing.

    Args:
        request: FastAPI request object
        project_id: The project ID
        x_github_event: GitHub event type header
        x_hub_signature_256: GitHub signature header
        x_github_delivery: GitHub delivery ID header

    Returns:
        Processing status

    Args:
        project_id (str):
        x_github_event (None | str | Unset):
        x_hub_signature_256 (None | str | Unset):
        x_github_delivery (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        project_id=project_id,
        client=client,
        x_github_event=x_github_event,
        x_hub_signature_256=x_hub_signature_256,
        x_github_delivery=x_github_delivery,
    ).parsed


async def asyncio_detailed(
    project_id: str,
    *,
    client: AuthenticatedClient | Client,
    x_github_event: None | str | Unset = UNSET,
    x_hub_signature_256: None | str | Unset = UNSET,
    x_github_delivery: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Handle Github Webhook

     Handle GitHub webhook events for a specific project.

    This endpoint receives webhook events from GitHub and triggers
    appropriate workflows for continuous indexing.

    Args:
        request: FastAPI request object
        project_id: The project ID
        x_github_event: GitHub event type header
        x_hub_signature_256: GitHub signature header
        x_github_delivery: GitHub delivery ID header

    Returns:
        Processing status

    Args:
        project_id (str):
        x_github_event (None | str | Unset):
        x_hub_signature_256 (None | str | Unset):
        x_github_delivery (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        x_github_event=x_github_event,
        x_hub_signature_256=x_hub_signature_256,
        x_github_delivery=x_github_delivery,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_id: str,
    *,
    client: AuthenticatedClient | Client,
    x_github_event: None | str | Unset = UNSET,
    x_hub_signature_256: None | str | Unset = UNSET,
    x_github_delivery: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Handle Github Webhook

     Handle GitHub webhook events for a specific project.

    This endpoint receives webhook events from GitHub and triggers
    appropriate workflows for continuous indexing.

    Args:
        request: FastAPI request object
        project_id: The project ID
        x_github_event: GitHub event type header
        x_hub_signature_256: GitHub signature header
        x_github_delivery: GitHub delivery ID header

    Returns:
        Processing status

    Args:
        project_id (str):
        x_github_event (None | str | Unset):
        x_hub_signature_256 (None | str | Unset):
        x_github_delivery (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            project_id=project_id,
            client=client,
            x_github_event=x_github_event,
            x_hub_signature_256=x_hub_signature_256,
            x_github_delivery=x_github_delivery,
        )
    ).parsed

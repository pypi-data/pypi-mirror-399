from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.repository_status import RepositoryStatus
from ...types import Response


def _get_kwargs(
    repository_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/repositories/{repository_id}".format(
            repository_id=quote(str(repository_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | RepositoryStatus | None:
    if response.status_code == 200:
        response_200 = RepositoryStatus.from_dict(response.json())

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
) -> Response[HTTPValidationError | RepositoryStatus]:
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
) -> Response[HTTPValidationError | RepositoryStatus]:
    """Get repository status

     Check the current indexing status of a repository.

    Args:
        repository_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | RepositoryStatus]
    """

    kwargs = _get_kwargs(
        repository_id=repository_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | RepositoryStatus | None:
    """Get repository status

     Check the current indexing status of a repository.

    Args:
        repository_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | RepositoryStatus
    """

    return sync_detailed(
        repository_id=repository_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    repository_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[HTTPValidationError | RepositoryStatus]:
    """Get repository status

     Check the current indexing status of a repository.

    Args:
        repository_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | RepositoryStatus]
    """

    kwargs = _get_kwargs(
        repository_id=repository_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | RepositoryStatus | None:
    """Get repository status

     Check the current indexing status of a repository.

    Args:
        repository_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | RepositoryStatus
    """

    return (
        await asyncio_detailed(
            repository_id=repository_id,
            client=client,
        )
    ).parsed

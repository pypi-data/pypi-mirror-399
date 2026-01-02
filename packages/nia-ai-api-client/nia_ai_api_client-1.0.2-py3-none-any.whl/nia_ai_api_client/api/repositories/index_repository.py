from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.index_repository_response_200 import IndexRepositoryResponse200
from ...models.repository_request import RepositoryRequest
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: RepositoryRequest,
    x_git_hub_token: str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_git_hub_token, Unset):
        headers["X-GitHub-Token"] = x_git_hub_token

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/repositories",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | IndexRepositoryResponse200 | None:
    if response.status_code == 200:
        response_200 = IndexRepositoryResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 429:
        response_429 = Error.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Error | IndexRepositoryResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: RepositoryRequest,
    x_git_hub_token: str | Unset = UNSET,
) -> Response[Error | IndexRepositoryResponse200]:
    r"""Index a new repository

     Start indexing a GitHub repository. The repository must be public or the request must include
    a GitHub token with appropriate access rights. Supports indexing specific folders within a
    repository
    by providing a path like \"owner/repo/tree/branch/folder\".

    Args:
        x_git_hub_token (str | Unset):
        body (RepositoryRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | IndexRepositoryResponse200]
    """

    kwargs = _get_kwargs(
        body=body,
        x_git_hub_token=x_git_hub_token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: RepositoryRequest,
    x_git_hub_token: str | Unset = UNSET,
) -> Error | IndexRepositoryResponse200 | None:
    r"""Index a new repository

     Start indexing a GitHub repository. The repository must be public or the request must include
    a GitHub token with appropriate access rights. Supports indexing specific folders within a
    repository
    by providing a path like \"owner/repo/tree/branch/folder\".

    Args:
        x_git_hub_token (str | Unset):
        body (RepositoryRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | IndexRepositoryResponse200
    """

    return sync_detailed(
        client=client,
        body=body,
        x_git_hub_token=x_git_hub_token,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: RepositoryRequest,
    x_git_hub_token: str | Unset = UNSET,
) -> Response[Error | IndexRepositoryResponse200]:
    r"""Index a new repository

     Start indexing a GitHub repository. The repository must be public or the request must include
    a GitHub token with appropriate access rights. Supports indexing specific folders within a
    repository
    by providing a path like \"owner/repo/tree/branch/folder\".

    Args:
        x_git_hub_token (str | Unset):
        body (RepositoryRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | IndexRepositoryResponse200]
    """

    kwargs = _get_kwargs(
        body=body,
        x_git_hub_token=x_git_hub_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: RepositoryRequest,
    x_git_hub_token: str | Unset = UNSET,
) -> Error | IndexRepositoryResponse200 | None:
    r"""Index a new repository

     Start indexing a GitHub repository. The repository must be public or the request must include
    a GitHub token with appropriate access rights. Supports indexing specific folders within a
    repository
    by providing a path like \"owner/repo/tree/branch/folder\".

    Args:
        x_git_hub_token (str | Unset):
        body (RepositoryRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | IndexRepositoryResponse200
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            x_git_hub_token=x_git_hub_token,
        )
    ).parsed

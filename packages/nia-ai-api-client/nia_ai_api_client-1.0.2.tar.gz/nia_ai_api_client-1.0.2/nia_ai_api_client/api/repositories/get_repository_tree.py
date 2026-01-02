from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.git_hub_tree_response import GitHubTreeResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository_id: str,
    *,
    branch: str | Unset = UNSET,
    include_paths: list[str] | Unset = UNSET,
    exclude_paths: list[str] | Unset = UNSET,
    file_extensions: list[str] | Unset = UNSET,
    exclude_extensions: list[str] | Unset = UNSET,
    show_full_paths: bool | Unset = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["branch"] = branch

    json_include_paths: list[str] | Unset = UNSET
    if not isinstance(include_paths, Unset):
        json_include_paths = include_paths

    params["include_paths"] = json_include_paths

    json_exclude_paths: list[str] | Unset = UNSET
    if not isinstance(exclude_paths, Unset):
        json_exclude_paths = exclude_paths

    params["exclude_paths"] = json_exclude_paths

    json_file_extensions: list[str] | Unset = UNSET
    if not isinstance(file_extensions, Unset):
        json_file_extensions = file_extensions

    params["file_extensions"] = json_file_extensions

    json_exclude_extensions: list[str] | Unset = UNSET
    if not isinstance(exclude_extensions, Unset):
        json_exclude_extensions = exclude_extensions

    params["exclude_extensions"] = json_exclude_extensions

    params["show_full_paths"] = show_full_paths

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/repositories/{repository_id}/tree".format(
            repository_id=quote(str(repository_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | GitHubTreeResponse | None:
    if response.status_code == 200:
        response_200 = GitHubTreeResponse.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())

        return response_404

    if response.status_code == 429:
        response_429 = Error.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Error | GitHubTreeResponse]:
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
    branch: str | Unset = UNSET,
    include_paths: list[str] | Unset = UNSET,
    exclude_paths: list[str] | Unset = UNSET,
    file_extensions: list[str] | Unset = UNSET,
    exclude_extensions: list[str] | Unset = UNSET,
    show_full_paths: bool | Unset = False,
) -> Response[Error | GitHubTreeResponse]:
    """Get repository tree structure

     Get the file and folder structure directly from GitHub API (no indexing required).
    This endpoint provides a fast way to explore repository structure with flexible filtering
    options for paths and file extensions.

    Args:
        repository_id (str):
        branch (str | Unset):
        include_paths (list[str] | Unset):
        exclude_paths (list[str] | Unset):
        file_extensions (list[str] | Unset):
        exclude_extensions (list[str] | Unset):
        show_full_paths (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | GitHubTreeResponse]
    """

    kwargs = _get_kwargs(
        repository_id=repository_id,
        branch=branch,
        include_paths=include_paths,
        exclude_paths=exclude_paths,
        file_extensions=file_extensions,
        exclude_extensions=exclude_extensions,
        show_full_paths=show_full_paths,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository_id: str,
    *,
    client: AuthenticatedClient | Client,
    branch: str | Unset = UNSET,
    include_paths: list[str] | Unset = UNSET,
    exclude_paths: list[str] | Unset = UNSET,
    file_extensions: list[str] | Unset = UNSET,
    exclude_extensions: list[str] | Unset = UNSET,
    show_full_paths: bool | Unset = False,
) -> Error | GitHubTreeResponse | None:
    """Get repository tree structure

     Get the file and folder structure directly from GitHub API (no indexing required).
    This endpoint provides a fast way to explore repository structure with flexible filtering
    options for paths and file extensions.

    Args:
        repository_id (str):
        branch (str | Unset):
        include_paths (list[str] | Unset):
        exclude_paths (list[str] | Unset):
        file_extensions (list[str] | Unset):
        exclude_extensions (list[str] | Unset):
        show_full_paths (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | GitHubTreeResponse
    """

    return sync_detailed(
        repository_id=repository_id,
        client=client,
        branch=branch,
        include_paths=include_paths,
        exclude_paths=exclude_paths,
        file_extensions=file_extensions,
        exclude_extensions=exclude_extensions,
        show_full_paths=show_full_paths,
    ).parsed


async def asyncio_detailed(
    repository_id: str,
    *,
    client: AuthenticatedClient | Client,
    branch: str | Unset = UNSET,
    include_paths: list[str] | Unset = UNSET,
    exclude_paths: list[str] | Unset = UNSET,
    file_extensions: list[str] | Unset = UNSET,
    exclude_extensions: list[str] | Unset = UNSET,
    show_full_paths: bool | Unset = False,
) -> Response[Error | GitHubTreeResponse]:
    """Get repository tree structure

     Get the file and folder structure directly from GitHub API (no indexing required).
    This endpoint provides a fast way to explore repository structure with flexible filtering
    options for paths and file extensions.

    Args:
        repository_id (str):
        branch (str | Unset):
        include_paths (list[str] | Unset):
        exclude_paths (list[str] | Unset):
        file_extensions (list[str] | Unset):
        exclude_extensions (list[str] | Unset):
        show_full_paths (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | GitHubTreeResponse]
    """

    kwargs = _get_kwargs(
        repository_id=repository_id,
        branch=branch,
        include_paths=include_paths,
        exclude_paths=exclude_paths,
        file_extensions=file_extensions,
        exclude_extensions=exclude_extensions,
        show_full_paths=show_full_paths,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository_id: str,
    *,
    client: AuthenticatedClient | Client,
    branch: str | Unset = UNSET,
    include_paths: list[str] | Unset = UNSET,
    exclude_paths: list[str] | Unset = UNSET,
    file_extensions: list[str] | Unset = UNSET,
    exclude_extensions: list[str] | Unset = UNSET,
    show_full_paths: bool | Unset = False,
) -> Error | GitHubTreeResponse | None:
    """Get repository tree structure

     Get the file and folder structure directly from GitHub API (no indexing required).
    This endpoint provides a fast way to explore repository structure with flexible filtering
    options for paths and file extensions.

    Args:
        repository_id (str):
        branch (str | Unset):
        include_paths (list[str] | Unset):
        exclude_paths (list[str] | Unset):
        file_extensions (list[str] | Unset):
        exclude_extensions (list[str] | Unset):
        show_full_paths (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | GitHubTreeResponse
    """

    return (
        await asyncio_detailed(
            repository_id=repository_id,
            client=client,
            branch=branch,
            include_paths=include_paths,
            exclude_paths=exclude_paths,
            file_extensions=file_extensions,
            exclude_extensions=exclude_extensions,
            show_full_paths=show_full_paths,
        )
    ).parsed

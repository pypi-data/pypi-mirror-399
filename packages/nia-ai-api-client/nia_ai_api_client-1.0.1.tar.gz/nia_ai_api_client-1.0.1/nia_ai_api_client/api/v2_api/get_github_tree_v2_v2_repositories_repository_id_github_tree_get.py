from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository_id: str,
    *,
    branch: None | str | Unset = UNSET,
    include_paths: None | str | Unset = UNSET,
    exclude_paths: None | str | Unset = UNSET,
    file_extensions: None | str | Unset = UNSET,
    exclude_extensions: None | str | Unset = UNSET,
    show_full_paths: bool | Unset = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_branch: None | str | Unset
    if isinstance(branch, Unset):
        json_branch = UNSET
    else:
        json_branch = branch
    params["branch"] = json_branch

    json_include_paths: None | str | Unset
    if isinstance(include_paths, Unset):
        json_include_paths = UNSET
    else:
        json_include_paths = include_paths
    params["include_paths"] = json_include_paths

    json_exclude_paths: None | str | Unset
    if isinstance(exclude_paths, Unset):
        json_exclude_paths = UNSET
    else:
        json_exclude_paths = exclude_paths
    params["exclude_paths"] = json_exclude_paths

    json_file_extensions: None | str | Unset
    if isinstance(file_extensions, Unset):
        json_file_extensions = UNSET
    else:
        json_file_extensions = file_extensions
    params["file_extensions"] = json_file_extensions

    json_exclude_extensions: None | str | Unset
    if isinstance(exclude_extensions, Unset):
        json_exclude_extensions = UNSET
    else:
        json_exclude_extensions = exclude_extensions
    params["exclude_extensions"] = json_exclude_extensions

    params["show_full_paths"] = show_full_paths

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/repositories/{repository_id}/github-tree".format(
            repository_id=quote(str(repository_id), safe=""),
        ),
        "params": params,
    }

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
    repository_id: str,
    *,
    client: AuthenticatedClient | Client,
    branch: None | str | Unset = UNSET,
    include_paths: None | str | Unset = UNSET,
    exclude_paths: None | str | Unset = UNSET,
    file_extensions: None | str | Unset = UNSET,
    exclude_extensions: None | str | Unset = UNSET,
    show_full_paths: bool | Unset = False,
) -> Response[Any | HTTPValidationError]:
    """Get Github Tree V2

     Get the file tree directly from GitHub Trees API. DEPRECATED: Use /tree instead.

    Args:
        repository_id (str):
        branch (None | str | Unset): Branch to get tree from
        include_paths (None | str | Unset): Comma-separated paths to include
        exclude_paths (None | str | Unset): Comma-separated paths to exclude
        file_extensions (None | str | Unset): Comma-separated extensions to include
        exclude_extensions (None | str | Unset): Comma-separated extensions to exclude
        show_full_paths (bool | Unset): Show full file paths Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
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
    branch: None | str | Unset = UNSET,
    include_paths: None | str | Unset = UNSET,
    exclude_paths: None | str | Unset = UNSET,
    file_extensions: None | str | Unset = UNSET,
    exclude_extensions: None | str | Unset = UNSET,
    show_full_paths: bool | Unset = False,
) -> Any | HTTPValidationError | None:
    """Get Github Tree V2

     Get the file tree directly from GitHub Trees API. DEPRECATED: Use /tree instead.

    Args:
        repository_id (str):
        branch (None | str | Unset): Branch to get tree from
        include_paths (None | str | Unset): Comma-separated paths to include
        exclude_paths (None | str | Unset): Comma-separated paths to exclude
        file_extensions (None | str | Unset): Comma-separated extensions to include
        exclude_extensions (None | str | Unset): Comma-separated extensions to exclude
        show_full_paths (bool | Unset): Show full file paths Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
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
    branch: None | str | Unset = UNSET,
    include_paths: None | str | Unset = UNSET,
    exclude_paths: None | str | Unset = UNSET,
    file_extensions: None | str | Unset = UNSET,
    exclude_extensions: None | str | Unset = UNSET,
    show_full_paths: bool | Unset = False,
) -> Response[Any | HTTPValidationError]:
    """Get Github Tree V2

     Get the file tree directly from GitHub Trees API. DEPRECATED: Use /tree instead.

    Args:
        repository_id (str):
        branch (None | str | Unset): Branch to get tree from
        include_paths (None | str | Unset): Comma-separated paths to include
        exclude_paths (None | str | Unset): Comma-separated paths to exclude
        file_extensions (None | str | Unset): Comma-separated extensions to include
        exclude_extensions (None | str | Unset): Comma-separated extensions to exclude
        show_full_paths (bool | Unset): Show full file paths Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
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
    branch: None | str | Unset = UNSET,
    include_paths: None | str | Unset = UNSET,
    exclude_paths: None | str | Unset = UNSET,
    file_extensions: None | str | Unset = UNSET,
    exclude_extensions: None | str | Unset = UNSET,
    show_full_paths: bool | Unset = False,
) -> Any | HTTPValidationError | None:
    """Get Github Tree V2

     Get the file tree directly from GitHub Trees API. DEPRECATED: Use /tree instead.

    Args:
        repository_id (str):
        branch (None | str | Unset): Branch to get tree from
        include_paths (None | str | Unset): Comma-separated paths to include
        exclude_paths (None | str | Unset): Comma-separated paths to exclude
        file_extensions (None | str | Unset): Comma-separated extensions to include
        exclude_extensions (None | str | Unset): Comma-separated extensions to exclude
        show_full_paths (bool | Unset): Show full file paths Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
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

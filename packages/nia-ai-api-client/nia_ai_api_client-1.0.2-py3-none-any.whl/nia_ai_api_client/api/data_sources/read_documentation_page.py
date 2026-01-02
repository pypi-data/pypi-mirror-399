from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.read_documentation_page_response_200 import ReadDocumentationPageResponse200
from ...types import UNSET, Response, Unset


def _get_kwargs(
    source_id: str,
    *,
    path: str,
    line_start: int | Unset = UNSET,
    line_end: int | Unset = UNSET,
    max_length: int | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["path"] = path

    params["line_start"] = line_start

    params["line_end"] = line_end

    params["max_length"] = max_length

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/data-sources/{source_id}/read".format(
            source_id=quote(str(source_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | ReadDocumentationPageResponse200 | None:
    if response.status_code == 200:
        response_200 = ReadDocumentationPageResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = Error.from_dict(response.json())

        return response_403

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
) -> Response[Error | ReadDocumentationPageResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    source_id: str,
    *,
    client: AuthenticatedClient | Client,
    path: str,
    line_start: int | Unset = UNSET,
    line_end: int | Unset = UNSET,
    max_length: int | Unset = UNSET,
) -> Response[Error | ReadDocumentationPageResponse200]:
    """Read documentation page content

     Read content of a documentation page by its virtual filesystem path.
    More intuitive than remembering URLs - just use the path from doc_tree or doc_ls.
    Supports line range slicing and length truncation for efficient content retrieval.

    Args:
        source_id (str):
        path (str):
        line_start (int | Unset):
        line_end (int | Unset):
        max_length (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | ReadDocumentationPageResponse200]
    """

    kwargs = _get_kwargs(
        source_id=source_id,
        path=path,
        line_start=line_start,
        line_end=line_end,
        max_length=max_length,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    source_id: str,
    *,
    client: AuthenticatedClient | Client,
    path: str,
    line_start: int | Unset = UNSET,
    line_end: int | Unset = UNSET,
    max_length: int | Unset = UNSET,
) -> Error | ReadDocumentationPageResponse200 | None:
    """Read documentation page content

     Read content of a documentation page by its virtual filesystem path.
    More intuitive than remembering URLs - just use the path from doc_tree or doc_ls.
    Supports line range slicing and length truncation for efficient content retrieval.

    Args:
        source_id (str):
        path (str):
        line_start (int | Unset):
        line_end (int | Unset):
        max_length (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | ReadDocumentationPageResponse200
    """

    return sync_detailed(
        source_id=source_id,
        client=client,
        path=path,
        line_start=line_start,
        line_end=line_end,
        max_length=max_length,
    ).parsed


async def asyncio_detailed(
    source_id: str,
    *,
    client: AuthenticatedClient | Client,
    path: str,
    line_start: int | Unset = UNSET,
    line_end: int | Unset = UNSET,
    max_length: int | Unset = UNSET,
) -> Response[Error | ReadDocumentationPageResponse200]:
    """Read documentation page content

     Read content of a documentation page by its virtual filesystem path.
    More intuitive than remembering URLs - just use the path from doc_tree or doc_ls.
    Supports line range slicing and length truncation for efficient content retrieval.

    Args:
        source_id (str):
        path (str):
        line_start (int | Unset):
        line_end (int | Unset):
        max_length (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | ReadDocumentationPageResponse200]
    """

    kwargs = _get_kwargs(
        source_id=source_id,
        path=path,
        line_start=line_start,
        line_end=line_end,
        max_length=max_length,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    source_id: str,
    *,
    client: AuthenticatedClient | Client,
    path: str,
    line_start: int | Unset = UNSET,
    line_end: int | Unset = UNSET,
    max_length: int | Unset = UNSET,
) -> Error | ReadDocumentationPageResponse200 | None:
    """Read documentation page content

     Read content of a documentation page by its virtual filesystem path.
    More intuitive than remembering URLs - just use the path from doc_tree or doc_ls.
    Supports line range slicing and length truncation for efficient content retrieval.

    Args:
        source_id (str):
        path (str):
        line_start (int | Unset):
        line_end (int | Unset):
        max_length (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | ReadDocumentationPageResponse200
    """

    return (
        await asyncio_detailed(
            source_id=source_id,
            client=client,
            path=path,
            line_start=line_start,
            line_end=line_end,
            max_length=max_length,
        )
    ).parsed

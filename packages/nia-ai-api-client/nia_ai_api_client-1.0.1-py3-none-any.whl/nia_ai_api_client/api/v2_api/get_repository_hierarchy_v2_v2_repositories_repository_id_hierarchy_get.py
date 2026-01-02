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
    include_classes: bool | Unset = True,
    include_methods: bool | Unset = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["include_classes"] = include_classes

    params["include_methods"] = include_methods

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/repositories/{repository_id}/hierarchy".format(
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
    include_classes: bool | Unset = True,
    include_methods: bool | Unset = False,
) -> Response[Any | HTTPValidationError]:
    """Get Repository Hierarchy V2

     Get the file hierarchy for a repository.

    Args:
        repository_id (str):
        include_classes (bool | Unset): Include class names Default: True.
        include_methods (bool | Unset): Include method names Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        repository_id=repository_id,
        include_classes=include_classes,
        include_methods=include_methods,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository_id: str,
    *,
    client: AuthenticatedClient | Client,
    include_classes: bool | Unset = True,
    include_methods: bool | Unset = False,
) -> Any | HTTPValidationError | None:
    """Get Repository Hierarchy V2

     Get the file hierarchy for a repository.

    Args:
        repository_id (str):
        include_classes (bool | Unset): Include class names Default: True.
        include_methods (bool | Unset): Include method names Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        repository_id=repository_id,
        client=client,
        include_classes=include_classes,
        include_methods=include_methods,
    ).parsed


async def asyncio_detailed(
    repository_id: str,
    *,
    client: AuthenticatedClient | Client,
    include_classes: bool | Unset = True,
    include_methods: bool | Unset = False,
) -> Response[Any | HTTPValidationError]:
    """Get Repository Hierarchy V2

     Get the file hierarchy for a repository.

    Args:
        repository_id (str):
        include_classes (bool | Unset): Include class names Default: True.
        include_methods (bool | Unset): Include method names Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        repository_id=repository_id,
        include_classes=include_classes,
        include_methods=include_methods,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository_id: str,
    *,
    client: AuthenticatedClient | Client,
    include_classes: bool | Unset = True,
    include_methods: bool | Unset = False,
) -> Any | HTTPValidationError | None:
    """Get Repository Hierarchy V2

     Get the file hierarchy for a repository.

    Args:
        repository_id (str):
        include_classes (bool | Unset): Include class names Default: True.
        include_methods (bool | Unset): Include method names Default: False.

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
            include_classes=include_classes,
            include_methods=include_methods,
        )
    ).parsed

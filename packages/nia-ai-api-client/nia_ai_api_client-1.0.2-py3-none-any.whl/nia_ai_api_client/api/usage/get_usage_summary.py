from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.usage_summary_response import UsageSummaryResponse
from ...types import Response


def _get_kwargs() -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/usage",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | UsageSummaryResponse | None:
    if response.status_code == 200:
        response_200 = UsageSummaryResponse.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 500:
        response_500 = Error.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Error | UsageSummaryResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[Error | UsageSummaryResponse]:
    """Get usage summary

     Get the current user's usage summary for the current billing period.

    Returns usage counts and limits for all metered operations including:
    - **queries**: Search, grep, doc_read, read_source_content operations
    - **deep_research**: Deep research agent usage
    - **web_search**: Web search operations
    - **package_search**: Package source code search
    - **oracle**: Oracle research agent usage
    - **contexts**: Context sharing operations
    - **indexing**: Repository and documentation indexing

    Free tier users have monthly limits on certain operations.
    Pro users have unlimited usage for most operations.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | UsageSummaryResponse]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
) -> Error | UsageSummaryResponse | None:
    """Get usage summary

     Get the current user's usage summary for the current billing period.

    Returns usage counts and limits for all metered operations including:
    - **queries**: Search, grep, doc_read, read_source_content operations
    - **deep_research**: Deep research agent usage
    - **web_search**: Web search operations
    - **package_search**: Package source code search
    - **oracle**: Oracle research agent usage
    - **contexts**: Context sharing operations
    - **indexing**: Repository and documentation indexing

    Free tier users have monthly limits on certain operations.
    Pro users have unlimited usage for most operations.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | UsageSummaryResponse
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[Error | UsageSummaryResponse]:
    """Get usage summary

     Get the current user's usage summary for the current billing period.

    Returns usage counts and limits for all metered operations including:
    - **queries**: Search, grep, doc_read, read_source_content operations
    - **deep_research**: Deep research agent usage
    - **web_search**: Web search operations
    - **package_search**: Package source code search
    - **oracle**: Oracle research agent usage
    - **contexts**: Context sharing operations
    - **indexing**: Repository and documentation indexing

    Free tier users have monthly limits on certain operations.
    Pro users have unlimited usage for most operations.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | UsageSummaryResponse]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
) -> Error | UsageSummaryResponse | None:
    """Get usage summary

     Get the current user's usage summary for the current billing period.

    Returns usage counts and limits for all metered operations including:
    - **queries**: Search, grep, doc_read, read_source_content operations
    - **deep_research**: Deep research agent usage
    - **web_search**: Web search operations
    - **package_search**: Package source code search
    - **oracle**: Oracle research agent usage
    - **contexts**: Context sharing operations
    - **indexing**: Repository and documentation indexing

    Free tier users have monthly limits on certain operations.
    Pro users have unlimited usage for most operations.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | UsageSummaryResponse
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed

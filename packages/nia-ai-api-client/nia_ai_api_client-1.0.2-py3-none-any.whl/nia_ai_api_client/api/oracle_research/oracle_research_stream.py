from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.oracle_research_request import OracleResearchRequest
from ...types import Response


def _get_kwargs(
    *,
    body: OracleResearchRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/oracle/stream",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Error | str | None:
    if response.status_code == 200:
        response_200 = response.text
        return response_200

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = Error.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = Error.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Error | str]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: OracleResearchRequest,
) -> Response[Error | str]:
    """Oracle research with real-time streaming (Pro only)

     Execute Oracle research with Server-Sent Events (SSE) streaming for real-time progress updates.

    This endpoint streams research progress including:
    - **iteration_start**: New research iteration beginning
    - **tool_start**: Tool execution starting with action name and reason
    - **tool_complete**: Tool finished with success/failure status
    - **generating_report**: Final report synthesis starting
    - **complete**: Research finished with full result
    - **heartbeat**: Connection keep-alive (every 0.5s during idle)
    - **error**: Error occurred during research

    The Oracle agent uses extended thinking and has access to all tools including
    web search, code search, documentation search, and the doc filesystem tools
    (doc_tree, doc_ls, doc_read, doc_grep).

    Args:
        body (OracleResearchRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | str]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: OracleResearchRequest,
) -> Error | str | None:
    """Oracle research with real-time streaming (Pro only)

     Execute Oracle research with Server-Sent Events (SSE) streaming for real-time progress updates.

    This endpoint streams research progress including:
    - **iteration_start**: New research iteration beginning
    - **tool_start**: Tool execution starting with action name and reason
    - **tool_complete**: Tool finished with success/failure status
    - **generating_report**: Final report synthesis starting
    - **complete**: Research finished with full result
    - **heartbeat**: Connection keep-alive (every 0.5s during idle)
    - **error**: Error occurred during research

    The Oracle agent uses extended thinking and has access to all tools including
    web search, code search, documentation search, and the doc filesystem tools
    (doc_tree, doc_ls, doc_read, doc_grep).

    Args:
        body (OracleResearchRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | str
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: OracleResearchRequest,
) -> Response[Error | str]:
    """Oracle research with real-time streaming (Pro only)

     Execute Oracle research with Server-Sent Events (SSE) streaming for real-time progress updates.

    This endpoint streams research progress including:
    - **iteration_start**: New research iteration beginning
    - **tool_start**: Tool execution starting with action name and reason
    - **tool_complete**: Tool finished with success/failure status
    - **generating_report**: Final report synthesis starting
    - **complete**: Research finished with full result
    - **heartbeat**: Connection keep-alive (every 0.5s during idle)
    - **error**: Error occurred during research

    The Oracle agent uses extended thinking and has access to all tools including
    web search, code search, documentation search, and the doc filesystem tools
    (doc_tree, doc_ls, doc_read, doc_grep).

    Args:
        body (OracleResearchRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | str]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: OracleResearchRequest,
) -> Error | str | None:
    """Oracle research with real-time streaming (Pro only)

     Execute Oracle research with Server-Sent Events (SSE) streaming for real-time progress updates.

    This endpoint streams research progress including:
    - **iteration_start**: New research iteration beginning
    - **tool_start**: Tool execution starting with action name and reason
    - **tool_complete**: Tool finished with success/failure status
    - **generating_report**: Final report synthesis starting
    - **complete**: Research finished with full result
    - **heartbeat**: Connection keep-alive (every 0.5s during idle)
    - **error**: Error occurred during research

    The Oracle agent uses extended thinking and has access to all tools including
    web search, code search, documentation search, and the doc filesystem tools
    (doc_tree, doc_ls, doc_read, doc_grep).

    Args:
        body (OracleResearchRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | str
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed

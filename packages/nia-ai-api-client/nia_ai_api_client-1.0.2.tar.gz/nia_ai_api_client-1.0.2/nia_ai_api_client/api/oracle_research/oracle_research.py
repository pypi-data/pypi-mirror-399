from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.oracle_research_request import OracleResearchRequest
from ...models.oracle_research_response import OracleResearchResponse
from ...types import Response


def _get_kwargs(
    *,
    body: OracleResearchRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/oracle",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | OracleResearchResponse | None:
    if response.status_code == 200:
        response_200 = OracleResearchResponse.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = Error.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = Error.from_dict(response.json())

        return response_429

    if response.status_code == 500:
        response_500 = Error.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Error | OracleResearchResponse]:
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
) -> Response[Error | OracleResearchResponse]:
    """Oracle autonomous research agent (Pro only)

     Execute comprehensive Oracle research using the full autonomous agent with extended thinking.

    The Oracle agent uses extended thinking capabilities to plan and execute multi-step
    research autonomously. It has access to a diverse set of tools including:
    - **Discovery**: list_repositories, list_documentation
    - **Web Research**: run_web_search, web_fetch (server-side)
    - **Code Search**: run_indexed_repo_search, code_grep, get_github_tree, read_source_content
    - **Documentation**: run_doc_search, doc_tree, doc_ls, doc_read, doc_grep

    The agent will iteratively search and analyze your indexed repositories and documentation,
    perform web searches for external context, and synthesize findings into a comprehensive report.

    **Note**: This is a long-running operation (typically 30-180 seconds). For real-time progress
    updates, use the streaming endpoint `/oracle/stream` instead.

    Args:
        body (OracleResearchRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | OracleResearchResponse]
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
) -> Error | OracleResearchResponse | None:
    """Oracle autonomous research agent (Pro only)

     Execute comprehensive Oracle research using the full autonomous agent with extended thinking.

    The Oracle agent uses extended thinking capabilities to plan and execute multi-step
    research autonomously. It has access to a diverse set of tools including:
    - **Discovery**: list_repositories, list_documentation
    - **Web Research**: run_web_search, web_fetch (server-side)
    - **Code Search**: run_indexed_repo_search, code_grep, get_github_tree, read_source_content
    - **Documentation**: run_doc_search, doc_tree, doc_ls, doc_read, doc_grep

    The agent will iteratively search and analyze your indexed repositories and documentation,
    perform web searches for external context, and synthesize findings into a comprehensive report.

    **Note**: This is a long-running operation (typically 30-180 seconds). For real-time progress
    updates, use the streaming endpoint `/oracle/stream` instead.

    Args:
        body (OracleResearchRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | OracleResearchResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: OracleResearchRequest,
) -> Response[Error | OracleResearchResponse]:
    """Oracle autonomous research agent (Pro only)

     Execute comprehensive Oracle research using the full autonomous agent with extended thinking.

    The Oracle agent uses extended thinking capabilities to plan and execute multi-step
    research autonomously. It has access to a diverse set of tools including:
    - **Discovery**: list_repositories, list_documentation
    - **Web Research**: run_web_search, web_fetch (server-side)
    - **Code Search**: run_indexed_repo_search, code_grep, get_github_tree, read_source_content
    - **Documentation**: run_doc_search, doc_tree, doc_ls, doc_read, doc_grep

    The agent will iteratively search and analyze your indexed repositories and documentation,
    perform web searches for external context, and synthesize findings into a comprehensive report.

    **Note**: This is a long-running operation (typically 30-180 seconds). For real-time progress
    updates, use the streaming endpoint `/oracle/stream` instead.

    Args:
        body (OracleResearchRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | OracleResearchResponse]
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
) -> Error | OracleResearchResponse | None:
    """Oracle autonomous research agent (Pro only)

     Execute comprehensive Oracle research using the full autonomous agent with extended thinking.

    The Oracle agent uses extended thinking capabilities to plan and execute multi-step
    research autonomously. It has access to a diverse set of tools including:
    - **Discovery**: list_repositories, list_documentation
    - **Web Research**: run_web_search, web_fetch (server-side)
    - **Code Search**: run_indexed_repo_search, code_grep, get_github_tree, read_source_content
    - **Documentation**: run_doc_search, doc_tree, doc_ls, doc_read, doc_grep

    The agent will iteratively search and analyze your indexed repositories and documentation,
    perform web searches for external context, and synthesize findings into a comprehensive report.

    **Note**: This is a long-running operation (typically 30-180 seconds). For real-time progress
    updates, use the streaming endpoint `/oracle/stream` instead.

    Args:
        body (OracleResearchRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | OracleResearchResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed

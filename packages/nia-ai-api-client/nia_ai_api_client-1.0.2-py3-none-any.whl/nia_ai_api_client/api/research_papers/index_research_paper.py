from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.research_paper_request import ResearchPaperRequest
from ...models.research_paper_response import ResearchPaperResponse
from ...types import Response


def _get_kwargs(
    *,
    body: ResearchPaperRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/research-papers",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | ResearchPaperResponse | None:
    if response.status_code == 200:
        response_200 = ResearchPaperResponse.from_dict(response.json())

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

    if response.status_code == 500:
        response_500 = Error.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Error | ResearchPaperResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ResearchPaperRequest,
) -> Response[Error | ResearchPaperResponse]:
    """Index a research paper

     Index a research paper from arXiv. The paper's PDF is extracted,
    enriched with metadata from the arXiv API (title, authors, abstract, categories),
    and indexed into the vector store for semantic search.

    Supports multiple input formats:
    - Full arXiv URL: https://arxiv.org/abs/2312.00752
    - PDF URL: https://arxiv.org/pdf/2312.00752.pdf
    - Raw new-format ID: 2312.00752
    - Raw old-format ID: hep-th/9901001
    - With version: 2312.00752v1

    Papers are globally deduplicated - if another user has already indexed a paper,
    you'll get instant access to the existing index.

    Args:
        body (ResearchPaperRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | ResearchPaperResponse]
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
    body: ResearchPaperRequest,
) -> Error | ResearchPaperResponse | None:
    """Index a research paper

     Index a research paper from arXiv. The paper's PDF is extracted,
    enriched with metadata from the arXiv API (title, authors, abstract, categories),
    and indexed into the vector store for semantic search.

    Supports multiple input formats:
    - Full arXiv URL: https://arxiv.org/abs/2312.00752
    - PDF URL: https://arxiv.org/pdf/2312.00752.pdf
    - Raw new-format ID: 2312.00752
    - Raw old-format ID: hep-th/9901001
    - With version: 2312.00752v1

    Papers are globally deduplicated - if another user has already indexed a paper,
    you'll get instant access to the existing index.

    Args:
        body (ResearchPaperRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | ResearchPaperResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ResearchPaperRequest,
) -> Response[Error | ResearchPaperResponse]:
    """Index a research paper

     Index a research paper from arXiv. The paper's PDF is extracted,
    enriched with metadata from the arXiv API (title, authors, abstract, categories),
    and indexed into the vector store for semantic search.

    Supports multiple input formats:
    - Full arXiv URL: https://arxiv.org/abs/2312.00752
    - PDF URL: https://arxiv.org/pdf/2312.00752.pdf
    - Raw new-format ID: 2312.00752
    - Raw old-format ID: hep-th/9901001
    - With version: 2312.00752v1

    Papers are globally deduplicated - if another user has already indexed a paper,
    you'll get instant access to the existing index.

    Args:
        body (ResearchPaperRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | ResearchPaperResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: ResearchPaperRequest,
) -> Error | ResearchPaperResponse | None:
    """Index a research paper

     Index a research paper from arXiv. The paper's PDF is extracted,
    enriched with metadata from the arXiv API (title, authors, abstract, categories),
    and indexed into the vector store for semantic search.

    Supports multiple input formats:
    - Full arXiv URL: https://arxiv.org/abs/2312.00752
    - PDF URL: https://arxiv.org/pdf/2312.00752.pdf
    - Raw new-format ID: 2312.00752
    - Raw old-format ID: hep-th/9901001
    - With version: 2312.00752v1

    Papers are globally deduplicated - if another user has already indexed a paper,
    you'll get instant access to the existing index.

    Args:
        body (ResearchPaperRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | ResearchPaperResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed

from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.deep_research_request import DeepResearchRequest
from ...models.deep_research_response import DeepResearchResponse
from ...models.error import Error
from ...types import Response


def _get_kwargs(
    *,
    body: DeepResearchRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/search/deep",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DeepResearchResponse | Error | None:
    if response.status_code == 200:
        response_200 = DeepResearchResponse.from_dict(response.json())

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

    if response.status_code == 503:
        response_503 = Error.from_dict(response.json())

        return response_503

    if response.status_code == 504:
        response_504 = Error.from_dict(response.json())

        return response_504

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[DeepResearchResponse | Error]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: DeepResearchRequest,
) -> Response[DeepResearchResponse | Error]:
    """Deep research agent (Pro only)

     Perform deep, multi-step research on a topic using advanced AI research capabilities.
    This endpoint is only available for Pro subscription users. The research agent will
    analyze multiple sources, synthesize information, and provide comprehensive answers
    with citations.

    Args:
        body (DeepResearchRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeepResearchResponse | Error]
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
    body: DeepResearchRequest,
) -> DeepResearchResponse | Error | None:
    """Deep research agent (Pro only)

     Perform deep, multi-step research on a topic using advanced AI research capabilities.
    This endpoint is only available for Pro subscription users. The research agent will
    analyze multiple sources, synthesize information, and provide comprehensive answers
    with citations.

    Args:
        body (DeepResearchRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeepResearchResponse | Error
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: DeepResearchRequest,
) -> Response[DeepResearchResponse | Error]:
    """Deep research agent (Pro only)

     Perform deep, multi-step research on a topic using advanced AI research capabilities.
    This endpoint is only available for Pro subscription users. The research agent will
    analyze multiple sources, synthesize information, and provide comprehensive answers
    with citations.

    Args:
        body (DeepResearchRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeepResearchResponse | Error]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: DeepResearchRequest,
) -> DeepResearchResponse | Error | None:
    """Deep research agent (Pro only)

     Perform deep, multi-step research on a topic using advanced AI research capabilities.
    This endpoint is only available for Pro subscription users. The research agent will
    analyze multiple sources, synthesize information, and provide comprehensive answers
    with citations.

    Args:
        body (DeepResearchRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeepResearchResponse | Error
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed

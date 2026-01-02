from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_oracle_job_response_200 import CreateOracleJobResponse200
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
        "url": "/oracle/jobs",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CreateOracleJobResponse200 | Error | None:
    if response.status_code == 200:
        response_200 = CreateOracleJobResponse200.from_dict(response.json())

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

    if response.status_code == 500:
        response_500 = Error.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[CreateOracleJobResponse200 | Error]:
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
) -> Response[CreateOracleJobResponse200 | Error]:
    """Create Oracle research job (Pro only)

     Create a new Oracle research job that runs asynchronously.

    This is the recommended way to run Oracle research as it:
    - Queues jobs for reliable execution
    - Supports concurrency limits per user
    - Enables reconnection to running jobs
    - Provides job status tracking and history

    After creating a job, subscribe to `/oracle/jobs/{job_id}/stream` for real-time progress.

    Args:
        body (OracleResearchRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateOracleJobResponse200 | Error]
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
) -> CreateOracleJobResponse200 | Error | None:
    """Create Oracle research job (Pro only)

     Create a new Oracle research job that runs asynchronously.

    This is the recommended way to run Oracle research as it:
    - Queues jobs for reliable execution
    - Supports concurrency limits per user
    - Enables reconnection to running jobs
    - Provides job status tracking and history

    After creating a job, subscribe to `/oracle/jobs/{job_id}/stream` for real-time progress.

    Args:
        body (OracleResearchRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateOracleJobResponse200 | Error
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: OracleResearchRequest,
) -> Response[CreateOracleJobResponse200 | Error]:
    """Create Oracle research job (Pro only)

     Create a new Oracle research job that runs asynchronously.

    This is the recommended way to run Oracle research as it:
    - Queues jobs for reliable execution
    - Supports concurrency limits per user
    - Enables reconnection to running jobs
    - Provides job status tracking and history

    After creating a job, subscribe to `/oracle/jobs/{job_id}/stream` for real-time progress.

    Args:
        body (OracleResearchRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateOracleJobResponse200 | Error]
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
) -> CreateOracleJobResponse200 | Error | None:
    """Create Oracle research job (Pro only)

     Create a new Oracle research job that runs asynchronously.

    This is the recommended way to run Oracle research as it:
    - Queues jobs for reliable execution
    - Supports concurrency limits per user
    - Enables reconnection to running jobs
    - Provides job status tracking and history

    After creating a job, subscribe to `/oracle/jobs/{job_id}/stream` for real-time progress.

    Args:
        body (OracleResearchRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateOracleJobResponse200 | Error
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed

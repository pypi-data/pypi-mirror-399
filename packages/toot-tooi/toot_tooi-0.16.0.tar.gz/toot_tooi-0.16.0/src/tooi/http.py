import logging
import time
from functools import cache
from types import SimpleNamespace
from typing import Optional, Tuple, Unpack

import aiohttp
from aiohttp import ClientResponse
from aiohttp.client import _RequestOptions  # type: ignore

from tooi import USER_AGENT

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Represents an error response from the API."""

    def __init__(self, message: str | None = None, cause: Exception | None = None):
        assert message or cause
        self.message = message or str(cause)
        self.cause = cause
        super().__init__(self.message)


class ResponseError(APIError):
    """Raised when the API returns a response with status code >= 400."""

    def __init__(self, status_code: int, error: str | None, description: str | None):
        self.status_code = status_code
        self.error = error
        self.description = description

        msg = f"HTTP {status_code}"
        msg += f". Error: {error}" if error else ""
        msg += f". Description: {description}" if description else ""
        super().__init__(msg)


def create_client_session(
    base_url: str | None = None,
    access_token: str | None = None,
):
    headers = {"User-Agent": USER_AGENT}

    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    return aiohttp.ClientSession(
        base_url=base_url,
        trace_configs=[logger_trace_config()],
        headers=headers,
    )


@cache
def get_session():
    """Returns an authenticated session to interact with the logged in instance"""
    from tooi.credentials import get_active_credentials

    application, account = get_active_credentials()
    return create_client_session(application.base_url, account.access_token)


async def close_session():
    session = get_session()
    await session.close()
    get_session.cache_clear()


async def request(method: str, url: str, **kwargs: Unpack[_RequestOptions]) -> ClientResponse:
    session = get_session()

    try:
        async with session.request(method, url, **kwargs) as response:
            if response.ok:
                await response.read()
                return response
            else:
                error, description = await get_error(response)
                raise ResponseError(response.status, error, description)
    except aiohttp.ClientError as exc:
        logger.error(f"<-- {method} {url} Exception: {str(exc)}")
        logger.exception(exc)
        raise APIError(cause=exc)


async def anon_request(method: str, url: str, **kwargs: Unpack[_RequestOptions]) -> ClientResponse:
    try:
        async with create_client_session() as session:
            async with session.request(method, url, **kwargs) as response:
                if response.ok:
                    await response.read()
                    return response
                else:
                    error, description = await get_error(response)
                    raise ResponseError(response.status, error, description)
    except aiohttp.ClientError as exc:
        logger.error(f"<-- {method} {url} Exception: {str(exc)}")
        logger.exception(exc)
        raise APIError(cause=exc)


async def get_error(response: ClientResponse) -> Tuple[Optional[str], Optional[str]]:
    """Attempt to extract the error and error description from response body.

    See: https://docs.joinmastodon.org/entities/error/
    """
    try:
        data = await response.json()
        return data.get("error"), data.get("error_description")
    except Exception:
        return None, None


def logger_trace_config() -> aiohttp.TraceConfig:
    async def on_request_start(
        _: aiohttp.ClientSession,
        context: SimpleNamespace,
        params: aiohttp.TraceRequestStartParams,
    ):
        context.start = time.monotonic()
        logger.info(f"--> {params.method} {params.url}")

    async def on_request_end(
        _: aiohttp.ClientSession,
        context: SimpleNamespace,
        params: aiohttp.TraceRequestEndParams,
    ):
        elapsed = round(1000 * (time.monotonic() - context.start))
        logger.info(f"<-- {params.method} {params.url} HTTP {params.response.status} {elapsed}ms")

    trace_config = aiohttp.TraceConfig()
    trace_config.on_request_start.append(on_request_start)
    trace_config.on_request_end.append(on_request_end)
    return trace_config

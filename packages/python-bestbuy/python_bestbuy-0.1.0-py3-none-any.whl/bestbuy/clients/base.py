import abc
import logging
from types import TracebackType
from typing import Any, Dict, List, Type

import httpx
from pydantic import ValidationError

from ..configs import BaseConfig
from ..exceptions import ConfigError
from ..loggers import make_console_logger
from ..utils import check_for_json_errors, check_for_xml_errors

from ..typing import SyncAsync


class BaseClient:
    config_parser: Type[BaseConfig]

    def __init__(
        self,
        client: httpx.Client | httpx.AsyncClient,
        options: Dict[str, Any] | BaseConfig | None = None,
        **kwargs: Any,
    ) -> None:
        try:
            if options is None:
                options = self.config_parser(**kwargs)
            elif isinstance(options, dict):
                options = self.config_parser(**options)
        except ValidationError as e:
            errors = []
            for error in e.errors():
                field = ".".join(str(loc) for loc in error["loc"])
                msg = error["msg"]
                errors.append(f"{field}: {msg}")
            raise ConfigError(
                "Configuration validation failed:\n  - " + "\n  - ".join(errors)
            ) from e
        self.options = options
        self.logger = self.options.logger or make_console_logger()
        self.logger.setLevel(self.options.log_level)
        self._clients: List[httpx.Client | httpx.AsyncClient] = []
        self.client = client

    @property
    def base_url(self):
        return self.options.base_url

    @property
    def client(self) -> httpx.Client | httpx.AsyncClient:
        return self._clients[-1]

    @client.setter
    def client(self, client: httpx.Client | httpx.AsyncClient) -> None:
        client.base_url = httpx.URL(self.base_url)
        client.timeout = httpx.Timeout(timeout=self.options.timeout_ms / 1_000)
        headers: Dict[str, str] = {"X-API-KEY": self.options.api_key}
        if self.options.content_type:
            headers["Content-Type"] = self.options.content_type
        client.headers = httpx.Headers(headers)
        self._clients.append(client)

    @abc.abstractmethod
    def request(self, request: httpx.Request) -> SyncAsync[httpx.Response]:
        raise NotImplementedError


class Client(BaseClient):
    client: httpx.Client

    def __init__(
        self,
        client: httpx.Client | None = None,
        options: Dict[str, Any] | BaseConfig | None = None,
        **kwargs: Any,
    ) -> None:
        if client is None:
            client = httpx.Client()
        super().__init__(client, options, **kwargs)

    def __enter__(self) -> "Client":
        self.client = httpx.Client()
        self.client.__enter__()
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        traceback: TracebackType,
    ) -> None:
        self.client.__exit__(exc_type, exc_value, traceback)
        del self._clients[-1]

    def close(self) -> None:
        self.client.close()

    def request(self, request: httpx.Request) -> httpx.Response:
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(
                f"Request: {request.method} {request.url}\n"
                f"Headers: {dict(request.headers)}\n"
                f"Body: {request.content.decode('utf-8') if request.content else None}"
            )
        response = self.client.send(request)
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(
                f"Response: {response.status_code} {response.reason_phrase}\n"
                f"Headers: {dict(response.headers)}\n"
                f"Body: {response.text}"
            )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            content_type = e.response.headers.get("content-type", "")
            if "xml" in content_type:
                check_for_xml_errors(e.response.text)
            elif "json" in content_type:
                check_for_json_errors(e.response.text)
            raise
        return response


class AsyncClient(BaseClient):
    client: httpx.AsyncClient

    def __init__(
        self,
        client: httpx.AsyncClient | None = None,
        options: Dict[str, Any] | BaseConfig | None = None,
        **kwargs: Any,
    ) -> None:
        if client is None:
            client = httpx.AsyncClient()
        super().__init__(client, options, **kwargs)

    async def __aenter__(self) -> "AsyncClient":
        self.client = httpx.AsyncClient()
        await self.client.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        traceback: TracebackType,
    ) -> None:
        await self.client.__aexit__(exc_type, exc_value, traceback)
        del self._clients[-1]

    async def aclose(self) -> None:
        await self.client.aclose()

    async def request(self, request: httpx.Request) -> httpx.Response:
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(
                f"Request: {request.method} {request.url}\n"
                f"Headers: {dict(request.headers)}\n"
                f"Body: {request.content.decode('utf-8') if request.content else None}"
            )
        response = await self.client.send(request)
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(
                f"Response: {response.status_code} {response.reason_phrase}\n"
                f"Headers: {dict(response.headers)}\n"
                f"Body: {response.text}"
            )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            content_type = e.response.headers.get("content-type", "")
            if "xml" in content_type:
                check_for_xml_errors(e.response.text)
            elif "json" in content_type:
                check_for_json_errors(e.response.text)
            raise
        return response

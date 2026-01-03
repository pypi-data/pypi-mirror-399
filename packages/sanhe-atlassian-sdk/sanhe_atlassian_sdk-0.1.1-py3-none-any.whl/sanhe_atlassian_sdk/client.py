# -*- coding: utf-8 -*-

"""
Atlassian REST API client with sync and async HTTP support.
"""

import typing as T
from functools import cached_property

import httpx
from pydantic import BaseModel, Field

T_KWARGS = dict[str, T.Any]
T_RESPONSE = T_KWARGS


def _get_site_url(url: str) -> str:
    """
    Convert any of these url to https://mycompany.atlassian.net

    - https://mycompany.atlassian.net/wiki/spaces/SPACEKEY/...
    - https://mycompany.atlassian.net/jira/core/projects/PROJECTKEY/board/...
    """
    parts = url.split("/")
    return "/".join(parts[:3])


class Atlassian(BaseModel):
    """
    Atlassian API client supporting both synchronous and asynchronous requests.
    """

    url: str = Field()
    username: str = Field()
    password: str = Field()
    sync_client_kwargs: T_KWARGS = Field(default_factory=dict)
    async_client_kwargs: T_KWARGS = Field(default_factory=dict)

    def model_post_init(self, context):
        self.url = _get_site_url(self.url)

    @property
    def default_headers(self) -> T.Dict[str, T.Any]:
        """Return default HTTP headers for JSON requests."""
        return {"Content-Type": "application/json"}

    @property
    def default_http_basic_auth(self) -> "httpx.BasicAuth":
        """Return HTTP basic auth credentials."""
        return httpx.BasicAuth(username=self.username, password=self.password)

    @property
    def default_client_kwargs(self) -> T_KWARGS:
        """Return default kwargs for HTTP client initialization."""
        return {
            "auth": self.default_http_basic_auth,
            "headers": self.default_headers,
        }

    @cached_property
    def sync_client(self) -> "httpx.Client":
        """Return a cached synchronous HTTP client."""
        sync_client_kwargs = self.default_client_kwargs
        sync_client_kwargs.update(self.sync_client_kwargs)
        return httpx.Client(**sync_client_kwargs)

    @cached_property
    def async_client(self) -> "httpx.AsyncClient":
        """Return a cached asynchronous HTTP client."""
        async_client_kwargs = self.default_client_kwargs
        async_client_kwargs.update(self.async_client_kwargs)
        return httpx.AsyncClient(**async_client_kwargs)

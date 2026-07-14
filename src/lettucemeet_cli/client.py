"""GraphQL API client for LettuceMeet."""

from __future__ import annotations

from typing import Any, Optional

import requests

from lettucemeet_cli.config import GRAPHQL_ENDPOINT, load_token


class LettuceMeetError(Exception):
    """Raised when the LettuceMeet API returns an error."""


class GraphQLClient:
    """Low-level GraphQL client for the LettuceMeet API."""

    def __init__(self, token: Optional[str] = None) -> None:
        self.token = token or load_token()
        self._session = requests.Session()

    @property
    def authenticated(self) -> bool:
        return self.token is not None

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def execute(
        self,
        query: str,
        variables: Optional[dict] = None,
        operation_name: Optional[str] = None,
    ) -> dict[str, Any]:
        """Execute a GraphQL query or mutation and return the data dict."""
        payload: dict[str, Any] = {"query": query}
        if variables:
            payload["variables"] = variables
        if operation_name:
            payload["operationName"] = operation_name

        resp = self._session.post(
            GRAPHQL_ENDPOINT,
            headers=self._headers(),
            json=payload,
        )

        if resp.status_code != 200:
            raise LettuceMeetError(
                f"HTTP {resp.status_code}: {resp.text[:200]}"
            )

        body = resp.json()

        if "errors" in body:
            msgs = [e.get("message", "Unknown error") for e in body["errors"]]
            raise LettuceMeetError("; ".join(msgs))

        return body.get("data", {})

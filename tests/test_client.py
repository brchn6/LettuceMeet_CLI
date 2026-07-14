"""Tests for GraphQL client."""
import json
import pytest
import requests_mock
from lettucemeet_cli.client import GraphQLClient, LettuceMeetError
from lettucemeet_cli.config import GRAPHQL_ENDPOINT


@pytest.fixture
def client():
    return GraphQLClient(token="test-token-123")


@pytest.fixture
def no_session(session_file):
    """Ensure no token file exists for tests that expect no token."""
    # session_file is already empty from conftest
    pass


class TestGraphQLClient:
    def test_init_with_token(self):
        c = GraphQLClient("my-token")
        assert c.token == "my-token"

    def test_init_no_token(self, no_session):
        c = GraphQLClient()
        assert c.token is None
        assert not c.authenticated

    def test_authenticated_true_with_token(self, client):
        assert client.authenticated

    def test_headers_with_token(self, client):
        headers = client._headers()
        assert headers["Authorization"] == "Bearer test-token-123"
        assert headers["Content-Type"] == "application/json"

    def test_headers_without_token(self, no_session):
        c = GraphQLClient()
        headers = c._headers()
        assert "Authorization" not in headers

    def test_execute_success(self, client):
        with requests_mock.Mocker() as m:
            m.post(GRAPHQL_ENDPOINT, json={"data": {"event": {"id": "ABC"}}})
            result = client.execute("query { event(id: \"ABC\") { id } }")
            assert result == {"event": {"id": "ABC"}}

    def test_execute_returns_errors(self, client):
        with requests_mock.Mocker() as m:
            m.post(GRAPHQL_ENDPOINT, json={"errors": [{"message": "Not found"}]})
            with pytest.raises(LettuceMeetError, match="Not found"):
                client.execute("query { event(id: \"X\") { id } }")

    def test_execute_http_error(self, client):
        with requests_mock.Mocker() as m:
            m.post(GRAPHQL_ENDPOINT, status_code=401, json={"message": "Unauthorized"})
            with pytest.raises(LettuceMeetError, match="401"):
                client.execute("query { event(id: \"X\") { id } }")

    def test_execute_sends_operation_name(self, client):
        with requests_mock.Mocker() as m:
            m.post(GRAPHQL_ENDPOINT, json={"data": {"ok": True}})
            client.execute(
                "query EventQuery($id: ID!) { event(id: $id) { id } }",
                variables={"id": "J5R5a"},
                operation_name="EventQuery",
            )
            req = m.request_history[0]
            body = json.loads(req.text)
            assert body["operationName"] == "EventQuery"
            assert body["variables"] == {"id": "J5R5a"}

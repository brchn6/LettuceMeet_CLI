"""High-level typed API operations for LettuceMeet."""

from __future__ import annotations

from typing import Any

from lettucemeet_cli.client import GraphQLClient
from lettucemeet_cli.models import (
    CreateEventInput,
    CreatePollResponseInput,
    Event,
)

# ---- Queries ----

_EVENT_QUERY = """
query EventQuery($id: ID!) {
  event(id: $id) {
    id
    title
    description
    type
    pollStartTime
    pollEndTime
    maxScheduledDurationMins
    timeZone
    pollDates
    start
    end
    isScheduled
    createdAt
    updatedAt
    user { id }
    googleEvents { title start end }
    pollResponses {
      id
      user {
        __typename
        ... on AnonymousUser { name email }
        ... on User { id name email }
      }
      availabilities { start end }
      event { id }
    }
  }
}
"""


def get_event(client: GraphQLClient, event_id: str) -> Event:
    """Fetch an event with all poll responses."""
    data = client.execute(
        _EVENT_QUERY,
        variables={"id": event_id},
        operation_name="EventQuery",
    )
    return Event.from_api_data(data["event"])


# ---- Mutations ----

_CREATE_EVENT_MUTATION = """
mutation CreateEventMutation($input: CreateEventInput!) {
  createEvent(input: $input) {
    event {
      id
      title
      type
      description
      pollStartTime
      pollEndTime
      maxScheduledDurationMins
      timeZone
      pollDates
      isScheduled
      createdAt
      updatedAt
      user {
        events { id }
        eventsRespondedTo { id }
        id
      }
    }
  }
}
"""


def create_event(client: GraphQLClient, inp: CreateEventInput) -> dict[str, Any]:
    """Create a new poll event. Returns the created event dict."""
    data = client.execute(
        _CREATE_EVENT_MUTATION,
        variables={"input": inp.to_api_variables()},
        operation_name="CreateEventMutation",
    )
    return data["createEvent"]["event"]


_CREATE_POLL_RESPONSE_MUTATION = """
mutation CreatePollResponseMutation($input: CreatePollResponseInput!) {
  createPollResponse(input: $input) {
    pollResponse {
      id
      user {
        __typename
        ... on AnonymousUser { name email }
        ... on User { id name email }
      }
      availabilities { start end }
      event { id }
    }
  }
}
"""


def create_poll_response(
    client: GraphQLClient, inp: CreatePollResponseInput
) -> dict[str, Any]:
    """Submit availability to an event poll. Returns the created poll response dict."""
    data = client.execute(
        _CREATE_POLL_RESPONSE_MUTATION,
        variables=inp.to_api_variables(),
        operation_name="CreatePollResponseMutation",
    )
    return data["createPollResponse"]["pollResponse"]

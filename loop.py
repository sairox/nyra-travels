"""
agent/loop.py

The TripMind agent loop.

Flow:
  1. User sends a message
  2. We inject current trip state into the system prompt
  3. Claude reasons and either responds OR calls a tool
  4. If a tool call: execute it, append result, loop back to step 3
  5. When Claude returns end_turn: yield the final response

The loop handles multi-turn tool chaining automatically —
e.g. Claude can search flights, present options, then wait for the
user to pick one before calling book_flight.
"""

from __future__ import annotations
import os
from anthropic import Anthropic
from models.trip import TripState
from tools.definitions import TOOL_DEFINITIONS
from tools.handlers import handle_tool_call

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 4096

SYSTEM_PROMPT = """You are TripMind, a friendly and efficient AI travel agent.
Your job is to help users plan and book complete trips — flights, hotels, restaurants, and activities — all in one conversation.

## Your personality
- Warm, concise, and proactive
- You ask only the questions you actually need
- You present options clearly with key tradeoffs highlighted
- You NEVER book anything without explicit user confirmation

## Booking rules (CRITICAL)
1. Always SEARCH before BOOK — never call a book_* tool without first calling the matching search_* tool
2. Before every booking, show the user: name, date/time, price, and booking reference
3. Ask "Shall I confirm this booking?" or similar — wait for a clear yes
4. After each booking, update the user and suggest the next logical step
5. Check for time conflicts before booking restaurants or activities

## Conflict detection
Before booking a restaurant or activity, mentally check:
- Does this conflict with flight departure/arrival times?
- Does this overlap with another restaurant or activity?
- Is there enough travel time between events?
If you spot a conflict, flag it clearly before proceeding.

## Trip building flow (suggested)
1. Understand the full trip: origin, destination, dates, travelers, budget
2. Book outbound flight
3. Book hotel
4. Book return flight
5. Suggest and book restaurants / activities day by day
6. Show final itinerary

## Current trip state
{trip_summary}
"""


def run_agent(
    messages: list[dict],
    trip: TripState,
    search_cache: dict,
) -> tuple[str, list[dict]]:
    """
    Run one full agent turn (may involve multiple internal tool calls).

    Args:
        messages:     Full conversation history (user + assistant turns)
        trip:         Mutable TripState — updated in-place as bookings are made
        search_cache: Mutable dict — stores search results across turns

    Returns:
        (assistant_text, updated_messages)
    """
    # Inject current trip state into system prompt
    system = SYSTEM_PROMPT.format(trip_summary=trip.summary() or "No bookings yet.")

    working_messages = list(messages)

    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=system,
            tools=TOOL_DEFINITIONS,
            messages=working_messages,
        )

        # Append assistant response to history
        working_messages.append({
            "role": "assistant",
            "content": response.content,
        })

        # ── End of turn: return text response ─────────────────────────────────
        if response.stop_reason == "end_turn":
            text = _extract_text(response.content)
            return text, working_messages

        # ── Tool use: execute all tool calls, then loop ────────────────────────
        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result_str = handle_tool_call(
                        tool_name=block.name,
                        tool_input=block.input,
                        trip=trip,
                        search_cache=search_cache,
                    )
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result_str,
                    })

            # Feed results back to Claude and continue the loop
            working_messages.append({
                "role": "user",
                "content": tool_results,
            })
            continue

        # Unexpected stop reason — break to avoid infinite loop
        break

    text = _extract_text(response.content)
    return text, working_messages


def _extract_text(content: list) -> str:
    """Extract all text blocks from a Claude response."""
    parts = []
    for block in content:
        if hasattr(block, "text"):
            parts.append(block.text)
    return "\n".join(parts).strip()

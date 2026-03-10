"""
tools/handlers.py

Dispatches Claude tool_use calls to the appropriate data functions.
This is the only file you need to change when swapping mock data for real APIs.

Pattern:
  1. Claude returns a tool_use block with name + input
  2. handle_tool_call() routes it here
  3. Result is returned as a tool_result message back to Claude
"""

from __future__ import annotations
import json
from models.trip import TripState
from tools import mock_data


def handle_tool_call(
    tool_name: str,
    tool_input: dict,
    trip: TripState,
    search_cache: dict,        # stores last search results so book_* can look up by ID
) -> str:
    """
    Execute a tool call and return a JSON string result.
    `search_cache` persists across turns so booking tools can find search results.
    """
    try:
        result = _dispatch(tool_name, tool_input, trip, search_cache)
        return json.dumps(result, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})


def _dispatch(tool_name: str, inp: dict, trip: TripState, cache: dict) -> dict:

    # ── Flights ───────────────────────────────────────────────────────────────
    if tool_name == "search_flights":
        flights = mock_data.search_flights(
            origin=inp["origin"],
            destination=inp["destination"],
            date=inp["date"],
            passengers=inp.get("passengers", trip.num_travelers),
            cabin_class=inp.get("cabin_class", "economy"),
        )
        cache["flights"] = flights          # store for book_flight
        return {"flights": [f.model_dump() for f in flights]}

    if tool_name == "book_flight":
        flights = cache.get("flights", [])
        booking = mock_data.book_flight(
            flight_id=inp["flight_id"],
            passenger_name=inp["passenger_name"],
            all_flights=flights,
        )
        # Determine outbound vs return based on what's already booked
        if trip.flight_outbound is None:
            trip.flight_outbound = booking
        else:
            trip.flight_return = booking
        return {"booking": booking.model_dump(), "message": "Flight booked successfully!"}

    # ── Hotels ────────────────────────────────────────────────────────────────
    if tool_name == "search_hotels":
        hotels = mock_data.search_hotels(
            city=inp["city"],
            check_in=inp["check_in"],
            check_out=inp["check_out"],
            guests=inp.get("guests", trip.num_travelers),
        )
        cache["hotels"] = hotels
        return {"hotels": [h.model_dump() for h in hotels]}

    if tool_name == "book_hotel":
        hotels = cache.get("hotels", [])
        booking = mock_data.book_hotel(
            hotel_id=inp["hotel_id"],
            guest_name=inp["guest_name"],
            num_guests=inp.get("num_guests", trip.num_travelers),
            all_hotels=hotels,
        )
        trip.hotel = booking
        return {"booking": booking.model_dump(), "message": "Hotel booked successfully!"}

    # ── Restaurants ───────────────────────────────────────────────────────────
    if tool_name == "search_restaurants":
        restaurants = mock_data.search_restaurants(
            city=inp["city"],
            date=inp["date"],
            party_size=inp.get("party_size", trip.num_travelers),
            cuisine=inp.get("cuisine"),
        )
        cache.setdefault("restaurants", []).extend(restaurants)
        return {"restaurants": [r.model_dump() for r in restaurants]}

    if tool_name == "book_restaurant":
        restaurants = cache.get("restaurants", [])
        booking = mock_data.book_restaurant(
            restaurant_id=inp["restaurant_id"],
            guest_name=inp["guest_name"],
            party_size=inp.get("party_size", trip.num_travelers),
            time=inp["time"],
            date=inp["date"],
            all_restaurants=restaurants,
        )
        trip.restaurants.append(booking)
        return {"booking": booking.model_dump(), "message": "Restaurant reserved successfully!"}

    # ── Activities ────────────────────────────────────────────────────────────
    if tool_name == "search_activities":
        activities = mock_data.search_activities(
            city=inp["city"],
            date=inp["date"],
            num_participants=inp.get("num_participants", trip.num_travelers),
            category=inp.get("category"),
        )
        cache.setdefault("activities", []).extend(activities)
        return {"activities": [a.model_dump() for a in activities]}

    if tool_name == "book_activity":
        activities = cache.get("activities", [])
        booking = mock_data.book_activity(
            activity_id=inp["activity_id"],
            guest_name=inp["guest_name"],
            num_participants=inp.get("num_participants", trip.num_travelers),
            all_activities=activities,
        )
        trip.activities.append(booking)
        return {"booking": booking.model_dump(), "message": "Activity booked successfully!"}

    # ── Itinerary ─────────────────────────────────────────────────────────────
    if tool_name == "get_itinerary":
        return {"itinerary": trip.summary(), "trip": trip.model_dump()}

    raise ValueError(f"Unknown tool: {tool_name}")

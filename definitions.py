"""
tools/definitions.py

Claude tool schemas.  These are passed directly to the Anthropic API.
Each tool maps 1-to-1 with a function in mock_data.py (and later, real APIs).

When you swap mock data for real APIs:
  1. Keep these definitions unchanged
  2. Only update the handler functions in tools/handlers.py
"""

TOOL_DEFINITIONS = [

    # ── Flights ───────────────────────────────────────────────────────────────
    {
        "name": "search_flights",
        "description": (
            "Search for available flights between two cities on a given date. "
            "Returns up to 3 flight options with prices, times, and airline details. "
            "Always call this before book_flight."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "origin": {
                    "type": "string",
                    "description": "IATA airport code or city name, e.g. 'JFK' or 'New York'"
                },
                "destination": {
                    "type": "string",
                    "description": "IATA airport code or city name, e.g. 'NRT' or 'Tokyo'"
                },
                "date": {
                    "type": "string",
                    "description": "Departure date in YYYY-MM-DD format"
                },
                "passengers": {
                    "type": "integer",
                    "description": "Number of passengers (default 1)",
                    "default": 1
                },
                "cabin_class": {
                    "type": "string",
                    "enum": ["economy", "premium_economy", "business", "first"],
                    "description": "Cabin class preference (default economy)",
                    "default": "economy"
                }
            },
            "required": ["origin", "destination", "date"]
        }
    },

    {
        "name": "book_flight",
        "description": (
            "Book a specific flight that was returned by search_flights. "
            "IMPORTANT: Always show the user the flight details and get explicit confirmation "
            "before calling this tool. Never book without confirmation."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "flight_id": {
                    "type": "string",
                    "description": "The flight ID from search_flights results"
                },
                "passenger_name": {
                    "type": "string",
                    "description": "Full name of the passenger"
                }
            },
            "required": ["flight_id", "passenger_name"]
        }
    },

    # ── Hotels ────────────────────────────────────────────────────────────────
    {
        "name": "search_hotels",
        "description": (
            "Search for available hotels in a city for given dates. "
            "Returns up to 3 options with prices, ratings, and amenities. "
            "Always call this before book_hotel."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name, e.g. 'Tokyo' or 'Paris'"
                },
                "check_in": {
                    "type": "string",
                    "description": "Check-in date in YYYY-MM-DD format"
                },
                "check_out": {
                    "type": "string",
                    "description": "Check-out date in YYYY-MM-DD format"
                },
                "guests": {
                    "type": "integer",
                    "description": "Number of guests (default 1)",
                    "default": 1
                }
            },
            "required": ["city", "check_in", "check_out"]
        }
    },

    {
        "name": "book_hotel",
        "description": (
            "Book a specific hotel that was returned by search_hotels. "
            "IMPORTANT: Always show the user the hotel details and price total, "
            "and get explicit confirmation before calling this tool."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "hotel_id": {
                    "type": "string",
                    "description": "The hotel ID from search_hotels results"
                },
                "guest_name": {
                    "type": "string",
                    "description": "Full name of the primary guest"
                },
                "num_guests": {
                    "type": "integer",
                    "description": "Number of guests"
                }
            },
            "required": ["hotel_id", "guest_name", "num_guests"]
        }
    },

    # ── Restaurants ───────────────────────────────────────────────────────────
    {
        "name": "search_restaurants",
        "description": (
            "Search for restaurants with availability on a given date and city. "
            "Returns up to 3 options with available booking times. "
            "Always call this before book_restaurant."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name"
                },
                "date": {
                    "type": "string",
                    "description": "Desired dining date in YYYY-MM-DD format"
                },
                "party_size": {
                    "type": "integer",
                    "description": "Number of diners (default 2)",
                    "default": 2
                },
                "cuisine": {
                    "type": "string",
                    "description": "Optional cuisine preference, e.g. 'Japanese', 'Italian'"
                }
            },
            "required": ["city", "date"]
        }
    },

    {
        "name": "book_restaurant",
        "description": (
            "Reserve a table at a restaurant returned by search_restaurants. "
            "IMPORTANT: Confirm with the user before booking. "
            "Check that the time doesn't conflict with other bookings in the itinerary."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "restaurant_id": {
                    "type": "string",
                    "description": "The restaurant ID from search_restaurants results"
                },
                "guest_name": {
                    "type": "string",
                    "description": "Name for the reservation"
                },
                "party_size": {
                    "type": "integer",
                    "description": "Number of diners"
                },
                "time": {
                    "type": "string",
                    "description": "Booking time in HH:MM format, must be from available_times"
                },
                "date": {
                    "type": "string",
                    "description": "Booking date in YYYY-MM-DD format"
                }
            },
            "required": ["restaurant_id", "guest_name", "party_size", "time", "date"]
        }
    },

    # ── Activities ────────────────────────────────────────────────────────────
    {
        "name": "search_activities",
        "description": (
            "Search for activities and experiences in a city on a given date. "
            "Returns tours, classes, excursions and more. "
            "Always call this before book_activity."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name"
                },
                "date": {
                    "type": "string",
                    "description": "Activity date in YYYY-MM-DD format"
                },
                "num_participants": {
                    "type": "integer",
                    "description": "Number of participants (default 1)",
                    "default": 1
                },
                "category": {
                    "type": "string",
                    "description": "Optional category filter: 'Tour', 'Adventure', or 'Culture'"
                }
            },
            "required": ["city", "date"]
        }
    },

    {
        "name": "book_activity",
        "description": (
            "Book an activity returned by search_activities. "
            "IMPORTANT: Confirm total price and timing with the user before booking."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "activity_id": {
                    "type": "string",
                    "description": "The activity ID from search_activities results"
                },
                "guest_name": {
                    "type": "string",
                    "description": "Name for the booking"
                },
                "num_participants": {
                    "type": "integer",
                    "description": "Number of participants"
                }
            },
            "required": ["activity_id", "guest_name", "num_participants"]
        }
    },

    # ── Itinerary ─────────────────────────────────────────────────────────────
    {
        "name": "get_itinerary",
        "description": (
            "Returns the current trip itinerary with all confirmed bookings. "
            "Call this whenever the user asks to see their trip summary, "
            "or after completing a set of bookings."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
]

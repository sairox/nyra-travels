"""
tools/mock_data.py

Realistic mock data for all booking categories.
Each function mirrors the signature you'll use when wiring up real APIs —
just swap the function body for an HTTP call to Duffel / Booking.com / etc.

Swap guide:
  search_flights  → Duffel  POST /air/offer_requests
  search_hotels   → Booking.com Affiliate API  /v1/static/accommodations
  search_restaurants → OpenTable  /restref/api/2/restaurants
  search_activities  → Viator  /products/search
"""

from __future__ import annotations
import random
import uuid
from datetime import datetime, timedelta
from models.trip import (
    FlightResult, HotelResult, RestaurantResult, ActivityResult,
    FlightBooking, HotelBooking, RestaurantBooking, ActivityBooking,
)

# ── Helpers ───────────────────────────────────────────────────────────────────

def _ref() -> str:
    return uuid.uuid4().hex[:6].upper()

def _add_hours(time_str: str, hours: float) -> str:
    """Add hours to an ISO datetime string."""
    dt = datetime.fromisoformat(time_str)
    return (dt + timedelta(hours=hours)).isoformat()


# ── Flights ───────────────────────────────────────────────────────────────────

AIRLINES = [
    ("United Airlines", "UA"),
    ("Delta Air Lines", "DL"),
    ("American Airlines", "AA"),
    ("British Airways", "BA"),
    ("Lufthansa", "LH"),
    ("Emirates", "EK"),
    ("Japan Airlines", "JL"),
]

def search_flights(
    origin: str,
    destination: str,
    date: str,
    passengers: int = 1,
    cabin_class: str = "economy",
) -> list[FlightResult]:
    """Return 3 mock flight options."""
    random.seed(f"{origin}{destination}{date}")
    results = []
    base_prices = [420.0, 310.0, 560.0]
    durations = [480, 540, 420]
    stops_list = [1, 0, 1]
    dep_hours = ["08:30", "13:15", "21:45"]

    for i, (airline, code) in enumerate(random.sample(AIRLINES, 3)):
        dep_time = f"{date}T{dep_hours[i]}:00"
        arr_time = _add_hours(dep_time, durations[i] / 60)
        results.append(FlightResult(
            id=f"FL-{_ref()}",
            airline=airline,
            flight_number=f"{code}{random.randint(100, 999)}",
            origin=origin.upper(),
            destination=destination.upper(),
            departure_time=dep_time,
            arrival_time=arr_time,
            duration_minutes=durations[i],
            stops=stops_list[i],
            price_usd=round(base_prices[i] * passengers, 2),
            cabin_class=cabin_class,
        ))
    return results


def book_flight(flight_id: str, passenger_name: str, all_flights: list[FlightResult]) -> FlightBooking:
    """Confirm a flight booking."""
    flight = next((f for f in all_flights if f.id == flight_id), None)
    if not flight:
        raise ValueError(f"Flight {flight_id} not found in search results")
    return FlightBooking(
        booking_ref=f"TM-FL-{_ref()}",
        flight=flight,
        passenger_name=passenger_name,
    )


# ── Hotels ────────────────────────────────────────────────────────────────────

HOTEL_TEMPLATES = {
    "default": [
        ("The Grand Plaza", 5, ["Pool", "Spa", "Gym", "Restaurant", "Bar"], 9.1),
        ("Comfort Inn Central", 3, ["Gym", "Free WiFi", "Breakfast"], 7.8),
        ("Boutique & Co.", 4, ["Rooftop Bar", "Free WiFi", "Concierge"], 8.5),
    ]
}

def search_hotels(
    city: str,
    check_in: str,
    check_out: str,
    guests: int = 1,
) -> list[HotelResult]:
    """Return 3 mock hotel options."""
    check_in_dt = datetime.strptime(check_in, "%Y-%m-%d")
    check_out_dt = datetime.strptime(check_out, "%Y-%m-%d")
    nights = (check_out_dt - check_in_dt).days or 1

    random.seed(f"{city}{check_in}")
    base_prices = [320.0, 95.0, 185.0]
    templates = HOTEL_TEMPLATES.get(city.lower(), HOTEL_TEMPLATES["default"])

    results = []
    for i, (name, stars, amenities, rating) in enumerate(templates):
        ppn = base_prices[i]
        results.append(HotelResult(
            id=f"HT-{_ref()}",
            name=f"{name} {city}",
            city=city,
            stars=stars,
            address=f"{random.randint(1, 200)} Main Street, {city}",
            check_in=check_in,
            check_out=check_out,
            price_per_night_usd=ppn,
            total_price_usd=round(ppn * nights, 2),
            amenities=amenities,
            rating=rating,
        ))
    return results


def book_hotel(hotel_id: str, guest_name: str, num_guests: int, all_hotels: list[HotelResult]) -> HotelBooking:
    hotel = next((h for h in all_hotels if h.id == hotel_id), None)
    if not hotel:
        raise ValueError(f"Hotel {hotel_id} not found")
    return HotelBooking(
        booking_ref=f"TM-HT-{_ref()}",
        hotel=hotel,
        guest_name=guest_name,
        num_guests=num_guests,
    )


# ── Restaurants ───────────────────────────────────────────────────────────────

RESTAURANT_TEMPLATES = [
    ("Sakura Garden", "Japanese", "$$$", 4.7),
    ("La Trattoria", "Italian", "$$", 4.4),
    ("The Rooftop Grill", "American", "$$$", 4.6),
    ("Spice Route", "Indian", "$$", 4.5),
    ("Le Petit Bistro", "French", "$$$$", 4.8),
]

def search_restaurants(
    city: str,
    date: str,
    party_size: int = 2,
    cuisine: str | None = None,
) -> list[RestaurantResult]:
    """Return 3 mock restaurant options with available times."""
    random.seed(f"{city}{date}")
    templates = RESTAURANT_TEMPLATES
    if cuisine:
        templates = [t for t in templates if cuisine.lower() in t[1].lower()] or templates

    selected = random.sample(templates, min(3, len(templates)))
    results = []
    for name, cuis, price_range, rating in selected:
        times = ["18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "21:00"]
        available = random.sample(times, random.randint(3, 5))
        results.append(RestaurantResult(
            id=f"RS-{_ref()}",
            name=f"{name} {city}",
            city=city,
            cuisine=cuis,
            address=f"{random.randint(1, 300)} Dining St, {city}",
            price_range=price_range,
            rating=rating,
            available_times=sorted(available),
            date=date,
        ))
    return results


def book_restaurant(
    restaurant_id: str,
    guest_name: str,
    party_size: int,
    time: str,
    date: str,
    all_restaurants: list[RestaurantResult],
) -> RestaurantBooking:
    restaurant = next((r for r in all_restaurants if r.id == restaurant_id), None)
    if not restaurant:
        raise ValueError(f"Restaurant {restaurant_id} not found")
    if time not in restaurant.available_times:
        raise ValueError(f"Time {time} is not available. Choose from: {restaurant.available_times}")
    return RestaurantBooking(
        booking_ref=f"TM-RS-{_ref()}",
        restaurant=restaurant,
        guest_name=guest_name,
        party_size=party_size,
        time=time,
        date=date,
    )


# ── Activities ────────────────────────────────────────────────────────────────

ACTIVITY_TEMPLATES = [
    ("City Walking Tour", "Tour", 3.0, 35.0),
    ("Cooking Class", "Culture", 4.0, 120.0),
    ("Sunset Boat Cruise", "Adventure", 2.5, 85.0),
    ("Museum Skip-the-Line", "Culture", 2.0, 25.0),
    ("Bike Tour of Old Town", "Adventure", 3.5, 50.0),
]

def search_activities(
    city: str,
    date: str,
    num_participants: int = 1,
    category: str | None = None,
) -> list[ActivityResult]:
    """Return 3 mock activity options."""
    random.seed(f"{city}{date}act")
    templates = ACTIVITY_TEMPLATES
    if category:
        templates = [t for t in templates if category.lower() in t[1].lower()] or templates

    selected = random.sample(templates, min(3, len(templates)))
    results = []
    start_times = ["09:00", "10:30", "14:00", "15:30"]
    for i, (name, cat, duration, price_pp) in enumerate(selected):
        results.append(ActivityResult(
            id=f"AC-{_ref()}",
            name=f"{name} — {city}",
            city=city,
            description=f"Experience the best of {city} with our {name.lower()}.",
            date=date,
            start_time=start_times[i % len(start_times)],
            duration_hours=duration,
            price_per_person_usd=price_pp,
            total_price_usd=round(price_pp * num_participants, 2),
            category=cat,
        ))
    return results


def book_activity(
    activity_id: str,
    guest_name: str,
    num_participants: int,
    all_activities: list[ActivityResult],
) -> ActivityBooking:
    activity = next((a for a in all_activities if a.id == activity_id), None)
    if not activity:
        raise ValueError(f"Activity {activity_id} not found")
    return ActivityBooking(
        booking_ref=f"TM-AC-{_ref()}",
        activity=activity,
        guest_name=guest_name,
        num_participants=num_participants,
    )

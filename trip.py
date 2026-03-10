"""
models/trip.py
Pydantic models for the TripMind domain.
Replace with DB models (SQLModel / SQLAlchemy) when you add persistence.
"""

from __future__ import annotations
from typing import Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime


# ── Flights ───────────────────────────────────────────────────────────────────

class FlightResult(BaseModel):
    id: str
    airline: str
    flight_number: str
    origin: str
    destination: str
    departure_time: str          # ISO 8601 e.g. "2025-06-15T08:30:00"
    arrival_time: str
    duration_minutes: int
    stops: int
    price_usd: float
    cabin_class: str


class FlightBooking(BaseModel):
    booking_ref: str
    flight: FlightResult
    passenger_name: str
    status: Literal["confirmed", "pending", "cancelled"] = "confirmed"


# ── Hotels ────────────────────────────────────────────────────────────────────

class HotelResult(BaseModel):
    id: str
    name: str
    city: str
    stars: int
    address: str
    check_in: str               # date string e.g. "2025-06-15"
    check_out: str
    price_per_night_usd: float
    total_price_usd: float
    amenities: list[str]
    rating: float               # 0–10


class HotelBooking(BaseModel):
    booking_ref: str
    hotel: HotelResult
    guest_name: str
    num_guests: int
    status: Literal["confirmed", "pending", "cancelled"] = "confirmed"


# ── Restaurants ───────────────────────────────────────────────────────────────

class RestaurantResult(BaseModel):
    id: str
    name: str
    city: str
    cuisine: str
    address: str
    price_range: Literal["$", "$$", "$$$", "$$$$"]
    rating: float               # 0–5
    available_times: list[str]  # e.g. ["18:00", "18:30", "19:00"]
    date: str                   # "2025-06-16"


class RestaurantBooking(BaseModel):
    booking_ref: str
    restaurant: RestaurantResult
    guest_name: str
    party_size: int
    time: str
    date: str
    status: Literal["confirmed", "pending", "cancelled"] = "confirmed"


# ── Activities ────────────────────────────────────────────────────────────────

class ActivityResult(BaseModel):
    id: str
    name: str
    city: str
    description: str
    date: str
    start_time: str
    duration_hours: float
    price_per_person_usd: float
    total_price_usd: float
    category: str               # e.g. "Tour", "Adventure", "Culture"


class ActivityBooking(BaseModel):
    booking_ref: str
    activity: ActivityResult
    guest_name: str
    num_participants: int
    status: Literal["confirmed", "pending", "cancelled"] = "confirmed"


# ── Trip State ─────────────────────────────────────────────────────────────────
# Holds everything the agent knows about the current trip in-session.
# In Phase 2, persist this to PostgreSQL.

class TripState(BaseModel):
    trip_id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex[:8])
    destination: Optional[str] = None
    origin: Optional[str] = None
    departure_date: Optional[str] = None
    return_date: Optional[str] = None
    num_travelers: int = 1
    budget_usd: Optional[float] = None

    # Confirmed bookings
    flight_outbound: Optional[FlightBooking] = None
    flight_return: Optional[FlightBooking] = None
    hotel: Optional[HotelBooking] = None
    restaurants: list[RestaurantBooking] = Field(default_factory=list)
    activities: list[ActivityBooking] = Field(default_factory=list)

    def summary(self) -> str:
        """Human-readable trip summary for injecting into the agent context."""
        lines = [f"Trip ID: {self.trip_id}"]
        if self.origin and self.destination:
            lines.append(f"Route: {self.origin} → {self.destination}")
        if self.departure_date:
            lines.append(f"Dates: {self.departure_date} → {self.return_date or 'TBD'}")
        lines.append(f"Travelers: {self.num_travelers}")

        if self.flight_outbound:
            f = self.flight_outbound.flight
            lines.append(f"✈ Outbound: {f.airline} {f.flight_number} on {f.departure_time} (ref: {self.flight_outbound.booking_ref})")
        if self.flight_return:
            f = self.flight_return.flight
            lines.append(f"✈ Return: {f.airline} {f.flight_number} on {f.departure_time} (ref: {self.flight_return.booking_ref})")
        if self.hotel:
            h = self.hotel.hotel
            lines.append(f"🏨 Hotel: {h.name}, {h.city} ({h.check_in} → {h.check_out}) (ref: {self.hotel.booking_ref})")
        for r in self.restaurants:
            lines.append(f"🍽 Restaurant: {r.restaurant.name} on {r.date} at {r.time} (ref: {r.booking_ref})")
        for a in self.activities:
            lines.append(f"🎯 Activity: {a.activity.name} on {a.activity.date} at {a.activity.start_time} (ref: {a.booking_ref})")

        return "\n".join(lines)

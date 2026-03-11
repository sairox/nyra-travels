# Nyra Travels ✈

End-to-end AI travel agent — flights, hotels, restaurants, and activities in one conversation.

Built with Python + FastAPI + Claude API (Anthropic).

Created by Sai Vikas Nethi and Shivani Nanda
---

## Project Structure

```
tripmind/
├── main.py                 # Entry point (uvicorn server)
├── test_agent.py           # CLI test — run without a server
├── requirements.txt
├── .env.example            # Copy to .env and add your API key
│
├── agent/
│   └── loop.py             # ★ Core agent loop (Claude + tool use)
│
├── tools/
│   ├── definitions.py      # Claude tool schemas (the API contract)
│   ├── handlers.py         # Routes tool calls → data functions
│   └── mock_data.py        # Mock data (swap for real APIs in Phase 2)
│
├── models/
│   └── trip.py             # Pydantic models: TripState, bookings, etc.
│
└── api/
    └── server.py           # FastAPI routes
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up your API key

```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
```

Get your key at: https://console.anthropic.com

### 3. Run the CLI (easiest way to test)

```bash
python test_agent.py
```

Example conversation:
```
You: I want to fly from New York to Tokyo for 7 days in June
You: 2 people, budget around $3000 each
You: Book the cheapest flight option
You: Yes, confirm
```

### 4. Run the API server

```bash
python main.py
# or
uvicorn main:app --reload
```

API runs at http://localhost:8000
Docs at http://localhost:8000/docs

### 5. Test the API

```bash
# Start a conversation
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I want to fly from Chicago to Paris for 5 days in July"}'

# Continue (use the session_id from the response)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Book option 1", "session_id": "YOUR_SESSION_ID"}'

# Check trip state
curl http://localhost:8000/trip/YOUR_SESSION_ID
```

---

## Swapping Mock Data for Real APIs

All mock data is in `tools/mock_data.py`. Each function has a comment showing
the real API endpoint to replace it with:

| Function | Real API | Docs |
|---|---|---|
| `search_flights` | Duffel | https://duffel.com/docs |
| `book_flight` | Duffel | https://duffel.com/docs |
| `search_hotels` | Booking.com Affiliate | https://developers.booking.com |
| `book_hotel` | Booking.com Affiliate | https://developers.booking.com |
| `search_restaurants` | OpenTable | https://platform.otapicloud.com |
| `book_restaurant` | OpenTable | https://platform.otapicloud.com |
| `search_activities` | Viator | https://partnerresources.viator.com |
| `book_activity` | Viator | https://partnerresources.viator.com |

**Important:** The tool `definitions.py` and `handlers.py` don't change when
you swap APIs — only the function bodies in `mock_data.py`.

---

## Roadmap

- [x] Phase 1: Agent loop + mock data (you are here)
- [ ] Phase 1b: Wire up Duffel (flights) + Booking.com (hotels)
- [ ] Phase 2: OpenTable (restaurants) + Viator (activities)
- [ ] Phase 2b: Conflict detection engine
- [ ] Phase 2c: Shareable itinerary export
- [ ] Phase 3: Flight status monitoring + disruption re-booking
- [ ] Phase 3b: Group travel coordination

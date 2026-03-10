"""
test_agent.py

Run the TripMind agent directly in your terminal — no server needed.
Great for rapid iteration and testing the agent loop.

Usage:
    python test_agent.py

Type 'quit' or 'exit' to stop.
Type 'trip' to see your current itinerary.
Type 'reset' to start a new trip.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("ANTHROPIC_API_KEY"):
    print("ERROR: ANTHROPIC_API_KEY not set. Copy .env.example to .env and add your key.")
    sys.exit(1)

from models.trip import TripState
from agent.loop import run_agent

def main():
    print("\n" + "="*60)
    print("  ✈  TripMind AI — Travel Agent (Mock Data Mode)")
    print("="*60)
    print("Tell me where you'd like to go and I'll plan your trip!")
    print("Commands: 'trip' = show itinerary | 'reset' = new trip | 'quit' = exit")
    print("="*60 + "\n")

    messages = []
    trip = TripState()
    search_cache = {}

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye! Safe travels! ✈")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit"):
            print("Goodbye! Safe travels! ✈")
            break

        if user_input.lower() == "trip":
            summary = trip.summary()
            print(f"\n--- Your Trip ---\n{summary}\n-----------------\n")
            continue

        if user_input.lower() == "reset":
            messages = []
            trip = TripState()
            search_cache = {}
            print("Trip reset. Start fresh!\n")
            continue

        # Append user message
        messages.append({"role": "user", "content": user_input})

        print("\nTripMind: ", end="", flush=True)
        reply, messages = run_agent(messages, trip, search_cache)
        print(reply)
        print()

if __name__ == "__main__":
    main()

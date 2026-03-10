"""
main.py — TripMind entry point

Run with:
    python main.py
or:
    uvicorn main:app --reload
"""

import uvicorn
from api.server import app  # noqa: F401  (re-exported for uvicorn)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

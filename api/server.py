"""
Nexus API — FastAPI server with SSE streaming
Run: uvicorn api.server:app --reload --port 8000
"""

import os
import json
import queue
import threading
import asyncio

from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from nexus import Orchestrator

app = FastAPI(title="Nexus", version="1.0.0", description="Multi-Agent Research System by Rewrite Labs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

VALID_FORMATS = {"report", "blog", "summary", "essay", "tweet-thread", "linkedin", "newsletter", "slides"}


@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/run")
async def run_agent(
    goal: str   = Query(..., min_length=3, description="Research goal or question"),
    format: str = Query("report", description="Output format"),
    model: str  = Query("llama-3.3-70b-versatile", description="Groq model"),
):
    if not goal.strip():
        return {"error": "goal cannot be empty"}

    fmt = format if format in VALID_FORMATS else "report"
    event_queue: queue.Queue = queue.Queue()

    def worker():
        try:
            orch = Orchestrator(model=model, output_format=fmt)
            orch.run(goal.strip(), on_event=lambda e: event_queue.put(e))
        except Exception as exc:
            event_queue.put({"type": "error", "message": str(exc)})
        finally:
            event_queue.put(None)  # sentinel — signals end of stream

    threading.Thread(target=worker, daemon=True).start()

    async def event_stream():
        while True:
            event = await asyncio.to_thread(event_queue.get)
            if event is None:
                yield "data: [DONE]\n\n"
                break
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control":    "no-cache",
            "Connection":       "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

#!/usr/bin/env python

"""
Entry point for the Google Analytics MCP server.
Compatible con Railway + Claude SSE.
"""

import os

from fastapi import FastAPI, Request
from starlette.routing import Mount, Route
from mcp.server.sse import SseServerTransport
import uvicorn

from analytics_mcp import coordinator


# =========================================
# FASTAPI
# =========================================

app = FastAPI()

# =========================================
# SSE TRANSPORT
# =========================================

sse = SseServerTransport("/messages/")


# =========================================
# SSE ENDPOINT
# =========================================

async def handle_sse(request: Request):

    async with sse.connect_sse(
        request.scope,
        request.receive,
        request._send,
    ) as streams:

        await coordinator.app.run(
            streams[0],
            streams[1],
            coordinator.app.create_initialization_options(),
        )


# =========================================
# ROUTES
# =========================================

app.router.routes.append(
    Route("/sse", endpoint=handle_sse)
)

app.router.routes.append(
    Mount("/messages/", app=sse.handle_post_message)
)


# =========================================
# HEALTH CHECK
# =========================================

@app.get("/")
async def root():

    return {
        "status": "online",
        "service": "google-analytics-mcp"
    }


# =========================================
# START SERVER
# =========================================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 8080))

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port
    )

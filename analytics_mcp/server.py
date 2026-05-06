#!/usr/bin/env python

# Copyright 2025 Google LLC All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/usr/bin/env python

import os
import asyncio
import sys

import analytics_mcp.coordinator as coordinator

from fastapi import FastAPI
from mcp.server.sse import SseServerTransport
from starlette.routing import Mount, Route
import uvicorn

app = FastAPI()

sse = SseServerTransport("/messages/")


async def handle_sse(request):

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


app.router.routes.append(
    Route("/sse", endpoint=handle_sse)
)

app.router.routes.append(
    Mount("/messages/", app=sse.handle_post_message)
)


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 8080))

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port
    )

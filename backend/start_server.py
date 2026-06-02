import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import uvicorn

uvicorn.run("app.main:app", host="127.0.0.1", port=8000, log_level="info")

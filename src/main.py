import asyncio
import uvicorn
from datetime import datetime
from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/public", StaticFiles(directory="public"), name="public")

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home(request: Request):
    templates = Jinja2Templates(directory="templates")
    return templates.TemplateResponse("index.html", {"request": request })


@app.get('/stream')
async def message_stream(request: Request):
    STREAM_DELAY = 1  # second
    RETRY_TIMEOUT = 15000  # milisecond
    def new_messages():
        # Add logic here to check for new messages
        yield 'Hello World'
    async def event_generator():
        count = 0
        max_count = 10
        while count <= max_count:
            # If client closes connection, stop sending events
            if await request.is_disconnected():
                break

            # Checks for new messages and return them to client if any
            if new_messages():
                msg_id = datetime.now().second
                now = datetime.now()
                date_time_str = now.strftime("%m/%d/%Y %H:%M:%S")
                msg = {
                    "event": "NEW_MESSAGE", # this is the event key to use inside the addEventListener
                    "id": msg_id,
                    "retry": RETRY_TIMEOUT,
                    "data": date_time_str
                }
                if count > max_count-1:
                    msg = {
                        "event": "END_OF_MESSAGES", # this is the event key to use inside the addEventListener
                        "id": "END_OF_MESSAGES_ID",
                        "data": "NO MORE MESSAGES"
                    }

                yield msg

            await asyncio.sleep(STREAM_DELAY)
            count += 1

    return EventSourceResponse(event_generator())
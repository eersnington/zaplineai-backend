# Install required packages
# pip install fastapi twilio pyngrok 'uvicorn[standard]' python-multipart
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request, Response, WebSocket
import logging
import os
from pydantic import BaseModel
from pyngrok import ngrok

from lib.db import db
from lib.auth import check_user
from lib.custom_exception import CustomException
from lib.twilio_functions import call_accept, call_stream, update_phone
from routers.phone import router as phone_router
from routers.metrics import router as metrics_router
logging.getLogger().setLevel(logging.INFO)

load_dotenv()


"""
    FastAPI
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()
    logging.info("Connected to the database")
    bots = await db.bot.find_many()

    for bot in bots:
        async def call():
            voice_response = call_accept(public_url, bot.phone_no)
            return Response(content=str(voice_response), media_type="application/xml")

        async def stream(websocket: WebSocket):
            call_stream(websocket)

        add_route(f"{bot.phone_no}/call", call)
        add_route(f"{bot.phone_no}/stream", stream)

    logging.info("Bots loaded")

    yield
    await db.disconnect()
    logging.info("Disconnected from the database")

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(phone_router)
app.include_router(metrics_router)

"""
    NGROK
"""
NGROK_TOKEN = os.getenv("NGROK_TOKEN")
ngrok.set_auth_token(NGROK_TOKEN)
PORT = 5000
public_url = ngrok.connect(PORT, bind_tls=True).public_url


"""
    PYDANTIC FORMS
"""


class BotForm(BaseModel):
    user_id: str


"""
    Functions
"""


def route_matches(route, route_name):
    return route.path_format == f"{route_name}"


def add_route(route_name, func=None):
    async def dynamic_controller():
        return {"message": f"dynamic - {route_name}"}

    if func:
        app.add_api_route(route_name, func, methods=["GET"])
    else:
        app.add_api_route(route_name, dynamic_controller, methods=["GET"])


@app.exception_handler(CustomException)
async def unicorn_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": f"{exc.detail}"},
    )


@app.get("/")
async def root():
    return {"message": "The answer to life the universe and everything is 42. | ZaplineAI API is running."}


@app.get("/bots/add")
async def add(form: BotForm):
    await check_user(form.user_id)

    phone_number = await db.bot.find_first(where={"userId": form.user_id})

    async def call():
        voice_response = call_accept(public_url, phone_number)
        return Response(content=str(voice_response), media_type="application/xml")

    async def stream(websocket: WebSocket):
        call_stream(websocket)

    try:
        update_phone(public_url, phone_number)
        add_route(f"{phone_number}/call", call)
        add_route(f"{phone_number}/stream", stream)
    except Exception as e:
        raise CustomException(status_code=500, detail=str(e))

    return {"message": f"Bot is streaming at {phone_number}!"}


@app.get("/bots/remove")
async def remove(form: BotForm):
    await check_user(form.user_id)

    phone_number = await db.bot.find_first(where={"userId": form.user_id})
    removed = False
    for i, r in enumerate(app.router.routes):
        if route_matches(r, f"{phone_number}/call") or route_matches(r, f"{phone_number}/stream"):
            removed = True
            del app.router.routes[i]

    if removed:
        return {"message": f"Bot is no longer streaming at {phone_number}!"}

    return {"message": f"Bot stream not found {phone_number}!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=False)

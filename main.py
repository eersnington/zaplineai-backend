# Install required packages
# pip install fastapi twilio pyngrok 'uvicorn[standard]' python-multipart
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request, Response, WebSocket
import logging
import os
from pydantic import BaseModel

from twilio.rest import Client
from pyngrok import ngrok

from lib.custom_exception import CustomException
from lib.twilio_functions import call_accept, call_stream, update_phone
logging.getLogger().setLevel(logging.INFO)

load_dotenv()


"""
    FastAPI
"""
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

"""
    NGROK
"""
NGROK_TOKEN = os.getenv("NGROK_TOKEN")
ngrok.set_auth_token(NGROK_TOKEN)
PORT = 5051
public_url = ngrok.connect(PORT, bind_tls=True).public_url


"""
    PYDANTIC FORMS
"""


class BotAddForm(BaseModel):
    user_id: str
    phone_number: str


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
async def add(form: BotAddForm):
    async def call():
        voice_response = call_accept(public_url, form.phone_number)
        return Response(content=str(voice_response), media_type="application/xml")

    async def stream(websocket: WebSocket):
        call_stream(websocket)

    add_route(f"{form.phone_number}/call", call)
    add_route(f"{form.phone_number}/stream", stream)
    update_phone(public_url, form.phone_number)  # TODO: Add try catch
    return {"message": f"Bot is streaming at {form.phone_number}!"}


@app.get("/bots/remove")
async def remove(name: str):
    for i, r in enumerate(app.router.routes):
        if route_matches(r, name):
            del app.router.routes[i]
            return {"message": f"Endpoint /dyn/{name} removed"}

    return {"message": f"Endpoint /dyn/{name} not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=False)

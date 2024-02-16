# Install required packages
# nvidia-smi | grep 'python' | awk '{ print $5 }' | xargs -n1 kill -9
# pip install fastapi twilio pyngrok 'uvicorn[standard]' python-multipart
from dotenv import load_dotenv, find_dotenv
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
logging.getLogger('twilio').setLevel(logging.WARNING)
logging.getLogger('pyngrok').setLevel(logging.WARNING)
logging.getLogger('faster_whisper').setLevel(logging.WARNING)

load_dotenv(find_dotenv(), override=True)


"""
    FastAPI
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()
    logging.info("Connected to the database")
    bots = await db.bot.find_many()

    if os.environ.get("PRODUCTION_MODE") == "False":
        logging.info("Skipped loading bots")
    else:
        for bot in bots:
            profile = await db.profile.find_first(where={"userId": bot.userId})
            await bot_routes(bot.phone_no, public_url, profile.brandname)
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
PORT = 5005
public_url = ngrok.connect(PORT, bind_tls=True).public_url

logging.info(f"Public URL: {public_url}")


"""
    PYDANTIC FORMS
"""


class BotForm(BaseModel):
    user_id: str


"""
    Functions
"""


async def bot_routes(phone_no: str, public_url: str, brand: str):
    async def call(request: Request):
        voice_response = await call_accept(request=request,
            public_url=public_url, phone_number=phone_no[1:])

        return Response(content=str(voice_response), media_type="application/xml")

    async def stream(websocket: WebSocket):
        await call_stream(websocket, phone_no=phone_no, brand_name=brand)

    try:
        update_phone(public_url,  phone_no[1:])
        add_route(f"/{phone_no[1:]}/call", call)
        add_route(f"/{phone_no[1:]}/stream", stream, websock=True)

        return f"Bot is streaming at f{phone_no}!"
    except Exception as e:
        raise CustomException(status_code=500, detail=str(e))


def route_matches(route, route_name):
    return route.path_format == f"{route_name}"

    
def check_route(phone_number: str):
    for i, r in enumerate(app.router.routes):
        if route_matches(r, f"{phone_number[1:]}/call") or route_matches(r, f"{phone_number[1:]}/stream"):
            return True, i
    return False, None


def add_route(route_name, func, websock=False):
    if websock:
        app.add_websocket_route(route_name, func)
    else:
        app.add_api_route(route_name, func, methods=["POST"])


def delete_route(phone_number: str, pos: int):
    try:
        del app.router.routes[pos]
        return True
    except Exception as e:
        return False


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

    bot = await db.bot.find_first(where={"userId": form.user_id})

    if not bot:
        raise CustomException(status_code=404, detail="Bot not found")
    
    profile = await db.profile.find_first(where={"userId": form.user_id})

    if not profile:
        raise CustomException(status_code=404, detail="Profile not found")
    
    response = await bot_routes(bot.phone_no, public_url, profile.brandname)

    return {"message": response}


@app.get("/bots/status")
async def status(form: BotForm):
    await check_user(form.user_id)

    bot = await db.bot.find_first(where={"userId": form.user_id})

    if not bot:
        raise CustomException(status_code=404, detail="Bot not found")
    
    phone_number = bot.phone_no
    
    status, _ = check_route(phone_number)

    if status:
        return {"message": f"Bot is streaming at {phone_number}!"}

    return {"message": f"Bot stream not found {phone_number}!"}


@app.get("/bots/remove")
async def remove(form: BotForm):
    await check_user(form.user_id)

    bot = await db.bot.find_first(where={"userId": form.user_id})

    if not bot:
        raise CustomException(status_code=404, detail="Bot not found")
    
    phone_number = bot.phone_no

    status, i = check_route(phone_number)

    if status:
        delete_route(phone_number)    
        return {"message": f"Bot is no longer streaming at {phone_number}!"}

    return {"message": f"Bot stream not found {phone_number}!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=False)
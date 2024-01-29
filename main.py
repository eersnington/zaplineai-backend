# Install required packages
# pip install fastapi twilio pyngrok 'uvicorn[standard]' python-multipart
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request
import logging

from lib.custom_exception import CustomException
logging.getLogger().setLevel(logging.INFO)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


def route_matches(route, name):
    return route.path_format == f"/dyn/{name}"


def add_route(name, func):
    async def dynamic_controller():
        return {"message": f"dynamic - {name}"}

    if func:
        app.add_api_route(f"/dyn/{name}", func, methods=["GET"])
    else:
        app.add_api_route(f"/dyn/{name}", dynamic_controller, methods=["GET"])


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
async def add(name: str):
    add_route(name, None)
    return {"message": f"Endpoint /dyn/{name} added"}


@app.get("/bots/remove")
async def remove(name: str):
    for i, r in enumerate(app.router.routes):
        if route_matches(r, name):
            del app.router.routes[i]
            return {"message": f"Endpoint /dyn/{name} removed"}

    return {"message": f"Endpoint /dyn/{name} not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)

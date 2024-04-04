import time
import json

from fastapi import FastAPI, Request, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from pydantic import BaseModel
from typing import List
from config import REDIS_CLIENT


class SPAStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        try:
            return await super().get_response(path, scope)
        except (HTTPException, StarletteHTTPException) as ex:
            if ex.status_code == 404:
                return await super().get_response("index.html", scope)
            else:
                raise ex


app = FastAPI()


origins = ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def check_url(request: Request, call_next):
    start_time = int(time.time())
    response = await call_next(request)
    process_time = int(time.time()) - start_time
    response.headers["X-Process-Time"] = str(process_time)

    return response


@app.get("/")
async def get_status():
    return {
        "status": True,
    }


@app.get("/")
async def get_status():
    return {
        "status": True,
    }


@app.get("/payload")
async def save_sensor_payload(id: str, sensor_type: str, value: str):
    print(id, sensor_type, value)

    sensor_key = f"sensor:{id}"
    data = {
        "id": id,
        "sensor_type": sensor_type,
        "value": value,
        "timestamp": int(time.time()),
    }

    REDIS_CLIENT.rpush(sensor_key, json.dumps(data))
    return {"status": True, "payload": data}


@app.get("/logs/{id}")
async def get_sensor_logs(id: str):

    sensor_logs = REDIS_CLIENT.lrange(f"sensor:{id}", 0, -1)

    return {"status": True, "data": [json.loads(log) for log in sensor_logs]}

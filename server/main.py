import time
import json

from fastapi import FastAPI, Request, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from pydantic import BaseModel
from typing import List


from utils import post_webhook, get_llm_response
from constant import PLANT_EVENTS

from config import REDIS_CLIENT, DISCORD_WEBHOOK_URL, OPENAI_API_URL, OPENAI_API_KEY


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


def str_to_float(s):
    try:
        return float(s)
    except ValueError:
        print("Could not convert the string to an integer.")
        return None


def append_sensor_logs(id: str, sensor_type: str, data: dict):
    sensor_key = f"sensor:{id}:{sensor_type}"
    REDIS_CLIENT.rpush(sensor_key, json.dumps(data))
    return sensor_key


def get_sensor_logs(id: str, sensor_type: str):
    sensor_logs = REDIS_CLIENT.lrange(f"sensor:{id}:{sensor_type}", 0, -1)
    return [json.loads(log) for log in sensor_logs]


@app.get("/payload")
async def save_sensor_payload(id: str, sensor_type: str, value: str):
    print(id, sensor_type, value)

    value = str_to_float(value)

    data = {
        "id": id,
        "sensor_type": sensor_type,
        "value": value,
        "timestamp": int(time.time()),
    }

    append_sensor_logs(id, sensor_type, data)

    EVENT_MESSAGE = None
    if sensor_type == "temp":
        if value < 16:
            EVENT_MESSAGE = PLANT_EVENTS.COLD_TEMP
        elif value > 30:
            EVENT_MESSAGE = PLANT_EVENTS.HOT_TEMP

    elif sensor_type == "humidity":
        if value < 30:
            EVENT_MESSAGE = PLANT_EVENTS.LOW_HUMIDITY
        elif value > 80:
            EVENT_MESSAGE = PLANT_EVENTS.HIGH_HUMIDITY

    elif sensor_type == "moisture":
        if value < 20:
            EVENT_MESSAGE = PLANT_EVENTS.UNDERWATERING
        elif value > 70:
            EVENT_MESSAGE = PLANT_EVENTS.OVERWATERING

    elif sensor_type == "light":
        if value < 0.1:
            EVENT_MESSAGE = PLANT_EVENTS.LIGHT_INTENSITY_LOW
        elif value > 0.8:
            EVENT_MESSAGE = PLANT_EVENTS.LIGHT_INTENSITY_HIGH

    if EVENT_MESSAGE != None:
        response = get_llm_response(
            OPENAI_API_URL,
            OPENAI_API_KEY,
            {
                "model": "mistral:latest",
                "messages": [
                    {
                        "role": "system",
                        "content": "I want you to act as a plant that can communicate and respond to different environmental conditions. You will receive events such as HOT_TEMP, COLD_TEMP, LOW_HUMIDITY, HIGH_HUMIDITY, OVERWATERING, UNDERWATERING, LIGHT_INTENSITY_LOW, and LIGHT_INTENSITY_HIGH. For each event, you will generate a message to inform the user about your condition, using a casual, anthropomorphic style. Think of expressing your needs and feelings as if you were a plant experiencing these conditions, allowing users to understand and empathize with your state. Respond directly and conversationally to convey what you require or how the current conditions are affecting you. Provide only ONE short and concise response.",
                    },
                    {
                        "role": "user",
                        "content": EVENT_MESSAGE,
                    },
                ],
                "stream": False,
            },
        )
        post_webhook(DISCORD_WEBHOOK_URL, response)

    return {"status": True, "payload": data}


@app.get("/logs/{id}/{sensor_type}")
async def get_logs(id: str, sensor_type: str):
    sensor_logs = REDIS_CLIENT.lrange(f"sensor:{id}:{sensor_type}", 0, -1)
    return {"status": True, "data": [json.loads(log) for log in sensor_logs]}

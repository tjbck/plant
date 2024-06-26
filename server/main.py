from fastapi import FastAPI, Request, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException


import time
import json
import numpy as np
from pydantic import BaseModel
from typing import List


from utils import post_webhook, sent_bot_message, get_llm_response
from constant import PLANT_EVENTS, PERSONALITY_TYPES

from config import (
    REDIS_CLIENT,
    DISCORD_WEBHOOK_URL,
    OPENAI_API_URL,
    OPENAI_API_KEY,
    MODEL,
)


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

PERSONALITY = PERSONALITY_TYPES.SARCASTIC
SYSTEM_PROMPT = f"I want you to act as a plant that can communicate and respond to different environmental conditions. You will receive events such as temperature, humidity, moisture, and light. For each event, you will generate a message to inform the user about your condition, using a casual, anthropomorphic style. Think of expressing your needs and feelings as if you were a plant experiencing these conditions, allowing users to understand and empathize with your state. Respond directly and conversationally to convey what you require or how the current conditions are affecting you. Provide only ONE short and concise response. {PERSONALITY.value}"


app.state.PREVIOUS_EVENT = PLANT_EVENTS.NORMAL.value

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

    logs = get_sensor_logs(id, sensor_type)
    last_10_log_values = [log["value"] for log in logs[-10:]]
    average_value = np.mean(last_10_log_values)

    EVENT_MESSAGE = None
    if sensor_type == "temp":
        if average_value < 16:
            EVENT_MESSAGE = PLANT_EVENTS.COLD_TEMP.value
        elif average_value > 30:
            EVENT_MESSAGE = PLANT_EVENTS.HOT_TEMP.value

    elif sensor_type == "humidity":
        if average_value < 30:
            EVENT_MESSAGE = PLANT_EVENTS.LOW_HUMIDITY.value
        elif average_value > 80:
            EVENT_MESSAGE = PLANT_EVENTS.HIGH_HUMIDITY.value

    elif sensor_type == "moisture":
        if average_value < 20:
            EVENT_MESSAGE = PLANT_EVENTS.UNDERWATERING.value
        elif average_value > 70:
            EVENT_MESSAGE = PLANT_EVENTS.OVERWATERING.value

    elif sensor_type == "light":
        if average_value < 10:
            EVENT_MESSAGE = PLANT_EVENTS.LIGHT_INTENSITY_LOW.value
        elif average_value > 80:
            EVENT_MESSAGE = PLANT_EVENTS.LIGHT_INTENSITY_HIGH.value

    print(EVENT_MESSAGE)

    if EVENT_MESSAGE != None and app.state.PREVIOUS_EVENT != EVENT_MESSAGE:
        app.state.PREVIOUS_EVENT = EVENT_MESSAGE
        response = get_llm_response(
            OPENAI_API_URL,
            OPENAI_API_KEY,
            {
                "model": MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": f"Sensor Type: {sensor_type}, Value: {value}, Message: {EVENT_MESSAGE}",
                    },
                ],
                "stream": False,
            },
        )

        if response:
            print(response)
            post_webhook(DISCORD_WEBHOOK_URL, response.strip().strip('"'))

    return {"status": True, "payload": data}


@app.get("/logs/{id}/{sensor_type}")
async def get_logs(id: str, sensor_type: str):
    sensor_logs = REDIS_CLIENT.lrange(f"sensor:{id}:{sensor_type}", 0, -1)
    return {"status": True, "data": [json.loads(log) for log in sensor_logs]}


class EventForm(BaseModel):
    user_id: str
    event: str


@app.post("/event")
async def set_event(form_data: EventForm):

    try:
        EVENT_MESSAGE = PLANT_EVENTS[form_data.event].value

        sensor_type = None
        sensor_value = None

        if EVENT_MESSAGE == PLANT_EVENTS.COLD_TEMP.value:
            sensor_type = "temp"
            sensor_value = 15
        elif EVENT_MESSAGE == PLANT_EVENTS.HOT_TEMP.value:
            sensor_type = "temp"
            sensor_value = 31
        elif EVENT_MESSAGE == PLANT_EVENTS.LOW_HUMIDITY.value:
            sensor_type = "humidity"
            sensor_value = 20
        elif EVENT_MESSAGE == PLANT_EVENTS.HIGH_HUMIDITY.value:
            sensor_type = "humidity"
            sensor_value = 81
        elif EVENT_MESSAGE == PLANT_EVENTS.UNDERWATERING.value:
            sensor_type = "humidity"
            sensor_value = 15
        elif EVENT_MESSAGE == PLANT_EVENTS.OVERWATERING.value:
            sensor_type = "humidity"
            sensor_value = 81
        elif EVENT_MESSAGE == PLANT_EVENTS.LIGHT_INTENSITY_LOW.value:
            sensor_type = "light"
            sensor_value = 5
        elif EVENT_MESSAGE == PLANT_EVENTS.LIGHT_INTENSITY_HIGH.value:
            sensor_type = "light"
            sensor_value = 90

        print(EVENT_MESSAGE)

        if EVENT_MESSAGE != None:
            app.state.PREVIOUS_EVENT = EVENT_MESSAGE
            response = get_llm_response(
                OPENAI_API_URL,
                OPENAI_API_KEY,
                {
                    "model": MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": SYSTEM_PROMPT,
                        },
                        {
                            "role": "user",
                            "content": f"Sensor Type: {sensor_type}, Value: {sensor_value}, Message: {EVENT_MESSAGE}",
                        },
                    ],
                    "stream": False,
                },
            )

            if response:
                print(response)
                sent_bot_message(form_data.user_id, response.strip().strip('"'))

        return {"status": True, "event": EVENT_MESSAGE}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong :/",
        )


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatMessagesForm(BaseModel):
    messages: List[ChatMessage]


@app.post("/chat")
async def chat(form_data: ChatMessagesForm):

    messages = [
        {
            "role": "system",
            "content": f"You are a sentient plant. Express your needs and feelings in one short, concise sentence to help users empathize with your condition. Current State: {app.state.PREVIOUS_EVENT}\n{PERSONALITY.value if app.state.PREVIOUS_EVENT != PLANT_EVENTS.NORMAL.value else 'I am thriving and happy! 🥰'}",
        },
        *form_data.model_dump()["messages"],
    ]

    print(messages)
    response = get_llm_response(
        OPENAI_API_URL,
        OPENAI_API_KEY,
        {
            "model": MODEL,
            "messages": messages,
            "stream": False,
        },
    )

    response = response.strip()
    print(response)
    return {"status": True, "response": response}

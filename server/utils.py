import requests
from typing import Optional


def post_webhook(url: str, message: str) -> bool:
    try:
        payload = {}
        payload["content"] = message

        print(payload)

        r = requests.post(url, json=payload)
        r.raise_for_status()
        return True
    except Exception as e:
        print(e)
        return False


def sent_bot_message(user_id: str, message: str) -> bool:
    try:
        r = requests.post(
            f"http://localhost:3737/id/{user_id}",
            json={"content": message},
        )
        r.raise_for_status()

        data = r.json()
        return data["status"] if "status" in data else False
    except Exception as e:
        print(e)
        return False


def get_llm_response(url: str, key: str, body: str) -> Optional[dict]:
    print(url, key, body)
    try:
        r = requests.post(
            f"{url}/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json=body,
        )
        r.raise_for_status()

        data = r.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(e)
        return None

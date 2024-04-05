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


def get_llm_response(url: str, key: str, body: str) -> Optional[dict]:
    print(url, key, body)
    try:
        r = requests.post(
            f"{url}/chat/completion",
            headers={"Authorization": f"Bearer {key}"},
            json=body,
        )
        r.raise_for_status()

        data = r.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return None

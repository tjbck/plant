import requests


def post_webhook(url: str, message: str) -> bool:
    try:
        payload = {}
        payload["content"] = message

        r = requests.post(url, json=payload)
        r.raise_for_status()
        return True
    except Exception as e:
        print(e)
        return False

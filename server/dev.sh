PORT="${PORT:-5555}"
uvicorn main:app --port $PORT --host 0.0.0.0 --forwarded-allow-ips '*' --reload
#!/usr/bin/env bash

uvicorn main:app --host 0.0.0.0 --port 5555 --forwarded-allow-ips '*'

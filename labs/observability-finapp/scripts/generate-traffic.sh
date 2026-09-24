#!/usr/bin/env bash

set -u

echo "Generating /db traffic. Press Ctrl+C to stop."

while true; do
  curl -s -o /dev/null     -w "DB request: %{time_total}s\n"     http://localhost:8080/db
  sleep 1
done

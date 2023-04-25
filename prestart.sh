#!/usr/bin/env bash

echo "* * * * *  find /app/static -type f -name \$(date -d \"-$STORAGE_TIME days\" --iso)\"*\" -delete" | crontab -

cron

exec "$@"

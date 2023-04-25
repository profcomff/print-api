#!/usr/bin/env bash

echo "0 */1 * * *  find $STATIC_FOLDER -type f -name \$(date -d \"-$STORAGE_TIME hours\" --iso)\"*\" -delete" | crontab -

cron

exec "$@"

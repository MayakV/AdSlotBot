#!/bin/bash
echo "0 * * * * root " \
"HOSTNAME=$HOSTNAME " \
"PORT=$PORT " \
"DB_NAME=$DB_NAME " \
"API_ID=$API_ID " \
"API_HASH=$API_HASH " \
"HOURS_TO_SCRAPE=$HOURS_TO_SCRAPE " \
"python -u /bin/scraper.py > /proc/1/fd/1 2>/proc/1/fd/2" >> /etc/crontab && cron -f
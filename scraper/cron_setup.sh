#!/bin/bash
# Looks ugly bot works
# echo "*/5 * * * * root HOSTNAME=$HOSTNAME PORT=$PORT DB_NAME=$DB_NAME python -u /bin/update_db.py > /proc/1/fd/1 2>/proc/1/fd/2" >> /etc/crontab
# The line above writes cron instruction in crontab
# The intsruction is launching /bin/update_db.py with python every 5 minutes under root user with soe environment variables
# Output from said command redirected to console -u flag in python is needed for docker to see console output
# && cron -f
# After writing in crontab it launches cron in foreground so that container wouldn't stop automaticaly
echo "0 * * * * root " \
"HOSTNAME=$HOSTNAME " \
"PORT=$PORT " \
"DB_NAME=$DB_NAME " \
"API_ID=$API_ID " \
"API_HASH=$API_HASH " \
"HOURS_TO_SCRAPE=$HOURS_TO_SCRAPE " \
"python -u /bin/scraper.py > /proc/1/fd/1 2>/proc/1/fd/2" >> /etc/crontab && cron -f
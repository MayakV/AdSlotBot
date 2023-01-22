# Install the base requirements for the app.
# This stage is to support development.
FROM python:3.10 AS base

# Install cron
RUN apt-get update && apt-get install cron -y -qq

# Install requirements
COPY ./scraper/py_requirements.txt .
RUN pip install -r py_requirements.txt

# Copy script and libraries
COPY ./scraper/scraper.py ./bin/scraper.py
# TODO need to fix this to generate name.session in scraper
# TODO probably need to forward message from telegram to ot chat and pass code to scraper somehow
COPY ./scraper/name.session ./bin/name.session
COPY ./shared ./shared

# Looks ugly bot works
# echo "*/5 * * * * root HOSTNAME=$HOSTNAME PORT=$PORT DB_NAME=$DB_NAME python -u /bin/update_db.py > /proc/1/fd/1 2>/proc/1/fd/2" >> /etc/crontab
# The line above writes cron instruction in crontab
# The intsruction is launching /bin/update_db.py with python every 5 minutes under root user with soe environment variables
# Output from said command redirected to console -u flag in python is needed for docker to see console output
# && cron -f
# After writing in crontab it launches cron in foreground so that container wouldn't stop automaticaly
ENTRYPOINT echo "0 * * * * root "
    \ "HOSTNAME=$HOSTNAME "
    \ "PORT=$PORT "
    \ "DB_NAME=$DB_NAME "
    \ "API_ID=$API_ID "
    \ "API_HASH=$API_HASH "
    \ "HOURS_TO_SCRAPE=$HOURS_TO_SCRAPE "
    \ "python -u /bin/scraper.py > /proc/1/fd/1 2>/proc/1/fd/2" >> /etc/crontab && cron -f

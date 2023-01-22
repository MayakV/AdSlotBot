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
COPY ./scraper/cron_setup.sh ./bin/cron_setup.sh
# TODO need to fix this to generate name.session in scraper
# TODO probably need to forward message from telegram to ot chat and pass code to scraper somehow
COPY ./scraper/name.session ./bin/name.session
COPY ./shared ./shared

RUN ["chmod", "+x", "/bin/cron_setup.sh"]
ENTRYPOINT cron_setup.sh

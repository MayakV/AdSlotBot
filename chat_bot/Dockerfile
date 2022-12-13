# Install the base requirements for the app.
# This stage is to support development
FROM python:3.10 AS base
COPY ./chat_bot/py_requirements.txt .
RUN pip install -r py_requirements.txt
COPY ./chat_bot/test_bot.py ./bin
COPY ./shared ./shared
#RUN ./bin/test_bot.py
#RUN hello.py

#     command: bash -c "./wait-for-it.sh db:27017; python hello.py"

#FROM ubuntu:20.04 AS app-base
#RUN apt update
# Installing https also installs systemd.
#RUN dnf -y install httpd procps less; systemctl enable httpd
#RUN mkdir /appl/

#COPY cprinter /appl/
#COPY cprinter.service /etc/systemd/system/

#COPY goprinter/goprinter /appl/
#COPY goprinter.service /etc/systemd/system/

#STOPSIGNAL SIGRTMIN+3
#EXPOSE 80
#CMD [ "/sbin/init" ]

#RUN apt -y install vsftpd 

#COPY vsftpd.conf /etc/vsftpd.conf
#RUN ufw allow from any to any port 20,21,10000:10100 proto tcp
#RUN systemctl restart vsftpd
#RUN useradd -m ftpuser
#RUN passwd ftpuser
#RUN bash -c "echo FTP TESTING > /home/ftpuser/FTP-TEST"
#WORKDIR /home/ftpuser
#RUN wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | apt-key add -
#RUN echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list
#RUN apt-get install -y mongodb-org
#RUN systemctl start mongod

#RUN systemctl daemon-reload
#RUN systemctl start test_bot
#RUN systemctl enable test_bot

#FROM node:18-alpine AS app-base
#WORKDIR /app
#COPY app/package.json app/yarn.lock ./
#COPY app/spec ./spec
#COPY app/src ./src
#
## Run tests to validate app
#FROM app-base AS test
#RUN yarn install
#RUN yarn test
#
## Clear out the node_modules and create the zip
#FROM app-base AS app-zip-creator
#COPY --from=test /app/package.json /app/yarn.lock ./
#COPY app/spec ./spec
#COPY app/src ./src
#RUN apk add zip && \
#    zip -r /app.zip /app
#
## Dev-ready container - actual files will be mounted in
#FROM base AS dev
#CMD ["mkdocs", "serve", "-a", "0.0.0.0:8000"]
#
## Do the actual build of the mkdocs site
#FROM base AS build
#COPY . .
#RUN mkdocs build
#
## Extract the static content from the build
## and use a nginx image to serve the content
#FROM nginx:alpine
#COPY --from=app-zip-creator /app.zip /usr/share/nginx/html/assets/app.zip
#COPY --from=build /app/site /usr/share/nginx/html
#
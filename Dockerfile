FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir /challenge && chmod 700 /challenge
# RUN echo "{\"flag\":\"$(cat /root/flag.txt)\"}" > /challenge/metadata.json
RUN echo "{\"flag\":\"$(cat flag.txt)\"}" > /challenge/metadata.json

RUN pip install --no-cache-dir flask
RUN pip install bootstrap-flask

RUN mkdir -p /app/database

EXPOSE 8080
# The comment below is parsed by cmgr. You can reference the port by the name
# given, but if there is only one port published, you don't have to use the name
# PUBLISH 8080 AS web


CMD ["python", "app.py","--treatment"]


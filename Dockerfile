FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install --no-cache-dir flask
RUN pip install bootstrap-flask

RUN mkdir -p /app/database

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

ENV TREATMENT=false

EXPOSE 8080

ENTRYPOINT ["python", "app.py","--treatment"]

# Default command (can be overridden)
CMD []

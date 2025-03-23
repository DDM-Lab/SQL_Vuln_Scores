FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask
RUN pip install bootstrap-flask

# Create directory for databases
RUN mkdir -p /app/database

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

EXPOSE 8080

CMD ["flask", "run", "--port=8080"]

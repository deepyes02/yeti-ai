FROM python:3.11.10-slim

WORKDIR /app

ENV TZ="Asia/Tokyo"

# Install gcc and libpq-dev in one step, then clean up, these are needed by python builds
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app
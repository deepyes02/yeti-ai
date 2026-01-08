#!/bin/sh
docker compose down -v
docker compose up -d
docker attach backend

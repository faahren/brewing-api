# syntax=docker/dockerfile:1

FROM python:3.9-slim-buster

ENV POETRY_VERSION=1.5.1 \
  PORT=5000

# Install poetry
RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
WORKDIR /app
COPY poetry.lock pyproject.toml /app/
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --no-root
COPY app/ /app/
COPY config/* /app/
RUN ls

# Project initialization:
CMD gunicorn main:app -w 2 --threads 2 -b 0.0.0.0:${PORT}

FROM python:3.13-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ARG CONTAINER_PORT=8000
EXPOSE ${CONTAINER_PORT}

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_DIR="/app"

# Needed for docker build to succeed
ENV DATABASE_URL=postgres://user:password@localhost:5432/db

# Add new user to run the whole thing as non-root.
RUN set -ex \
    && addgroup --gid 1000 app \
    && adduser --uid 1000 --gid 1000 --home ${APP_DIR} --disabled-password app;

WORKDIR $APP_DIR

COPY pyproject.toml uv.lock ./
# Deploy in the global env of the container instead of a uv-specific venv
ENV UV_PROJECT_ENVIRONMENT="/usr/local/"
RUN uv sync --locked

COPY --chown=app:app . .

RUN uv run python manage.py collectstatic --no-input

RUN chown 1000:1000 -R /app
USER app
VOLUME [ "/app/medias" ]

ENTRYPOINT ["./entrypoint.sh"]

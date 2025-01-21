FROM python:3.13

EXPOSE ${CONTAINER_PORT}

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV GECKODRIVER_URL=https://github.com/mozilla/geckodriver/releases/download/v0.32.0/geckodriver-v0.32.0-linux32.tar.gz
ENV APP_DIR="/app"

# Configure Poetry
ENV POETRY_VERSION=2.0.1
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv
ENV POETRY_CACHE_DIR=/opt/.cache

# Needed for docker build to succeed
ENV DATABASE_URL=postgres://user:password@localhost:5432/db

# Add new user to run the whole thing as non-root.
RUN set -ex \
    && addgroup --gid 1000 app \
    && adduser --uid 1000 --gid 1000 --home ${APP_DIR} --disabled-password app;

# Install poetry separated from system interpreter
RUN python3 -m venv ${POETRY_VENV} \
    && ${POETRY_VENV}/bin/pip install -U pip setuptools \
    && ${POETRY_VENV}/bin/pip install poetry==${POETRY_VERSION}

# Add `poetry` to PATH
ENV PATH="${PATH}:${POETRY_VENV}/bin"

WORKDIR $APP_DIR

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

COPY --chown=app:app . .

RUN poetry run python manage.py collectstatic --no-input --ignore=*.sass

USER app

ENTRYPOINT ["./entrypoint.sh"]

# https://stackoverflow.com/a/40454758/21676629
CMD ["sh", "-c", "poetry run python manage.py runserver 0.0.0.0:$CONTAINER_PORT"]

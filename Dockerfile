FROM python:3.10

EXPOSE ${HOST_PORT}

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV GECKODRIVER_URL=https://github.com/mozilla/geckodriver/releases/download/v0.32.0/geckodriver-v0.32.0-linux32.tar.gz
ENV APP_DIR="/app"

# Configure Poetry
ENV POETRY_VERSION=1.8.2
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv
ENV POETRY_CACHE_DIR=/opt/.cache

# Add new user to run the whole thing as non-root.
RUN set -ex \
    && addgroup app \
    && adduser --ingroup app --home ${APP_DIR} --disabled-password app;

# Install poetry separated from system interpreter
RUN python3 -m venv ${POETRY_VENV} \
    && ${POETRY_VENV}/bin/pip install -U pip setuptools \
    && ${POETRY_VENV}/bin/pip install poetry==${POETRY_VERSION}

# Add `poetry` to PATH
ENV PATH="${PATH}:${POETRY_VENV}/bin"

WORKDIR $APP_DIR

COPY pyproject.toml poetry.lock ./
RUN poetry install

COPY --chown=app:app . .

RUN poetry run python manage.py collectstatic --no-input --ignore=*.sass

USER app

ENTRYPOINT ["./entrypoint.sh"]

# https://stackoverflow.com/a/40454758/21676629
CMD ["sh", "-c", "poetry run python manage.py runserver 0.0.0.0:$HOST_PORT"]

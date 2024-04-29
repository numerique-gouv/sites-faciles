FROM python:3.10

EXPOSE ${HOST_PORT}

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV GECKODRIVER_URL=https://github.com/mozilla/geckodriver/releases/download/v0.32.0/geckodriver-v0.32.0-linux32.tar.gz
ENV APP_DIR="/app"

# Add new user to run the whole thing as non-root.
RUN set -ex \
    && addgroup app \
    && adduser --ingroup app --home ${APP_DIR} --disabled-password app;


WORKDIR $APP_DIR

COPY Pipfile Pipfile.lock ${PROJECT_DIR}/
RUN pip install pipenv --no-cache-dir \
    && pipenv install --system --deploy

COPY --chown=app:app . .

RUN make init

USER app

ENTRYPOINT ["./entrypoint.sh"]

# https://stackoverflow.com/a/40454758/21676629
CMD ["sh", "-c", "pipenv run python manage.py runserver 0.0.0.0:$HOST_PORT"]

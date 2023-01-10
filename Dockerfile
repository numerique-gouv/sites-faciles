FROM python:3.10

EXPOSE 8000

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV GECKODRIVER_URL=https://github.com/mozilla/geckodriver/releases/download/v0.32.0/geckodriver-v0.32.0-linux32.tar.gz
ENV APP_DIR="/app"

# For behave tests
RUN apt-get update && apt-get install -y --no-install-recommends firefox-esr
RUN wget -qO- $GECKODRIVER_URL | tar xvz -C /usr/bin/

# Add new user to run the whole thing as non-root.
RUN set -ex \
    && addgroup app \
    && adduser --ingroup app --home $APP_DIR --disabled-password app;

RUN python -m pip install --upgrade pip

WORKDIR $APP_DIR

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY --chown=app:app . .

RUN python manage.py collectstatic --no-input

USER app

ENTRYPOINT ["./entrypoint.sh"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

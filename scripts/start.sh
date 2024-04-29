#!/bin/bash

pipenv run gunicorn config.wsgi --log-file -

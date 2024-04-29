#!/bin/bash

gunicorn config.wsgi --log-file -

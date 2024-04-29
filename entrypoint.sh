#!/bin/sh -l
set -ex

make update

exec "$@"

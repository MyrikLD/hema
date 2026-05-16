#!/bin/sh
set -e
alembic upgrade head
exec python -m hema.main

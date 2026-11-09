#!/bin/sh
set -e

mkdir -p /srv/internal /srv/uploads

exec python app.py

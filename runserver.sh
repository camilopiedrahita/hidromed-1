#!/bin/bash
. /root/.virtualenvs/hidromed/bin/activate
cd /root/hidromed/config
gunicorn wsgi:application
exec $@


#!/bin/bash

set -e

echo 'start deploy'

echo 'git pull'
git pull

echo 'migrate'
/opt/star-burger/env/bin/python /opt/star-burger/manage.py migrate

echo 'restart star-burger daemon'
systemctl restart star-burger

echo 'completed deploy'
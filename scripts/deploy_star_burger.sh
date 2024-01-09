#!/bin/bash

set -e

echo 'start deploy'

echo 'git pull'
git pull

echo 'installing python packages'
/opt/star-burger/env/bin/pip install -r /opt/star-burger/requirements.txt

echo 'installing js packages'
npm ci --dev

echo 'parcel build bundles'
/opt/star-burger/node_modules/.bin/parcel build /opt/star-burger/bundles-src/index.js --dist-dir /opt/star-burger/bundles --public-url="./"

echo 'migrate'
/opt/star-burger/env/bin/python /opt/star-burger/manage.py migrate --noinput

echo 'collectstatic'
/opt/star-burger/env/bin/python /opt/star-burger/manage.py collectstatic --noinput

echo 'restart star-burger daemon'
systemctl restart star-burger

echo 'reload nginx daemon'
systemctl reload nginx
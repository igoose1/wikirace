#!/bin/bash
BIN=/srv/wikirace/env/bin

case $(hostname) in
wikirace|wikirace.*) BRANCH=prod;;
qa-wikirace|qa-wikirace.*) BRANCH=qa;;
*) BRANCH=master;;
esac

set -e
cd /srv/wikirace/app/

git fetch -q origin $BRANCH
git reset -q --hard FETCH_HEAD

version=`git rev-parse --short HEAD`
cp -f -R /srv/wikirace/app/wiki/static/ /srv/wikirace/static/${version}/
echo $version > /srv/wikirace/static/current_version.txt

$BIN/pip -qq install --index-url http://mirror/pypi --trusted-host mirror -r requirements.txt
$BIN/python manage.py migrate
sudo /etc/init.d/uwsgi restart
sudo /etc/init.d/nginx restart

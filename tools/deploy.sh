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

$BIN/pip -qq install --index-url http://mirror.p.lksh.ru/pypi --trusted-host mirror.p.lksh.ru -r requirements.txt
$BIN/python manage.py migrate
sudo /etc/init.d/uwsgi restart
sudo /etc/init.d/nginx restart

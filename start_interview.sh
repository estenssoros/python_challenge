#!/bin/bash
wget https://github.com/twbs/bootstrap/releases/download/v3.3.7/bootstrap-3.3.7-dist.zip
unzip -o -d temp bootstrap-3.3.7-dist.zip

STATIC_DIR="myapp/swimlane/static/swimlane"
mkdir -p $STATIC_DIR
mv temp/bootstrap-3.3.7-dist/css $STATIC_DIR
mv temp/bootstrap-3.3.7-dist/js $STATIC_DIR
mv temp/bootstrap-3.3.7-dist/fonts $STATIC_DIR


wget -O $STATIC_DIR/css/dropzone.css https://raw.githubusercontent.com/enyo/dropzone/master/dist/dropzone.css
wget -O $STATIC_DIR/js/dropzone.js https://raw.githubusercontent.com/enyo/dropzone/master/dist/dropzone.js
wget -O $STATIC_DIR/js/leaflet.markercluster-src.js https://s3.amazonaws.com/sebsbucket/cdn/leaflet.markercluster-src.js

rm -rf temp
rm *.zip

source mysql_cnf.sh
mysql -u${MYSQL_USERNAME} -h${MYSQL_HOST} -vvv < start_interview.sql

pip install -r requirements.txt
python myapp/manage.py migrate
python myapp/manage.py runserver

#!/usr/bin/env bash
DB_USER=$(echo $RCJ_DATABASE_CONNECTION | grep -oP "\:\/\/\K.*(?=\:)")
DB_PASS=$(echo $RCJ_DATABASE_CONNECTION | grep -oP "\:\/\/.*\:\K.*(?=\@)")
DB_HOST=$(echo $RCJ_DATABASE_CONNECTION | grep -oP "\@\K.*(?=\/)")
DB_NAME=$(echo $RCJ_DATABASE_CONNECTION | grep -oP "\@.*\/\K[^\?]*(?=\??.*$)")
echo "conn = $RCJ_DATABASE_CONNECTION"
echo "host = $DB_HOST"
echo "user = $DB_USER"
echo "pass = $DB_PASS"
echo "name = $DB_NAME"
echo "CREATE DATABASE IF NOT EXISTS $DB_NAME;" | mysql -u $DB_USER -p$DB_PASS -h $DB_HOST --protocol TCP
python rcj_soccer db init
python rcj_soccer db migrate
python rcj_soccer db upgrade
python run.py
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
cd /srv/
if [ ! -z "$RCJ_DATABASE_MIGRATE" ]; then
    if [ ! -z "$RCJ_DATABASE_INIT" ]; then
        python3.6 -m rcj_soccer db init
    elif [ ! "$(ls -A /srv/migration_data)" ]; then
        python3.6 -m rcj_soccer db init
    else
        mkdir -p /srv/migrations
        cp -R /srv/migration_data/* /srv/migrations/
    fi
    python3.6 -m rcj_soccer db migrate
    python3.6 -m rcj_soccer db upgrade

    rm -rf /srv/migration_data/*
    cp -R /srv/migrations/* /srv/migration_data/
fi

echo "now calling run..."
python3.6 run.py

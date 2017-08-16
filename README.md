# RCJ Soccer Scoring Platform

This system manages the soccer draws, refereeing and scoring for RoboCup Junior Australia.

To configure, pass in environment variables, start MariaDB and then run the image:

```bash
export RCJ_DATABASE_CONNECTION="mysql+pymysql://YOUR_DB_USER:YOUR_DB_PASS@mariadb/YOUR_DB_NAME"
export RCJ_SMS_USERNAME="YOUR_SMS_BROADCAST_ACCOUNT"
export RCJ_SMS_PASSWORD="YOUR_SMS_BROADCAST_PASSWORD"
export RCJ_SMS_FROM="RoboCupJnr"
export RCJ_SECRETS_KEY="YOUR_SECRET_KEY"

./build_docker.sh -t soccer

docker run --name=mariadb -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=YOUR_DB_PASS centos/mariadb

docker run -e "RCJ_DATABASE_CONNECTION=$RCJ_DATABASE_CONNECTION" \
           -e "RCJ_SMS_USERNAME=$RCJ_SMS_USERNAME" \
           -e "RCJ_SMS_PASSWORD=$RCJ_SMS_PASSWORD" \
           -e "RCJ_SMS_FROM=$RCJ_SMS_FROM" \
           -e "RCJ_SECRETS_KEY=$YOUR_SECRET_KEY" \
           -e "RCJ_DATABASE_MIGRATE=yes" \
           -e "RCJ_DATABASE_INIT0=yes" \
           -v "/srv/migrations:/srv/migration_data:rw" \
           --network="bridge" \
           --restart always \
           --name "rcj_soccer" \
           --link mariadb:mariadb \
           -d -p 5000:5000 soccer
```

Alternatively, use rcj-infrastructure to automatically use the latest version and configure MariaDB.
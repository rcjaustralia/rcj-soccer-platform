# RCJ Soccer Scoring Platform

*Build Status:* [![CircleCI](https://circleci.com/gh/rcjaustralia/rcj-soccer-platform.svg?style=svg)](https://circleci.com/gh/rcjaustralia/rcj-soccer-platform)

This system manages the soccer draws, refereeing and scoring for RoboCup Junior Australia.

To configure, pass in environment variables, start MariaDB and then run the image:

```bash
export RCJ_DATABASE_CONNECTION="mysql+pymysql://YOUR_DB_USER:YOUR_DB_PASS@mariadb/YOUR_DB_NAME"
export RCJ_SMS_USERNAME="YOUR_SMS_BROADCAST_ACCOUNT"
export RCJ_SMS_PASSWORD="YOUR_SMS_BROADCAST_PASSWORD"
export RCJ_SMS_PROVIDER="sms_broadcast"
export RCJ_SMS_FROM="RoboCupJnr"
export RCJ_SECRETS_KEY="YOUR_SECRET_KEY"
export RCJ_API_TOKEN="ANOTHER_SECRET_STRING"

./build_docker.sh -t soccer  # Only required if building your own image

docker network create --driver bridge rcj_network

docker run --restart always --network=rcj_network -v /srv/mariadb:/var/lib/mysql:rw --name=mariadb -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD="YOUR_DB_PASS" centos/mariadb

# IF THIS IS A CLEAN INSTALL, YOU MUST CREATE THE DATABASE:
# docker exec -it mariadb bash
# $ mysqladmin -uroot -pYOUR_DB_PASS create YOUR_DB_NAME
# $ exit

docker run -e "RCJ_DATABASE_CONNECTION=$RCJ_DATABASE_CONNECTION" \
           -e "RCJ_SMS_USERNAME=$RCJ_SMS_USERNAME" \
           -e "RCJ_SMS_PASSWORD=$RCJ_SMS_PASSWORD" \
           -e "RCJ_SMS_FROM=$RCJ_SMS_FROM" \
           -e "RCJ_SMS_PROVIDER=$RCJ_SMS_PROVIDER" \
           -e "RCJ_SECRETS_KEY=$RCJ_SECRETS_KEY" \
           -e "RCJ_DATABASE_MIGRATE=yes" \
           -e "RCJ_DATABASE_INIT0=yes" \
           -e "RCJ_API_TOKEN=$RCJ_API_TOKEN" \
           -v "/srv/migrations:/srv/migration_data:rw" \
           --network=rcj_network \
           --restart always \
           --name "rcj_soccer" \
           --link mariadb:mariadb \
           -d -p 5000:5000 rcjaustralia/rcj-soccer-platform
```

To use Twilio instead of SMS Broadcast as the messaging provider, use the following environment variables:
```
RCJ_SMS_PROVIDER=twilio
RCJ_SMS_SID=YOUR_ACCOUNT_SID
RCJ_SMS_TOKEN=YOUR_AUTH_TOKEN
RCJ_SMS_FROM=RoboCupJnr
```

Everything except competitions can be configured via the web UI. Competitions must be added directly to the database, for example:

```bash
docker exec -it mariadb bash
$ mysql -uroot -pYOUR_DB_PASS YOUR_DB_NAME
> INSERT INTO competition(name, fb_link, twitter_link, event_sponsor_link, event_sponsor_img, is_active, start_date) VALUES('Queensland State Competition', 'robocupjunioraustralia', '#RCJQ', 'https://www.uq.edu.au', '/static/images/sponsors/uq.png', 1, '2019-08-10');
> exit;
$ exit
```

You will then need to configure the RCJ App Server (required for SSL): https://github.com/rcjaustralia/rcj-app-server

**Note: You MUST create a user as soon as a competition is created, and then login as them and mark them as an as Administrator on the Users panel.** 

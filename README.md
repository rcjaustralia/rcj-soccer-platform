# RCJ Soccer Scoring Platform

*Build Status:* [![CircleCI](https://circleci.com/gh/rcjaustralia/rcj-soccer-platform.svg?style=svg)](https://circleci.com/gh/rcjaustralia/rcj-soccer-platform)

This system manages the soccer draws, robot scrutiny, refereeing, scoring and volunteer management for RoboCup Junior Australia.

## Pre-Requisites
* Vultr DNS (required for [rcj-app-server](https://github.com/rcjaustralia/rcj-app-server))
* For small (<25 teams), a VM with 1 core, 2GB memory and 20GB disk space is sufficient. For larger competitions (up to 250 teams), 4 cores, 8GB memory and 32GB disk space is sufficient. All of the instructions below were done on a CentOS 7 VM and no other OS has been tested. Due to the real-time refereeing component, it is recommended to run the VM as close to the competition location as possible to minmise network latency (for this reason, all Australian competitions were run on a Sydney-based VM).
* [SMS Broadcast](https://www.smsbroadcast.com.au) account with enough credits for each user to login.
* Docker [installed on the VM](https://docs.docker.com/install/linux/docker-ce/centos/)

## Usage
To run, pass in environment variables, start MariaDB and then run the image. Replace the `YOUR_*` environment variables with the real values. 

```bash
export RCJ_DATABASE_NAME="rcj"
export RCJ_DATABASE_USER="root" # bad but works
export RCJ_DATABASE_PASS="YOUR_DB_PASS" # your password here
export RCJ_DATABASE_CONNECTION="mysql+pymysql://$RCJ_DATABASE_USER:$RCJ_DATABASE_PASS@mariadb/$RCJ_DATABASE_NAME"
export RCJ_SMS_USERNAME="YOUR_SMS_BROADCAST_ACCOUNT"
export RCJ_SMS_PASSWORD="YOUR_SMS_BROADCAST_PASSWORD"
export RCJ_SMS_PROVIDER="sms_broadcast"
export RCJ_SMS_FROM="RoboCupJnr"
export RCJ_SECRETS_KEY=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 64)
export RCJ_API_TOKEN=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 64)

# If using docker instead of podman (e.g. CentOS 7):
# alias podman="docker"

mkdir -p $HOME/srv/mariadb

# To build from the source code:
# ./build_docker.sh -t soccer

podman pod create --name rcj -p 80:80 -p 443:443

# If using SELinux, the following will allow unprivileged users
# to use port 80+ (instead of 1024+):
# sudo sysctl net.ipv4.ip_unprivileged_port_start=80

podman run --restart always \
           --pod rcj \
           -v "$HOME/srv/mariadb:/var/lib/mysql:rw" \
           --name mariadb -d \
           -e MYSQL_ROOT_PASSWORD="$RCJ_DATABASE_PASS" mariadb:10

# Check it is running:
podman logs mariadb

# If there is an error about permission denied for /var/lib/mysql
# then SELinux is blocking it. You can either temporarily disable
# SELinux (setenforce 0) or use the following to allow the folder:
# sudo chcon -Rt svirt_sandbox_file_t $HOME/srv/mariadb

# IF THIS IS A CLEAN INSTALL, YOU MUST CREATE THE DATABASE:
# podman exec -it mariadb mysqladmin -u$RCJ_DATABASE_USER -p$RCJ_DATABASE_PASS create $RCJ_DATABASE_NAME

mkdir -p $HOME/srv/migrations

# If SELinux is enabled, run:
# sudo chcon -Rt svirt_sandbox_file_t $HOME/srv/migrations

podman run -e "RCJ_DATABASE_CONNECTION=$RCJ_DATABASE_CONNECTION" \
           -e "RCJ_SMS_USERNAME=$RCJ_SMS_USERNAME" \
           -e "RCJ_SMS_PASSWORD=$RCJ_SMS_PASSWORD" \
           -e "RCJ_SMS_FROM=$RCJ_SMS_FROM" \
           -e "RCJ_SMS_PROVIDER=$RCJ_SMS_PROVIDER" \
           -e "RCJ_SECRETS_KEY=$RCJ_SECRETS_KEY" \
           -e "RCJ_DATABASE_MIGRATE=yes" \
           -e "RCJ_DATABASE_INIT0=yes" \
           -e "RCJ_API_TOKEN=$RCJ_API_TOKEN" \
           -v "$HOME/srv/migrations:/srv/migration_data:rw" \
           --pod rcj \
           --restart always \
           --name "rcj_soccer" \
           -d rcjaustralia/rcj-soccer-platform
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
podman exec -it mariadb mysql -u$RCJ_DATABASE_USER -p $RCJ_DATABASE_NAME
> INSERT INTO competition(id, name, fb_link, twitter_link, event_sponsor_link, event_sponsor_img, is_active, start_date) VALUES('rcjq', 'Queensland State Competition', 'robocupjunioraustralia', '#RCJQ', 'https://www.uq.edu.au', '/static/images/sponsors/uq.png', 1, '2019-08-10');
> exit;
```

You will then need to configure the RCJ App Server (required for SSL and optional load balancing if >500 teams): https://github.com/rcjaustralia/rcj-app-server

**Note: You MUST create a user as soon as a competition is created, and then login as them and mark them as an as Administrator on the Users panel.** 

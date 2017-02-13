# RCJ Soccer Scoring Platform

This system manages the soccer draws, refereeing and scoring for RoboCup Junior Australia.

TODO: Dockerize it.

To configure, pass in environment variables:

```bash
export RCJ_DATABASE_CONNECTION="mysql+pymysql://YOUR_DB_USER:YOUR_DB_PASS@localhost/YOUR_DB_NAME"
export RCJ_SMS_USERNAME="YOUR_SMS_BROADCAST_ACCOUNT"
export RCJ_SMS_PASSWORD="YOUR_SMS_BROADCAST_PASSWORD"
export RCJ_SMS_FROM="RoboCupJnr"
export RCJ_SECRETS_KEY="YOUR_SECRET_KEY"
```
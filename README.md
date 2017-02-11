# RCJ Soccer Scoring Platform

This system manages the soccer draws, refereeing and scoring for RoboCup Junior Australia.

TODO: Dockerize it.

To configure, pass in environment variables:

```bash
export RCJ_DATABASE_CONNECTION="mysql+pymysql://root:userPass01@localhost/rcja"
export RCJ_SMS_USERNAME="troberts0"
export RCJ_SMS_PASSWORD="RCJfor2016"
export RCJ_SMS_FROM="RoboCupJnr"
export RCJ_SECRETS_KEY="foo0bars014o33afsasf"
```
import requests
import logging
from . import config
logger = logging.getLogger(__name__)


def send(to, message):
    r = requests.post("https://api.smsbroadcast.com.au/api-adv.php", data={
        "username": config.get("sms", "username").strip(),
        "password": config.get("sms", "password").strip(),
        "to": to,
        "from": config.get("sms", "from").strip(),
        "message": message
    })
    logger.info("SMS sent: {}", r.text)


def balance():
    req = requests.get("https://api.smsbroadcast.com.au/api-adv.php", params={
        "username": config.get("sms", "username").strip(),
        "password": config.get("sms", "password").strip(),
        "action": "balance"
    })

    if "OK" in req.text:
        return int(req.text.split(":")[1])
    else:
        return None

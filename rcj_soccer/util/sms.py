import requests
import logging
from . import config
from twilio.rest import Client
logger = logging.getLogger(__name__)


class SMSProvider(object):
    def __init__(self):
        raise NotImplemented("constructor")

    def send(self, to, message):
        raise NotImplemented("send")

    def balance(self):
        raise NotImplemented("balance")

    def has_balance(self):
        raise NotImplemented("has_balance")


class SMSBroadcast(SMSProvider):
    username = None
    password = None
    from_addr = None

    def __init__(self, username=None, password=None, from_addr=None):
        self.username = username or config.get("sms", "username").strip()
        self.password = password or config.get("sms", "password").strip()
        self.from_addr = from_addr or config.get("sms", "from").strip()

    def send(self, to, message):
        r = requests.post("https://api.smsbroadcast.com.au/api-adv.php", data={
            "username": self.username,
            "password": self.password,
            "to": to,
            "from": self.from_addr,
            "message": message
        })
        logger.info("SMS Broadcast - sent: {0}".format(r.text))

    def balance(self):
        req = requests.get(
            "https://api.smsbroadcast.com.au/api-adv.php",
            params={
                "username": self.username,
                "password": self.password,
                "action": "balance"
            }
        )

        if "OK" in req.text:
            balance = int(req.text.split(":")[1])
            logger.info("SMS Broadcast - balance: {0}".format(balance))
            return balance
        else:
            return None

    def has_balance(self):
        return True


class Twilio(SMSProvider):
    from_addr = None
    client = None

    def __init__(self, sid=None, token=None, from_addr=None):
        self.from_addr = from_addr or config.get("sms", "from").strip()

        account_sid = sid or config.get("sms", "sid").strip()
        token = token or config.get("sms", "token").strip()

        self.client = Client(account_sid, token)

    def send(self, to, message):
        to = str(to)

        if not to.startswith("+61"):
            if to.startswith("61"):
                to = "+" + to
            elif to.startswith("0"):
                to = "+61" + to[1:]
            else:
                raise NotImplemented("Unknown phone number: {0}".format(to))

        self.client.messages.create(
            to=to,
            from_=self.from_addr,
            body=message
        )

        logger.info("Twilio - sent: {0}".format(to))

    def has_balance(self):
        return False

    def balance(self):
        raise NotImplemented("balance")


_provider = None


def get_provider():
    global _provider

    if _provider is None:
        if config.get("sms", "provider").lower() == "twilio":
            _provider = Twilio()
        else:
            _provider = SMSBroadcast()
    return _provider

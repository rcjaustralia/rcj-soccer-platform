# The only variable you should change inside this app:
CONFIG_PATH = "/etc/rcja-soccer.conf"

# End configuration.  For more config see config-defaults.conf
import ConfigParser, os

config = ConfigParser.ConfigParser()
config.readfp(open("config.conf", "r"))
config.read(CONFIG_PATH)
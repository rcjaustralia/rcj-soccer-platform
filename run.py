from rcj_soccer import application
import warnings
import logging
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    logging.warning(UserWarning("This is not a production ready server"))
    application.run("0.0.0.0", 5000)

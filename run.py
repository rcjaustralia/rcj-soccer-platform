from rcj_soccer import application
import logging
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    host = "0.0.0.0"
    port = 5000
    try:
        import bjoern
        bjoern.run(application, host, port)
    except ImportError:
        logging.warning(UserWarning("This is not a production ready server"))
        application.run(host, port)

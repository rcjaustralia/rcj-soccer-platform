from rcj_soccer import application
import logging
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    host = "0.0.0.0"
    port = 5000

    server_fn = type(application).run
    arguments = {
        "host": host,
        "port": port
    }
    logger.info("Starting app...")
    try:
        import waitress
        server_fn = waitress.serve
        logger.info("Using waitress")
        arguments["threads"] = 8
    except ImportError:
        pass
    try:
        import sanic
        server_fn = sanic.Sanic.run
        logger.info("Using sanic")
        arguments["workers"] = 8
    except ImportError:
        pass
    try:
        import bjoern
        server_fn = bjoern.run
        logger.info("Using bjoern")
    except ImportError:
        pass
    server_fn(application, **arguments)

logger.warn("Running run.py with name: ", __name__)

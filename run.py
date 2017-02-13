from rcj_soccer import application
import logging
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    host = "0.0.0.0"
    port = 5000

    server_fn = type(application).run
    try:
        import waitress
        server_fn = waitress.serve
    except ImportError:
        pass
    try:
        import sanic
        server_fn = sanic.Sanic.run
    except ImportError:
        pass
    try:
        import bjoern
        server_fn = bjoern.run
    except ImportError:
        pass
    server_fn(application, host, port)

from app import app as application
import loader
import bjoern

if __name__ == "__main__":
    bjoern.run(application, "0.0.0.0", 5000, reuse_port=True)

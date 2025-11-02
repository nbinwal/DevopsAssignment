from flask import Flask, jsonify
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import os
import logging
logging.basicConfig(level=logging.INFO)

flask_app = Flask(__name__)

APP_VERSION = os.getenv("APP_VERSION", "1.0")
APP_TITLE = os.getenv("APP_TITLE", "Devops for Cloud Assignment")

REQUEST_COUNT = Counter("requests_total", "Total number of requests to /get_info")

@flask_app.route("/get_info")
def get_info():
    REQUEST_COUNT.inc()
    pod_name = os.getenv("HOSTNAME", "unknown-pod")
    flask_app.logger.info(f"Request served by pod: {pod_name}")
    return jsonify({
        "APP_VERSION": APP_VERSION,
        "APP_TITLE": APP_TITLE
    })

@flask_app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

try:
    from asgiref.wsgi import WsgiToAsgi
    app = WsgiToAsgi(flask_app)
except ImportError:
    app = flask_app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

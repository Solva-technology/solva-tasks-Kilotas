import os
import logging
import json
from logging.handlers import RotatingFileHandler
from datetime import datetime

LOG_DIR = os.path.join(os.getcwd(), "logs")
LOG_PATH = os.path.join(LOG_DIR, "app.log")
os.makedirs(LOG_DIR, exist_ok=True)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        }

        if isinstance(record.args, dict):
            payload.update(record.args)
        return json.dumps(payload, ensure_ascii=False)

def setup_logging():
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    fh = RotatingFileHandler(LOG_PATH, maxBytes=5_000_000, backupCount=5)
    fh.setLevel(logging.INFO)
    fh.setFormatter(JsonFormatter())

    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    ch.setFormatter(JsonFormatter())

    root.addHandler(fh)
    root.addHandler(ch)
    return root

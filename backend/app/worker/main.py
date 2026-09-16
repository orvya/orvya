import logging
import time

from sqlalchemy import text

from app.db import engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("orvya.worker")


def run() -> None:
    logger.info("worker iniciado")
    while True:
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
        except Exception as exc:
            logger.warning("banco indisponivel para o worker: %s", type(exc).__name__)
        time.sleep(30)


if __name__ == "__main__":
    run()

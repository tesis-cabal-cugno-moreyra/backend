import logging
from time import time, sleep
import psycopg2
import environ

env = environ.Env()

try:
    environ.Env.read_env()
except FileNotFoundError:
    pass  # Log here!
check_timeout = env("POSTGRES_CHECK_TIMEOUT", default=30)
check_interval = env("POSTGRES_CHECK_INTERVAL", default=1)
interval_unit = "second" if check_interval == 1 else "seconds"
config = {
    "dbname": env("POSTGRES_DB", default="postgres"),
    "user": env("POSTGRES_USER", default="postgres"),
    "password": env("POSTGRES_PASSWORD", default=""),
    "host": env("DATABASE_URL", default="postgres")
}

start_time = time()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def pg_isready(host, user, password, dbname):
    while time() - start_time < check_timeout:
        try:
            conn = psycopg2.connect(**vars())
            logger.info("Postgres is ready! ✨ 💅")
            conn.close()
            return True
        except psycopg2.OperationalError:
            logger.info(f"Postgres isn't ready. Waiting for {check_interval} {interval_unit}...")
            sleep(check_interval)

    logger.error(f"We could not connect to Postgres within {check_timeout} seconds.")
    return False


pg_isready(**config)

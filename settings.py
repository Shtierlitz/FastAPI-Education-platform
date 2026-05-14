from envparse import Env

env = Env()
env.read_envfile(".env")

REAL_DATABASE_URL = env.str("REAL_DATABASE_URL")

TEST_DATABASE_URL = env.str("TEST_DATABASE_URL")


def to_sync_database_url(database_url: str) -> str:
    return database_url.replace("+asyncpg", "")

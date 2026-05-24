from envparse import Env

env = Env()
env.read_envfile(".env")

REAL_DATABASE_URL = env.str("REAL_DATABASE_URL")

TEST_DATABASE_URL = env.str("TEST_DATABASE_URL", default=REAL_DATABASE_URL)


def to_sync_database_url(database_url: str) -> str:
    return database_url.replace("+asyncpg", "")


APP_PORT = env.int("APP_PORT", default=8000)

ACCESS_TOKEN_EXPIRE_MINUTES = env.int("ACCESS_TOKEN_EXPIRE_MINUTES", default=30)
SECRET_KEY = env.str("SECRET_KEY")
ALGORITHM = env.str("ALGORITHM", default="HS256")

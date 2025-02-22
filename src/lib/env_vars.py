import os
from enum import Enum

from dotenv import load_dotenv

load_dotenv(override=True)


class Environment(Enum):
    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"
    TEST = "test"


class EnvVars:
    OPENAI_API_KEY: str
    ENV: str
    PORT: str

    def __init__(self):
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        env_value = os.getenv('ENV')
        self.ENV = Environment(
            env_value) if env_value in Environment._value2member_map_ else None
        self.PORT = os.getenv('PORT')
        self.DATABASE_URL = os.getenv('DATABASE_URL')

        # Run assertions to ensure the variables are not None and not empty
        self._assert_env_vars()

    def _assert_env_vars(self):
        assert self.OPENAI_API_KEY is not None and self.OPENAI_API_KEY.strip(
        ) != "", "OPENAI_API_KEY is not set or is empty."
        assert self.ENV is not None, f"ENV must be one of {list(Environment._value2member_map_.keys())}."
        assert self.PORT is not None and self.PORT.strip(
        ) != "", "PORT is not set or is empty."
        assert self.DATABASE_URL is not None and self.DATABASE_URL.strip(
        ) != "", "DATABASE_URL is not set or is empty."


env_vars = EnvVars()

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pydantic.types import SecretStr

class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="settings/.env", env_file_encoding="utf-8", extra="ignore"
    )

class OpenWeatherMapConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="OPEN") # env_prefix="" - с какой подстроки начинаются переменные

    WEATHERMAP_API: SecretStr

class RedisConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="REDIS_")

    HOST: SecretStr

class Config(BaseSettings): # Здесь объединяем все конфиги
    owm: OpenWeatherMapConfig = Field(default_factory=OpenWeatherMapConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)

    @classmethod
    def load(cls) -> "Config":
        return cls()
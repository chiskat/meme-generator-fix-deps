from pathlib import Path
from typing import Optional, Union

import toml
from pydantic import BaseModel

from .compat import model_dump, type_validate_python
from .dirs import get_config_file

config_file_path = get_config_file("config.toml")


class MemeConfig(BaseModel):
    load_builtin_memes: bool = True
    meme_dirs: list[Path] = []
    meme_disabled_list: list[str] = []


class ResourceConfig(BaseModel):
    resource_url: Optional[str] = None
    resource_urls: list[str] = [
        "https://raw.githubusercontent.com/MemeCrafters/meme-generator/",
        "https://mirror.ghproxy.com/https://raw.githubusercontent.com/MemeCrafters/meme-generator/",
        "https://cdn.jsdelivr.net/gh/MemeCrafters/meme-generator@",
        "https://fastly.jsdelivr.net/gh/MemeCrafters/meme-generator@",
        "https://raw.gitmirror.com/MemeCrafters/meme-generator/",
    ]


class GifConfig(BaseModel):
    gif_max_size: float = 10
    gif_max_frames: int = 100


class TranslatorConfig(BaseModel):
    baidu_trans_appid: str = ""
    baidu_trans_apikey: str = ""


class ServerConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 2233


class S3StorageConfig(BaseModel):
    enabled: bool = False
    endpoint_url: Optional[str] = None
    region: Optional[str] = None
    bucket: str = ""
    access_key_id: str = ""
    secret_access_key: str = ""
    session_token: Optional[str] = None
    result_prefix: str = "meme-generator/artifact"
    preview_prefix: str = "meme-generator/preview"
    public_base_url: Optional[str] = None
    path_style: bool = True


class RedisConfig(BaseModel):
    enabled: bool = False
    url: str = "redis://localhost:6379/0"
    key_prefix: str = "meme-generator:preview"


class StorageConfig(BaseModel):
    s3: S3StorageConfig = S3StorageConfig()
    redis: RedisConfig = RedisConfig()


class LogConfig(BaseModel):
    log_level: Union[int, str] = "INFO"


class Config(BaseModel):
    meme: MemeConfig = MemeConfig()
    resource: ResourceConfig = ResourceConfig()
    gif: GifConfig = GifConfig()
    translate: TranslatorConfig = TranslatorConfig()
    server: ServerConfig = ServerConfig()
    storage: StorageConfig = StorageConfig()
    log: LogConfig = LogConfig()

    @classmethod
    def load(cls) -> "Config":
        return type_validate_python(cls, toml.load(config_file_path))

    def dump(self):
        with open(config_file_path, "w", encoding="utf-8") as f:
            toml.dump(model_dump(self), f)


if not config_file_path.exists():
    meme_config = Config()
    config_file_path.write_text(
        "[meme]\nload_builtin_memes = true\n", encoding="utf8"
    )
else:
    meme_config = Config.load()

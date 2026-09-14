from typing import Literal, NamedTuple
from urllib.parse import quote
from uuid import uuid4

from .config import S3StorageConfig
from .exception import S3StorageError

_EXTENSIONS = {
    "image/gif": "gif",
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}

UploadKind = Literal["result", "preview"]


class S3UploadResult(NamedTuple):
    url: str
    object_key: str


def _normalize_prefix(prefix: str) -> str:
    return prefix.strip().strip("/")


def _build_object_key(
    config: S3StorageConfig,
    meme_key: str,
    media_type: str,
    upload_kind: UploadKind = "result",
) -> str:
    if upload_kind == "result":
        prefix = _normalize_prefix(config.result_prefix)
    else:
        prefix = _normalize_prefix(config.preview_prefix)
    extension = _EXTENSIONS.get(media_type, "bin")
    filename = f"{uuid4().hex}.{extension}"
    return f"{prefix}/{meme_key}/{filename}" if prefix else f"{meme_key}/{filename}"


def _build_public_url(config: S3StorageConfig, object_key: str) -> str:
    if public_base_url := config.public_base_url:
        return f"{public_base_url.rstrip('/')}/{quote(object_key, safe='/')}"

    encoded_object_key = quote(object_key, safe="/")

    if endpoint_url := config.endpoint_url:
        endpoint = endpoint_url.rstrip("/")
        if config.path_style:
            return f"{endpoint}/{config.bucket}/{encoded_object_key}"
        return f"{endpoint}/{encoded_object_key}"

    region = config.region or "us-east-1"
    return f"https://{config.bucket}.s3.{region}.amazonaws.com/{encoded_object_key}"


def upload_to_s3(
    content: bytes,
    media_type: str,
    meme_key: str,
    config: S3StorageConfig,
    upload_kind: UploadKind = "result",
) -> S3UploadResult:
    if not config.enabled:
        raise S3StorageError("S3 存储未启用，请在 config.toml 中配置 storage.s3")
    if not config.bucket:
        raise S3StorageError("S3 存储缺少 bucket 配置")

    try:
        import boto3
        from botocore.config import Config as BotoConfig
        from botocore.exceptions import BotoCoreError, ClientError
    except ImportError as e:
        raise S3StorageError(f"S3 依赖未安装：{e}") from e

    client_kwargs = {
        "config": BotoConfig(
            s3={"addressing_style": "path" if config.path_style else "auto"}
        )
    }
    if config.endpoint_url:
        client_kwargs["endpoint_url"] = config.endpoint_url
    if config.region:
        client_kwargs["region_name"] = config.region
    if bool(config.access_key_id) != bool(config.secret_access_key):
        raise S3StorageError("S3 access_key_id 与 secret_access_key 需要同时配置")
    if config.access_key_id and config.secret_access_key:
        client_kwargs["aws_access_key_id"] = config.access_key_id
        client_kwargs["aws_secret_access_key"] = config.secret_access_key
        if config.session_token:
            client_kwargs["aws_session_token"] = config.session_token

    object_key = _build_object_key(config, meme_key, media_type, upload_kind)

    try:
        client = boto3.client("s3", **client_kwargs)
        client.put_object(
            Bucket=config.bucket,
            Key=object_key,
            Body=content,
            ContentType=media_type,
        )
    except (BotoCoreError, ClientError) as e:
        raise S3StorageError(f"S3 上传失败：{e}") from e

    return S3UploadResult(
        url=_build_public_url(config, object_key),
        object_key=object_key,
    )

# meme-generator-next

本项目 fork 自 [MemeCrafters/meme-generator](https://github.com/MemeCrafters/meme-generator)。

特性升级：

- 处理了 `Pillow` 和 `pil-utils` 的依赖版本，以避免和 Astrbot 新版本不兼容；
- 依赖项包含 `pycairo`，因此在加载 [meme_emoji](https://github.com/anyliew/meme_emoji) 时不再提示缺少依赖；
- 支持自定义 `config.toml` 文件路径，详见 [配置文件路径](#配置文件路径)；
- 支持自动上传 S3 并返回 URL；
- 支持通过 Redis 连接，缓存预览图。

# 特性升级介绍

## 配置文件路径

作为包导入或 Docker 部署时，可通过 `MEME_GENERATOR_CONFIG_FILE` 指定配置文件路径，文件名不必为 `config.toml`：

```yaml
services:
  meme-generator:
    volumes:
      - ./config:/config
    environment:
      MEME_GENERATOR_CONFIG_FILE: /config/config.toml
```

命令行启动时，可使用 `--config-file` 参数指定配置文件路径：

```bash
# CLI 用法
meme --config-file /path/to/config.toml run

# Web Server
python -m meme_generator.app --config-file=/path/to/config.toml
```

兼容说明：旧版本的 `MEME_GENERATOR_CONFIG_DIR` 环境变量（目录形式）仍然有效，但已不推荐使用；`--config-dir` 参数已被 `--config-file` 取代。

## S3 存储

在 `config.toml` 中启用 S3 后，HTTP Server 会为每个表情新增一个 `/memes/{key}/url/` 端点。该端点的请求参数与原有的 `/memes/{key}/` 端点完全相同，生成成功后会自动上传到 S3，并返回 JSON：

```json
{
  "url": "https://cdn.example.com/meme-generator/artifact/petpet/xxx.gif",
  "meme_key": "petpet",
  "object_key": "meme-generator/artifact/petpet/xxx.gif"
}
```

生成结果的对象名格式为 `{result_prefix}/{meme_key}/{random_key}.{extension}`，预览图为 `{preview_prefix}/{meme_key}/{random_key}.{extension}`。其中 `random_key` 为 32 位 UUID 随机十六进制字符串，不包含日期。

生成结果和预览图分别使用 `result_prefix` 与 `preview_prefix`，没有通用对象前缀配置。

配置示例：

```toml
[storage.s3]
enabled = true
# 自定义 S3 兼容服务地址；AWS 官方 S3 可以留空
endpoint_url = "https://s3.example.com"
region = "ap-northeast-1"
bucket = "meme-generator"
access_key_id = "your-access-key-id"
secret_access_key = "your-secret-access-key"
# 生成结果前缀
result_prefix = "meme-generator/artifact"
# 预览图前缀
preview_prefix = "meme-generator/preview"
# 推荐配置为 bucket 的公开访问地址；留空时会根据 endpoint/region 生成 S3 URL
public_base_url = "https://cdn.example.com"
# 大多数 S3 兼容服务（MinIO、Cloudflare R2 等）需要 path_style = true
path_style = true
```

返回的 `url` 需要能被访问；如果使用私有 bucket，请将 `public_base_url` 指向具有读取权限的 CDN/反向代理，或自行生成预签名 URL。

Docker 部署时，也可以使用环境变量来配置：

```yaml
services:
  meme-generator:
    environment:
      S3_ENABLED: 'true'
      S3_ENDPOINT_URL: 'https://s3.example.com'
      S3_REGION: 'ap-northeast-1'
      S3_BUCKET: 'meme-generator'
      S3_ACCESS_KEY_ID: 'your-access-key-id'
      S3_SECRET_ACCESS_KEY: 'your-secret-access-key'
      S3_SESSION_TOKEN: ''
      S3_RESULT_PREFIX: 'meme-generator/artifact'
      S3_PREVIEW_PREFIX: 'meme-generator/preview'
      S3_PUBLIC_BASE_URL: 'https://cdn.example.com'
      S3_PATH_STYLE: 'true'
```

## Redis 预览缓存

启用 S3 和 Redis 后，每个表情都会新增 `GET /memes/{key}/preview/url/` 端点。第一次访问时会生成预览图并上传到 S3，然后将返回的公开 URL 写入 Redis；后续访问会直接返回缓存中的 URL：

```json
{
  "url": "https://cdn.example.com/meme-generator/preview/petpet/xxx.gif",
  "meme_key": "petpet"
}
```

Redis 配置示例：

```toml
[storage.redis]
enabled = true
url = "redis://localhost:6379/0"
key_prefix = "meme-generator:preview"
```

`key_prefix` 用于区分不同部署的缓存键。缓存写入时不设置过期时间；如果 Redis 配置了 `maxmemory-policy`，请避免选择会主动删除键的淘汰策略，或使用专门的 Redis 实例。

Docker 部署时，也可以使用环境变量来配置：

```yaml
services:
  meme-generator:
    environment:
      REDIS_ENABLED: 'true'
      REDIS_URL: 'redis://localhost:6379/0'
      REDIS_KEY_PREFIX: 'meme-generator:preview'
```

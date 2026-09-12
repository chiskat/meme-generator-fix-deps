# meme-generator-fix-deps

本项目 fork 自 [MemeCrafters/meme-generator](https://github.com/MemeCrafters/meme-generator)。

特性升级：

- 处理了 `Pillow` 和 `pil-utils` 的依赖版本，以避免和 Astrbot 新版本不兼容；
- 可以通过环境变量 `MEME_GENERATOR_CONFIG_DIR` 指定 `config.toml` 所在的目录。

# meme-generator-fix-deps

本项目 fork 自 [MemeCrafters/meme-generator](https://github.com/MemeCrafters/meme-generator)。

特性升级：

- 处理了 `Pillow` 和 `pil-utils` 的依赖版本，以避免和 Astrbot 新版本不兼容；
- 可以通过环境变量 `MEME_GENERATOR_CONFIG_DIR` 指定 `config.toml` 所在的目录，无配置文件时会自动生成一份；
- 如果通过命令行启动，也可以通过 `--config-dir` 参数指定 `config.toml` 所在的目录；
- 依赖项包含 `pycairo`，因此在加载 [meme_emoji](https://github.com/anyliew/meme_emoji) 时不再提示缺少依赖。

#! /usr/bin/env bash

config_dir="${MEME_GENERATOR_CONFIG_DIR:-$HOME/.config/meme_generator}"
mkdir -p "$config_dir"

envsubst < /app/config.toml.template > "$config_dir/config.toml"

exec python -m meme_generator.app

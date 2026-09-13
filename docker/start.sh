#!/usr/bin/env bash
set -euo pipefail

config_dir="${MEME_GENERATOR_CONFIG_DIR:-$HOME/.config/meme_generator}"

# Allow the container to be started as:
#   docker run ... image --config-dir /path/to/config
# Other commands are passed through so `docker run ... image bash` still works.
if [ "$#" -gt 0 ]; then
  case "$1" in
    --config-dir|--config-dir=*)
      while [ "$#" -gt 0 ]; do
        case "$1" in
          --config-dir)
            if [ "$#" -lt 2 ]; then
              echo "--config-dir requires a path" >&2
              exit 1
            fi
            config_dir="$2"
            shift 2
            ;;
          --config-dir=*)
            config_dir="${1#--config-dir=}"
            shift
            ;;
          *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
        esac
      done
      ;;
    *)
      exec "$@"
      ;;
  esac
fi

if [ -z "$config_dir" ]; then
  echo "Config directory must not be empty" >&2
  exit 1
fi

export MEME_GENERATOR_CONFIG_DIR="$config_dir"
mkdir -p "$config_dir"

config_file="$config_dir/config.toml"
if [ ! -f "$config_file" ]; then
    envsubst < /app/config.toml.template > "$config_file"
fi

exec python -m meme_generator.app --config-dir "$config_dir"

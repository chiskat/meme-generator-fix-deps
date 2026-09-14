#!/usr/bin/env bash
set -euo pipefail

if [ -n "${MEME_GENERATOR_CONFIG_FILE:-}" ]; then
  config_file="$MEME_GENERATOR_CONFIG_FILE"
elif [ -n "${MEME_GENERATOR_CONFIG_DIR:-}" ]; then
  # Backward compatibility with the deprecated directory-style configuration
  config_file="$MEME_GENERATOR_CONFIG_DIR/config.toml"
else
  config_file="$HOME/.config/meme_generator/config.toml"
fi

# Allow the container to be started as:
#   docker run ... image --config-file /path/to/config.toml
# Other commands are passed through so `docker run ... image bash` still works.
if [ "$#" -gt 0 ]; then
  case "$1" in
    --config-file|--config-file=*)
      while [ "$#" -gt 0 ]; do
        case "$1" in
          --config-file)
            if [ "$#" -lt 2 ]; then
              echo "--config-file requires a path" >&2
              exit 1
            fi
            config_file="$2"
            shift 2
            ;;
          --config-file=*)
            config_file="${1#--config-file=}"
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

if [ -z "$config_file" ]; then
  echo "Config file path must not be empty" >&2
  exit 1
fi

export MEME_GENERATOR_CONFIG_FILE="$config_file"
mkdir -p "$(dirname "$config_file")"

if [ ! -f "$config_file" ]; then
    envsubst < /app/config.toml.template > "$config_file"
fi

exec python -m meme_generator.app --config-file "$config_file"

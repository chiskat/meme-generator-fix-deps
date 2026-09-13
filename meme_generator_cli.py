"""CLI entry point that applies ``--config-dir`` before package imports."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

CONFIG_DIR_ENV = "MEME_GENERATOR_CONFIG_DIR"


def _apply_config_dir_option() -> None:
    parser = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
    parser.add_argument("--config-dir", dest="config_dir")
    args, remaining = parser.parse_known_args(sys.argv[1:])

    if args.config_dir:
        config_dir = Path(args.config_dir).expanduser()
        os.environ[CONFIG_DIR_ENV] = str(config_dir)

    argv = sys.argv[:1] if sys.argv else ["meme"]
    sys.argv[:] = [*argv, *remaining]


def main() -> None:
    _apply_config_dir_option()
    from meme_generator.cli import main

    main()


if __name__ == "__main__":
    main()

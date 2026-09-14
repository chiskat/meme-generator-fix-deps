"""CLI entry point that applies ``--config-file`` before package imports."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

CONFIG_FILE_ENV = "MEME_GENERATOR_CONFIG_FILE"


def _apply_config_file_option() -> None:
    parser = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
    parser.add_argument("--config-file", dest="config_file")
    args, remaining = parser.parse_known_args(sys.argv[1:])

    if args.config_file is not None:
        if not args.config_file:
            parser.error("--config-file must not be empty")
        config_file = Path(args.config_file).expanduser()
        os.environ[CONFIG_FILE_ENV] = str(config_file)

    argv = sys.argv[:1] if sys.argv else ["meme"]
    sys.argv[:] = [*argv, *remaining]


def main() -> None:
    _apply_config_file_option()
    from meme_generator.cli import main

    main()


if __name__ == "__main__":
    main()

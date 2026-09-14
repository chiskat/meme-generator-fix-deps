import argparse
import os
import sys
from pathlib import Path

CONFIG_FILE_ENV = "MEME_GENERATOR_CONFIG_FILE"


def _is_module_invocation(module_name: str) -> bool:
    orig_argv = getattr(sys, "orig_argv", [])
    try:
        option_index = orig_argv.index("-m")
    except ValueError:
        return False
    return (
        option_index + 1 < len(orig_argv) and orig_argv[option_index + 1] == module_name
    )


def _apply_config_file_option() -> None:
    if not _is_module_invocation("meme_generator.app"):
        return

    parser = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
    parser.add_argument("--config-file", dest="config_file")
    args, remaining = parser.parse_known_args(sys.argv[1:])

    if args.config_file is None:
        return
    if not args.config_file:
        parser.error("--config-file must not be empty")

    os.environ[CONFIG_FILE_ENV] = str(Path(args.config_file).expanduser())
    sys.argv[:] = [sys.argv[0], *remaining]


_apply_config_file_option()

from meme_generator.config import meme_config as config
from meme_generator.manager import add_meme as add_meme
from meme_generator.manager import get_meme as get_meme
from meme_generator.manager import get_meme_keys as get_meme_keys
from meme_generator.manager import get_memes as get_memes
from meme_generator.manager import load_meme as load_meme
from meme_generator.manager import load_memes as load_memes
from meme_generator.meme import CommandShortcut as CommandShortcut
from meme_generator.meme import Meme as Meme
from meme_generator.meme import MemeArgsModel as MemeArgsModel
from meme_generator.meme import MemeArgsType as MemeArgsType
from meme_generator.meme import MemeParamsType as MemeParamsType
from meme_generator.meme import ParserArg as ParserArg
from meme_generator.meme import ParserOption as ParserOption
from meme_generator.version import __version__ as __version__

if config.meme.load_builtin_memes:
    for path in (Path(__file__).parent / "memes").iterdir():
        load_meme(f"meme_generator.memes.{path.name}")
for meme_dir in config.meme.meme_dirs:
    load_memes(meme_dir)

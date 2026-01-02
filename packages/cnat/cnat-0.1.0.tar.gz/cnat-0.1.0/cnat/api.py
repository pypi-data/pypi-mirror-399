from dataclasses import dataclass
from pathlib import Path
import sys
import os

from .utils import warning
from . import cli


@dataclass
class Args:
    file: str
    lang: str
    get: bool
    keep: bool
    reverse: bool
    

def cnat(file: str, lang: str, reverse: bool = False,
         keep: bool = False, get: bool = False) -> Path|None:
    args    = Args(file, lang, get, keep, reverse)
    file    = str(args.file)
    native  = args.lang.strip().lower()
    reverse = args.reverse
    lang    = cli.detect_target_lang(file)

    if not lang:
        warning(f"unsupported file extension: {file}")
        sys.exit(1)

    mod    = cli.import_translator(native)
    script = cli.translate(file, mod, lang, native, reverse)

    if args.get: return script
    if not args.keep: os.remove(script)

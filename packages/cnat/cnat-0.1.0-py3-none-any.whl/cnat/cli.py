from pathlib import Path
import subprocess
import importlib
import argparse
import sys
import os
import re

from .utils import warning


EXT_TO_TARGET = {
    ".py": "python",
    ".go": "go",
    ".js": "javascript",
}

TARGET_RUNNERS = {
    "python": ["python"],
    "go": ["go", "run"],
    "javascript": ["node"],
}


def get_args():
    parser = argparse.ArgumentParser(description="Translate code to native language syntax.")
    parser.add_argument("file", help="Path to the code file")
    parser.add_argument("--lang", required=True, help="Native language to translate from (e.g. shona)")
    parser.add_argument("--run", action="store_true", help="Run the translated script")
    parser.add_argument("--keep", action="store_true", help="Keep the translated file")
    parser.add_argument("--reverse", action="store_true", help="Reverse translation (e.g., python to native)")
    return parser.parse_args()


def detect_target_lang(file_path):
    ext = Path(file_path).suffix
    return EXT_TO_TARGET.get(ext, None)


def import_translator(lang):
    try:
        return importlib.import_module(f"cnat.translators.{lang}")
    except ModuleNotFoundError:
        warning(f"translator for '{lang}' not found.")
        exit(1)


def tokenize(line):
    seps    = [".", ":", ",", "(", ")", "[", "]", "{", "}"]
    pattern = f"({'|'.join(map(re.escape, seps))})|\\s+"
    return re.split(pattern, line)


def translate(path, mod, lang, native, reverse=False):
    src        = Path(path).read_text()
    lines      = src.splitlines()
    translated = []

    token_map = {"python": mod.PY_TOKEN_MAP}
    token_map = {v: k for k, v in token_map[lang].items()} if reverse else token_map[lang]

    for line in lines:
        new_line = ""
        tokens   = re.findall(r'\w+|\W+', line)
        for token in tokens:
            new_line += token_map.get(token.strip(), token)
        translated.append(new_line)

    output_path = Path().cwd() / (f"{native}_"
                + path.split(os.sep)[-1])
    output_path.write_text("\n".join(translated))
    return output_path


def main():
    args    = get_args()
    file    = args.file
    native  = args.lang.strip().lower()
    reverse = args.reverse
    lang    = detect_target_lang(file)

    if not lang:
        warning(f"unsupported file extension: {file}")
        sys.exit(1)

    mod        = import_translator(native)
    translated = translate(file, mod, lang, native, reverse)

    if args.run:
        runner = TARGET_RUNNERS.get(lang)
        if not runner:
            warning(f"no runner defined for lang {lang!r}")
        else: subprocess.run([*runner, str(translated)])

    if not args.keep: os.remove(translated)


if __name__ == "__main__": main()

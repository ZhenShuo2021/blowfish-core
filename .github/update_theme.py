# /// script
# requires-python = ">=3.10,<=3.13"
# dependencies = [
#     "requests",
#     "colorama",
#     "gitignore_parser",
# ]
# ///

# This script is for a minimal replacement of any Hugo theme. The main functionality works like .gitignore.
# You can run the script with uv or any project manager supports PEP 723.

import argparse
import logging
import os
import shutil
import sys
from pathlib import Path
from colorama import init

from gitignore_parser import parse_gitignore

from utils import (
    download_and_extract,
    load_ignore_patterns,
    preserve_files,
    update_ignore_pattern,
    clear_directory,
    setup_logging,
    restore_files,
)

init(autoreset=True)


def copy_repository(source_dir: Path, ignore_file: str) -> None:
    logging.debug(f"Copying repository from {source_dir} with ignore file {ignore_file}")

    if not source_dir.exists() or not source_dir.is_dir():
        logging.error(f"Source directory does not exist: {source_dir}")
        sys.exit(1)

    if not os.path.exists(ignore_file):
        logging.error(f"Ignore file not found: {ignore_file}")
        sys.exit(1)

    matches = parse_gitignore(ignore_file)

    for root, dirs, files in os.walk(source_dir):
        rel_path = os.path.relpath(root, source_dir)

        for file in files:
            src_path = os.path.join(root, file)

            if matches(os.path.abspath(src_path)):
                logging.debug(f"Skipping file (matched by gitignore): {os.path.relpath(src_path, source_dir)}")
                continue

            dst_path = file if rel_path == "." else os.path.join(rel_path, file)
            Path(dst_path).parent.mkdir(parents=True, exist_ok=True)

            try:
                shutil.copy2(src_path, dst_path)
                logging.debug(f"Copied file: {os.path.relpath(src_path, source_dir)} -> {dst_path}")
            except Exception as e:
                logging.error(f"Failed to copy file {os.path.relpath(src_path, source_dir)}: {e}")
                sys.exit(1)

        dirs_to_remove = []
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if matches(os.path.abspath(dir_path)):
                logging.debug(f"Skipping directory (matched by gitignore): {os.path.relpath(dir_path, source_dir)}")
                dirs_to_remove.append(dir_name)

        for dir_name in dirs_to_remove:
            dirs.remove(dir_name)

    logging.info(f"Repository copy completed from {source_dir} to root directory")


def main() -> None:
    ORIGINAL_REPO_URL = "https://github.com/nunocoracao/blowfish"
    REPO_NAME = "blowfish"

    # .gitignore alike ignore file
    IGNORE_FILE = os.path.join(".github", ".theme_ignore")

    # source file extract destination
    SOURCE_DIR = Path(".github") / ".temp_repo"

    # do not delete these files while clearing (only prevent from clearing, will still covered by source code files)
    IGNORE_CLEAR = [".git", ".github", ".venv", ".vscode", "README.md", "requirements.txt", str(SOURCE_DIR)]

    # files to preserve, will be restored before final clearing job
    PRESERVE_FILES = [
        "README.md",
        "foo/bar",
        "LICENSE",
        os.path.join(".github", ".temp_repo"),
        os.path.join("layouts", "_default", "foo", "bar.txt"),
        os.path.join("layouts", "_default", "foo", "bar"),
    ]

    # temporary path for PRESERVE_FILE
    PRESERVE_ROOT = Path(".github") / "temp"

    # check ignore file exists
    PATTERNS = load_ignore_patterns(IGNORE_FILE)

    if SOURCE_DIR.exists():
        logging.debug(f"Removing existing source directory: {SOURCE_DIR}")
        shutil.rmtree(SOURCE_DIR)

    if PRESERVE_ROOT.exists():
        logging.debug(f"Removing existing source directory: {PRESERVE_ROOT}")
        shutil.rmtree(PRESERVE_ROOT)

    SOURCE_DIR.mkdir(parents=True, exist_ok=True)

    preserve_files(PRESERVE_ROOT, PRESERVE_FILES)
    download_and_extract(ORIGINAL_REPO_URL, REPO_NAME, SOURCE_DIR)
    original_ignore_file = update_ignore_pattern(SOURCE_DIR, PATTERNS)

    clear_directory(IGNORE_CLEAR)
    copy_repository(SOURCE_DIR, str(SOURCE_DIR / ".gitignore"))
    restore_files(PRESERVE_ROOT, PRESERVE_FILES)

    # restore .gitignore
    with open(".gitignore", "w") as f:
        f.write(original_ignore_file)

    if SOURCE_DIR.exists():
        logging.debug(f"Cleaning up source directory: {SOURCE_DIR}")
        shutil.rmtree(SOURCE_DIR)

    logging.debug("Update completed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update script with logging control.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output (DEBUG level)")
    group.add_argument("-q", "--quiet", action="store_true", help="Suppress all output except errors")

    args = parser.parse_args()

    if args.quiet:
        log_level = logging.ERROR
    elif args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    setup_logging(log_level)
    main()

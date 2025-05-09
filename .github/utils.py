import logging
import logging.config
import shutil
import sys
import tarfile
from pathlib import Path
from typing import Any, Callable

import gitignore_parser
import requests
from colorama import Fore, Style


class ColorFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": Fore.LIGHTBLACK_EX,
        "INFO": Fore.WHITE,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        log_message = super().format(record)
        return f"{self.COLORS.get(record.levelname, Fore.WHITE)}{log_message}{Style.RESET_ALL}"


def setup_logging(log_level: int) -> None:
    logging_config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "colored": {
                "()": ColorFormatter,
                "format": "%(asctime)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%dT%H:%M:%S%z",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "colored",
                "stream": sys.stdout,
            },
        },
        "root": {
            "handlers": ["console"],
            "level": log_level,
        },
    }
    logging.config.dictConfig(logging_config)


def preserve_files(preserve_root: Path, preserve_files: list[str]) -> None:
    for relative_path in preserve_files:
        src = Path(relative_path)
        if src.exists():
            dest = preserve_root / relative_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(src, dest)
            logging.debug(f"File preserved: {relative_path}")
        else:
            logging.warning(f"File to preserve not found: {relative_path}")


def restore_files(preserve_root: Path, preserve_files: list[str]) -> None:
    for relative_path in preserve_files:
        src = preserve_root / relative_path
        if src.exists():
            dest = Path(relative_path)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(src, dest)
            logging.debug(f"File restored: {relative_path}")
        else:
            logging.warning(f"Cannot restore, temporary file not found: {src}")
    if preserve_root.exists():
        try:
            shutil.rmtree(preserve_root)
            logging.debug(f"Temporary directory removed: {preserve_root}")
        except Exception as e:
            logging.error(f"Could not remove temporary directory {preserve_root}: {e}")
            sys.exit(1)


def download_and_extract(repo_url: str, repo_name: str, source_dir: Path) -> None:
    try:
        logging.info("Start downloading source code...")
        response = requests.get(f"{repo_url}/archive/refs/heads/main.tar.gz")
        response.raise_for_status()

        archive_path = Path(".github") / "source-code.tar.gz"
        with archive_path.open("wb") as f:
            f.write(response.content)
        logging.info(f"Download completed: {archive_path}")

        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(source_dir, filter="data")
        archive_path.unlink()

        extracted_dir = source_dir / f"{repo_name}-main"
        temp_dir = source_dir.with_name(f"{source_dir.name}_temp")
        shutil.move(str(extracted_dir), str(temp_dir))
        shutil.rmtree(source_dir)
        shutil.move(str(temp_dir), str(source_dir))
        logging.debug(f"Extraction completed: {source_dir}")

    except Exception as e:
        logging.error(f"Download or extraction failed: {e!s}")
        sys.exit(1)


def update_ignore_pattern(source_dir: Path, patterns: list[str]) -> str:
    """Update the .gitignore, and return the original file for backup"""
    path = source_dir / ".gitignore"
    original = path.read_text(encoding="utf-8")
    with path.open("a") as f:
        if original and not original.endswith("\n"):
            f.write("\n")
        for p in patterns:
            f.write(p + "\n")
    return original


def clear_directory(ignore_clear: list[str]) -> None:
    logging.debug("Start clearing directory")
    for item in Path(".").iterdir():
        if item.name not in ignore_clear:
            if item.is_dir():
                shutil.rmtree(item)
                logging.debug(f"Directory removed: {item}")
            else:
                item.unlink()
                logging.debug(f"File removed: {item}")


def load_ignore_patterns(ignore_file: str) -> list[str]:
    patterns = []
    ignore_file_path = Path(ignore_file)
    if ignore_file_path.exists():
        try:
            with open(ignore_file_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    patterns.append(line)
            logging.debug(f"Load ignore file {ignore_file} successfully")
        except Exception as e:
            logging.warning(f"Could not read ignore file {ignore_file}: {e}")
    else:
        logging.error(f"Ignore file '{ignore_file}' not found. No user-defined ignore patterns loaded.")
        sys.exit(1)
    return patterns


def load_gitignore_patterns(ignore_file: str) -> Callable[[str], bool]:
    return gitignore_parser.parse_gitignore(ignore_file)


def should_exclude_path(path: str, ignore_parser: Callable[[str], bool], base_dir: Path) -> bool:
    return ignore_parser(path)

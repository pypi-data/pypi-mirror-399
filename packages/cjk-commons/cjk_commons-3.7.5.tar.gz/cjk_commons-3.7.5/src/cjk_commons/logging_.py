import logging
import sys
from pathlib import Path

import loguru


def add_logging_arguments(parser) -> None:
    """Добавить аргументы для логирования"""

    parser.add_argument(
        "-l",
        "--level",
        help="Set log's level",
        nargs="?",
    )
    parser.add_argument(
        "--log-file",
        help="Set log file",
        nargs="?",
    )
    parser.add_argument(
        "--log-file-level",
        help="Set log file's level",
        nargs="?",
    )


def add_loggers(args, logger: loguru.logger, log_file_name: str = "") -> None:
    """Добавить логеры"""

    if args.level is not None:
        level_str = args.level
    else:
        level_str = "INFO"

    level_str = level_str.upper()
    level_int = getattr(logging, level_str, None)

    if not isinstance(level_int, int):
        raise ValueError(f"Invalid log level '{level_str}'")

    logger.remove()

    logger.add(sys.stderr, level=level_str)

    if args.log_file is not None:
        log_file_path = Path(args.log_file)

        if log_file_path.is_dir():
            if Path(log_file_name).stem == log_file_name:
                log_file_name += ".log"

            log_file_path = Path(log_file_path, log_file_name)

        if args.log_file_level is not None:
            log_file_level_str = args.log_file_level
        else:
            log_file_level_str = "INFO"

        log_file_level_str = log_file_level_str.upper()
        log_file_level_int = getattr(logging, log_file_level_str, None)

        if not isinstance(log_file_level_int, int):
            raise ValueError(f"Invalid log file level '{log_file_level_str}'")

        logger.add(log_file_path, level=log_file_level_str)

"""
Utility script to clean up corrupted Celery Beat schedule files.

This script can be run manually to remove corrupted celerybeat-schedule files
when Celery Beat fails to start due to EOFError or other corruption issues.

Usage:
    python scripts/cleanup_celery_beat.py
    python scripts/cleanup_celery_beat.py --schedule-file custom-schedule
"""

import argparse
import sys
from pathlib import Path
import shutil
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def cleanup_celery_beat_schedule(schedule_filename: str = "celerybeat-schedule", base_dir: Path = None):
    """
    Remove all Celery Beat schedule files to allow recreation.
    
    Args:
        schedule_filename: Base name of the schedule file (default: celerybeat-schedule)
        base_dir: Directory where schedule files are located (default: current directory)
    """
    if base_dir is None:
        base_dir = Path.cwd()
    else:
        base_dir = Path(base_dir)
    
    schedule_path = base_dir / schedule_filename
    
    # Check for common shelve file extensions
    schedule_files = [
        schedule_path,
        base_dir / f"{schedule_filename}.dat",
        base_dir / f"{schedule_filename}.dir",
        base_dir / f"{schedule_filename}.bak",
    ]
    
    removed_count = 0
    for file_path in schedule_files:
        if file_path.exists():
            try:
                if file_path.is_file():
                    file_path.unlink()
                    logger.info(f"Removed: {file_path}")
                    removed_count += 1
                elif file_path.is_dir():
                    shutil.rmtree(file_path)
                    logger.info(f"Removed directory: {file_path}")
                    removed_count += 1
            except Exception as e:
                logger.error(f"Failed to remove {file_path}: {e}")
        else:
            logger.debug(f"File does not exist: {file_path}")
    
    if removed_count > 0:
        logger.info(f"Successfully removed {removed_count} schedule file(s).")
        logger.info("Celery Beat will recreate the schedule files on next start.")
    else:
        logger.info("No schedule files found to remove.")


def main():
    parser = argparse.ArgumentParser(
        description="Clean up corrupted Celery Beat schedule files"
    )
    parser.add_argument(
        "--schedule-file",
        default="celerybeat-schedule",
        help="Base name of the schedule file (default: celerybeat-schedule)"
    )
    parser.add_argument(
        "--directory",
        type=str,
        help="Directory where schedule files are located (default: current directory)"
    )
    
    args = parser.parse_args()
    
    base_dir = Path(args.directory) if args.directory else None
    
    try:
        cleanup_celery_beat_schedule(args.schedule_file, base_dir)
        return 0
    except Exception as e:
        logger.error(f"Error cleaning up schedule files: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())


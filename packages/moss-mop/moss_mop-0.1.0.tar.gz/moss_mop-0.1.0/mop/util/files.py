import os
import sys

from ascii_colors import ASCIIColors


def file_size_format(size: int) -> str:
    power = 2 ** 10
    n = 0
    power_labels = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return f"{size:.2f} {power_labels[n]}B"


def check_env_file():
    if not os.path.exists('.env'):
        warning_msg = "Warning: Startup directory must contain .env file for multi-instance support."
        ASCIIColors.yellow(warning_msg)

        if sys.stdin.isatty():
            response = input("Do you want to continue? [y/N]: ")
            if response.lower() != "y":
                ASCIIColors.red("Server startup cancelled")
                return False
    return True
import argparse

from ascii_colors import ASCIIColors

from mop.conf import settings
from mop import __version__ as core_version


def parse_args(is_uvicorn_mode: bool=False):
    parser = argparse.ArgumentParser(
        description="FastAPI Server with separate working and input directories"
    )

    parser.add_argument(
        "--host",
        default=settings.HOST,
        help="Server host (default: from env or 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=settings.PORT,
        help="Server port (default: from env or 8000)"
    )
    args = parser.parse_args()
    return args

def display_splash_screen(args: argparse.Namespace):
    ASCIIColors.cyan(f"""
        ╔══════════════════════════════════════════════════════════════╗
        ║                   🚀 MoP Server v{core_version}                      ║
        ║          -------------------------------------------         ║
        ╚══════════════════════════════════════════════════════════════╝
        """)
    ASCIIColors.magenta("\n📡 Server Configuration:")
    ASCIIColors.white("    ├─ Host: ", end="")
    ASCIIColors.yellow(f"{args.host}")
    ASCIIColors.white("    ├─ Port: ", end="")
    ASCIIColors.yellow(f"{args.port}")
    ASCIIColors.white("    ├─ Address: ", end="")
    ASCIIColors.yellow(f"http://{args.host}:{args.port}")
    ASCIIColors.white("    ├─ Docs: ", end="")
    ASCIIColors.yellow(f"http://{args.host}:{args.port}/api/v1/docs")

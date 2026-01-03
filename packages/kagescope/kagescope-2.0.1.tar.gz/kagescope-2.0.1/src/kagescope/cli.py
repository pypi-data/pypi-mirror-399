import argparse
from pathlib import Path
from .ui import (
    select_language,
    show_banner,
    show_purpose,
    ask_domains,
    ask_output_dir,
)
from .core import run_recon
from .utils import ensure_tools

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-t", nargs="+")
    args = parser.parse_args()

    ensure_tools()

    if args.t:
        domains = args.t
        out = Path("outputs")
    else:
        lang = select_language()
        show_banner()
        show_purpose(lang)
        out = Path(ask_output_dir())
        domains = ask_domains()

    run_recon(domains, out)

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rich.console import Console

from .ui import banner, pick_language_and_targets
from .core import run_pipeline

console = Console()


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="kagescope",
        description="Low-noise recon CLI (subdomains, live, api, js, ports, tech).",
    )
    p.add_argument(
        "-t",
        "--targets",
        nargs="+",
        metavar="DOMAIN",
        help="Targets (space-separated). Example: google.com github.com",
    )
    p.add_argument(
        "-o",
        "--out",
        default="outputs",
        help="Output base directory (default: outputs)",
    )
    p.add_argument(
        "--lang",
        choices=["tr", "en"],
        help="Force language (tr/en). If omitted, interactive prompt is shown in UI mode.",
    )
    return p


def main() -> None:
    args = build_parser().parse_args()

    # Non-UI mode: user provided targets via -t
    non_ui = bool(args.targets)

    if non_ui:
        lang = args.lang or "en"
        targets = [t.strip() for t in args.targets if t.strip()]
        out_base = Path(args.out)
        banner(lang=lang)
        summary = run_pipeline(targets=targets, out_base=out_base, lang=lang, show_progress=True)
        console.print(summary.render())
        console.print(f"[green]Saved to:[/green] {summary.out_dir}")
        return

    # UI mode (no -t)
    lang, out_base, targets = pick_language_and_targets(default_out=args.out)
    banner(lang=lang)
    summary = run_pipeline(targets=targets, out_base=Path(out_base), lang=lang, show_progress=True)
    console.print(summary.render())
    console.print(f"[green]Saved to:[/green] {summary.out_dir}")


if __name__ == "__main__":
    main()

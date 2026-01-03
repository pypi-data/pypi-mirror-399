import re
from pathlib import Path
from rich.console import Console
from rich.progress import track
from .utils import run_cmd

console = Console()

API_PATHS = ["/api", "/api/v1", "/api/v2", "/health", "/status"]

JS_REGEX = re.compile(
    r"(api[_-]?key|token|secret|password|authorization)",
    re.IGNORECASE
)

def detect_tech(hosts: list[str]) -> list[str]:
    return run_cmd(["httpx", "-silent", "-tech-detect"] + hosts)

def scan_ports(domain: str) -> list[str]:
    return run_cmd([
        "naabu",
        "-host", domain,
        "-top-ports", "100",
        "-silent"
    ])

def scan_js_leaks(hosts: list[str]) -> list[str]:
    leaks = []
    js_urls = []

    for h in hosts:
        js_urls += run_cmd([
            "httpx",
            "-silent",
            "-mc", "200",
            "-match-regex", r"\.js",
            "-u", h
        ])

    for js in set(js_urls):
        content = run_cmd(["curl", "-s", js])
        for line in content:
            if JS_REGEX.search(line):
                leaks.append(f"{js} :: {line.strip()}")

    return leaks

def api_check(hosts: list[str]) -> list[str]:
    hits = []
    for h in hosts:
        for p in API_PATHS:
            hits += run_cmd([
                "httpx",
                "-silent",
                "-status-code",
                "-mc", "200,301,302,401,403",
                "-u", h + p
            ])
    return hits

def run_recon(domains: list[str], out_root: Path):
    out_root.mkdir(parents=True, exist_ok=True)

    for domain in domains:
        ddir = out_root / domain
        ddir.mkdir(exist_ok=True)

        subs = sorted(set(
            run_cmd(["subfinder", "-d", domain, "-silent"]) +
            run_cmd(["assetfinder", "--subs-only", domain])
        ))
        (ddir / "subs.txt").write_text("\n".join(subs))

        live_raw = run_cmd([
            "httpx",
            "-silent",
            "-status-code",
            "-mc", "200,301,302,401,403"
        ] + subs)

        live = [l.split()[0] for l in live_raw]
        (ddir / "live.txt").write_text("\n".join(live))

        tech = detect_tech(live)
        ports = scan_ports(domain)
        js_leaks = scan_js_leaks(live)
        api_hits = api_check(live)

        (ddir / "tech.txt").write_text("\n".join(tech))
        (ddir / "ports.txt").write_text("\n".join(ports))
        (ddir / "js_leaks.txt").write_text("\n".join(js_leaks))
        (ddir / "api_hits.txt").write_text("\n".join(api_hits))

        console.print(
            f"[green]✔ {domain}[/green] "
            f"subs={len(subs)} "
            f"live={len(live)} "
            f"tech={len(tech)} "
            f"ports={len(ports)} "
            f"js_leaks={len(js_leaks)} "
            f"api_hits={len(api_hits)}"
        )

    console.print(f"\n[green]Results saved to:[/green] {out_root.resolve()}")

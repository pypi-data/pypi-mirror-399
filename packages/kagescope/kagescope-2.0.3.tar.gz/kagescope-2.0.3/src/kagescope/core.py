from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import re
import subprocess
from typing import Iterable

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn

console = Console()

STATUS_KEEP = {"200", "301", "302", "401", "403"}
CRITICAL_PORTS = "21,22,23,25,53,80,110,143,443,445,3306,5432,6379,8080,8443"
API_PATHS = ["/api", "/api/v1", "/v1", "/health", "/swagger", "/swagger/index.html", "/openapi.json"]
JS_KEYWORDS = [
    "api_key", "apikey", "secret", "token", "bearer", "authorization", "client_secret",
    "aws_access_key_id", "aws_secret_access_key", "private_key", "x-api-key"
]


def _run(cmd: list[str], stdin: str | None = None) -> str:
    p = subprocess.run(
        cmd,
        input=stdin,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    return p.stdout.strip()


def _ensure_tools() -> None:
    # we assume user installs: subfinder, assetfinder, httpx, nmap
    # optional: (none)
    return


def discover_subdomains(domain: str) -> list[str]:
    out = set()
    out.update(_run(["subfinder", "-d", domain, "-silent"]).splitlines())
    out.update(_run(["assetfinder", "--subs-only", domain]).splitlines())
    return sorted(x for x in out if x)


def probe_http_status(hosts: list[str]) -> dict[str, str]:
    """
    httpx output assumed: https://host [200] ...
    we keep only host + status
    """
    raw = _run(["httpx", "-silent", "-status-code"], "\n".join(hosts))
    live: dict[str, str] = {}
    for line in raw.splitlines():
        m = re.search(r"(https?://\S+)\s+\[(\d{3})\]", line)
        if not m:
            continue
        url, code = m.group(1), m.group(2)
        if code in STATUS_KEEP:
            live[url] = code
    return live


def tech_detect(urls: list[str]) -> list[str]:
    raw = _run(["httpx", "-silent", "-tech-detect"], "\n".join(urls))
    return [x for x in raw.splitlines() if x.strip()]


def api_check(urls: list[str]) -> dict[str, str]:
    found: dict[str, str] = {}
    for base in urls:
        for p in API_PATHS:
            raw = _run(["httpx", "-silent", "-status-code", "-path", p], base)
            m = re.search(r"(https?://\S+)\s+\[(\d{3})\]", raw)
            if not m:
                continue
            full, code = m.group(1), m.group(2)
            if code in STATUS_KEEP:
                found[full] = code
    return found


def js_leak_scan(urls: list[str], limit: int = 50) -> list[str]:
    """
    Low-noise approach:
    - Use httpx to extract JS URLs (if supported via -extract-regex),
      otherwise fallback: try / and grep for .js references.
    """
    hits: list[str] = []
    # lightweight: fetch homepage only for each url
    for u in urls[:limit]:
        html = _run(["httpx", "-silent", "-path", "/"], u)
        # find js files in HTML
        js_urls = set(re.findall(r'https?://[^"\']+\.js(?:\?[^"\']*)?', html))
        for js in list(js_urls)[:10]:
            body = _run(["httpx", "-silent"], js)
            lowered = body.lower()
            if any(k in lowered for k in JS_KEYWORDS):
                hits.append(js)
    return sorted(set(hits))


def critical_port_scan(domain: str) -> list[str]:
    raw = _run(["nmap", "-Pn", "--open", "-p", CRITICAL_PORTS, domain])
    lines = []
    for line in raw.splitlines():
        if "/tcp" in line and "open" in line:
            lines.append(line.strip())
    return lines


@dataclass
class Summary:
    targets: list[str]
    out_dir: str
    subdomains: int
    live: int
    api_hits: int
    js_hits: int
    tech_lines: int
    open_ports: int

    def render(self) -> str:
        return (
            f"[green]Summary[/green]\n"
            f"Targets: {', '.join(self.targets)}\n"
            f"Subdomains: {self.subdomains}\n"
            f"Live (kept {sorted(STATUS_KEEP)}): {self.live}\n"
            f"API hits: {self.api_hits}\n"
            f"JS hints: {self.js_hits}\n"
            f"Tech lines: {self.tech_lines}\n"
            f"Open critical ports: {self.open_ports}\n"
        )


def run_pipeline(targets: list[str], out_base: Path, lang: str, show_progress: bool = True) -> Summary:
    _ensure_tools()
    out_base.mkdir(parents=True, exist_ok=True)

    # Single run folder (no timestamp spam): outputs/<first_target> if one, else outputs/multi
    folder_name = targets[0] if len(targets) == 1 else "multi"
    out_dir = out_base / folder_name
    out_dir.mkdir(parents=True, exist_ok=True)

    all_subs: list[str] = []
    all_live: dict[str, str] = {}
    all_tech: list[str] = []
    all_api: dict[str, str] = {}
    all_js: list[str] = []
    all_ports: list[str] = []

    progress = Progress(
        SpinnerColumn(style="green"),
        TextColumn("[white]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console,
    ) if show_progress else None

    def step(desc: str, fn):
        if progress:
            task = progress.add_task(desc, total=1)
            res = fn()
            progress.update(task, advance=1)
            return res
        return fn()

    if progress:
        progress.start()

    try:
        for t in targets:
            subs = step(f"Subdomain discovery: {t}", lambda: discover_subdomains(t))
            all_subs.extend(subs)

            live = step(f"Live probe (httpx): {t}", lambda: probe_http_status(subs or [t]))
            all_live.update(live)

            tech = step(f"Tech fingerprint: {t}", lambda: tech_detect(list(live.keys()) or [f"https://{t}"]))
            all_tech.extend(tech)

            api = step(f"API checks: {t}", lambda: api_check(list(live.keys()) or [f"https://{t}"]))
            all_api.update(api)

            js = step(f"JS hints scan: {t}", lambda: js_leak_scan(list(live.keys()) or [f"https://{t}"]))
            all_js.extend(js)

            ports = step(f"Critical ports (nmap): {t}", lambda: critical_port_scan(t))
            all_ports.extend(ports)

    finally:
        if progress:
            progress.stop()

    # Dedup + write minimal files
    subs_u = sorted(set(all_subs))
    live_lines = [f"{u} {code}" for u, code in sorted(all_live.items())]
    api_lines = [f"{u} {code}" for u, code in sorted(all_api.items())]
    js_u = sorted(set(all_js))
    tech_u = [x for x in all_tech if x.strip()]
    ports_u = sorted(set(all_ports))

    (out_dir / "subs.txt").write_text("\n".join(subs_u) + ("\n" if subs_u else ""), encoding="utf-8")
    (out_dir / "live.txt").write_text("\n".join(live_lines) + ("\n" if live_lines else ""), encoding="utf-8")
    (out_dir / "api.txt").write_text("\n".join(api_lines) + ("\n" if api_lines else ""), encoding="utf-8")
    (out_dir / "js_hints.txt").write_text("\n".join(js_u) + ("\n" if js_u else ""), encoding="utf-8")
    (out_dir / "tech.txt").write_text("\n".join(tech_u) + ("\n" if tech_u else ""), encoding="utf-8")
    (out_dir / "ports.txt").write_text("\n".join(ports_u) + ("\n" if ports_u else ""), encoding="utf-8")

    summary = Summary(
        targets=targets,
        out_dir=str(out_dir),
        subdomains=len(subs_u),
        live=len(all_live),
        api_hits=len(all_api),
        js_hits=len(js_u),
        tech_lines=len(tech_u),
        open_ports=len(ports_u),
    )
    (out_dir / "summary.json").write_text(json.dumps(summary.__dict__, indent=2), encoding="utf-8")
    return summary

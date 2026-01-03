import subprocess
from shutil import which

REQUIRED_TOOLS = [
    "subfinder",
    "assetfinder",
    "httpx",
    "naabu",
    "curl"
]

def ensure_tools():
    missing = [t for t in REQUIRED_TOOLS if which(t) is None]
    if missing:
        raise RuntimeError(f"Missing required tools: {', '.join(missing)}")

def run_cmd(cmd: list[str]) -> list[str]:
    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True
    )
    return [l.strip() for l in proc.stdout.splitlines() if l.strip()]

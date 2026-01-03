from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

console = Console()

ASCII = r"""

 ____  __.                       _________                           
|    |/ _|____     ____   ____  /   _____/ ____  ____ ______   ____  
|      < \__  \   / ___\_/ __ \ \_____  \_/ ___\/  _ \\____ \_/ __ \ 
|    |  \ / __ \_/ /_/  >  ___/ /        \  \__(  <_> )  |_> >  ___/ 
|____|__ (____  /\___  / \___  >_______  /\___  >____/|   __/ \___  >
        \/    \//_____/      \/        \/     \/      |__|        \/ 
"""


def banner(lang: str = "en") -> None:
    console.print(Text(ASCII, style="green"))
    if lang == "tr":
        body = (
            "Amaç:\n"
            "• Subdomain toplar\n"
            "• Live hostları tespit eder (200/301/302/401/403)\n"
            "• API endpoint kontrolü yapar\n"
            "• JS dosyalarında hızlı sızıntı izi arar\n"
            "• Kritik portları kontrol eder\n"
            "• Hızlı teknoloji tespiti yapar\n\n"
            "Kullanım:\n"
            "  kagescope                (UI)\n"
            "  kagescope -t google.com github.com   (CLI)\n"
        )
    else:
        body = (
            "Purpose:\n"
            "• Collect subdomains\n"
            "• Detect live hosts (200/301/302/401/403)\n"
            "• Check common API endpoints\n"
            "• Quick JS leak hints scan\n"
            "• Scan critical ports\n"
            "• Fast technology fingerprinting\n\n"
            "Usage:\n"
            "  kagescope                (UI)\n"
            "  kagescope -t google.com github.com   (CLI)\n"
        )

    console.print(Panel(Text(body, style="white"), border_style="green"))


def pick_language_and_targets(default_out: str = "outputs") -> tuple[str, str, list[str]]:
    console.print(Panel("1 Türkçe\n2 English", title="Language / Dil", border_style="green"))
    choice = Prompt.ask("Select [1/2]", default="1").strip()
    lang = "tr" if choice == "1" else "en"

    if lang == "tr":
        out_base = Prompt.ask("Çıktı klasörü", default=default_out).strip() or default_out
        raw = Prompt.ask("Domain(ler) (ör: google.com github.com)").strip()
    else:
        out_base = Prompt.ask("Output folder", default=default_out).strip() or default_out
        raw = Prompt.ask("Targets (e.g., google.com github.com)").strip()

    targets = [t.strip() for t in raw.replace(",", " ").split() if t.strip()]
    return lang, out_base, targets

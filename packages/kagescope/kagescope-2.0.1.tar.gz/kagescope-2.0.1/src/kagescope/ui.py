from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

GREEN = "green"
WHITE = "white"

ASCII = r"""
 ____  __.                       _________                           
|    |/ _|____     ____   ____  /   _____/ ____  ____ ______   ____  
|      < \__  \   / ___\_/ __ \ \_____  \_/ ___\/  _ \\____ \_/ __ \ 
|    |  \ / __ \_/ /_/  >  ___/ /        \  \__(  <_> )  |_> >  ___/ 
|____|__ (____  /\___  / \___  >_______  /\___  >____/|   __/ \___  >
        \/    \//_____/      \/        \/     \/      |__|        \/ 
"""

def select_language() -> str:
    console.print(
        Panel("1 Türkçe\n2 English", title="Language / Dil", border_style=GREEN)
    )
    return "tr" if Prompt.ask("Select [1/2]", default="1") == "1" else "en"

def show_banner():
    console.print(f"[{GREEN}]{ASCII}[/{GREEN}]")

def show_purpose(lang: str):
    if lang == "tr":
        text = (
            "kageScope pasif bir recon aracıdır.\n\n"
            "• Subdomain toplar\n"
            "• Live hostları tespit eder (200/301/302/401/403)\n"
            "• API endpoint kontrolü yapar\n"
            "• JavaScript dosyalarında sızıntı arar\n"
            "• Sadece kritik portları kontrol eder\n"
            "• Hızlı teknoloji tespiti yapar\n\n"
            "Amaç: Minimum gürültü, maksimum görünürlük."
        )
    else:
        text = (
            "kageScope is a passive reconnaissance tool.\n\n"
            "• Subdomain discovery\n"
            "• Live host detection (200/301/302/401/403)\n"
            "• API endpoint checks\n"
            "• JavaScript leak scanning\n"
            "• Critical port checks\n"
            "• Fast technology detection\n\n"
            "Goal: Maximum visibility with minimum noise."
        )

    console.print(
        Panel(text, title="Purpose / Amaç", border_style=GREEN, style=WHITE)
    )

def ask_output_dir() -> str:
    return Prompt.ask("Output directory", default="outputs")

def ask_domains() -> list[str]:
    raw = Prompt.ask(
        "Domains (comma separated)\nExample: example1.com, example2.com"
    )
    return [
        d.strip().replace("https://", "").replace("http://", "")
        for d in raw.split(",") if d.strip()
    ]

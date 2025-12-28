import os
import time
import requests
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
from rich.panel import Panel

# --- Configuration ---
BASE_URL = "https://maps.izurvive.com/maps/ChernarusPlus-Top/1.26.0/tiles/6"
X_RANGE = range(0, 64) 
Y_RANGE = range(0, 64) 
SAVE_DIR = Path("tiles")
DELAY = 0.05 

console = Console()

def harvest_tiles():
    SAVE_DIR.mkdir(exist_ok=True)
    
    total_expected = len(X_RANGE) * len(Y_RANGE)
    
    # 1. Validation Phase
    existing_files = list(SAVE_DIR.glob("*.webp"))
    console.print(Panel(
        f"[bold green]TILE HARVESTER ONLINE[/bold green]\n"
        f"[green]Target Grid:[/green] {len(X_RANGE)}x{len(Y_RANGE)}\n"
        f"[green]Local Inventory:[/green] {len(existing_files)} / {total_expected} tiles",
        border_style="green"
    ))

    # 2. Network Session
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) TileScanner/2.1"
    })

    # Use 'dots' instead of 'binary' to avoid KeyError
    with Progress(
        SpinnerColumn(spinner_name="dots", style="bold green"),
        TextColumn("[bold green]{task.description}"),
        BarColumn(bar_width=None, style="dim green", complete_style="green"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console,
    ) as progress:

        task = progress.add_task("Synchronizing...", total=total_expected)

        for x in X_RANGE:
            for y in Y_RANGE:
                filename = f"{x}-{y}.webp"
                file_path = SAVE_DIR / filename
                
                if file_path.exists() and file_path.stat().st_size > 0:
                    progress.advance(task)
                    continue

                url = f"{BASE_URL}/{x}/{y}.webp"
                
                try:
                    response = session.get(url, timeout=10)
                    if response.status_code == 200:
                        with open(file_path, "wb") as f:
                            f.write(response.content)
                        time.sleep(DELAY)
                    elif response.status_code == 404:
                        # Some maps aren't perfect squares; skip 404s quietly
                        pass
                    else:
                        progress.console.print(f"[red]![/red] Server Error {response.status_code} at {x}-{y}")
                
                except Exception as e:
                    progress.console.print(f"[bold red]![/bold red] Link severed at {x}-{y}: {e}")
                
                progress.advance(task)

    console.print(Panel("[bold green]DATABASE SYNCHRONIZED[/bold green]", border_style="green"))

if __name__ == "__main__":
    harvest_tiles()
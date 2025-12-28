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
    initial_count = len(list(SAVE_DIR.glob("*.webp")))
    
    # Track stats for the final report
    downloaded_count = 0
    skipped_count = 0

    console.print(Panel(
        f"[bold green]TILE HARVESTER ONLINE[/bold green]\n"
        f"[green]Target Grid:[/green] {len(X_RANGE)}x{len(Y_RANGE)}\n"
        f"[green]Local Inventory:[/green] {initial_count} / {total_expected} tiles",
        border_style="green"
    ))

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) TileScanner/2.1"
    })

    with Progress(
        SpinnerColumn(spinner_name="dots", style="bold green"),
        TextColumn("[bold green]{task.description} [white]({task.completed}/{task.total})[/white]"),
        BarColumn(bar_width=None, style="dim green", complete_style="green"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console,
    ) as progress:

        task = progress.add_task("Processing...", total=total_expected)

        for x in X_RANGE:
            for y in Y_RANGE:
                filename = f"{x}-{y}.webp"
                file_path = SAVE_DIR / filename
                
                # Check for existing files
                if file_path.exists() and file_path.stat().st_size > 0:
                    progress.console.print(f"[dim str]  [skipping][/dim str] {filename} exists, skipping..")
                    skipped_count += 1
                    progress.advance(task)
                    continue

                url = f"{BASE_URL}/{x}/{y}.webp"
                
                try:
                    response = session.get(url, timeout=10)
                    if response.status_code == 200:
                        with open(file_path, "wb") as f:
                            f.write(response.content)
                        progress.console.print(f"[bold green]  [downloaded][/bold green] {filename}")
                        downloaded_count += 1
                        time.sleep(DELAY)
                    elif response.status_code == 404:
                        progress.console.print(f"[dim yellow]  [not found][/dim yellow] {filename} (404)")
                    else:
                        progress.console.print(f"[bold red]  [error][/bold red] {filename} - Status {response.status_code}")
                
                except Exception as e:
                    progress.console.print(f"[bold red]  [failed][/bold red] {filename}: {e}")
                    time.sleep(1) 
                
                progress.advance(task)

    # Final summary panel
    console.print(Panel(
        f"[bold green]SYNCHRONIZATION COMPLETE[/bold green]\n\n"
        f"Files Skipped: {skipped_count}\n"
        f"Files Downloaded: {downloaded_count}\n"
        f"Total Status: [white]{len(list(SAVE_DIR.glob('*.webp')))}[/white] / {total_expected} tiles present.",
        border_style="green"
    ))

if __name__ == "__main__":
    harvest_tiles()
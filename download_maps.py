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
    
    downloaded_count = 0
    skipped_count = 0

    console.print(Panel(
        f"[bold green]TILE HARVESTER ONLINE[/bold green]\n"
        f"[green]Grid:[/green] {len(X_RANGE)}x{len(Y_RANGE)} | [green]Initial:[/green] {initial_count}/{total_expected}",
        border_style="green"
    ))

    session = requests.Session()
    session.headers.update({"User-Agent": "TileScanner/2.1"})

    with Progress(
        SpinnerColumn(spinner_name="dots", style="bold green"),
        # Removed table_column_id to fix the TypeError
        TextColumn("[bold green]STATUS:[/bold green] {task.fields[status]}"),
        BarColumn(bar_width=None, style="dim green", complete_style="green"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console,
        refresh_per_second=10 
    ) as progress:

        # Initialize the task with a default 'status' field
        task = progress.add_task("Syncing", total=total_expected, status="Booting...")

        for x in X_RANGE:
            for y in Y_RANGE:
                filename = f"{x}-{y}.webp"
                file_path = SAVE_DIR / filename
                
                # Check for existing files
                if file_path.exists() and file_path.stat().st_size > 0:
                    progress.update(task, status=f"Skipping {filename}", advance=1)
                    skipped_count += 1
                    continue

                try:
                    response = session.get(f"{BASE_URL}/{x}/{y}.webp", timeout=10)
                    if response.status_code == 200:
                        with open(file_path, "wb") as f:
                            f.write(response.content)
                        progress.update(task, status=f"Fetched {filename}", advance=1)
                        downloaded_count += 1
                        time.sleep(DELAY)
                    elif response.status_code == 404:
                        progress.update(task, status=f"Missing {filename} (404)", advance=1)
                    else:
                        progress.update(task, status=f"Error {response.status_code}", advance=1)
                
                except Exception:
                    progress.update(task, status="Retry link...", advance=1)
                    time.sleep(1)

    console.print(Panel(
        f"[bold green]SYNCHRONIZATION COMPLETE[/bold green]\n"
        f"New: {downloaded_count} | Skipped: {skipped_count}",
        border_style="green"
    ))

if __name__ == "__main__":
    harvest_tiles()
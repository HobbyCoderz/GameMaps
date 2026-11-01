import os
from pathlib import Path
from PIL import Image
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn
from rich.panel import Panel

# --- Configuration ---
TILE_DIR = Path("tiles")
OUTPUT_FILE = "Chernarus_Full_Map.png"
TILE_SIZE = 256
GRID_SIZE = 64  # 0 to 63
TOTAL_PIXELS = GRID_SIZE * TILE_SIZE  # 16384

console = Console()

def stitch_map():
    # 1. Check for missing tiles before starting
    console.print(Panel(
        f"[bold green]INITIATING MASTER STITCH[/bold green]\n"
        f"Target Resolution: {TOTAL_PIXELS} x {TOTAL_PIXELS}\n"
        f"Format: 32-bit RGBA PNG",
        border_style="green"
    ))

    # Create the large blank canvas
    # Note: This requires about 1GB of RAM for the object itself
    full_map = Image.new('RGBA', (TOTAL_PIXELS, TOTAL_PIXELS))

    with Progress(
        TextColumn("[bold green]Stitching Row {task.fields[row]}"),
        BarColumn(style="dim green", complete_style="green"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:

        task = progress.add_task("Assembling", total=GRID_SIZE, row=0)

        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                tile_name = f"{x}-{y}.webp"
                tile_path = TILE_DIR / tile_name

                if tile_path.exists():
                    try:
                        with Image.open(tile_path) as tile:
                            # Calculate pixel position
                            # x = column, y = row
                            full_map.paste(tile, (x * TILE_SIZE, y * TILE_SIZE))
                    except Exception as e:
                        console.print(f"[red]Error processing {tile_name}: {e}[/red]")
                
            progress.update(task, advance=1, row=y)

    # 2. Saving the file
    console.print("[yellow]Encoding and saving large PNG file... This may take a minute.[/yellow]")
    full_map.save(OUTPUT_FILE, "PNG")
    
    console.print(Panel(
        f"[bold green]STITCH COMPLETE[/bold green]\n"
        f"File saved as: [white]{OUTPUT_FILE}[/white]\n"
        f"Final Size: {TOTAL_PIXELS}px square",
        border_style="green"
    ))

if __name__ == "__main__":
    if not TILE_DIR.exists():
        console.print("[bold red]Error: 'tiles' directory not found![/bold red]")
    else:
        stitch_map()
import re

# Configuration
input_file_path = 'map_tiles.txt'

# Regex pattern to capture (x) and (y) from the zoom 6 path
# (\d+) creates a "capture group" for one or more digits
pattern = r'/6/(\d+)/(\d+)\.webp'

def calculate_tile_ranges():
    x_coords = []
    y_coords = []

    try:
        with open(input_file_path, 'r', encoding='utf-8') as file:
            for line in file:
                match = re.search(pattern, line)
                if match:
                    # Convert captured strings to integers
                    x_coords.append(int(match.group(1)))
                    y_coords.append(int(match.group(2)))

        if not x_coords or not y_coords:
            print("No matching tile URLs found in the file.")
            return

        # Calculate Min/Max
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)

        # Calculate Dimensions
        width_in_tiles = max_x - min_x + 1
        height_in_tiles = max_y - min_y + 1
        total_tiles = width_in_tiles * height_in_tiles

        print("--- Map Tile Analysis (Zoom 6) ---")
        print(f"X Range: {min_x} to {max_x} (Width: {width_in_tiles} tiles)")
        print(f"Y Range: {min_y} to {max_y} (Height: {height_in_tiles} tiles)")
        print(f"Total Tiles in Grid: {total_tiles}")
        print(f"Resolution: {width_in_tiles * 256} x {height_in_tiles * 256} pixels")

    except FileNotFoundError:
        print(f"Error: '{input_file_path}' not found.")

if __name__ == "__main__":
    calculate_tile_ranges()
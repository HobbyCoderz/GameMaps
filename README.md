# Game Maps

Welcome to Game Maps! This web application empowers you to create and manage interactive, custom maps for your favorite video games. Easily upload your game maps and transform them into dynamic interfaces where you can place markers to track points of interest, resources, and critical locations.

**Key Features:**

*   **Map Management:** Add, select, and delete game maps.
*   **Interactive Markers:** Create, edit, and delete markers with details like titles, types, coordinates, notes, and custom images.
*   **Dynamic UI:** Navigate your maps with an interactive sidebar that lists, filters, and sorts markers, allowing you to quickly locate any point of interest.

Built with Python/Flask and Leaflet.js, Game Maps provides a seamless experience for enhancing your gaming adventures.

# How to Use Game Maps

## Installation on Windows

Follow these steps to set up the project on your Windows machine:

```bash
git clone https://github.com/HobbyCoderz/GameMaps.git
cd GameMaps
```

### Using uv (Recommended)

If you use `uv` for environment management:

```bash
uv venv
.venv\Scripts\activate
uv pip install -r requirements.txt
```

### Using Python's venv

If you prefer Python's built-in `venv`:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Preparing Your Game Map

Before launching the application, prepare your game map image:

1.  **Capture Screenshot:** Take a screenshot of your game map.
2.  **Stitch Images (if necessary):** If your map is large, zoom in and capture multiple screenshots. Use an image editor to stitch these together into a single, cohesive image file.
3.  **Place in `maps` Folder:** Save the final image file into the `maps` directory within the project.

## Launching the Application

Once your environment is set up and your map image is prepared:

```bash
python app.py
```

After running the command, observe the console output for the application's URL and port. It should typically be: `http://127.0.0.1:5000/`

## Using the Application

1.  **Create a New Map:**
    *   Click the "Create Map" button.
    *   Enter a descriptive name for your map.
    *   Type the exact filename of your prepared game map image (e.g., `my_map.jpg`).
2.  **Select Map:** Choose your newly created map from the dropdown menu.
3.  **Add Map Markers:**
    *   To add a marker, `CTRL + Click` on the desired location on the map.
    *   To attach an image to a marker, click the "Browse" button and select your image file.
4.  **Edit Markers:** All marker details (name, type, coordinates, notes, image) can be edited by clicking the "Edit" button associated with the marker.
# `mapshot`

Generate the _perfect_ satellite image.

---

`mapshot` is a tool for creating _perfect_ satellite map screenshots of cities, states, countries, or basically anything (streets, rivers, _et cetera_). It automatically fetches object boundaries from OpenStreetMap, calculates the smallest square needed to fit the entire object, and renders a satellite image!

---

### Function

1. **Query OpenStreetMap**: Fetches city boundary polygon via Nominatim API
2. **Calculate square bounds**: Finds minimal square that encompasses the entire city
3. **Reproject to Web Mercator**: Converts from lat/lon to metric projection (EPSG:3857)
4. **Render satellite tiles**: Downloads and composites Esri World Imagery basemap
5. **Export image**: Saves as PNG with no axes or decorations

### Installation

Clone the repo:

```bash
git clone https://github.com/yourusername/mapshot.git
cd mapshot
```

Create and activate a virtual environment and install dependencies:

```bash
python3 -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
pip install -r requirements.txt
```

### Single City

Generate a mapshot for a single city:

```bash
python3 mapshot.py "Fujikawaguchiko, Japan"
```

With custom zoom level (higher = more detail):

```bash
python3 mapshot.py "El Calafate, Santa Cruz, AR" --zoom 15
```

### Multiple Cities

Process multiple cities from a CSV file:

```bash
python3 mapshot.py --csv <path to CSV>/cities.csv --zoom 12
```

The CSV file should have one column with name `object`.

### Command-Line Options

```bash
> python3 mapshot.py --help
```

```text
Usage: mapshot.py [OPTIONS] [CITYNAME]

  Generate square satellite imagery for cities.

Options:
  --csv PATH      Process cities from CSV file
  --zoom INTEGER  Zoom level for basemap (default: None)
  --help          Show this message and exit.
```

### Output

All images are saved to the `images/` directory with sanitized filenames:

### Limitations

- Needs internet connection for API requests and tile downloads
- Very large objects may take longer to render
- Images depend on Nominatim search results
- Remote/unrecognized locations may not return results

"""Return image."""
import os
import csv
import sys
import re
import requests
import geopandas as gpd
from shapely.geometry import box
import matplotlib.pyplot as plt
import contextily as cx

def mapshot(cityname):
    """Create a mapshot of the inputted city."""
    print("Starting\tmapshot()")

    data = osm(cityname)

    if not data:
        raise ValueError("City not found")

    # Convert response data (polygon_geojson) into geopandas dataframe
    gdf = gpd.GeoDataFrame.from_features(
        [{"geometry": data[0]["geojson"], "properties": {}}],
        crs="EPSG:4326"
    )
    # Convert to metric (instead of angular) representation
    gdf = gdf.to_crs(epsg=3857)

    min_x, min_y, max_x, max_y = gdf.total_bounds
    side = max(max_x - min_x, max_y - min_y)

    x_center = (min_x + max_x) / 2
    y_center = (min_y + max_y) / 2

    square = box(
        x_center - side / 2,
        y_center - side / 2,
        x_center + side / 2,
        y_center + side / 2
    )
    # Create a perfectly square geopandas dataframe centered on cityname
    square_gdf = gpd.GeoDataFrame(geometry=[square], crs=gdf.crs)

    safe_name = re.sub(r'[^a-zA-Z0-9]+', '_', cityname).strip('_')
    generate_plt(square_gdf, square, f"{safe_name.lower()}_out.png")


def mapshot_from_csv(filepath):
    """Process multiple cities from CSV file."""
    print(f"Starting\tmapshot_from_csv()")

    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cityname = row.get('city')
            try:
                mapshot(cityname.strip())
            except Exception as e:
                print(f"Error processing '{cityname}': {e}")

def generate_plt(square_gdf, square, output_file):
    """Generate final output image."""
    print("Starting\tgenerate_plt")

    img_size = 2048
    _, ax = plt.subplots(
        figsize=(img_size / 256, img_size / 256),
        dpi=256
    )

    square_gdf.boundary.plot(ax=ax, linewidth=0)

    print("\tAdding basemap")

    cx.add_basemap(
        ax,
        source=cx.providers.Esri.WorldImagery,
        zoom=12,
        attribution=False
    )

    print("\tDone adding basemap")

    ax.set_xlim(square.bounds[0], square.bounds[2])
    ax.set_ylim(square.bounds[1], square.bounds[3])
    ax.axis("off")

    os.makedirs("images", exist_ok=True)
    output_path = os.path.join("images", output_file)

    print("\tSaving image")

    plt.savefig(
        output_path,
        dpi=256,
        bbox_inches="tight",
        pad_inches=0
    )
    plt.close()

    print(f"Saved {output_file}")

def osm(cityname):
    """Make request to Nomatim API search endpoint."""
    print("Starting\tosm")

    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": cityname,
        "format": "json",
        "polygon_geojson": 1
    }

    response = requests.get(url, params=params, headers={"User-Agent": "mapshot-script"})
    return response.json()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 mapshot.py <cityname>")
        print("       python3 mapshot.py --csv <filepath>")
        exit(1)

    print("Starting\tmapshot")
    if sys.argv[1] == "--csv":
        if len(sys.argv) != 3:
            print("Usage: python3 mapshot.py <cityname>")
            print("       python3 mapshot.py --csv <filepath>")
            exit(1)
        mapshot_from_csv(sys.argv[2])
    else:
        mapshot(sys.argv[1])

"""Return image."""
import os
import csv
import sys
import re
import click
import requests
import geopandas as gpd
from shapely.geometry import box
import matplotlib.pyplot as plt
import contextily as cx


@click.command()
@click.argument('cityname', required=False)
@click.option(
    '--csv',
    'csv_file',
    type=click.Path(exists=True),
    help='Process cities from CSV file'
)
@click.option(
    '--zoom',
    default=None,
    type=int,
    help='Zoom level for basemap (default: None)'
)
def main(cityname, csv_file, zoom):
    """Generate square satellite imagery for cities."""
    if csv_file:
        mapshot_from_csv(csv_file, zoom)
    elif cityname:
        mapshot(cityname, zoom)
    else:
        click.echo("Error: Provide either a city name or --csv file")
        click.echo("Usage: python3 mapshot.py <cityname>")
        click.echo("       python3 mapshot.py --csv <filepath>")
        sys.exit(1)


def mapshot(cityname, zoom):
    """Create a mapshot of the inputted city."""
    print(f"Starting\tmapshot({cityname})")

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
    generate_plt(square_gdf, square, f"{safe_name.lower()}_out.png", zoom)


def mapshot_from_csv(filepath, zoom):
    """Process multiple cities from CSV file."""
    print("Starting\tmapshot_from_csv()")
    print("--" * 25)

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cityname = row.get('object')
            mapshot(cityname.strip(), zoom)


def generate_plt(square_gdf, square, output_file, zoom):
    """Generate final output image."""
    print("Starting\tgenerate_plt")

    img_size = 2048
    _, ax = plt.subplots(
        figsize=(img_size / 256, img_size / 256),
        dpi=256
    )

    square_gdf.boundary.plot(ax=ax, linewidth=0)

    print("\t\tAdding basemap")

    if zoom:
        cx.add_basemap(
            ax,
            source=cx.providers.Esri.WorldImagery,
            zoom=zoom,
            attribution=False
        )
    else:
        cx.add_basemap(
            ax,
            source=cx.providers.Esri.WorldImagery,
            attribution=False
        )

    print("\t\tDone adding basemap")

    ax.set_xlim(square.bounds[0], square.bounds[2])
    ax.set_ylim(square.bounds[1], square.bounds[3])
    ax.axis("off")

    os.makedirs("images", exist_ok=True)
    output_path = os.path.join("images", output_file)

    print("\t\tSaving image")

    plt.savefig(
        output_path,
        dpi=256,
        bbox_inches="tight",
        pad_inches=0
    )
    plt.close()

    print(f"Saved images/{output_file}")
    print("--" * 25)


def osm(cityname):
    """Make request to Nomatim API search endpoint."""
    print("Starting\tosm")

    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": cityname,
        "format": "json",
        "polygon_geojson": 1
    }

    response = requests.get(
        url,
        params=params,
        headers={"User-Agent": "mapshot-script"},
        timeout=10
    )
    return response.json()


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter

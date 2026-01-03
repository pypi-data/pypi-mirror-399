"""Main module."""

import os
import json
import random
import string

import ee
import shapefile
import ipyleaflet
from ipyleaflet import (
    FullScreenControl,
    LayersControl,
    DrawControl,
    MeasureControl,
    ScaleControl,
    TileLayer,
)


# ---------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------

def random_string(length=6):
    """Generate a random string."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def shp_to_geojson(in_shp, out_geojson=None):
    """Converts a shapefile to GeoJSON.

    Args:
        in_shp (str): Path to input shapefile (.shp)
        out_geojson (str, optional): Path to output GeoJSON

    Returns:
        dict: GeoJSON dictionary
    """
    in_shp = os.path.abspath(in_shp)

    if not os.path.exists(in_shp):
        raise FileNotFoundError("The provided shapefile could not be found.")

    sf = shapefile.Reader(in_shp)
    geojson = sf.__geo_interface__

    if out_geojson is None:
        return geojson

    out_geojson = os.path.abspath(out_geojson)
    out_dir = os.path.dirname(out_geojson)
    os.makedirs(out_dir, exist_ok=True)

    with open(out_geojson, "w") as f:
        json.dump(geojson, f)

    return geojson


# ---------------------------------------------------------------------
# Map class
# ---------------------------------------------------------------------

class Map(ipyleaflet.Map):
    """Interactive map based on ipyleaflet."""

    def __init__(self, **kwargs):
        kwargs.setdefault("center", [40, -100])
        kwargs.setdefault("zoom", 4)
        kwargs.setdefault("scroll_wheel_zoom", True)

        super().__init__(**kwargs)

        self.layout.height = kwargs.get("height", "500px")

        self.add_control(FullScreenControl())
        self.add_control(LayersControl(position="topright"))
        self.add_control(DrawControl(position="topleft"))
        self.add_control(MeasureControl())
        self.add_control(ScaleControl(position="bottomleft"))

        google_map = kwargs.get("google_map", "ROADMAP")

        if google_map == "HYBRID":
            url = "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}"
            name = "Google Satellite"
        else:
            url = "https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}"
            name = "Google Maps"

        self.add_layer(
            TileLayer(
                url=url,
                attribution="Google",
                name=name,
            )
        )

    # -----------------------------------------------------------------

    def add_geojson(self, in_geojson, style=None, layer_name="Untitled"):
        """Adds a GeoJSON layer to the map."""

        if layer_name == "Untitled":
            layer_name = f"Untitled_{random_string()}"

        if isinstance(in_geojson, str):
            if not os.path.exists(in_geojson):
                raise FileNotFoundError("The provided GeoJSON file could not be found.")
            with open(in_geojson) as f:
                data = json.load(f)

        elif isinstance(in_geojson, dict):
            data = in_geojson

        else:
            raise TypeError("The input geojson must be a str or dict.")

        if style is None:
            style = {
                "stroke": True,
                "color": "#000000",
                "weight": 2,
                "opacity": 1,
                "fill": True,
                "fillColor": "#0000ff",
                "fillOpacity": 0.4,
            }

        geo_json = ipyleaflet.GeoJSON(
            data=data,
            style=style,
            name=layer_name,
        )
        self.add_layer(geo_json)

    # -----------------------------------------------------------------

    def add_shapefile(self, in_shp, style=None, layer_name="Untitled"):
        """Adds a shapefile to the map."""
        geojson = shp_to_geojson(in_shp)
        self.add_geojson(geojson, style=style, layer_name=layer_name)


    # -----------------------------------------------------------------


    def shp_to_geojson(in_shp, out_geojson=None):
    
        in_shp = os.path.abspath(in_shp)

        if not os.path.exists(in_shp):
            raise FileNotFoundError("The provided shapefile could not be found.")

        sf = shapefile.Reader(in_shp)
        geojson = sf.__geo_interface__

        if out_geojson is None:
            return geojson
        else:
            out_geojson = os.path.abspath(out_geojson)
            out_dir = os.path.dirname(out_geojson)
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)
            with open(out_geojson, "w") as f:
                f.write(json.dumps(geojson))


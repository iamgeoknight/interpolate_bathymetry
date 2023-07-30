# import libraries
import verde as vd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
import rasterio as rio
from rasterio.transform import from_origin

# Reading bathymetry point data
gdf = gpd.read_file('NSWOEH/NSWOEH.shp')
df = gdf[['X', 'Y', 'Z']]

# Get the region/extent of the data from the coordinates
region = vd.get_region((df.X, df.Y))

# interpolate bathymetry data
def interpolate(spacing, df, interpolation, region):
    if (interpolation == "knn"):
        interpolator = vd.KNeighbors()    
    elif (interpolation == "cubic"):
        interpolator = vd.Cubic()
    elif (interpolation == "linear"):
        interpolator = vd.Linear()

    interpolator.fit((df.X, df.Y), df.Z)   

    return interpolator.grid(region=region, spacing=spacing, data_names=['bathymetry'])

# export interpolated bathymetry to a GeoTIFF file
def export_to_tiff(tiff_name, crs, region, spacing, grid_bathymetry):
    meta = {
        "count": 1,
        "dtype": "float32",
        "height": grid_bathymetry.shape[0],
        "width": grid_bathymetry.shape[1],
        "transform": from_origin(
            region[0], region[3], spacing, spacing
        ),
        "crs": crs,
    }

    # Save the interpolated points to a GeoTIFF file
    with rio.open(f'{tiff_name}.tiff', "w", **meta) as dst:
        dst.write(np.flip(grid_bathymetry, 0), 1)

# Interpolation spacing
spacing = 50

# KNeighbors interpolation
grid = interpolate(spacing, df, 'knn', region)

# Get interpolation weights for the grid
grid_bathymetry = grid.bathymetry
export_to_tiff('knn', str(gdf.crs), region, spacing, grid_bathymetry)

# Cubic interpolation
grid = interpolate(spacing, df, 'cubic', region)

# Get interpolation weights for the grid
grid_bathymetry = grid.bathymetry
export_to_tiff('cubic', str(gdf.crs), region, spacing, grid_bathymetry)

# Linear interpolation
grid = interpolate(spacing, df, 'linear', region)

# Get interpolation weights for the grid
grid_bathymetry = grid.bathymetry
export_to_tiff('linear', str(gdf.crs), region, spacing, grid_bathymetry)
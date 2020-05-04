import geopandas as gpd
import requests
import matplotlib.pyplot as plt


json_url = "https://opendata.arcgis.com/datasets/bbe7d09a81fc40c8a7c9f4c80155842e_0.geojson"

tracts = gpd.read_file(json_url)
preview = tracts.head()

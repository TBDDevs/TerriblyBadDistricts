import folium as fol
import geopandas as gpd
import json

REPUBLICAN_PARTY = 1
DEMOCRATIC_PARTY = 2

def generate_dem_map():
    base = fol.Map(location=[39.0457549, -76.6413], zoom_start=8)

    df = gpd.read_file("maryland-congressional-districts.geojson")

    partynum = [1, 2, 2, 2, 2, 2, 2, 2]


    df["partynum"] = partynum
    df["FID"] = partynum
    print(df)
    fol.Choropleth(
        name = "dataproc",
        geo_data = df,
        data = df,
        key_on = "feature.properties.partynum",
        columns = ["partynum", "FID"],
        fill_color = "RdBu",
    ).add_to(base)


    fol.LayerControl().add_to(base)

    base.save('templates/democratic_map.html')


import folium as fol
import random
import pandas
import geopandas
import dataProcessor
import shapely.geometry
from shapely.geometry import LineString

REPUBLICAN_PARTY = 1
DEMOCRATIC_PARTY = 0

pandas.options.mode.chained_assignment = None


def generate():
    print("Creating map...")
    base = fol.Map(location=[39.0457549, -76.6413], zoom_start=8)

    """
    print("Invoking census blocks processor/predictor...")
    predOut = dataProcessor.getData()

    print("Applying default dissolve field (party number)...")
    predOut["dissolvefield"] = predOut["partynum"]
    """

    # WHICH PARTY SHOULD WIN?
    FAVORED_PARTY = REPUBLICAN_PARTY

    NON_FAVORED_PARTY = DEMOCRATIC_PARTY if FAVORED_PARTY == REPUBLICAN_PARTY else REPUBLICAN_PARTY

    """
    print("Splitting up favored party districts by county, with randomization...")
    for i, row in predOut.iterrows():
        if row["partynum"] == FAVORED_PARTY:
            county = int(row["CNTY2010"])
            if random.randint(0,2) == 0:
                county += 1
            predOut.loc[i, "dissolvefield"] = county

    print("Merging nearby non-favored party districts...")
    for i, row in predOut.iterrows():
        if row["partynum"] == FAVORED_PARTY:
            neighbours = predOut[predOut.geometry.touches(row['geometry'])]
            nonFavoredCount = len(neighbours) - list(neighbours["partynum"]).count(FAVORED_PARTY)
            if nonFavoredCount > 2:
                predOut.loc[i, "dissolvefield"] = NON_FAVORED_PARTY

    print("STARTING DISSOLVE...")
    dissolved = predOut.dissolve(by='dissolvefield')
    print("Dissolve done.")
    
    print("Saving...")
    dissolved.to_file("dissolved_output.shp")
    """

    dissolved = geopandas.read_file("dissolved_output.shp")
    disFilt = dissolved[dissolved["partynum"] == NON_FAVORED_PARTY]
    disFilt = disFilt.explode()
    disFiltNewCrs = disFilt.to_crs("epsg:3857")
    disFilt["area"] = disFiltNewCrs["geometry"].area / 10**6
    disFilt = disFilt[disFilt["area"] > 7]

    firstCentroid = list(disFilt.centroid)[0]
    connectorList = []
    centroids = geopandas.GeoDataFrame()
    centroids["geometry"] = disFilt.centroid
    centroids["alreadyconnected"] = False
    """
    for row in disFilt.centroid:
        connector = LineString([firstCentroid, row]).buffer(0.005)
        connectorList.append(connector)
    """
    for i, blah in centroids.iterrows():
        row = blah.geometry
        if row == firstCentroid:
            continue
        centroids["dist"] = centroids["geometry"].distance(row)
        closestOtherPoint = centroids[centroids["alreadyconnected"] == False].sort_values("dist").iloc[1]["geometry"]
        connector = LineString([closestOtherPoint, row]).buffer(0.005)
        connectorList.append(connector)
        centroids.at[i, "alreadyconnected"] = True

    connSeries = geopandas.GeoSeries(connectorList)
    disSer = disFilt["geometry"]
    disSer = disSer.append(connSeries)
    print("Done making connectors")

    merged = disSer.unary_union
    #merged = disSer

    mergedFrame = geopandas.GeoDataFrame()
    mergedFrame["geometry"] = geopandas.GeoSeries(shapely.geometry.Polygon(merged.exterior))
    mergedFrame["FID"] = 1
    mergedFrame["partynum"] = NON_FAVORED_PARTY
    mergedFrame.crs = disFilt.crs

    print("Rendering map...")
    fol.Choropleth(
            name = "dataproc",
            geo_data = mergedFrame,
            data = mergedFrame,
            key_on = "feature.properties.FID",
            columns = ["FID", "partynum"],
            fill_color = "Accent"
    ).add_to(base)
    fol.LayerControl().add_to(base)

    base.save('templates/democratic_map.html')

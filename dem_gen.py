import folium as fol
import random
import pandas
import geopandas
import dataProcessor
import shapely.geometry
from shapely.geometry import LineString
import datetime

REPUBLICAN_PARTY = 1
DEMOCRATIC_PARTY = 0

pandas.options.mode.chained_assignment = None


# Stopwatch print. Keeps track of time between prints.
def swprint(printstr):
    td = (datetime.datetime.now() - swprint.time)
    secsElapsed = "%0.1f" % td.total_seconds()
    print(" Took", secsElapsed, "seconds.")
    print(printstr, end="", flush=True)
    swprint.time = datetime.datetime.now()

swprint.time = datetime.datetime.now()


def generate():

    # WHICH PARTY SHOULD WIN?
    FAVORED_PARTY = DEMOCRATIC_PARTY

    NON_FAVORED_PARTY = DEMOCRATIC_PARTY if FAVORED_PARTY == REPUBLICAN_PARTY else REPUBLICAN_PARTY

    print("")
    print("T.B.D. GERRYMANDERED MAP GENERATOR")
    print("==================================")
    print("")
    print("Gerrymandering in FAVOR of Party:", FAVORED_PARTY, end=" ")
    if FAVORED_PARTY == REPUBLICAN_PARTY:
        print("(Republicans)")
    else:
        print("(Democrats)")
    startTime = datetime.datetime.now()
    print("Starting at time", startTime.strftime("%T"))
    print("")

    print("Creating map...", end="")
    base = fol.Map(location=[39.0457549, -76.6413], zoom_start=8)

    swprint("Invoking census blocks processor/predictor...")
    predOut = dataProcessor.getData()

    swprint("Applying default dissolve field (party number)...")
    predOut["dissolvefield"] = predOut["partynum"]

    swprint("Splitting up favored party districts by county, with randomization...")
    for i, row in predOut.iterrows():
        if row["partynum"] == FAVORED_PARTY:
            county = int(row["CNTY2010"])
            if random.randint(0,2) == 0:
                county += 1
            predOut.loc[i, "dissolvefield"] = county

    swprint("Merging nearby non-favored party districts...")
    for i, row in predOut.iterrows():
        if row["partynum"] == FAVORED_PARTY:
            neighbours = predOut[predOut.geometry.touches(row['geometry'])]
            nonFavoredCount = len(neighbours) - list(neighbours["partynum"]).count(FAVORED_PARTY)
            if nonFavoredCount > 2:
                predOut.loc[i, "dissolvefield"] = NON_FAVORED_PARTY

    swprint("STARTING DISSOLVE...")
    dissolved = predOut.dissolve(by='dissolvefield')
    print(" Dissolve done.")
    
    swprint("Saving progress...")
    dissolved.to_file("temp/dissolved_output.shp")
    swprint("Reading dissolved file...")
    dissolved = geopandas.read_file("temp/dissolved_output.shp")

    swprint("Filtering to only include non-favored party districts...")
    disFilt = dissolved[dissolved["partynum"] == NON_FAVORED_PARTY]
    swprint("Exploding multipolygon to polygons...")
    disFilt = disFilt.explode()
    swprint("Calculating area and filtering out districts with km2 < 7...")
    disFiltNewCrs = disFilt.to_crs("epsg:3857")
    disFilt["area"] = disFiltNewCrs["geometry"].area / 10**6
    disFilt = disFilt[disFilt["area"] > 7]

    swprint("Creating centroids table...")
    firstCentroid = list(disFilt.centroid)[0]
    connectorList = []
    centroids = geopandas.GeoDataFrame()
    centroids["geometry"] = disFilt.centroid
    centroids["alreadyconnected"] = False

    swprint("CREATING CONNECTORS...")
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
    print(" Connectors done.")

    swprint("APPLYING UNARY UNION (SECOND DISSOLVE)...")
    merged = disSer.unary_union
    #merged = disSer
    print(" Unary union done.")

    swprint("Moving into new GeoDataFrame...")
    mergedFrame = geopandas.GeoDataFrame()
    mergedFrame["geometry"] = geopandas.GeoSeries(shapely.geometry.Polygon(merged.exterior))
    mergedFrame["FID"] = 1
    mergedFrame["partynum"] = NON_FAVORED_PARTY
    mergedFrame.crs = disFilt.crs

    #mergedFrame = geopandas.read_file("temp/bigDemDistrict.shp")

    swprint("Reading Maryland boundary shapefile...")
    allOfMd = geopandas.read_file("temp/mdbound.shp")
    allOfMd = allOfMd.to_crs(mergedFrame.crs)

    swprint("SUBTRACTING...")
    mdFavored = geopandas.overlay(allOfMd, mergedFrame, how="difference")
    print("Done subtracting.")

    swprint("Exploding favored-party multipolygon to polygons...")
    favexplode = mdFavored.explode()
    swprint("Calculating area and filtering out districts with km2 < 5...")
    favexplode["area"] = favexplode.to_crs("epsg:3857")["geometry"].area / 10**6
    favexplode = favexplode[favexplode["area"] > 5]

    swprint("Editing partynum column...")
    mergedFrame["partynum"] = 100
    favexplode["partynum"] = -100
    combinedDistricts = pandas.concat([mergedFrame, favexplode], ignore_index=True)
    for i, blah in combinedDistricts.iterrows():
        combinedDistricts.at[i, "partynum"] = i

    swprint("Saving final district map to file...")
    combinedDistricts.to_file("temp/combinedDistricts2_favparty" + str(FAVORED_PARTY) + ".shp")
    swprint("Reading final district map from file...")
    combinedDistricts = geopandas.read_file("temp/combinedDistricts2_favparty" + str(FAVORED_PARTY) + ".shp")
    for i, blah in combinedDistricts.iterrows():
        combinedDistricts.at[i, "FID"] = i

    swprint("Rendering map...")
    fol.Choropleth(
            name = "dataproc",
            geo_data = combinedDistricts,
            data = combinedDistricts,
            key_on = "feature.properties.partynum",
            columns = ["partynum", "FID"],
            fill_color = "BuGn"
            #bins = len(combinedDistricts)
    ).add_to(base)
    fol.LayerControl().add_to(base)

    swprint("Gerrymandering and rendering process completed.")
    print("")
    elapsedTime = datetime.datetime.now() - startTime
    elapsedMinutes, elapsedSeconds = divmod(elapsedTime.seconds, 60)
    print("Total elapsed time:", elapsedMinutes, "minutes,", elapsedSeconds, "seconds.")
    print("")

    base.save('templates/democratic_map.html')

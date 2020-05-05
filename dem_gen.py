import folium as fol
import random
import pandas
import dataProcessor

REPUBLICAN_PARTY = 1
DEMOCRATIC_PARTY = 0

pandas.options.mode.chained_assignment = None


def generate():
    print("Creating map...")
    base = fol.Map(location=[39.0457549, -76.6413], zoom_start=8)

    print("Taking subset...")
    predOut = dataProcessor.getData()

    print("Applying default dissolve field (party number)...")
    predOut["dissolvefield"] = predOut["partynum"]

    # WHICH PARTY SHOULD WIN?
    FAVORED_PARTY = DEMOCRATIC_PARTY

    NON_FAVORED_PARTY = DEMOCRATIC_PARTY if FAVORED_PARTY == REPUBLICAN_PARTY else REPUBLICAN_PARTY

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

    print("Rendering map...")
    fol.Choropleth(
            name = "dataproc",
            geo_data = dissolved,
            data = dissolved,
            key_on = "feature.properties.FID",
            columns = ["FID", "partynum"],
            fill_color = "Accent"
    ).add_to(base)
    fol.LayerControl().add_to(base)

    base.save('templates/democratic_map.html')

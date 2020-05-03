from flask import Flask, render_template
import folium as fol
import random
import pandas

import dataProcessor

app = Flask(__name__)

REPUBLICAN_PARTY = 1
DEMOCRATIC_PARTY = 0

pandas.options.mode.chained_assignment = None

@app.route('/')
def index():
    print("Creating map...")
    base = fol.Map(location=[39.0457549, -76.6413], zoom_start=8)

    #fol.GeoJson('bbe7d09a81fc40c8a7c9f4c80155842e_0.geojson').add_to(base)
    #print(dataProcessor.df.head())

    print("Taking subset...")
    predOut = dataProcessor.df[["partynum", "geometry", "FID", "CNTY2010"]]

    print("Applying default dissolve field (party number)...")
    predOut["dissolvefield"] = predOut["partynum"]

    # WHICH PARTY SHOULD WIN?
    FAVORED_PARTY = REPUBLICAN_PARTY

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
    #print(dissolved)

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

    base.save('templates/base_map.html')
    return render_template('index.html')


@app.route('/base_map')
def base_map():
    return render_template('base_map.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0')
import geopandas

#function for classifying a row as democrat or republican
def classifier(row):
    DEM = 0
    REP = 1

    # if percentage of black population is greater than 14
    if row['PNHB'] > 14:
        # if percentage of senior population is over 31
        if row['PCTPOP65_'] > 31:
            return REP
        else:
            return DEM
    else:
        # if percentages of hispanic and asian populations is greater than 16
        if row['PNHA'] + row['PHISP'] > 16:
            return DEM
        else:
            return REP

#function that loads the data from the census, classifies it, and returns the data as a dataframe.
def getData():
    # load data from maryland census site
    url = "https://opendata.arcgis.com/datasets/bbe7d09a81fc40c8a7c9f4c80155842e_0.geojson"
    df = geopandas.read_file(url)


    # classifies instances by party
    df["partynum"] = df.apply(classifier, axis=1)

    return df

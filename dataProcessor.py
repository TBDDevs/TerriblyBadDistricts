import geopandas

def classifier(row):
        # if percentage of black population is greater than 14
        if row['PNHB'] > 14:
            # if percentage of senior population is over 31
            if row['PCTPOP65_'] > 31:
                return "rep"
            else:
                return "dem"
        else:
            # if percentages of hispanic and asian populations is greater than 16
            if row['PNHA'] + row['PHISP'] > 16:
                return 'dem'
            else:
                return "rep"

def getData():
    # load data from maryland census site
    url = "https://opendata.arcgis.com/datasets/bbe7d09a81fc40c8a7c9f4c80155842e_0.geojson"
    df = geopandas.read_file(url)


    # classifies instances by party
    df["party"] = df.apply(classifier, axis=1)

    # for checking number of each party
    #print(df['party'].value_counts())

    return df

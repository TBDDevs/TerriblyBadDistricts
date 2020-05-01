import geopandas

#load data from maryland census site
url = "https://opendata.arcgis.com/datasets/bbe7d09a81fc40c8a7c9f4c80155842e_0.geojson"
df = geopandas.read_file(url)

#this is just a temporary way to classify instances 
#assign row value based on percentage of non hispanic black persons
df.loc[df['PNHB'] >= 20, 'party'] = 'dem' 
df.loc[df['PNHB'] < 20, 'party'] = 'rep' 

print(df.head())

print(df['party'].value_counts())
import geopandas

#load data from maryland census site
url = "https://opendata.arcgis.com/datasets/bbe7d09a81fc40c8a7c9f4c80155842e_0.geojson"
print("Loading from", url)
df = geopandas.read_file(url)
print("Loaded.")
print(df)

df.to_csv()


#this is just a temporary way to classify instances 
#assign row value based on percentage of non hispanic black persons
df.loc[df['PNHB'] >= 20, 'party'] = 'dem' 
df.loc[df['PNHB'] >= 20, 'partynum'] = 0 
df.loc[df['PNHB'] < 20, 'party'] = 'rep' 
df.loc[df['PNHB'] < 20, 'partynum'] = 1     

print(df.head())

print(df['party'].value_counts())
import pandas as pd
import geopandas as gpd



def Prepare_la_homes_data() : 


	# Read the geoJSON file into a GeoPandas
	Homes = gpd.read_file("/Users/jules/la_homes.geojson")

	# Remove unwanted rows
	Homes = Homes.drop(Homes[(Homes.city != "LOS ANGELES CA")].index)
	Homes = Homes.drop(Homes[(Homes["size"] == 0)].index)
	Homes = Homes.reset_index()

	# Transform data from polygon to point for simplicity.
	# Get the Coordinates of the Centroid
	Homes["longitude"] = Homes["geometry"].centroid.x
	Homes["latitude"] = Homes["geometry"].centroid.y
	Homes = Homes.drop(columns=["geometry"])

	# Add new metrics
	for i in range(Homes.shape[0]) : 

		Homes.loc[i, "Price/SqFt"] = Homes.loc[i, "totalvalue"] / Homes.loc[i, "size"]
		Homes.loc[i, "Price/landvalue"] = Homes.loc[i, "totalvalue"] / Homes.loc[i, "landvalue"]
		Homes.loc[i, "landvalue/SqFt"] = Homes.loc[i, "landvalue"] / Homes.loc[i, "size"]


	# Save Data
	Homes.to_csv("/Users/jules/la_homes_Complete.csv")
	Homes.to_file("/Users/jules/la_homes_Cleaned.geojson", driver="GeoJSON")


def Prepare_Restaurant_data() :


	Price = {"$":1, "$$":2, "$$$":3, "$$$$":4, "$$$$$":5}

	# Load data
	Rest = pd.read_csv("/Users/jules/Los_Angeles_Restaurants.csv", header=None)
	Rest.drop_duplicates()

	# Remove Restaurants not in LA.
	Rest = Rest[Rest[8].str.contains('Los Angeles')]
	Rest = Rest.reset_index()

	# Using the price dictionary, transform $$ into ints. Also remove rows with no price given.
	for i in range(Rest.shape[0]) :
		if Rest.loc[i, 3] == "None" : 
			Rest.loc[i, "Price"] = "None"
		else :
			Rest.loc[i, "Price"] = Price[Rest.loc[i, 3]]
			print (i, Rest.loc[i, 3], Rest.loc[i, "Price"])

	Rest = Rest.drop(Rest[(Rest.Price == "None")].index)

	Rest.to_csv("/Users/jules/Los_Angeles_Restaurants_w_Price.csv")


def Aggregate_Crime_data() :

	Crime = pd.read_csv("/Users/jules/Crime_Data_LA.csv")

	# Round all the crime coordinates to two digits.
	# This will allow to aggregate the data based on location and reduce the file size
	for crime in range(Crime.shape[0]) :

		Crime.loc[crime, "LAT"] = round(Crime.loc[crime, "LAT"], 2)
		Crime.loc[crime, "LON"] = round(Crime.loc[crime, "LON"], 2)

	# Aggregate the data.
	Aggregated_Crime = Crime.groupby(['LAT', 'LON']).size().reset_index(name='counts')


Aggregate_Crime_data()
Prepare_Restaurant_data()
Prepare_la_homes_data()



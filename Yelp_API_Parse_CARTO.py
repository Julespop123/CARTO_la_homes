import pandas as pd
import math
from math import sin, cos, sqrt, atan2, radians
import numpy as np
import numpy
from numpy import genfromtxt
import json
import requests
import urllib
import os
import glob
import geopandas

# Function to calculate Distanc from Coordinates
def GetDistanceFromCoordinates(startlat, startlon, endlat, endlon) :
        
    # approximate radius of earth in km
    R = 6373.0

    lat1 = radians(startlat)
    lon1 = radians(startlon)
    lat2 = radians(endlat)
    lon2 = radians(endlon)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    return distance
    
    
# Function to get the business json info
def yelp_api_business_info(url, params, headers) :

    req = requests.get(url, params=params, headers=headers)
    parsed = json.loads(req.text)
    try:
        businesses = parsed["businesses"]
        return businesses
    except KeyError :
        check = parsed["error"]
    
    
# Create the list and append it to Dataframe
def get_business_list(businesses, Main, x) :
    
    i = x

    for business in businesses:
        
        Name = business["name"]
        Rating = business["rating"]
        try :
            Price = business["price"]
        except KeyError :
            Price = 'None'
        Coordinates = business["coordinates"]
        Longitude = Coordinates["longitude"]
        Latitude = Coordinates["latitude"]
        Location = business["location"]
        Address = Location["display_address"][0]
        try :
            City = Location["display_address"][1]
        except IndexError :
            City = 'None'
        Id = business["id"]
        
        Main = Main.append({'Name': Name, 'Rating': Rating, 'Price': Price, 'Longitude': Longitude, 'Latitude': Latitude, 'Address': Address, 'Id': Id, 'City': City}, ignore_index=True)
        
        
        i = i + 1

    return i, Main

# Enter your API key
api_key = ''
headers = {'Authorization': 'Bearer %s' % api_key}

url = 'https://api.yelp.com/v3/businesses/search'

# Geospatial varibales
bottom_right_corner = [33.71441214610023, -118.06740530586312]
top_left_corner = [34.33665736106487, -118.74293538654592]


# Figuring out cell size.
radius = 800
cell_size = ((radius / math.sqrt(2)) * 2) / 1000
print (cell_size)

print(GetDistanceFromCoordinates(bottom_right_corner[0], bottom_right_corner[1], top_left_corner[0], bottom_right_corner[1]))

cell_count_lat = int((GetDistanceFromCoordinates(bottom_right_corner[0], bottom_right_corner[1], top_left_corner[0], bottom_right_corner[1])) / cell_size) + 1
cell_count_long = int((GetDistanceFromCoordinates(bottom_right_corner[0], bottom_right_corner[1], bottom_right_corner[0], top_left_corner[1])) / cell_size) + 1

cell_size_lat = (top_left_corner[0] - bottom_right_corner[0]) / cell_count_lat
cell_size_long = (top_left_corner[1] - bottom_right_corner[1]) / cell_count_long

print ("Here is your cell count:\n\n", cell_count_lat, cell_count_long, "\n\n")



# Create a list of all the different points to look around. A grid for the city.

coordinates_list = []

for i in range(cell_count_lat) :

    for j in range(cell_count_long) :

        coordinates_list.append([bottom_right_corner[0] + cell_size_lat * i, bottom_right_corner[1] + cell_size_long * j])

print ("The amount of different calls: ", len(coordinates_list))


# Change these values when it bugs.
total_businesses = 0
count = 0

for coordinate in coordinates_list[count:] :

    x = 0
        
    print (coordinate, "\nTotal_businesses:", total_businesses, "\ncount:", count)
    
    count = count + 1
    sub_total_businesses = 0

    Main = pd.DataFrame(columns = ['Name', 'Rating', 'Price', 'Longitude', 'Latitude', 'Address', 'Id', 'City'])

    for offset in range(0, 1000, 50) :
    
        print ("Offset:", offset)
    
        if offset == 950 :
        
            print("OFFSET LIMIT HAS BEEN REACHED")
            exit()
        
        params = {'limit': 50, 'term':'restaurant', 'latitude': coordinate[0], 'longitude': coordinate[1], 'offset': offset, 'radius': radius}

        businesses = yelp_api_business_info(url, params, headers)
               
       # Check to see if there are still more features to be added. If not, it breaks the loop and moves on.
        if not businesses :
            break

        new_businesses = len(businesses)
        sub_total_businesses = sub_total_businesses + new_businesses

        x, Main = get_business_list(businesses, Main, x)
        
    Main.to_csv('/Users/jules/Los_Angeles_Restaurants.csv', mode='a', header=False)
    
    print ("\nIT HAS BEEN SAVED\n Total Businesses:", total_businesses, "\n Count:", count, "\n  Percent Complete:", (count/len(coordinates_list))*100)

    total_businesses = total_businesses + sub_total_businesses


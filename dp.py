import numpy as np
import pandas as pd              # работа с таблицами
import matplotlib.pyplot as plt  # графики
from geopy import distance
from math import radians, cos, sin, asin, sqrt
from numba import jit, njit

file = 'one_day_data.h5'
data = pd.read_hdf(file)    
data = pd.read_csv('temp.csv', names='time lat lon alt'.split(),skiprows=1)

lat_rad = []
lon_rad = []
for i in data.index[:]:
    lat_rad.append(np.deg2rad(data.lat[i]))
data.insert(loc=len(data.columns), column='lat_rad', value=lat_rad)

for i in data.index[:]:
    lon_rad.append(np.deg2rad(data.lon[i]))
data.insert(loc=len(data.columns), column='lon_rad', value=lon_rad)

path = './regions'
stations = []  # список, содержащий таблицы по каждому из трех регионов
for region in 'cal', 'jap', 'eur':
    stations.append(pd.read_csv(f'{path}/{region}.lst', names='site lat lon'.split()))
  
sites = stations[0]
site = sites.iloc[12]

lat=[]
for i in data.index[:]:
    lat.append(data.lat[i])

lon=[]
for i in data.index[:]:
    lon.append(data.lon[i])

def Haversine(lat1, lon1, lat2, lon2, radius=0):
    # print([type(i) for i in (lat1, lat2, lon1, lon2)])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * 6371 * asin(sqrt(a))  
    if (c < radius):
        d = True
    else:
        d = False
    return d

def when_iss_passed(station, lat2, lon2, radius=0):
    lat1 = station.lat
    lon1 = station.lon
    ind = []
    for i in lat, lon:
        lat2 = lat[i]
        lon2 = lon[i]
        h = Haversine(lat1, lon1, lat2, lon2, radius)
        if (h == True): ind.append(i)
    return ind
WIP = np.vectorize(when_iss_passed)
WIP(site, lat, lon, 200)





def when_iss_passed(station, iss_track, radius=0):
    lat1 = np.deg2rad(station.lat)
    lon1 = np.deg2rad(station.lon)
    ind = []
    for i in iss_track.index[:]:
        item = iss_track.loc[i]
        lat2 = item.lat_rad
        lon2 = item.lon_rad
        h = Haversine(lat1, lon1, lat2, lon2, radius)
        if (h == True): ind.append(i)
    return ind

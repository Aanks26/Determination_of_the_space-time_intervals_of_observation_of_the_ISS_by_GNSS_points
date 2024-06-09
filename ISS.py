import numpy as np
from math import cos
import pandas as pd
import datetime as dt

def when_iss_passed(station, iss_track, r = 0):
    radius = r / (2 * 6371)
    s_lat = np.deg2rad(station.lat)
    s_lon = np.deg2rad(station.lon)
    gr_lat = radius/ 111.11 #градусы отбора
    gr_lon = gr_lat / cos(s_lat)
    data = iss_track[['lat', 'lon', 'lat_rad', 'lon_rad']].copy()
    data['station_name'] = station.site
    data['dlat'] = data.lat_rad-s_lat
    data['dlon'] = data.lon_rad-s_lon
    data = data[(data['dlat'] < gr_lat) & (data['dlon'] < gr_lon)]
    data['sin_dlat2'] = np.sin(data.dlat/2)**2
    data['sin_dlon2'] = np.sin(data.dlon/2)**2
    data['cos_s_lat'] = np.cos(s_lat)
    data['cos_lat'] = np.cos(data.lat_rad)
    data['arcsin'] = np.arcsin((np.sqrt(data.sin_dlat2 + data.cos_lat * data.cos_s_lat * data.sin_dlon2)))
    data = data[data['arcsin'] < radius]
    data = data[['lat', 'lon']]
    return data



def sat_el_az (station, day, station_data, **kwargs):
    gnss_type = kwargs.get('gnss_type', 'G')
    nav_folder = kwargs.get('nav_folder', 'C:/Users/')
    h = kwargs.get('h', 455)
    angle = kwargs.get('angle', 30)
    time = station_data.index
    time = pd.to_datetime(time)
    time = time[time.date==day]
    day2 = day.strftime('%j')
    site_xyz = station['xyz']
    sat = list()
    if gnss_type == 'G':
        nav_file = nav_folder + '/brdc' + day2 + '0.' + day.strftime('%y') + 'n'
        for i in range(1, 33):
            for t in time[:]:
                timestamp = t
                sat_num = i
                sat_xyz = satellite_xyz(nav_file, gnss_type, sat_num, timestamp)
                el, az = xyz_to_el_az(site_xyz, sat_xyz)
                if el >= angle:
                    if sat_num not in sat:
                        sat.append(sat_num)
    if gnss_type == 'R':
        nav_file = nav_folder + '/brdc' + day2 + '0.' + day.strftime('%y') + 'g'
        for i in range(1, 25):
            for t in time[:]:
                timestamp = t
                sat_num = i
                sat_xyz = satellite_xyz(nav_file, gnss_type, sat_num, timestamp)
                el, az = xyz_to_el_az(site_xyz, sat_xyz)
                if el >= angle:
                    if sat_num not in sat:
                        sat.append(sat_num)
    return sat


def get_crossections(satellite, station, station_data, day, **kwargs):
    gnss_type = kwargs.get('gnss_type', 'G')
    nav_folder = kwargs.get('nav_folder', 'C:/Users/')
    day2 = day.strftime('%j')
    h = kwargs.get('h', 455)
    site_xyz = station['xyz']
    time = station_data.index
    time = pd.to_datetime(time)
    time = time[time.date==day]
    time_min = time.min().round('min')
    min = time.min().round('min')-dt.timedelta(minutes=10)
    max = time.max().round('min')+dt.timedelta(minutes=30)
    time2 = pd.date_range(min, max, freq='30S')
    col1 = 'ionospheric_lat(' + str(satellite) + ')'
    col2 = 'ionospheric_lon(' + str(satellite) + ')'
    df = pd.DataFrame(columns=[col1, col2])
    ion_lat = list()
    ion_lon = list()
    ts = list()
    if gnss_type == 'G':
        nav_file = nav_folder + '/brdc' + day2 + '0.' + day.strftime('%y') + 'n'
        for timestamp in time2[:]:
            sat_xyz = satellite_xyz(nav_file, gnss_type, satellite, timestamp)
            el, az = xyz_to_el_az(site_xyz, sat_xyz)
            params = np.deg2rad(np.array((station['location']['lat'], station['location']['lon'], h, az, el)))
            params[2] = h
            lat, lon = sub_ionospheric(*params)
            ion_lat.append(lat)
            ion_lon.append(lon)
            ts.append(timestamp)
    if gnss_type == 'R':
        nav_file = nav_folder + '/brdc' + day2 + '0.' + day.strftime('%y') + 'g'
        for timestamp in time2[:]:
            sat_xyz = satellite_xyz(nav_file, gnss_type, satellite, timestamp)
            el, az = xyz_to_el_az(site_xyz, sat_xyz)
            params = np.deg2rad(np.array((station['location']['lat'], station['location']['lon'], h, az, el)))
            params[2] = h
            lat, lon = sub_ionospheric(*params)
            ion_lat.append(lat)
            ion_lon.append(lon)
            ts.append(timestamp)
    df[col1] = np.rad2deg(ion_lat)
    df[col2] = np.rad2deg(ion_lon)
    df.index = ts
    return df, time_min


def sort(ISS_lat_rad, ISS_lon_rad, df_gc, **kwargs):
    radius = kwargs.get('radius', 1000)
    r = radius / (2 * 6371)
    df = df_gc[0]
    a,b = [column for column in df]
    df['ionospheric_lat_rad'] = np.deg2rad(df[a])
    df['ionospheric_lon_rad'] = np.deg2rad(df[b])
    #print(data.loc[df_gc[1]]['lat'], data.loc[df_gc[1]]['lon'])
    df['dlat'] = df.ionospheric_lat_rad-ISS_lat_rad
    df['dlon'] = df.ionospheric_lon_rad-ISS_lon_rad
    df['sin_dlat2'] = np.sin(df.dlat/2)**2
    df['sin_dlon2'] = np.sin(df.dlon/2)**2
    df['cos_ISS_lat'] = np.cos(ISS_lat_rad)
    df['cos_lat'] = np.cos(df.ionospheric_lat_rad)
    df['arcsin'] = np.arcsin(np.sqrt(df.sin_dlat2 + df.cos_ISS_lat * df.cos_lat * df.sin_dlon2))
    df = df[df['arcsin'] < r]
    df = df[[a, b]]
    return df

import streamlit as st
import pandas as pd
import fontus_db as db
import constants as cn

dfStations = pd.DataFrame
all_stations_list = []
    
def init(df):
    global dfStations
    global all_stations_list
    
    dfStations = df
    all_stations_list = dfStations[cn.STATION_NAME_COLUMN].tolist()
    all_stations_list.sort()

def get_table(use_all_stations, sel_station):
    global dfStations
    if use_all_stations:
        result = dfStations[cn.STATION_SUMMARY_TABLE_COLUMNS]
    else:
        df = dfStations[(dfStations[cn.STATION_NAME_COLUMN] == sel_station)]
        result = '<table style="font-size: 0.6em"><thead><tr><th>Field</th><th>Value</th></tr></thead>'
        for key, value in df.iteritems():
            result += '<tr><td>{0}</td><td>{1}</td><tr>'.format(key, df.iloc[-1][key])
        result += '</table>'
    
    return result
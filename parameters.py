import streamlit as st
import pandas as pd
import fontus_db as db
import constants as cn

dfParameters = pd.DataFrame
dfValues = pd.DataFrame
all_parameters_list = []

def init():
    global dfParameters
    global dfValues
    global all_parameters_list

    dfParameters = db.dfParameters
    dfValues = db.dfValues
    all_parameters_list = dfParameters[cn.PAR_NAME_COLUMN].unique().tolist()
    all_parameters_list.sort()

def get_table(use_all_stations, sel_stations_list):
    global dfParameters
    global dfValues

    if use_all_stations:
        result = dfParameters
    else:
        result = dfParameters
        #result = dfParameters[(dfStations['RIVER_NAME'].isin(sel_stations_list))]
        #result.sort(['RIVER_NAME', 'STATION_NAME'])
    return result

def get_parameters(df):
    result = df.PARM_DESCRIPTION.unique()
    result.sort('PARM_DESCRIPTION')
    return result

def get_sample_parameters(rivers_sel):
    # filter samples to include only samples listed in the rivers-selection
    result = db.dfValues[(db.dfValues['RIVER_NAME'].isin(rivers_sel))]
    # make unqique list of parameters from the filtered table
    lst_par = result.PARM.unique()
    # filter the parameter table to include only parameters from the filtered sample list
    result = db.dfParameters[(db.dfParameters[cn.PAR_NAME_COLUMN].isin(lst_par))]
    result = result.PARM_DESCRIPTION

    return result.tolist()

# returns the key for a given parameter description. the lists hold parameter descriptions, so they are easier to understand
# in the graphs, we need to reference the keys. e.g. Description: CALCIUM and key: CAUT.
def get_parameter_key(value):
    df = db.dfParameters[(db.dfParameters[cn.PAR_NAME_COLUMN] == value)]
    df = df.set_index(cn.PAR_NAME_COLUMN, drop = False)
    return  df.at[value,cn.PAR_NAME_COLUMN]
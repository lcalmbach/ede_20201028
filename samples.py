import streamlit as st
import pandas as pd
import fontus_db as db
import numpy as np
import constants as cn

def get_pivot_data(df):
    df = df.reset_index(drop = False)
    result = pd.pivot_table(df, values = cn.VALUES_VALUE_COLUMN, index=[cn.STATION_NAME_COLUMN, cn.SAMPLE_DATE_COLUMN, cn.VALUES_SAMPLENO_COLUMN], columns=[cn.PAR_NAME_COLUMN], aggfunc = np.average)
    return result

def get_table(sel_station):
    criteria = "{0} = '{1}'".format(cn.STATION_NAME_COLUMN, sel_station)
    result = db.read_values(criteria)
    result = get_pivot_data(result)
    
    return result

def get_number(station_name):
    result = db.dfSamples[db.dfSamples[cn.STATION_NAME_COLUMN] == station_name].count()[cn.STATION_NAME_COLUMN]
    return result



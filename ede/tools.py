'''
    collection of useful functions
'''
import config as cn
import streamlit as st
import pandas as pd
import numpy as np

def get_cs_item_list(lst, separator = ',', quote_string = ""):
    result = ''
    for item in lst:
        result += quote_string + str(item) + quote_string + separator
    result =  result[:-1]
    return result


def show_table(df, values):
    fig = go.Figure(data=[go.Table(
    header=dict(values=list(df.columns),
                fill_color='silver',
                line_color='darkslategray',
                align='left'),
    cells=dict(values=values,
               fill_color='white',
               line_color='darkslategray',
               align='left'))
    ])
    st.write(fig)

def get_pivot_data(df, group_by):
    if group_by == 'station':
        result = pd.pivot_table(df, values=cn.VALUES_VALUE_COLUMN, index=[cn.SAMPLE_DATE_COLUMN, cn.STATION_NAME_COLUMN, cn.MONTH_COLUMN, cn.YEAR_COLUMN], columns=[cn.PAR_NAME_COLUMN], aggfunc=np.average)
    elif group_by == cn.SEASON_COLUMN:
        result = pd.pivot_table(df, values=cn.VALUES_VALUE_COLUMN, index=[cn.SAMPLE_DATE_COLUMN, cn.MONTH_COLUMN, cn.STATION_NAME_COLUMN,cn.YEAR_COLUMN], columns=[cn.PAR_NAME_COLUMN], aggfunc=np.average)
    elif group_by == cn.YEAR_COLUMN:
        result = pd.pivot_table(df, values=cn.VALUES_VALUE_COLUMN, index=[cn.SAMPLE_DATE_COLUMN, cn.STATION_NAME_COLUMN, cn.YEAR_COLUMN], columns=[cn.PAR_NAME_COLUMN], aggfunc=np.average)
    else:
        result = pd.pivot_table(df, values=cn.VALUES_VALUE_COLUMN, index=[cn.SAMPLE_DATE_COLUMN, cn.STATION_NAME_COLUMN, cn.YEAR_COLUMN], columns=[cn.PAR_NAME_COLUMN], aggfunc=np.average)
    return result



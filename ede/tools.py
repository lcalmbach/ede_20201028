'''
    collection of useful functions
'''
import config as cn
import streamlit as st
import pandas as pd
import numpy as np
import base64

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

def get_table_download_link(df):
    '''Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    '''
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}">Download csv file</a>'
    
    return href

def transpose_dataframe(df):
    '''Transposes a dataframe that has exactly 1 row so column names become row headers
    in: dataframe with 1 row and n columns
    out: transposed dataframe with 2 columns and n rows
    '''

    result = pd.DataFrame({"Field":[], "Value":[]}) 
    for key, value in df.iteritems():
        df2 = pd.DataFrame({"Field": [key], "Value": [df.iloc[-1][key]]}) 
        result = result.append(df2)
    result = result.set_index('Field')
    return result
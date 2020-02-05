"""
    collection of useful functions
"""
import config as cn
import streamlit as st
import pandas as pd
import numpy as np
import base64
from random import seed
from random import randint
from datetime import datetime

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


def color_gradient(row, value_col: str, min_val: float, max_val: float, rgb: str) -> int:
    """
    projects a value on a color gradient scale given the min and max value. 
    the color gradient type is defined in the config, e.g. blue-green, red, blue etc.
    returns a string with rgb values
    """

    result = {'r': 0, 'g': 0, 'b': 0}
    if max_val - min_val != 0:
        x = int((row[value_col] - min_val) / (max_val - min_val) * 255)
    else:
        x = 0

    if cn.GRADIENT == 'blue-green':
        if row[value_col] > max_val:
            result['r'] = 255
        else:
            result['g'] = x
            result['b'] = abs(255 - x)
    return result[rgb]

def get_pivot_data(df, group_by):
    """
    Returns a pivot table from the raw data table. df must include the station name, the data column and the
    group by column.

    :param df:
    :param group_by:
    :return:
    """

    result = pd.pivot_table(df, values=cn.VALUES_VALUE_COLUMN, index=[cn.SAMPLE_DATE_COLUMN, cn.STATION_NAME_COLUMN,
                             group_by], columns=[cn.PAR_NAME_COLUMN], aggfunc=np.average)
    return result

def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}">Download csv file</a>'
    
    return href

def transpose_dataframe(df):
    """Transposes a dataframe that has exactly 1 row so column names become row headers
    in: dataframe with 1 row and n columns
    out: transposed dataframe with 2 columns and n rows
    """

    result = pd.DataFrame({"Field":[], "Value":[]}) 
    for key, value in df.iteritems():
        df2 = pd.DataFrame({"Field": [key], "Value": [df.iloc[-1][key]]}) 
        result = result.append(df2)
    result = result.set_index('Field')
    return result

def log(expression: str):
    """
    logs the expression with a timestamp to the console

    :param expression:
    :return:
    """

    print(datetime.now(), expression)
"""This example is a Streamlit implementation of an interactive groundwater quality data app.
This app allows to explore the Provincial Groundwater Monitoring Network dataset encompassing 
over XX years of data. The data can be explored using various Altair plots.
Author: Lukas Calmbach lcalmbach@gmail.com
"""

import streamlit as st
import pandas as pd
import numpy as np
import time
import altair as alt

import config as cn
import fontus as ft
import tools
import database as db

_controls = {}
dc = ft.DataCollection(0)

def ctrl(key):
    return _controls[key]

def main():
    init()
    show_menu()
    #st.sidebar.markdown('---')
    #txt.info_sideboard('ABOUT')

def init():
    global _controls
    global dc

    _controls = init_controls()
    # init the datacollection
    db.init()
    dc = ft.DataCollection(_controls['data_collection'])

def init_controls():
    '''initializes the controls dictionary holding the values for all widgets'''
    result = {
        'menu': ''
        , 'data_collection': cn.DEFAULT_DATA_COLLECTION_ID
        , 'dataset': 0
        , 'plot_type': ''
        , 'filter_stations_cb': True
        , 'station_list_multi': []
        , 'station_list': ''
        , 'xpar': ''
        , 'ypar': ''
        , 'plot_group_by': 'station'
        , 'group_by': 'year'
        , 'define_axis_limits': False
        , 'max_x': 0
        , 'max_y': 0
        , 'min_x': 0
        , 'min_y': 0
        , 'bin_size': 0
        , 'bar_direction': ''
        , 'filter_by_year': False       #check box if you want to select a year
        , 'filter_by_season': False      #check box if you want to select a month
        , 'filter_season': 0             #holds selected month
        , 'filter_year': 0              #holds selected year
        , 'plot_width' : cn.plot_width
        , 'plot_height' : cn.plot_height
        , 'show_data': False
    }
    return result

def info_sideboard():
    st.sidebar.subheader("About")
    text = "This app has been developed by [Lukas Calmbach](mailto:lcalmbach@gmail.com) using [Python](https://www.python.org/), [Streamlit](https://streamlit.io/) and [Altair](https://altair-viz.github.io/). All sourcecode is published on [github](https://github.com/lcalmbach/pwqmn)."
    st.sidebar.info(text)

def show_menu():
    global _controls

    st.sidebar.markdown('![logo]({}) <b>Environmental Data Explorer</b>'.format(cn.LOGO_REFERENCE), unsafe_allow_html=True)
    _controls['data_collection'] = st.sidebar.selectbox('Select a data collection', dc.data_collection_options, format_func = lambda x: dc.data_collection_display[x])

    #only show the dataset selection of there is more than 1 set
    if len(dc.dataset_options) > 1:
        _controls['dataset'] = st.sidebar.selectbox('Select a dataset', dc.dataset_options, format_func = lambda x: dc.dataset_display[x])
    else:
        _controls['dataset'] = dc.dataset_options[0]
    dc.dataset_id= _controls['dataset']
    # now that the dataset id is set init station and parameter lists
    
    st.sidebar.header('Menu')
    _controls['menu'] = st.sidebar.radio('', cn.menu_list, index = 0, key = None) # format_func=<class 'str'>, 
    st.sidebar.markdown('---')
    if _controls['menu'] == 'Info':
        dc.render_about_text()
        info_sideboard()
    elif _controls['menu'] == 'Help':
        tools.print_help()
    elif _controls['menu'] == 'Station information':
        dc.stations.render_menu(_controls)
    elif _controls['menu'] == 'Parameters information':
        dc.parameters.render_menu(_controls, dc.stations)
    elif _controls['menu'] == 'Plotting':
        plt = ft.Charting(dc, _controls)
        plt.render_menu()

if __name__ == "__main__":
    main()
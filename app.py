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

import constants as cn
import fontus_texts as txt
import fontus_db as db
import plots as plt
import stations, parameters, samples, tools
import data_collection as dc

_controls = {}

def ctrl(key):
    return _controls[key]

def main():
    init()
    show_menu()
    #st.sidebar.markdown('---')
    #txt.info_sideboard('ABOUT')

def init():
    global _controls

    _controls = init_controls()
    db.init()

# register all widgets
def init_controls():
    result = {
        'menu': ''
        , 'data_collection': ''  #chemistry, waterlevels, precipitation
        , 'dataset': ''
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

def plots_menu():
    global _controls

    _controls = plt.render_menu(_controls)
    if _controls['plot_group_by'] == 'none':
        criteria = tools.get_criteria_expression(_controls)
        df = db.read_values(criteria)
        plot_results_list = plt.plot('', df, _controls)
        # verify if the data has rows
        if (len(plot_results_list[1]) > 0):
            st.write(plot_results_list[0].properties(width = ctrl('plot_width'), height = ctrl('plot_height')))
            if ctrl('show_data'):
                st.dataframe(plot_results_list[1])
        else:
            st.write('Insufficient data')
    elif _controls['plot_group_by'] == 'year':
        pass
    elif _controls['plot_group_by'] == 'season':
        for season in cn.season_list:
            criteria = "{0} = '{1}'".format(cn.SEASON_COLUMN, season)
            df = db.read_values(criteria)
            if ctrl('filter_month'):
                df = dfStationValues[(df.MONTH == int(ctrl('month')))]
            if ctrl('filter_year'):
                df = df[(df.YEAR == int(ctrl('year')))]
            plot_title = season

            plot_results_list = plt.plot(plot_title, df, _controls)
            # verify if the data has rows
            if (len(plot_results_list[1]) > 0):
                st.write(plot_results_list[0].properties(width = ctrl('plot_width'), height = ctrl('plot_height')))
                if ctrl('show_data'):
                    st.dataframe(plot_results_list[1])
            else:
                st.write('Insufficient data for: ' + plot_title)
    elif _controls['plot_group_by'] == 'aquifer type':
        for group in stations.get_aquifer_types():
            criteria = "{0} = '{1}'".format(cn.AQUIFER_TYPE_COLUMN, group)
            df = db.read_values(criteria)

            plot_results_list = plt.plot(plot_title, df, _controls)
            # verify if the data has rows
            if (len(plot_results_list[1]) > 0):
                st.write(plot_results_list[0].properties(width = ctrl('plot_width'), height = ctrl('plot_height')))
                if ctrl('show_data'):
                    st.dataframe(plot_results_list[1])
            else:
                st.write('Insufficient data for: ' + plot_title)
    elif _controls['group_by'] == 'station' or _controls['plot_type'] == 'time series':
        # if a station filter is set, then loop through these stations otherwise loop through all stations
        list_of_stations = []
        if not ctrl('filter_stations_cb'):
            list_of_stations = stations.all_stations_list
        else:
            list_of_stations = ctrl('station_list_multi')

        for station in list_of_stations:
            criteria = "{0} = '{1}'".format(cn.STATION_NAME_COLUMN, station)
            dfStationValues = db.read_values(criteria)
            if ctrl('filter_month'):
                dfStationValues = dfStationValues[(dfStationValues.MONTH == int(ctrl('month')))]
            if ctrl('filter_year'):
                dfStationValues = dfStationValues[(dfStationValues.YEAR == int(ctrl('year')))]
            plot_title = station
            show_all_stations = True
            
            plot_results_list = plt.plot(plot_title, dfStationValues, _controls)
            # verify if the data has rows
            if (len(plot_results_list[1]) > 0):
                st.write(plot_results_list[0].properties(width = ctrl('plot_width'), height = ctrl('plot_height')))
                # if a station has been selected display a link to visit site on google maps
                if not show_all_stations and len(_controls['station_list_multi']) == 1:
                    stations.dfStations.set_index(cn.STATION_NAME_COLUMN, inplace = True)
                    lat = stations.dfStations.at[_controls['station'],'lat']
                    lon = stations.dfStations.at[_controls['station'],'lon']
                    loc = stations.dfStations.at[_controls['station'],'LOCATION']
                    lnk = 'Location: {0}. [Visit station on GOOGLE maps](https://www.google.com/maps/search/?api=1&query={1},{2} "open in GOOGLE maps")'.format(loc, lat, lon)
                    st.markdown(lnk)
                if ctrl('show_data'):
                    st.dataframe(plot_results_list[1])
            else:
                st.write('Insufficient data for: ' + plot_title)
    else:
        show_all_stations = True
        plot_title = 'Map'
        df = stations.dfStations
        if len(ctrl('station_list_multi')) == 1:
            pass
        elif len(ctrl('station_list_multi')) > 1:
            df = stations.dfStations[(stations.dfStations[cn.STATION_NAME_COLUMN].isin(ctrl('station_list_multi')))]
            if not show_all_stations:
                df = df[(df[cn.STATION_NAME_COLUMN] == ctrl('station'))]
        
        if df.shape[0] > 0:
            plt.plot_map(df, ctrl)
            st.write('if map appears empty, use mouse wheel to zoom out, until markers appear.')
        else:
            st.write('Insufficient data')

def show_menu():
    global _controls

    st.sidebar.markdown('![logo]({}) <b>Environmental Data Explorer</b>'.format(cn.LOGO_REFERENCE), unsafe_allow_html=True)
    _controls['data_collection'] = st.sidebar.selectbox('Data collection', db.DATA_COLLECTION_LIST)
    dsl = db.get_dataset_list(_controls['data_collection'])
    if len(dsl) > 1:
        _controls['dataset'] = st.sidebar.selectbox('Dataset', dsl)
    else:
        _controls['dataset'] = dsl[0]
    db.set_dataset_id(_controls['dataset'])
    # now that the dataset id is set init station and parameter lists
    parameters.init()
    stations.init()
    
    st.sidebar.header('Menu')
    _controls['menu'] = st.sidebar.radio('', cn.menu_list, index = 0, key = None) # format_func=<class 'str'>, 
    st.sidebar.markdown('---')
    if _controls['menu'] == 'Info':
        dc.render_about_text(_controls['data_collection'])
    elif _controls['menu'] == 'Help':
        txt.print_help()
    elif _controls['menu'] == 'Station information':
        stations.render_menu(_controls)
    elif _controls['menu'] == 'Parameters information':
        parameters.render_menu(_controls)
    elif _controls['menu'] == 'Plotting':
        plots_menu()

if __name__ == "__main__":
    main()
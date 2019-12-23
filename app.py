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

_controls = {}

def ctrl(key):
    return _controls[key]

def main():
    init()
    show_menu()
    st.sidebar.markdown('---')
    txt.info_sideboard('ABOUT')

def init():
    global _controls

    _controls = init_controls()
    db.init()
    stations.init(db.dfStations)
    parameters.init()
    txt.init()

# register all widgets
def init_controls():
    result = {
        'menu': ''
        , 'data_type': ''  #chemistry, waterlevels, precipitation
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
        , 'filter_by_month': False      #check box if you want to select a month
        , 'filter_month': 0             #holds selected month
        , 'filter_year': 0              #holds selected year
        , 'plot_width' : cn.plot_width
        , 'plot_height' : cn.plot_height
        , 'show_data': False
    }
    return result

def station_menu():
    global _controls

    st.subheader(ctrl('menu'))
    stations.init(db.dfStations)
    parameters.init()
    #sidebar menu
    _controls['filter_stations_cb'] = st.sidebar.checkbox('All wells', value=False, key=None)
    if not _controls['filter_stations_cb']:
        _controls['station_list'] = st.sidebar.selectbox(label = cn.STATION_WIDGET_NAME, options = stations.all_stations_list) 
    # content either html table of dataframe
    obj = stations.get_table(ctrl('filter_stations_cb'), ctrl('station_list'))
    #df.reset_index(inplace = True) #needed so station_name can be selected on plotly table
    if type(obj) is str:
        st.markdown(obj, unsafe_allow_html=True)
        criteria = "{0} = '{1}'".format(cn.STATION_NAME_COLUMN, ctrl('station_list'))
        text = '### {0} has {1} samples'.format(ctrl('station_list'), samples.get_number(ctrl('station_list')))
        st.markdown('')
        st.markdown(text)
        st.write(samples.get_table(ctrl('station_list')))
    else:  
        column_values = [obj.PGMN_WELL, obj.AQUIFER_LI, obj.STRATIGRAP, obj.WELL_DEPTH, obj.SCREEN_HOL, obj.first_year, obj.last_year, obj.number_of_samples]
        txt.show_table(obj, column_values)
    
    text = r'[View all wells on my google maps](https://drive.google.com/open?id=12WTf4bepPi9u6rtFDSMXIiBCOOzcz09p&usp=sharing)'
    st.markdown(text)

def parameters_menu():
    global _controls

    st.header(_controls['menu'])
    #sidebar menu
    _controls['filter_stations_cb'] = st.sidebar.checkbox('All wells', value=False, key=None)
    if not ctrl('filter_stations_cb'):
        _controls['station_list_multi'] = st.sidebar.multiselect(label = 'PGMN well', default = ('W0000083-1',), options = stations.all_stations_list) 
    # content
    df = parameters.get_table(ctrl('filter_stations_cb'), ctrl('station_list_multi'))
    df = df[[cn.PAR_NAME_COLUMN, cn.PAR_LABEL_COLUMN]]
    values = [df.ParameterName]
    txt.show_table(df, values)
    if not ctrl('filter_stations_cb'):
        text = "This parameter list only includes parameters having been measured in the selected well."
    else:
        text = "This parameter list includes all parameters having been measured in the monitoring network."
    st.markdown(text)

def plots_menu():
    global _controls

    _controls = plt.show_widgets(_controls)
    if _controls['plot_group_by'] == 'none':
        criteria = tools.get_criteria_expression(_controls)
        st.write(criteria)
        dfStationValues = db.read_values(criteria)
        
        plot_results_list = plt.plot('', dfStationValues, _controls)
        # verify if the data has rows
        if (len(plot_results_list[1]) > 0):
            st.write(plot_results_list[0].properties(width = ctrl('plot_width'), height = ctrl('plot_height')))
            if ctrl('show_data'):
                st.dataframe(plot_results_list[1])
        else:
            st.write('Insufficient data')
    elif _controls['group_by'] == 'station' or _controls['plot_type'] == 'time series':
        for station in ctrl('station_list_multi'):
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
                    db.dfStations.set_index('PGMN_WELL', inplace = True)
                    lat = db.dfStations.at[_controls['station'],'lat']
                    lon = db.dfStations.at[_controls['station'],'lon']
                    loc = db.dfStations.at[_controls['station'],'LOCATION']
                    lnk = 'Location: {0}. [Visit station on GOOGLE maps](https://www.google.com/maps/search/?api=1&query={1},{2} "open in GOOGLE maps")'.format(loc, lat, lon)
                    st.markdown(lnk)
                if ctrl('show_data'):
                    st.dataframe(plot_results_list[1])
            else:
                st.write('Insufficient data for: ' + plot_title)
    else:
        show_all_stations = True
        plot_title = 'Map'
        df = db.dfStations
        if len(ctrl('station_list_multi')) == 1:
            pass
        elif len(ctrl('station_list_multi')) > 1:
            df = db.dfStations[(db.dfStations[cn.STATION_NAME_COLUMN].isin(ctrl('station_list_multi')))]
            if not show_all_stations:
                df = df[(df[cn.STATION_NAME_COLUMN] == ctrl('station'))]
        
        if df.shape[0] > 0:
            plt.plot_map(df, ctrl)
            st.write('if map appears empty, use mouse wheel to zoom out, until markers appear.')
        else:
            st.write('Insufficient data')

def show_menu():
    global _controls

    st.sidebar.markdown('![logo](/static/images/logo.jpg "Logo")')
    st.sidebar.header('Menu')
    _controls['menu'] = st.sidebar.radio('', cn.menu_list, index = len(cn.menu_list) - 1, key = None) # format_func=<class 'str'>, 
    st.sidebar.markdown('---')

    if _controls['menu'] == 'Info':
        txt.print_main_about(db.dfStations, db.dfParameters, db.dfSamples)
    elif _controls['menu'] == 'Help':
        txt.print_help()
    elif _controls['menu'] == 'Station information':
        station_menu()
    elif _controls['menu'] == 'Parameters information':
        parameters_menu()
    elif _controls['menu'] == 'Plotting':
        plots_menu()

if __name__ == "__main__":
    main()
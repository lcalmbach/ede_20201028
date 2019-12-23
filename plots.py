import streamlit as st
import pandas as pd
import numpy as np
import time
import altair as alt
import fontus_db as db
import constants as cn
import stations, parameters

group_by_dic = {'station':cn.STATION_NAME_COLUMN,'month':cn.MONTH_COLUMN,'year':cn.YEAR_COLUMN,'season':cn.SEASON_COLUMN}

def get_pivot_data(df, group_by):
    if group_by == 'station':
        result = pd.pivot_table(df, values=cn.VALUES_VALUE_COLUMN, index=[cn.SAMPLE_DATE_COLUMN, cn.STATION_NAME_COLUMN, cn.MONTH_COLUMN, cn.YEAR_COLUMN], columns=[cn.PAR_NAME_COLUMN], aggfunc=np.average)
    elif group_by == cn.MONTH_COLUMN:
        result = pd.pivot_table(df, values=cn.VALUES_VALUE_COLUMN, index=[cn.SAMPLE_DATE_COLUMN, cn.MONTH_COLUMN, cn.STATION_NAME_COLUMN,cn.YEAR_COLUMN], columns=[cn.PAR_NAME_COLUMN], aggfunc=np.average)
    else:
        result = pd.pivot_table(df, values=cn.VALUES_VALUE_COLUMN, index=[cn.SAMPLE_DATE_COLUMN, cn.YEAR_COLUMN, ], columns=[cn.PAR_NAME_COLUMN], aggfunc=np.average)
    
    return result

# returns the label for a given parameter key. 
def get_label(value):
    df = db.dfParameters[(db.dfParameters[cn.PAR_NAME_COLUMN] == value)]
    df = df.set_index(cn.PAR_NAME_COLUMN, drop = False)
    return  df.at[value, cn.PAR_LABEL_COLUMN]

def plot(plt_title, df, ctrl):
    if (ctrl['plot_type']  == 'scatter plot'):
        return plot_scatter(plt_title, df, ctrl)
    elif (ctrl['plot_type'] == 'time series'):
        return plot_time_series(plt_title, df, ctrl)
    elif (ctrl['plot_type'] == 'histogram'):
        return plot_histogram(plt_title, df, ctrl)
    elif (ctrl['plot_type'] == 'box plot'):
        return plot_boxplot(plt_title, df, ctrl)
    elif (ctrl['plot_type'] == 'schoeller'):
        return plot_schoeller(plt_title, df, ctrl)
    elif (ctrl['plot_type'] == 'bar chart' and ctrl['bar_direction'] == 'horizontal'):
        return plot_bar_h(plt_title, df, ctrl)
    elif (ctrl['plot_type'] == 'bar chart' and ctrl['bar_direction'] == 'vertical'):
        return plot_bar_v(plt_title, df, ctrl)
    elif (ctrl['plot_type'] == 'map'):
        plot_map(plt_title, df, ctrl)
        return ''
    else:
        return 'invalid plottype'

def plot_schoeller(plt_title, df, ctrl):
    df = data.iris()

    base = alt.Chart(df).transform_window(
        index='count()'
        ).transform_fold(
            ['petalLength', 'petalWidth', 'sepalLength', 'sepalWidth']
        ).mark_line().encode(
            x = 'key:N',
            y = cn.VALUES_VALUE_COLUMN + ':Q',
            color = 'species:N',
            detail = 'index:N',
            opacity = alt.value(0.5)
        )
    return base

def plot_boxplot(plt_title, df, ctrl):
    result = []
    y_lab = get_label(ctrl['ypar'])
    x_lab = ''
    df = df[(df[cn.PAR_NAME_COLUMN] == ctrl['ypar']) & (df[cn.VALUES_VALUE_COLUMN] > 0)]
    
    if ctrl['max_y'] == ctrl['min_y']:
        scy = alt.Scale()
    else:
        scy = alt.Scale(domain=(ctrl['min_y'], ctrl['max_y']))
    
    base = alt.Chart(df, title = plt_title).mark_boxplot(clip=True).encode(
            alt.X(group_by_dic[ctrl['group_by']] + ':O', title = ctrl['group_by'].capitalize()),  #, axis=alt.Axis(labelAngle=0)
            alt.Y(cn.VALUES_VALUE_COLUMN + ':Q', title = y_lab, scale = scy)
            )
    result.append(base)
    result.append(df)
    return result

def plot_histogram(plt_title, df, ctrl):
    result = []
    x_lab = get_label(ctrl['ypar'])
    df = df[(df[cn.PAR_NAME_COLUMN] == ctrl['ypar']) & (df[cn.VALUES_VALUE_COLUMN] > 0)]
    df = df[[cn.VALUES_VALUE_COLUMN]]
    brush = alt.selection(type='interval', encodings=['x'])

    if ctrl['max_x'] == ctrl['min_x']:
        scx = alt.Scale()
    else:
        scx = alt.Scale(domain=(ctrl['min_x'], ctrl['max_x']))
    #use bin width if user defined
    if ctrl['bin_size'] > 0:
        bin_def = alt.Bin(step = ctrl['bin_size'])
    else:
        bin_def = alt.Bin()

    base = alt.Chart(df, title = plt_title).mark_bar().encode(
        alt.X('{}:Q'.format(cn.VALUES_VALUE_COLUMN), bin = bin_def, title = x_lab, scale = scx),
        
        y = 'count()',
    )
    
    result.append(base)
    result.append(df)
    return result

def plot_bar_h(plt_title, df, ctrl):
    result = []
    y_lab = get_label(ctrl['ypar'])
    df = df[(df[cn.PAR_NAME_COLUMN] == ctrl['ypar']) & (df[cn.VALUES_VALUE_COLUMN] > 0)]
    #brush = alt.selection(type='interval', encodings=['x'])
    if (ctrl['max_y'] == ctrl['min_y']):
        scy = alt.Scale()
    else:
        scy = alt.Scale(domain = [ctrl['min_y'], ctrl['max_y']])

    base = alt.Chart(data = df, title = plt_title).mark_bar().encode(
        alt.Y(group_by_dic[ctrl['group_by']] + ':O', title = ''),
        alt.X('mean({0}):Q'.format(cn.VALUES_VALUE_COLUMN), title = y_lab, scale = scy),
    )

    avg = alt.Chart(df).mark_rule(color='red').encode(
        x='mean({0}):Q'.format(cn.VALUES_VALUE_COLUMN)
    )
    
    result.append(base + avg)
    result.append(df)
    return result

def plot_bar_v(plt_title, df, ctrl):
    result = []
    y_lab = get_label(ctrl['ypar'])
    df = df[(df[cn.PAR_NAME_COLUMN] == ctrl['ypar']) & (df[cn.VALUES_VALUE_COLUMN] > 0)]
    #brush = alt.selection(type='interval', encodings=['x'])

    if (ctrl['max_y'] == ctrl['min_y']):
        scy = alt.Scale()
    else:
        scy = alt.Scale(domain= [ctrl['min_y'], ctrl['max_y']])
    
    base = alt.Chart(data = df, title = plt_title).mark_bar().encode(
        alt.X(group_by_dic[ctrl['group_by']] + ':O', title = ''),
        alt.Y('mean({0}):Q'.format(cn.VALUES_VALUE_COLUMN), title = y_lab, scale = scy),
    )

    avg = alt.Chart(df).mark_rule(color='red').encode(
        y = 'mean({0}):Q'.format(cn.VALUES_VALUE_COLUMN)
    )
    
    result.append(base + avg)
    result.append(df)
    return result

def plot_map(df, ctrl): 
    #df = df[(df[cn.STATION_NAME_COLUMN] == 19006403102)]
    #df = pd.DataFrame(
    #   np.random.randn(1000, 2) / [50, 50] + [46., -80.5],
    #    columns=[cn.LATITUDE_COLUMN, 'lon']
    #)
    #df = db.dfStations
    #df = df[df[cn.STATION_NAME_COLUMN].isin(rivers)]
    #if df.count == 0:
    #    df = dfStations

    midpoint = (np.average(df[cn.LATITUDE_COLUMN]), np.average(df[cn.LONGITUDE_COLUMN]))
    st.deck_gl_chart(
        viewport={
            "latitude": midpoint[0],
            "longitude": midpoint[1],
            "zoom": 20,
            "pitch": 0,
        },
        layers=[
            {
                'type': 'ScatterplotLayer',
                'data': df,
                'radiusScale': 10,
                'radiusMinPixels': 5,
                'radiusMaxPixels': 15,
                'elevationScale': 4,
                'elevationRange': [0, 10000],
                'getFillColor': [255,0,0]
            }
        ],
    )

def plot_time_series(plt_title, df, ctrl):
    result = []
    x_lab = ''
    y_lab = get_label(ctrl['ypar'])
    df = df[(df[cn.PAR_NAME_COLUMN] == ctrl['ypar']) & (df[cn.VALUES_VALUE_COLUMN] > 0)]
    if ctrl['max_y'] == ctrl['min_y']:
        scy = alt.Scale()
    else:
        scy = alt.Scale(domain=(ctrl['min_y'], ctrl['max_y']))

    base = alt.Chart(df, title = plt_title).mark_line(point = True, clip=True).encode(
        x = alt.X('SampleDate:T',
            axis=alt.Axis(title = '')),
        y = alt.Y('{}:Q'.format(cn.VALUES_VALUE_COLUMN),
            scale = scy,
            axis = alt.Axis(title = y_lab)
        ),
        color = alt.Color(cn.STATION_NAME_COLUMN,
            scale = alt.Scale(scheme = cn.color_schema)
        ),
        tooltip = [cn.STATION_NAME_COLUMN, cn.SAMPLE_DATE_COLUMN, cn.VALUES_VALUE_COLUMN]
        )
    result.append(base)
    result.append(df)
    return result

def plot_scatter(plt_title, df, ctrl):
    ok = False
    result = []

    # remove value < 0
    df = df.reset_index()
    df = df[(df[cn.PAR_NAME_COLUMN].isin([ctrl['xpar'], ctrl['ypar']]))]
    df = get_pivot_data(df, ctrl['group_by'])
    ok = (set([ctrl['xpar'], ctrl['ypar']]).issubset(df.columns))

    #filter for non values
    if ok:
        df = df[(df[ctrl['xpar']] > 0) & (df[ctrl['ypar']] > 0)]
        ok = len(df) > 0
    if ok:
        df = df.reset_index()
        x_lab = get_label(ctrl['xpar'])
        y_lab = get_label(ctrl['ypar'])

        if (ctrl['max_x'] == ctrl['min_x']):
            scx = alt.Scale()
        else:
            scx = alt.Scale(domain=(ctrl['min_x'], ctrl['max_x']))
        
        if ctrl['max_y'] == ctrl['min_y']:
            scy = alt.Scale()
        else:
            scy = alt.Scale(domain=(ctrl['min_y'], ctrl['max_x']))

        base = alt.Chart(df, title = plt_title).mark_circle(size = cn.symbol_size, clip = True).encode(
            x = alt.X(ctrl['xpar'] + ':Q',
                scale = scx,
                axis = alt.Axis(title = x_lab)),
            y = alt.Y(ctrl['ypar'] + ':Q',
                scale = scy,
                axis = alt.Axis(title = y_lab)),
                color = alt.Color(group_by_dic[ctrl['group_by']] + ':O',
                    scale=alt.Scale(scheme = cn.color_schema)
                ),
            tooltip=[cn.SAMPLE_DATE_COLUMN, group_by_dic[ctrl['group_by']], ctrl['xpar'], ctrl['ypar']]
        )
    else:
        dfEmpty = pd.DataFrame(data={'col1': [1, 2], 'col2': [3, 4]})
        base = alt.Chart(dfEmpty, title = plt_title).mark_circle(size = cn.symbol_size).encode()
        df = []
        
    result.append(base)
    result.append(df)
    return result

def show_widgets(ctrl):
    #ctrl['data_type'] = st.sidebar.selectbox('Data type', cn.data_type_list)

    ctrl['plot_type'] = st.sidebar.selectbox('Plot type', cn.plot_type_list)

    ctrl['plot_group_by'] = st.sidebar.selectbox('Plot group by', pd.Series(cn.plot_group_by_list))
    if ctrl['plot_type'] == 'time series':
        ctrl['group_by'] = 'station'
    else:
        ctrl['group_by'] = st.sidebar.selectbox('Markers group by', pd.Series(cn.group_by_list))

    parameters_list = parameters.all_parameters_list
    if ctrl['plot_type'] not in ['time series', 'histogram', 'boxplot', 'bar chart', 'map']:
        ctrl['xpar'] = parameters.get_parameter_key(st.sidebar.selectbox('X-parameter', parameters_list, index = 0))
    
    if ctrl['plot_type'] not in ['map']:
        ctrl['ypar'] = parameters.get_parameter_key(st.sidebar.selectbox('Y-parameter', parameters_list, index = 1))
    
    st.sidebar.markdown('---')
    st.sidebar.markdown('#### Filter')
    # filter for stations
    if ctrl['plot_type'] == 'time series':
        ctrl['filter_stations_cb'] = True
    else:
        ctrl['filter_stations_cb'] = st.sidebar.checkbox('Filter data by station', value=False, key=None)
    
    if ctrl['filter_stations_cb']:
        ctrl['station_list_multi'] = st.sidebar.multiselect(label = cn.STATION_WIDGET_NAME, default = (cn.DEFAULT_STATION,), options = stations.all_stations_list)
    
    #filter for month or year, this is hidden for plot type time series
    if ctrl['plot_type'] not in ['time series']:
        # only show year filter if no other time filter has been selected
        if not ctrl['filter_by_year']:
            ctrl['filter_by_month'] = st.sidebar.checkbox('Filter data by month', value = False, key=None)
            if ctrl['filter_by_month']:
                ctrl['filter_month'] = st.sidebar.slider(cn.MONTH_COLUMN, min_value = 1, max_value = 12, value=None)
        # only show month filter if no other time filter has been selected
        if not ctrl['filter_by_month']:
            ctrl['filter_by_year'] = st.sidebar.checkbox('Filter data by year', value=False, key=None)
            if ctrl['filter_by_year']:
                ctrl['filter_year'] = st.sidebar.slider('Year', min_value = int(db.first_year), max_value = int(db.last_year), value = int(db.first_year)) #db.first_year, max_value = db.last_year)
    
    if ctrl['plot_type'] == 'histogram':
        ctrl['bin_size'] = st.sidebar.number_input('Bin width')

    # various plot settings such as axis length, min max on axis etc
    st.sidebar.markdown('---')
    st.sidebar.markdown('#### Plot settings')
    ctrl['define_axis_limits'] = st.sidebar.checkbox('Define axis limits', value=False, key=None)
    if ctrl['define_axis_limits']:
        if ctrl['plot_type'] not in ['time series']:
            ctrl['min_x'] = st.sidebar.number_input('Minimum X', value= 0.0)
            ctrl['max_x'] = st.sidebar.number_input('Maximum X', value= 0.0)
        ctrl['min_y'] = st.sidebar.number_input('Minimum y', value= 0.0)
        ctrl['max_y'] = st.sidebar.number_input('Maximum y', value= 0.0)
    if ctrl['plot_type'] == 'bar chart':
        ctrl['bar_direction'] = st.sidebar.radio('Bars', ['vertical', 'horizontal'])

    ctrl['define_axis_length'] = st.sidebar.checkbox('Define axis length', value=False)
    if ctrl['define_axis_length']:
        ctrl['plot_width'] = st.sidebar.number_input('Width (pixel)', value = ctrl['plot_width'])
        ctrl['plot_height'] = st.sidebar.number_input('Height (pixel)', value = ctrl['plot_height'])
    
    ctrl['show_data'] = st.sidebar.checkbox('Show detail data', value = False, key = None)

    return ctrl
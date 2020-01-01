import streamlit as st
import pandas as pd
import fontus_db as db
import constants as cn
import tools, samples

dfStations = pd.DataFrame
all_stations_list = []
    
def init():
    global dfStations
    global all_stations_list
    
    dfStations = get_all_stations()
    all_stations_list = dfStations[cn.STATION_NAME_COLUMN].tolist()
    all_stations_list.sort()

def get_table(use_all_stations, sel_station_list):
    global dfStations

    if use_all_stations:
        query = "SELECT * FROM envdata.v_stations_all where dataset_id = {0}".format(db.DATASET_ID)
        result = db.execute_query(query)
    else:
        result = pd.DataFrame({"Field":[], "Value":[]}) 
        query = "SELECT * FROM envdata.v_stations_all where station_name = '{0}'".format(sel_station_list)
        df = db.execute_query(query)
        for key, value in df.iteritems():
            df2 = pd.DataFrame({"Field": [key], "Value": [df.iloc[-1][key]]}) 
            result = result.append(df2)
    return result.set_index('Field')

'''
retrieves the list of quifer type codes used in the current dataset
out: list
'''
def get_aquifer_types():
    query = "SELECT {0} FROM envdata.v_stations_all where dataset_id = {1} order by {0}".format(cn.AQUIFER_TYPE_COLUMN, db.DATASET_ID)
    result = db.execute_query(query)
    result = result[cn.AQUIFER_TYPE_COLUMN].unique()
    result = result.tolist()
    return result

def get_all_stations():
    query = "SELECT * FROM envdata.v_stations_all where dataset_id = {} order by {}".format(db.DATASET_ID, cn.STATION_NAME_COLUMN)
    result = db.execute_query(query)
    return result

def get_samples(criteria):
    query = "SELECT * FROM envdata.v_samples_all where {} order by {}".format(criteria, cn.SAMPLE_DATE_COLUMN)
    result = db.execute_query(query)
    #result = result[cn.STATION_NAME_COLUMN].tolist()
    return result

def render_menu(ctrl):
    st.subheader(ctrl['menu'])
    #sidebar menu
    ctrl['filter_stations_cb'] = st.sidebar.checkbox('All stations', value = False, key = None)
    if not ctrl['filter_stations_cb']:
        ctrl['station_list'] = st.sidebar.selectbox(label = cn.STATION_WIDGET_NAME, options = all_stations_list) 
    # content either html table of dataframe
    df = get_table(ctrl['filter_stations_cb'], ctrl['station_list'])
    #df.reset_index(inplace = True) #needed so station_name can be selected on plotly table
    if not ctrl['filter_stations_cb']:
        st.write(df)
        criteria = "{0} = '{1}' and {2} = {3}".format(cn.STATION_NAME_COLUMN, ctrl['station_list'], 'dataset_id', db.DATASET_ID)
        #show samples belonging to sample
        df = get_samples(criteria).set_index('id')
        text = '##### {0} has {1} samples'.format(ctrl['station_list'], len(df))
        st.markdown(text)
        st.write(df)
        #st.write(df.set_index('Field', inplace=True))
    else:  
        column_values = [df[cn.STATION_NAME_COLUMN], df.aquifer_lithology, df.stratigraphy, df.well_depth, df.screen_hole, df.min_year, df.max_year, df.number_of_samples]
        tools.show_table(df, column_values)
    
    text = r'[View all wells on my google maps](https://drive.google.com/open?id=12WTf4bepPi9u6rtFDSMXIiBCOOzcz09p&usp=sharing)'
    st.markdown(text)
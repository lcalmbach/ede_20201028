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
        query = "SELECT * FROM envdata.v_stations_all where station_name = '{0}'".format(sel_station_list)
        df = db.execute_query(query)
        result = '<table style="font-size: 0.8em"><thead><tr><th>Field</th><th>Value</th></tr></thead>'
        for key, value in df.iteritems():
            result += '<tr><td>{0}</td><td>{1}</td><tr>'.format(key, df.iloc[-1][key])
        result += '</table>'
    
    return result

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
    result = result[cn.STATION_NAME_COLUMN].tolist()
    return result

def render_menu(ctrl):
    st.subheader(ctrl['menu'])
    #sidebar menu
    ctrl['filter_stations_cb'] = st.sidebar.checkbox('All stations', value=False, key=None)
    if not ctrl['filter_stations_cb']:
        ctrl['station_list'] = st.sidebar.selectbox(label = cn.STATION_WIDGET_NAME, options = all_stations_list) 
    # content either html table of dataframe
    obj = get_table(ctrl['filter_stations_cb'], ctrl['station_list'])
    #df.reset_index(inplace = True) #needed so station_name can be selected on plotly table
    if type(obj) is str:
        st.markdown(obj, unsafe_allow_html=True)
        criteria = "{0} = '{1}' and {2} = {3}".format(cn.STATION_NAME_COLUMN, ctrl['station_list'], 'dataset_id', db.DATASET_ID)
        #show samples belonging to sample
        dfSamples = get_samples(criteria)
        text = '#### {0} has {1} samples'.format(ctrl['station_list'], len(dfSamples))
        st.markdown('')
        st.markdown(text)
        st.write(samples.get_table(ctrl['station_list']))
    else:  
        column_values = [obj[cn.STATION_NAME_COLUMN], obj.aquifer_lithology, obj.stratigraphy, obj.well_depth, obj.screen_hole, obj.first_year, obj.last_year, obj.number_of_samples]
        #txt.show_table(obj, column_values)
    
    text = r'[View all wells on my google maps](https://drive.google.com/open?id=12WTf4bepPi9u6rtFDSMXIiBCOOzcz09p&usp=sharing)'
    st.markdown(text)
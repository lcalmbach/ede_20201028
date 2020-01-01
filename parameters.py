import streamlit as st
import pandas as pd
import fontus_db as db
import constants as cn
import stations, tools

dfParameters = pd.DataFrame
dfValues = pd.DataFrame
all_parameters_list = []

def init():
    global dfParameters
    global all_parameters_list

    dfParameters = get_parameters()
    all_parameters_list = dfParameters[cn.PAR_NAME_COLUMN].tolist()

def get_parameters():
    query =  "select * from v_parameters_all where dataset_id = {0} order by {1}".format(db.DATASET_ID, cn.PAR_LABEL_COLUMN)
    result = db.execute_query(query)
    
    return result

def get_table(use_all_stations, sel_stations_list):
    global dfParameters
    global dfValues

    if use_all_stations:
        query = "select * from v_parameters_all where dataset_id = {}".format(db.DATASET_ID)
        result = db.execute_query(query)
    else:
        stations = tools.get_quoted_items_list(sel_stations_list)
        query = "select * from v_parameters_all where {0} in (select distinct {0} from envdata.values where dataset_id = {1} and station_name in ({2})) and dataset_id = {1}".format(cn.PAR_NAME_COLUMN, db.DATASET_ID, stations)
        result = db.execute_query(query)
    return result

def get_sample_parameters(station_name):
    # filter samples to include only samples listed in the rivers-selection
    result = db.dfValues[(db.dfValues[cn.STATION_NAME_COLUMN].isin(station_name))]
    # make unqique list of parameters from the filtered table
    lst_par = result.PARM.unique()
    # filter the parameter table to include only parameters from the filtered sample list
    result = db.dfParameters[(db.dfParameters[cn.PAR_NAME_COLUMN].isin(lst_par))]
    result = result.PARM_DESCRIPTION

    return result.tolist()

# returns the key for a given parameter description. the lists hold parameter descriptions, so they are easier to understand
# in the graphs, we need to reference the keys. e.g. Description: CALCIUM and key: CAUT.
def get_parameter_key(par_label):
    query = "Select * from v_parameters_all where dataset_id = {} and {} = '{}'".format(db.DATASET_ID, cn.PAR_LABEL_COLUMN, par_label)
    df = db.execute_query(query)
    return  df.at[0, cn.PAR_NAME_COLUMN]

def render_menu(ctrl):
    st.header(ctrl['menu'])
    #sidebar menu
    ctrl['filter_stations_cb'] = st.sidebar.checkbox('All stations', value=False, key=None)
    if not ctrl['filter_stations_cb']:
        ctrl['station_list_multi'] = st.sidebar.multiselect(label = cn.STATION_WIDGET_NAME, default = stations.all_stations_list[0], options = stations.all_stations_list) 
    # content
    st.write(ctrl['station_list_multi'])
    df = get_table(ctrl['filter_stations_cb'], ctrl['station_list_multi'])
    df = df[[cn.PAR_NAME_COLUMN, cn.PAR_LABEL_COLUMN, cn.PAR_UNIT_COLUMN]]
    values = [df[cn.PAR_NAME_COLUMN], df[cn.PAR_LABEL_COLUMN], df[cn.PAR_UNIT_COLUMN]]
    #txt.show_table(df, values)
    st.write("{} parameters found in stations {}".format(len(df.index), ','.join(ctrl['station_list_multi']) )) 
    st.write(df)
    if not ctrl['filter_stations_cb']:
        text = "This parameter list only includes parameters having been measured in the selected well."
    else:
        text = "This parameter list includes all parameters having been measured in the monitoring network."
    st.markdown(text)
'''
    collection of useful functions
'''
import constants as cn
import streamlit as st
import fontus_db as db

def get_quoted_items_list(lst, separator = ','):
    result = ''
    for item in lst:
        result += "'" + item + "'" + separator
    result =  result[:-1]
    return result


def get_criteria_expression(ctrl):
    result = 'dataset_id = {}'.format(db.DATASET_ID)

    if ctrl['filter_stations_cb']:
        selected_stations_list = get_quoted_items_list(ctrl['station_list_multi'], ',')
        result += " AND {0} in ({1})".format(cn.STATION_NAME_COLUMN, selected_stations_list)
    
    if ctrl['filter_by_season']:
        result += " AND {0} = '{1}'".format(cn.SEASON_COLUMN, ctrl['filter_season'])
    
    if ctrl['filter_by_year']:
        result += " AND {0} = {1}".format(cn.YEAR_COLUMN, ctrl['filter_year'])
    
    if ctrl['plot_type'] == 'scatter plot':
        par_list = get_quoted_items_list([ctrl['ypar'], ctrl['xpar']])
        st.write(par_list)
        result += " AND {} in ({})".format(cn.PAR_NAME_COLUMN, par_list)
    else:
        result += " AND {} = '{}'".format(cn.PAR_NAME_COLUMN, ctrl['ypar'])
    
    return result



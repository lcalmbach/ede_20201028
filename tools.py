'''
    collection of useful functions
'''
import constants as cn
import streamlit as st
import fontus_db as db

def get_cs_item_list(lst, separator = ',', quote_string = ""):
    result = ''
    for item in lst:
        result += quote_string + str(item) + quote_string + separator
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
    elif group_by == cn.MONTH_COLUMN:
        result = pd.pivot_table(df, values=cn.VALUES_VALUE_COLUMN, index=[cn.SAMPLE_DATE_COLUMN, cn.MONTH_COLUMN, cn.STATION_NAME_COLUMN,cn.YEAR_COLUMN], columns=[cn.PAR_NAME_COLUMN], aggfunc=np.average)
    else:
        result = pd.pivot_table(df, values=cn.VALUES_VALUE_COLUMN, index=[cn.SAMPLE_DATE_COLUMN, cn.YEAR_COLUMN, ], columns=[cn.PAR_NAME_COLUMN], aggfunc=np.average)
    
    return result



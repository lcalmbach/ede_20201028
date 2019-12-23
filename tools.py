'''
    collection of useful functions
'''
import constants as cn

def get_quoted_items_list(lst, separator):
    result = ''
    for item in lst:
        result += "'" + item + "'" + separator
    result =  result[:-1]
    return result

def get_criteria_expression(ctrl):
    result = ''

    if ctrl['filter_stations_cb']:
        selected_stations_list = get_quoted_items_list(ctrl['station_list_multi'], ',')
        result = "{0} in ({1})".format(cn.STATION_NAME_COLUMN, selected_stations_list)

    if ctrl['filter_by_month']:
        if len(result)>0:
            result += ' AND '
        result += "{0} = {1}".format(cn.MONTH_COLUMN, ctrl['filter_month'])
    if ctrl['filter_by_year']:
        if len(result)>0:
            result += ' AND '
        result += "{0} = {1}".format(cn.YEAR_COLUMN, ctrl['filter_year'])
    
    return result



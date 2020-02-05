import streamlit as st

text = "Roses are \textcolor{red}{red}, violets are \textcolor{blue}{blue}."
st.markdown(text)


def get_criteria_expression(self):
    """
    Creates the sql where clause for the set filter controls.
    :return: sql where clause
    """

    result: str = 'dataset_id = {}'.format(self.__parent.dataset_id)

    if not self.__parent.filter.station_filters:
        selected_station_list: list = tools.get_cs_item_list(self.__parent.filter.station_multilist, separator=',',
                                                             quote_string='')
        result += " AND {0} in ({1})".format('station_id', selected_station_list)

    if self.__parent.filter.filter_by_season_cb:
        result += " AND {0} = '{1}'".format(cn.SEASON_COLUMN, self.__parent.filter.season_list)

    if self.__parent.filter.filter_by_year_cb:
        if self.__parent.filter.year_slider[0] == self.__parent.filter.year_slider[1]:
            result += " AND {0} = {1}".format(cn.YEAR_COLUMN, self.__parent.filter.year_slider[0])
        else:
            result += " AND ({0} >= {1} AND {0} <= {2})".format(cn.YEAR_COLUMN, self.__parent.filter.year_slider[0],
                                                                self.__parent.filter.year_slider[1])
    if self.__plot_type == 'scatter plot':
        par_list = tools.get_cs_item_list([self.__xpar, self.__ypar])
        result += " AND {} in ({})".format('parameter_id', par_list)
    else:
        result += " AND {} = {}".format('parameter_id', self.__ypar)
    if self.__plot_type == 'map':
        result += " AND lat is not null and lon is not null and not (lat = 0 and lon = 0)"

    return result
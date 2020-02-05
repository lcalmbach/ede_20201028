"""
This module contains the classes fontus, stations, parameters and plotting
"""

__author__ = "Lukas Calmbach"

import pandas as pd

import numpy as np
import database as db
import locale

import altair as alt
import pyperclip as clipboard
import pydeck as pdk
import streamlit as st

import config as cn
import tools


class Fontus:
    """
    This class holds data on: 
    - the database connection
    - the available data collection in the database
    - the current data collection
    - the available datasets in the current data collectin
    - the current dataset
    """

    def __init__(self):
        """
        Create a new fontus session consisting of a data collection and sets id as the current data collection.
        """

        tools.log('Fontus.__init__, start')
        db.init()
        locale.setlocale(locale.LC_ALL, '')  # Use '' for auto, or force e.g. to 'en_US.UTF-8'
        self.__menu = 'Info'
        query = 'SELECT * FROM envdata.v_data_collections'
        self.__dfAll_data_collections = db.execute_query(query)
        values = self.__dfAll_data_collections[cn.DATA_COLLECTION_NAME_COLUMN].tolist()
        self.__data_collection_options = self.__dfAll_data_collections['id'].tolist()
        self.__data_collection_display = dict(zip(self.__data_collection_options, values))
        self.__dfAll_data_collections = self.__dfAll_data_collections.set_index('id')
        tools.log('__data_collection_id = 0, start')
        self.__data_collection_id = 0  # init attribute
        tools.log('__data_collection_id = 0, end')
        tools.log('__parent_id = cn.DEFAULT_DATA_COLLECTION_ID, start')
        self.__parent_id = cn.DEFAULT_DATA_COLLECTION_ID
        tools.log('__parent_id = cn.DEFAULT_DATA_COLLECTION_ID, end')
        self.__plots = Plots(self)
        tools.log('Fontus.__init__, end')

    @property
    def plots(self):
        """
        Returns a plots objects which is used to render plots and plots related
        UI controls
        :return:
        """

        return self.__plots

    @property
    def menu(self):
        """menu selection: info, plotting, parameters info, stations info"""

        return self.__menu

    @menu.setter
    def menu(self, menuitem):
        """menu selection: info, plotting, parameters info, stations info"""

        self.__menu = menuitem
        if self.__menu == 'Plotting' and self.__data_type != cn.DataType.chemistry.value:
            self.filter.filters_multilist = ['station']

            if len(self.filter.station_fields_multilist) > 0:
                self.filter.station_multilist = [self.filter.station_fields_multilist['station'].options[0]]

        self.filter.fill_controls()

    @property
    def filter(self):
        """Object holding all filter settings"""

        return self.__filter

    @property
    def dfAll_data_collections(self):
        """data frame holding all available data collection in the database"""

        return self.__dfAll_data_collections

    @property
    def data_collection_id(self):
        return self.__data_collection_id

    @data_collection_id.setter
    def data_collection_id(self, id):
        """Initializes the data collection id. sets parameter data_collection_id and reads related data from db"""

        if id != self.__data_collection_id:
            self.__data_collection_id = id
            query = "SELECT * FROM envdata.v_datasets where data_collection_id = {} order by {}".format(id,
                cn.DATASET_NAME_COLUMN)
            self.__dfDatasets = db.execute_query(query)
            values = self.__dfDatasets[cn.DATASET_NAME_COLUMN].tolist()
            self.__dataset_options = self.__dfDatasets['id'].tolist()
            self.__dataset_display = dict(zip(self.dataset_options, values))
            self.__google_maps_url = ''

            # set the new dataset_id
            query = "SELECT min(id) as id FROM envdata.v_datasets where data_collection_id = {}".format(id)
            df = db.execute_query(query)
            self.dataset_id = df.at[0, 'id']
            self.__menu = 'Info'

    @property
    def observations_view(self):
        """return view name for observations of the selected dataset"""
        return self.__observations_view

    @property
    def parameter_view(self):
        """return view name for the parameters tble of the selected dataset"""
        return self.__parameter_view

    @property
    def google_maps_url(self):
        return self.__google_maps_url

    def has_google_maps_url(self):
        return self.__google_maps_url not in (None, '')

    @property
    def dataset_id(self):
        """returns the dataset_id"""
        return self.__dataset_id

    @dataset_id.setter
    def dataset_id(self, id):
        """sets the dataset_id and retrieves a dataframe of all datasets belonging to the current data collection"""
        if id > 0:
            self.__dataset_id = id
            query = 'SELECT * FROM envdata.v_datasets where id = {}'.format(id)
            self.__dfCurr_dataset = db.execute_query(query)
            self.__dfCurr_dataset = self.__dfCurr_dataset.set_index('id')
            self.__observations_view = self.__dfCurr_dataset.at[id, 'result_view']
            self.__parameter_view = self.__dfCurr_dataset.at[id, 'parameter_view']
            self.__first_year = int(self.__dfCurr_dataset.at[id, 'first_year'])
            self.__last_year = int(self.__dfCurr_dataset.at[id, 'last_year'])
            self.__google_maps_url = self.__dfCurr_dataset.at[id, 'google_maps_url']
            self.__has_markers = self.__dfCurr_dataset.at[id, 'has_markers']
            self.__data_type = self.__dfCurr_dataset.at[id, 'data_type_id']
            query = "SELECT * FROM envdata.list_field where dataset_id = {} order by order_id".format(self.__dataset_id)
            df = db.execute_query(query)
            self.__filter = Filter(self, df)
            self.__station_main_display_view = self.__dfCurr_dataset.at[id, 'station_station_cols']
            self.__station_samples_display_view = self.__dfCurr_dataset.at[id, 'station_samples']
            self.__station_years_display_view = self.__dfCurr_dataset.at[id, 'station_samples_per_year']
            self.__parameters = Parameters(self)
            self.__stations = Stations(self)

    @property
    def station_main_display_view(self):
        """sql string querying columns for station display view, menu item stations info"""

        return self.__station_main_display_view

    @property
    def station_samples_display_view(self):
        """sql string querying columns for station display view, menu item stations info"""

        return self.__station_samples_display_view

    @property
    def station_years_display_view(self):
        """sql string querying columns for station display view, menu item stations info"""

        return self.__station_years_display_view

    @property
    def first_year(self):
        """Year of first sample collection"""
        return self.__first_year

    @property
    def data_type(self):
        """Returns data type for selected dataset:
        1:  chemistry
        2:  precipitation
        3:  water levels
        """
        return self.__data_type

    @property
    def has_markers(self):
        """If True data points in plots will be shown as circles"""
        return bool(self.__has_markers == 1)

    @property
    def last_year(self):
        """Year of most recent sample collection"""
        return self.__last_year

    @property
    def curr_data_collection(self):
        """Data frame holding current data collection record"""

        return self.__curr_data_collection

    @property
    def data_collection_options(self):
        """List of ids from data_collection table. the list is used to fill the data collection selection control"""

        return self.__data_collection_options

    @property
    def data_collection_display(self):
        return self.__data_collection_display

    @property
    def dataset_options(self):
        """List of ids from dataset table. the list is used to fill the dataset selection control"""
        return self.__dataset_options

    @property
    def dataset_display(self):
        """dictionary of dataset id:name pairs for current data collection"""
        return self.__dataset_display

    @property
    def stations(self):
        """Stations object associated with current data collection"""
        return self.__stations

    @property
    def parameters(self):
        """Parameters object associated with current data collection"""

        return self.__parameters

    def show_url_list(self):
        """
        In table refererence a list of url-references related to each data collection can be defined and rendered
        with this function.
        """

        query = "select html_reference from envdata.v_references where object_type_id = 1 and object_id = {}".format(
            self.data_collection_id)
        refs = db.execute_query(query)['html_reference'].tolist()
        for ref in refs:
            st.markdown('    * {}'.format(ref), unsafe_allow_html=True)

    def get_values(self, criteria):
        """Returns a data frame with all values matching the criteria"""

        def get_map_parameters_df():
            """
            Generates the query to sql query for a map showing average parameter for each station
            :return: sql query expression
            """

            q = """SELECT station_name, aquifer_type, depth_category, authority, water_body_name, 
                avg(calc_value) as calc_value, lat, lon FROM envdata.v_observations where {}
                group by station_name, aquifer_type, depth_category, authority, county, township, 
                water_body_name""".format(criteria)
            return q

        if self.menu == 'Plotting':
            if self.plots.plot_type == 'map':
                query = get_map_parameters_df()
            else:
                if self.plots.marker_group_by in ('none', 'station'):
                    group_by_expr = ''
                else:
                    group_by_expr = ', {}'.format(self.plots.marker_group_by)
                query = """ SELECT parameter_name, calc_value, sample_date as sample_date, station_name {} 
                from {} where {}""".format(group_by_expr, self.observations_view, criteria)

        result = db.execute_query(query)
        return result

    def render_about_text(self):
        """ Renders info on the selected data collection composed of: a header image, some explenatory text,
        a metadatatable for the data collection and metadata for each dataset included in the data collection
        """

        myid = self.__data_collection_id
        df = self.dfAll_data_collections
        st.image('static/images/' + df.at[myid, 'about_image'])
        st.write(df.at[myid, 'name_long'])
        text = df.at[myid, 'about_text']
        st.markdown(text)

        # metadata for 
        st.markdown('### Metadata from data owner:')
        st.markdown('* Publisher: {0}'.format(df.at[myid, 'publisher']))
        st.markdown('* Update frequency: {0}'.format(df.at[myid, 'update_frequency']))
        st.markdown('* Geographical coverage: {0}'.format(df.at[myid, 'geographical_coverage']))
        st.markdown('** Additional information on data collection: **')
        self.show_url_list()
        st.markdown('---')
        df = self.__dfDatasets
        list_of_dataset_ids = df['id'].tolist()
        df = df.set_index('id')
        st.markdown('### Summary of datasets available in the data collection:')
        for dataset in list_of_dataset_ids:
            n_samples = df.at[dataset, 'number_of_samples']
            description = df.at[dataset, 'description']

            st.markdown('#### Dataset: {0}'.format(df.at[dataset, 'name']))
            if description > '':
                st.markdown('* *Description*: {}'.format(description))
            st.markdown('* *Number of stations*: {0:n}'.format(df.at[dataset, 'number_of_stations']))
            st.markdown('* *Number of parameters*: {0:n}'.format(df.at[dataset, 'number_of_parameters']))
            if n_samples > 0:
                st.markdown('* *Number of sampling events*: {0:,}'.format(n_samples))
            st.markdown('* *Number of observations*: {0:n}'.format(df.at[dataset, 'number_of_observations']))
            st.markdown(
                '* *Time interval covered*: {} - {}'.format(df.at[dataset, 'first_year'], df.at[dataset, 'last_year']))

    def render_help(self):
        """Renders a help icon linking to the <read the docs> user manual"""

        st.sidebar.markdown(
            '<a href = "{}" target = "_blank"><img border="0" alt="Help" src="{}"></a>'.format(cn.USER_MANUAL_LINK,
                                                                                               cn.HELP_ICON),
            unsafe_allow_html=True)


class Filter:
    """ This class holds all filter control
    filter_stations_cb       if set, selected station attributes are shown to build a station filter
    station_list  a station multi list allowing to select multiple stations
    station_list
    filter_by_year_cb
    filter_year_slider
    filter_season_list
    x_list            x parameter
    x_list            y parameter
    """

    def __init__(self, parent, df_fields: pd.DataFrame):
        """initializes the filter.
        :param parent: parent of current object
        :param df_fields: data frame of filter fields
        """

        self.__parent = parent
        self.__df_filter_fields = df_fields
        self.filters_multilist = []
        self.__station_fields_multilist = dict([])
        self.__station_field_options = []
        self.station_multilist = []
        self.parameter_multilist = []
        self.parameter_list = 0
        self.year_slider = []
        self.season_list = 0

        self.__station_main_display_view = ''
        self.__station_samples_display_view = ''
        self.__station_years_display_view = ''

    def fill_controls(self):
        """Fills the dictionary __station_fields_multilist with all filter options for each menu item."""

        if len(self.__df_filter_fields) > 0:
            type_id = cn.dict_menu_filter_type[self.__parent.menu]
            tools.log('dfFilters = self., start')
            dfFilters = self.__df_filter_fields[(self.__df_filter_fields.type_id == type_id)]
            tools.log('dfFilters = self., end')
            dfFilters.set_index('key', inplace=True)
            tools.log('for row in dfFilters.itertuples, start')
            for row in dfFilters.itertuples(index=True):
                tools.log('self.__station_fields_multilist[row[0]], start')
                self.__station_fields_multilist[row[0]] = self.FilterItem(self.__parent, row)
                tools.log(row[0])
                self.__station_field_options.append(row[0])
            tools.log('fill_controls, end')

    @property
    def station_fields_multilist(self):
        """
        Returns the dictionary of filter controls for station filters. For example if the user selects aquifer and
        county from the list of available filterable fields, then two select boxes are shown to the user."""

        return self.__station_fields_multilist

    class FilterItem:
        """
        Filter item is used to dynamically generate UI station and parameter filter controls values are stored in
        table list_field.
        """

        def __init__(self, parent, row):
            self.key = row[0]
            self.field = row[3]
            self.label = row[4]
            self.default_value = row[5]
            self.value = []
            # for each menu context, a different view is used to build the options lists for stations and parameters
            # also, the views used depend on the dataset type: chemistry: using sample table, time series without sample
            # table
            if parent.data_type == cn.DataType.chemistry.value:
                dict_menu_menu_view = {
                    "Info": '',
                    "Station information": 'v_stations',
                    "Parameters information": 'v_parameters',
                    "Plotting": 'v_samples'
                }
            else:
                dict_menu_menu_view = {
                    "Info": '',
                    "Station information": 'v_time_series_stations',
                    "Parameters information": 'v_parameters',
                    "Plotting": 'v_time_series'
                }

            query = """select distinct value from distinct_value where column_name = '{0}' and dataset_id = {1} 
                order by value
                """.format(row[3], parent.dataset_id)
            tools.log(query + ', start')
            self.options = db.execute_query(query)['value'].tolist()
            tools.log(query + ', end')

    @property
    def get_expression(self) -> str:
        """Returns a filter expression depending on the menu context."""

        result = ''
        for key in self.__station_fields_multilist:
            item = self.__station_fields_multilist[key]
            if len(item.value) > 0:
                lis = tools.get_cs_item_list(item.value, ',', "'")
                result += '{} {} in ({})'.format((' AND ' if result > '' else ''), item.field, lis)

        return result

    def append_parameter_filter(self, criteria):
        """Appends a filter for x and y parameters for plots.

        :param criteria: where clause for sql statement

        :return result: initial criteria with additional filter for x and y parameter for scatter plots
                and y parameter only for most other plot types
        """

        result: str = criteria
        # in the plotting mode, parameters must be filtered for null values
        if self.__parent.menu == "Plotting":
            if self.__parent.plots.plot_type == 'scatter plot':
                par_list = tools.get_cs_item_list([self.__parent.plots.xpar, self.__parent.plots.ypar])
                result += " {} {} in ({})".format((' AND ' if result > '' else ''), 'parameter_id', par_list)
            else:
                result += " {} {} = {} AND calc_value is not null".format((' AND ' if result > '' else ''),
                                                                          'parameter_id', self.__parent.plots.ypar)
            if self.__parent.plots.plot_type == 'map':
                result += """ {} lat is not null and lon is not null and not (coalesce(lat,0) = 0 or 
                coalesce(lon,0) = 0)""".format((' AND ' if result > '' else ''))
        return result

    def render_menu(self):
        """
        Renders the filter menu. The filters_multilist is a list of filter objects read from the database
        each having a labal, default values und an options list, including all distinct values that should appear in the
        options list in the select box control for this filter.
        """

        st.sidebar.markdown('#### Data filters')
        self.filters_multilist = st.sidebar.multiselect(label='Filter data by', default=self.filters_multilist,
                                                        options=self.__station_field_options)

        for filt_fld in self.filters_multilist:
            item = self.__station_fields_multilist[filt_fld]
            criteria = self.get_expression
            if filt_fld == 'station':
                self.__parent.stations.refresh_options(criteria)
            elif filt_fld == 'parameter':
                self.__parent.parameters.refresh_options(criteria)
            item.value = st.sidebar.multiselect(label=item.label, options=item.options)


class Stations:
    """Holds all information on the stations related to the current dataset"""

    def __init__(self, parent):
        """
        Initializes the Stations objects holding all functions related to the station selection
        :param parent: session object, holding definition of data collection and dataset
        """

        self.__parent = parent
        if parent.data_type == cn.DataType.chemistry.value:
            self.station_view_name = 'v_stations'
        else:
            self.station_view_name = 'v_time_series_stations'

    def refresh_options(self, criteria):
        """
        Generates the list of stations. If a criteria is specified, only stations matching the criteria are
        used in the list.
        :param criteria: sql where clause
        """

        and_expression = '' if criteria == '' else ' AND '
        query = """SELECT station_name FROM envdata.{} where dataset_id = {} {} {} order by station_name;
                """.format(self.station_view_name, self.__parent.dataset_id, and_expression, criteria
                    , cn.STATION_NAME_COLUMN)
        df = db.execute_query(query)
        lis = df[cn.STATION_NAME_COLUMN].tolist()
        self.__parent.filter.station_fields_multilist['station'].options = lis

    def get_table(self, criteria):
        """
        Returns the metadata for all stations, if no station is selected, or the selected stations.
        :param criteria:
        :return: table as DataFrame
        """

        if criteria == '':
            query = self.__parent.station_main_display_view.format('1=1')
            df = db.execute_query(query)
        else:
            result = pd.DataFrame({"Field": [], "Value": []})
            st_lis = tools.get_cs_item_list(self.__parent.filter.station_multilist, ',', '')

            query = self.__parent.station_main_display_view.format(criteria)
            df = db.execute_query(query)

        if len(self.__parent.filter.station_fields_multilist['station'].value) == 1:
            df = tools.transpose_dataframe(df)

        return df

    def get_samples(self, sql_str: str, criteria: str):
        """
        Returns a DataFrame of samples as a DataFrame where column 0 is the field name and column 1 is its value

        Parameters
        ----------
        :param sql_str:     sql statement for stations view
        :param criteria:    sql where statement to be applied to station view
        :return:            dataframe with station list data
        """

        query = sql_str.format(criteria)
        result = db.execute_query(query)

        return result

    def draw_map(self, station_name, criteria):
        """Draws a map of all selected stations. If no filter is set, all stations are shown."""

        if criteria == '':
            query = """select lat, lon, id as value from {} where dataset_id = {} and not (lat = 0 and lon = 0)
                    """.format(self.station_view_name, self.__parent.dataset_id)
            title = 'All stations in dataset'
        else:
            query = """select lat, lon, id as value from {} where dataset_id = {} and not (lat = 0 and lon = 0) 
                    and {}""".format(self.station_view_name, self.__parent.dataset_id, criteria)
            title = station_name

        df = db.execute_query(query)
        self.__parent.plots.plot_map(title, df, 'ScatterplotLayer', '')

        if self.__parent.has_google_maps_url():
            text = r'[View all wells on my google maps]({})'.format(self.__parent.google_maps_url)
            st.markdown(text)

    def get_yearly_sample_summary_table(self, criteria) -> pd.DataFrame:
        """
        Returns a DataFrame with 1 record for every year when samples were collected
        :param criteria: where clause for sql statement
        :return:
        """

        query = self.__parent.station_years_display_view.format(criteria)
        df = db.execute_query(query)
        return df

    def render_menu(self):
        """
        Renders the station info menu controls and calls the procedures to show tables and a map for all or the
        selected stations.
        """

        # sidebar menu
        self.__parent.filter.render_menu()

        # content either html table of DataFrame
        criteria = self.__parent.filter.get_expression
        df = self.get_table(criteria)
        station_name = ''

        # df.reset_index(inplace = True) #needed so station_name can be selected on plotly table
        lis = self.__parent.filter.station_fields_multilist['station'].value
        if len(lis) == 1:
            station_name = lis[0]
            st.markdown('#### {}'.format(station_name))
            st.write(df)
            df.reset_index(inplace=True)  # make sure first column is exported
            st.markdown(tools.get_table_download_link(df), unsafe_allow_html=True)

            # show samples belonging to sample
            df = self.get_samples(self.__parent.station_samples_display_view, criteria)

            number_of_samples = len(df)

            # title is different for chem samples and time series, with only 1 parameter
            if self.__parent.data_type == cn.DataType.chemistry.value:
                # sample summary table
                text = '#### {0} has {1} samples'.format(station_name, number_of_samples)
                st.markdown(text)
                st.write(df)
                st.markdown(tools.get_table_download_link(df), unsafe_allow_html=True)

                # yearly summary table
                df = self.get_yearly_sample_summary_table(criteria)
                st.markdown('#### Samples by year')
                st.write(df)
            else:
                text = "#### Summary of measurements at station {}".format(station_name)
                st.markdown(text)
                st.write(df)
        else:
            st.markdown("#### Selected stations ({})".format(df.shape[0]))
            st.dataframe(df)

        st.markdown(tools.get_table_download_link(df), unsafe_allow_html=True)
        clipboard.copy(station_name)  # copy station name to clipboard so it can be pasted into google map if required
        self.draw_map(station_name, criteria)

    def get_values(self, criteria):
        """ Returns a data frame with all values matching the criteria"""

        query = "Select * from {} where {}".format(self.station_view_name, criteria)
        result = db.execute_query(query)
        return result


class Parameters:
    def __init__(self, parent):
        self.__parent = parent
        query = "select id, {0}, {1}, {2} from envdata.parameter where dataset_id = {3} order by {0}".format(
            cn.PAR_NAME_COLUMN, cn.PAR_LABEL_COLUMN, cn.PAR_UNIT_COLUMN, self.__parent.dataset_id)
        df = db.execute_query(query)
        values = df[cn.PAR_NAME_COLUMN].tolist()
        self.__parameters_options = df['id'].tolist()
        self.__parameters_display = dict(zip(self.__parameters_options, values))
        self.__dfParameters = df.set_index('id')

    @property
    def parent(self):
        return self.__parent

    @property
    def dfParameters(self):
        return self.__dfParameters

    @property
    def parameters_options(self):
        return self.__parameters_options

    @property
    def parameters_display(self):
        return self.__parameters_display

    def refresh_options(self, criteria):
        """
        Generates the list of parameters. if a criteria is specified, only parameters matching the criteria are
        used in the list.

        Parameters
        ----------
        :param criteria:
        :return:
        """
        if criteria == '':
            query = """SELECT parameter_name FROM envdata.v_parameters where dataset_id = {0} order by parameter_name;
                """.format(self.__parent.dataset_id)
        else:
            query = """SELECT parameter_name FROM envdata.v_parameters where dataset_id = {0} and {1} order by 
                parameter_name;""".format(self.__parent.dataset_id, criteria)
        df = db.execute_query(query)
        lis = df[cn.PAR_NAME_COLUMN].tolist()
        self.__parent.filter.station_fields_multilist['parameter'].options = lis

    # def get_table(self):
    #    """Returns a list of parameters matching the filters set. If no filter is set, all parameters are shown. if a single parameter is selected
    #    more detail about the selected parameter is shown including a link to more information on NIH Toxnet"""
    #
    #        st.write(self.__parent.filter.station_fields_multilist['parameter'].value)
    ###        if self.__parent.filter.station_fields_multilist['parameter'].value == []:
    #            query = """select t1.parameter_name, t1.formula, t1.unit, t2.min_value, t2.max_value, t2.average_value, t2.number_of_values
    #            from envdata.v_parameters where parameter_id in ({})""".format(self.__parent.dataset_id, self.__parent.filter.station_fields_multilist['parameter'].options)
    #            result = db.execute_query(query)
    #        else:
    #            stations = tools.get_cs_item_list(lst = self.__parent.filter.station_multilist, separator = ',', quote_string = '')
    #            query = """select t1.parameter_name, t1.formula, t1.unit, t2.min_value, t2.max_value, t2.average_value, t2.number_of_values from
    ##                        envdata.v_parameters t1
    ##                        inner join (select parameter_id, min(calc_value) min_value, max(calc_value) max_value, avg(calc_value) average_value, count(*) as number_of_values from
    #                        envdata.v_observations where dataset_id = {} and station_id in ({}) group by parameter_id) t2 on t2.parameter_id = t1.id""".format(self.__parent.dataset_id, stations)
    #            result = db.execute_query(query)
    #        return result

    # def get_sample_parameters(self, station_name):
    #    # filter samples to include only samples listed in the rivers-selection
    #    result = db.dfValues[(db.dfValues[cn.STATION_NAME_COLUMN].isin(station_name))]
    #    # make unqique list of parameters from the filtered table
    #    lst_par = result.PARM.unique()
    #    # filter the parameter table to include only parameters from the filtered sample list
    #    result = db.dfParameters[(db.dfParameters[cn.PAR_NAME_COLUMN].isin(lst_par))]
    #    result = result.PARM_DESCRIPTION
    #
    #    return result.tolist()

    # returns the key for a given parameter description. the lists hold parameter descriptions, so they are easier to understand
    # in the graphs, we need to reference the keys. e.g. Description: CALCIUM and key: CAUT.
    # def get_parameter_key(self, par_label):
    #    query = "Select * from v_parameters where dataset_id = {} and {} = '{}'".format(db.DATASET_ID, cn.PAR_LABEL_COLUMN, par_label)
    #    df = db.execute_query(query)
    #    return  df.at[0, cn.PAR_NAME_COLUMN]

    def render_all_parameters_table(self):
        """
        This function is invoked, if no parameter filter is set. A single table including the metadata of all parameters
        is shown in the view panel
        """

        query = """select parameter_name as Name, formula as Formula, unit as Unit, formula_Weight as FMW, valency as Valency, description
            from envdata.v_parameters where dataset_id = {} order by parameter_name""".format(self.__parent.dataset_id)
        df = db.execute_query(query)
        st.markdown('All parameters ({})'.format(df.shape[0]))
        st.write(df)

    def get_value(self, parameter, field):
        """
        Returns a metadata value from the parameter table for a specified parameter
        in: parameter id
            field name
        out: metadata value for parameter id
        """

        query = """select {} from v_parameters where dataset_id = {} and 
                parameter_name = '{}'""".format(field, self.__parent.dataset_id, parameter)
        df = db.execute_query(query)
        result = df.at[0, field]
        return result

    def render_multi_parameters_table(self, lis_par):
        """This function is invoked, if the parameter filter is set and multiple parameters are selected.
        The following tables are shown:
        * parameters metadata
        * parameter value summary per station
        """

        criteria = ''
        # get list of parameters: if no filter is set: all parameters
        # if parameters_group filter is set but no individual parameters: list froam parameter group
        # if individual parameters are specified: those
        if len(lis_par) == 0 and len(self.__parent.filter.filters_multilist) > 0:
            criteria = self.__parent.filter.get_expression
            criteria = 'and ' + criteria if criteria > '' else ''
        elif len(lis_par) > 0:
            parameters = tools.get_cs_item_list(lis_par, ',', "'")
            criteria = ' and parameter_name in ({})'.format(parameters)
        df = self.get_parameter_table(criteria)
        st.markdown('Parameters ({})'.format(df.shape[0]))
        st.write(df)
        st.markdown(tools.get_table_download_link(df), unsafe_allow_html=True)

    def get_parameter_table(self, criteria):
        """returns a DataFrame holding summary values for samples matching the specified
        in: 
        criteria: where clause of sql statement

        out
        DataFrame with summary information on parameter and station
        """

        if self.__parent.data_type == cn.DataType.chemistry.value:
            query = """select t1.parameter_name, t1.formula, cas_number as CRN, t1.unit, t2.min_value, t2.max_value, t2.average_value, 
                t2.number_of_values, t2.number_of_stations as stations, t2.first_year as 'First year',
                t2.last_year as 'Last year', t2.number_of_years as 'Number of years'
            from 
                envdata.v_parameters t1
                inner join (select parameter_id, min(calc_value) min_value, max(calc_value) max_value, 
                avg(calc_value) average_value, count(*) as number_of_values, 
                count(distinct station_id) as number_of_stations, min(year(sample_date)) as first_year, 
                max(year(sample_date)) as last_year, count(distinct year(sample_date)) as number_of_years
                from 
                envdata.v_observations_complete 
            where dataset_id = {} {} group by parameter_id) t2 on t2.parameter_id = t1.id
            order by t1.parameter_name""".format(self.__parent.dataset_id, criteria)
        else:
            query = """select t1.parameter_name, t1.unit, t2.min_value, t2.max_value, t2.average_value, t2.number_of_values,
                t2.number_of_stations as stations, t2.first_year as 'First year', t2.last_year as 'Last year', t2.number_of_years as 'Number of years'
            from 
                envdata.v_parameters t1
                inner join (select parameter_id, min(calc_value) min_value, max(calc_value) max_value, avg(calc_value) average_value, 
                count(*) as number_of_values, count(distinct station_id) as number_of_stations, min(year(sample_date)) as first_year, 
                max(year(sample_date)) as last_year, count(distinct year(sample_date)) as number_of_years
                from 
                envdata.v_time_series 
            where dataset_id = {} {} group by parameter_id) t2 on t2.parameter_id = t1.id""".format(
                self.__parent.dataset_id, criteria)
        df = db.execute_query(query)
        return df

    def get_parameter_summary_table(self, criteria):
        """returns a DataFrame holding summary values for samples matching the specified
        in: 
        criteria: where clause of sql statement

        out
        DataFrame with summary information on parameter and station
        """

        if self.__parent.data_type == cn.DataType.chemistry.value:
            query = """select t2.station as Station, t2.min_value, t2.max_value, t2.average_value, t2.number_of_values,
                t2.first_year as 'First year', t2.last_year as 'Last year', t2.number_of_years as 'Number of years'
            from 
                envdata.v_parameters t1
                inner join (select parameter_id, station_name as station, min(calc_value) min_value, max(calc_value) max_value, avg(calc_value) average_value, 
                count(*) as number_of_values, min(year(sample_date)) as first_year, 
                max(year(sample_date)) as last_year, count(distinct year(sample_date)) as number_of_years
                from 
                envdata.v_observations
                where dataset_id = {} {} group by parameter_name, station) t2 on t2.parameter_id = t1.id""".format(self.__parent.dataset_id, criteria)
        else:
            query = """select t2.station as Station, t2.min_value, t2.max_value, t2.average_value, t2.number_of_values,
                t2.first_year as 'First year', t2.last_year as 'Last year', t2.number_of_years as 'Number of years'
            from 
                envdata.v_parameters t1
                inner join (select parameter_id, station_name as station, min(calc_value) min_value, max(calc_value) max_value, avg(calc_value) average_value, 
                    count(*) as number_of_values, min(year(sample_date)) as first_year, 
                    max(year(sample_date)) as last_year, count(distinct year(sample_date)) as number_of_years
                    from 
                    envdata.v_time_series
            where dataset_id = {} {} group by parameter_name, station) t2 on t2.parameter_id = t1.id""".format(
                self.__parent.dataset_id, criteria)
        df = db.execute_query(query)
        return df

    def get_map_table(self, parameter: str) -> pd.DataFrame:
        """
        Returns a map plot ready table including: long/lat coordinates and a parameter value
        :param parameter: parmaeter to be plotted
        :return:
        """

        if self.__parent.data_type == cn.DataType.chemistry.value:
            query = """select lat, lon, station_name, t2.value from v_stations t1 inner join (select station_id, 
            avg(calc_value) as value from v_observations where calc_value is not null and 
            parameter_name = '{}' and dataset_id = {} group by station_id) t2 on t2.station_id = t1.id 
            where coalesce(t1.lat, 0) <> 0""".format(parameter, self.__parent.dataset_id)
        else:
            query = """select lat, lon, station_name, t2.value as calc_value from v_time_series_stations t1 
            inner join (select station_id, avg(calc_value) as value from v_time_series where dataset_id = {} group by 
            station_id) t2 on t2.station_id = t1.id where coalesce(t1.lat, 0)  <> 0
            """.format(self.__parent.dataset_id)
        df = db.execute_query(query)
        return df

    def render_single_parameters_table(self, lis: list) -> pd.DataFrame:
        """
        This function is invoked, if the parameter filter is set and multiple parameters are selected.
        The following tables are shown:
        * parameters metadata
        * parameter value summary per station
        * a map
        :param lis:
        :return:
        """
        if len(lis) > 0:
            # transposed info table on parameter
            parameter = lis[0]
            criteria = " and parameter_name = '{}'".format(lis[0])
            df = self.get_parameter_table(criteria)
            df = tools.transpose_dataframe(df)
            st.markdown("### {}".format(parameter))
            st.write(df)
            url = self.get_value(parameter, 'url')
            if url is not None:
                href = '<a href="{}" target = "_blank">More information (source: NIH-TOXNET)</a>'.format(url)
                st.markdown(href, unsafe_allow_html=True)
            # parameter-station values summary table
            df = self.get_parameter_summary_table(criteria)
            st.markdown("### Average {} per station".format(parameter))
            st.dataframe(df)
            st.markdown(tools.get_table_download_link(df), unsafe_allow_html=True)

            # map of locations where values can be found
            df = self.get_map_table(parameter)
            title = 'Map average ({})'.format(parameter)
            # make sure the station as coordinates
            self.parent.plots.plot_map(title=title, df=df, layer_type='ScatterplotLayer', value_col='value')
        else:
            st.info('Please select at least one parameter')

    def render_menu(self):
        """The function renders the sidebar menu for the parameters option menu item"""

        # sidebar menu
        self.__parent.filter.render_menu()

        # df.reset_index(inplace = True) #needed so station_name can be selected on plotly table
        lis = []
        # st.write(self.__parent.filter.station_fields_multilist.keys)
        if 'parameter' in self.__parent.filter.station_fields_multilist:
            lis = self.__parent.filter.station_fields_multilist['parameter'].value
        if len(lis) == 0:
            self.render_multi_parameters_table(lis)
        elif len(lis) == 1:
            df = self.render_single_parameters_table(lis)
        else:
            df = self.render_multi_parameters_table(lis)

        # df = df.set_index(cn.PAR_NAME_COLUMN)
        # df = df[[cn.PAR_NAME_COLUMN, cn.PAR_LABEL_COLUMN, cn.PAR_UNIT_COLUMN]]
        # values = [df[cn.PAR_NAME_COLUMN], df[cn.PAR_LABEL_COLUMN], df[cn.PAR_UNIT_COLUMN]]
        # txt.show_table(df, values)
        # st.write("{} parameters found in stations {}".format(len(df.index), ','.join(ctrl['station_list_multi']) ))


class Plots:
    """This class is used to generate plots and render plot related UI controls"""
    marker_group_by: str

    def __init__(self, parent):
        tools.log('Plots.__init__, start')
        self.__parent = parent
        self.__plot_type = 'bar chart'
        self.plot_groupby = ''
        self.marker_groupby = ''
        self.orientation = 'vertical'
        self.show_data_table = False
        self.plot_width = cn.plot_width
        self.plot_height = cn.plot_height
        self.xpar = 0
        self.ypar = 0
        self.define_axis_limits = False
        self.xax_min = 0
        self.xax_max = 0
        self.yax_min = 0
        self.yax_max = 0
        self.bin_size = 0
        tools.log('Plots.__init__, end')

    @property
    def plot_type(self):
        return self.__plot_type

    @plot_type.setter
    def plot_type(self, pt):
        """
        sets the plot type. For time series plots, the def sets the
        filter checkbox to true, so not all values from all stations are retrieved  
        """

        tools.log('self.plot_type = pt, start')
        self.__plot_type = pt
        tools.log('self.__plot_type = pt, end')

        if self.plot_type == 'time series':
            self.marker_group_by = 'station'
            self.__parent.filter.station_filters = ['station_name']
        tools.log(pt)
        tools.log('self.plot_type = pt, end')

    def render_menu(self):
        def handle_plot_group(_criteria_base):
            par = cn.group_by_display[self.plot_groupby]
            _lis = db.get_distinct_values(par, self.__parent.observations_view,
                                         self.__parent.dataset_id, _criteria_base)
            for _group in _lis:
                _criteria = "{} AND {} = '{}'".format(_criteria_base, par, _group)
                _tit = _group
                self.plot(title=_tit, criteria=_criteria)

        """Renders the plotting menu control on the sideboard and the specified plots on the work screen"""
        tools.log('plots.render_menu')
        self.render_controls()
        criteria_base = self.__parent.filter.get_expression
        criteria_base = self.__parent.filter.append_parameter_filter(criteria_base)
        if self.plot_groupby == 'none':
            criteria = criteria_base
            tit = ''
            self.plot(title=tit, criteria=criteria)
        elif self.plot_groupby == cn.STATION_NAME_COLUMN:
            # if a station filter is set, then loop through these stations otherwise loop through all stations
            if len(self.__parent.filter.station_fields_multilist['station'].value) > 0:
                list_of_stations = self.__parent.filter.station_fields_multilist['station'].value
            else:
                list_of_stations = self.__parent.filter.station_fields_multilist['station'].options

            for group in list_of_stations:
                criteria = criteria_base + " AND {0} = '{1}'".format(cn.STATION_NAME_COLUMN, group)
                tit = group
                self.plot(title=tit, criteria=criteria)

                # todo: move to plot def
                # if (len(plot_results[1]) > 0):
                #    st.write(plot_results[0].properties(width = self.plot_width, height = self.plot_height))
                #    # if a station has been selected display a link to visit site on google maps
                #    if not filter_stations_cb and len(self.__parent.filter.station_multilist) == 1:
                #        stations.dfStations.set_index(cn.STATION_NAME_COLUMN, inplace = True)
                #        lat = stations.dfStations.at[self.ctrl['station'],'lat']
                #        lon = stations.dfStations.at[self.ctrl['station'],'lon']
                #        loc = stations.dfStations.at[self.ctrl['station'],'LOCATION']
                #        lnk = 'Location: {0}. [Visit station on GOOGLE maps](https://www.google.com/maps/search/?api=1&query={1},{2} "open in GOOGLE maps")'.format(loc, lat, lon)
                #        st.markdown(lnk)
                #    if self.__show_data_table:
                #        st.dataframe(plot_results[1])
        else:
            handle_plot_group(criteria_base)

    def get_label(self, par_id):

        label = self.__parent.parameters.dfParameters.at[par_id, cn.PAR_LABEL_COLUMN]
        unit = self.__parent.parameters.dfParameters.at[par_id, cn.PAR_UNIT_COLUMN]
        return "{} ({})".format(label, unit)

    def plot(self, title, criteria):
        """
        Generates the selected plot type.
        Parameters:
        -----------
        :param title: title of plot
        :param criteria: filter limiting the data used to create the plot
        :return: list holding plot object and ...????
        """
        tools.log('plot, start')
        tools.log('df, start')
        df = self.__parent.get_values(criteria=criteria)
        tools.log('df, end')
        tools.log(df.shape[0])
        tools.log(df.shape[0] > 100000)
        data_ok = True

        if df.shape[0] > 500000:
            st.info('Data includes too many rows ({}). Please filter before plotting'.format(df.shape[0]))
            data_ok = False
        elif df.shape[0] > 50000:
            st.spinner(text='Data includes {} rows, this may take a while'.format(df.shape[0]))
            tools.log('{} rows'.df.shape[0])

        if data_ok:
            if self.plot_type == 'scatter plot':
                plot_results = self.plot_scatter(title, df)
            elif self.plot_type == 'time series':
                plot_results = self.plot_time_series(title, df)
            elif self.plot_type == 'histogram':
                plot_results = self.plot_histogram(title, df)
            elif self.plot_type == 'box plot':
                plot_results = self.plot_boxplot(title, df)
            elif self.plot_type == 'schoeller':
                plot_results = self.plot_schoeller(title, df)
            elif self.plot_type == 'bar chart' and self.__direction == 'horizontal':
                plot_results = self.plot_bar_h(title, df)
            elif self.plot_type == 'bar chart' and self.__direction == 'vertical':
                plot_results = self.plot_bar_v(title, df)
            elif self.plot_type == 'map':
                self.plot_map(title, df, layer_type='ScatterplotLayer', value_col='calc_value')
                plot_results = []
            else:
                plot_results = []

            # verify if the result list has items
            if self.plot_type == 'map':
                pass
            elif len(plot_results[1]) > 0:
                st.write(plot_results[0].properties(width=self.plot_width, height=self.plot_height))
                if self.__show_data_table:
                    st.dataframe(plot_results[1])
                    st.markdown(tools.get_table_download_link(plot_results[1]), unsafe_allow_html=True)
            else:
                st.info("Plot '{}' could not be generated: insufficient data".format(title))

    def plot_schoeller(self, title: str, df: pd.DataFrame):
        """ todo: schoeller plot"""
        st.write("#### {}".format(title))
        st.write(df)
        base = alt.Chart(df).transform_window(
            index='count()'
        ).transform_fold(
            ['petalLength', 'petalWidth', 'sepalLength', 'sepalWidth']
        ).mark_line().encode(
            x='key:N',
            y=cn.VALUES_VALUE_COLUMN + ':Q',
            color='species:N',
            detail='index:N',
            opacity=alt.value(0.5)
        )
        return base

    def plot_boxplot(self, title: str, df: pd.DataFrame) -> list:
        result = []
        y_lab = self.get_label(self.ypar)
        x_lab = ''
        if self.__yax_max == self.__yax_min:
            scy = alt.Scale()
        else:
            scy = alt.Scale(domain=(self.__yax_min, self.__yax_max))
        base = alt.Chart(df, title=title).mark_boxplot(clip=True).encode(
            alt.X('{}:O'.format(self.marker_group_by), title=x_lab),  # , axis=alt.Axis(labelAngle=0)
            alt.Y('{}:Q'.format(cn.VALUES_VALUE_COLUMN), title=y_lab, scale=scy)
        )
        result.append(base)
        result.append(df)
        return result

    def plot_histogram(self, title: str, df: pd.DataFrame) -> list:
        result = []
        x_lab = self.get_label(self.ypar)
        # df = df[(df[cn.PAR_NAME_COLUMN] == self.ypar) & (df[cn.VALUES_VALUE_COLUMN] > 0)]

        if self.marker_group_by == 'none':
            df = df[[cn.VALUES_VALUE_COLUMN, cn.STATION_NAME_COLUMN]]
        else:
            df = df[[cn.VALUES_VALUE_COLUMN, self.marker_group_by]]
        # brush = alt.selection(type='interval', encodings=['x'])

        if self.xax_max == self.xax_min:
            scx = alt.Scale()
        else:
            scx = alt.Scale(domain=(self.xax_min, self.xax_max))
        # use bin width if user defined
        if self.bin_size > 0:
            bin_def = alt.Bin(step=self.bin_size)
        else:
            bin_def = alt.Bin(maxbins=100)

        if self.marker_group_by == 'none':
            base = alt.Chart(df, title=title).mark_bar(clip=True
                                                       ).encode(
                alt.X('{}:Q'.format(cn.VALUES_VALUE_COLUMN), bin=bin_def, title=x_lab, scale=scx),
                alt.Y('count()', stack=None),
            )
        else:
            base = alt.Chart(df, title=title).mark_area(
                opacity=cn.OPACITY,
                clip=True,
                interpolate='step'
            ).encode(
                alt.X('{}:Q'.format(cn.VALUES_VALUE_COLUMN), bin=bin_def, title=x_lab, scale=scx),
                alt.Y('count()', stack=None),
                alt.Color('{}:N'.format(self.marker_group_by))
            )
        result.append(base)
        result.append(df)
        return result

    def plot_bar_h(self, title: str, df: pd.DataFrame) -> list:
        result = []
        y_lab = self.get_label(self.ypar)
        # df = df[(df[cn.PAR_NAME_COLUMN] == self.ypar) & (df[cn.VALUES_VALUE_COLUMN] > 0)]
        # brush = alt.selection(type='interval', encodings=['x'])
        if self.__yax_max == self.__yax_min:
            scy = alt.Scale()
        else:
            scy = alt.Scale(domain=[self.__yax_min, self.__yax_max])

        base = alt.Chart(data=df, title=title).mark_bar().encode(
            alt.Y('{}:O'.format(self.marker_group_by), title=''),
            alt.X('mean({0}):Q'.format(cn.VALUES_VALUE_COLUMN), title=y_lab, scale=scy),
        )

        avg = alt.Chart(df).mark_rule(color='red').encode(
            x='mean({0}):Q'.format(cn.VALUES_VALUE_COLUMN)
        )

        result.append(base + avg)
        result.append(df)
        return result

    def plot_bar_v(self, title: str, df: pd.DataFrame) -> list:
        result = []
        y_lab = self.get_label(self.ypar)
        # df = df[(df[cn.PAR_NAME_COLUMN] == self.ypar) & (df[cn.VALUES_VALUE_COLUMN] > 0)]
        # brush = alt.selection(type='interval', encodings=['x'])
        if self.__yax_max == self.__yax_min:
            scy = alt.Scale()
        else:
            scy = alt.Scale(domain=[self.__yax_min, self.__yax_max])

        base = alt.Chart(data=df, title=title).mark_bar().encode(
            alt.X('{}:O'.format(self.marker_group_by), title=''),
            alt.Y('mean({0}):Q'.format(cn.VALUES_VALUE_COLUMN), title=y_lab, scale=scy),
        )

        avg = alt.Chart(df).mark_rule(color='red').encode(
            y='mean({0}):Q'.format(cn.VALUES_VALUE_COLUMN)
        )

        result.append(base + avg)
        result.append(df)
        return result

    def plot_map(self, title: str, df: pd.DataFrame, layer_type: str, value_col: str):
        """
        Generates a map plot

        :param value_col: column holding parameter to be plotted
        :param layer_type: HexagonLayer or ScatterplotLayer
        :param title: title of plot
        :param df: dataframe with data to be plotted
        :return:
        """

        if df.shape[0] > 0:
            midpoint = (np.average(df[cn.LATITUDE_COLUMN]), np.average(df[cn.LONGITUDE_COLUMN]))
            st.markdown("### {}".format(title))

            if value_col:
                min_val: float = df[value_col].min()
                max_val: float = df[value_col].quantile(0.9)
                df["color_r"] = df.apply(lambda row: tools.color_gradient(row, value_col, min_val, max_val, 'r'), axis=1)
                df["color_g"] = df.apply(lambda row: tools.color_gradient(row, value_col, min_val, max_val, 'g'), axis=1)
                df["color_b"] = df.apply(lambda row: tools.color_gradient(row, value_col, min_val, max_val, 'b'), axis=1)
            else:
                df["color_r"] = 255
                df["color_g"] = 0
                df["color_b"] = 0
            if layer_type == 'HexagonLayer':
                layer = pdk.Layer(
                    'HexagonLayer',
                    df,
                    get_position="[lon, lat]",
                    auto_highlight=True,
                    elevation_scale=50,
                    pickable=True,
                    elevation_range=[0, 3000],
                    extruded=True,
                    coverage=1,
                    getFillColor="[color_r, color_g, color_b, color_a]",
                )
            elif layer_type == 'ScatterplotLayer':
                layer = pdk.Layer(
                    'ScatterplotLayer',
                    data=df,
                    pickable=True,
                    get_position="[lon, lat]",
                    get_radius=2000,
                    getFillColor="[color_r, color_g, color_b]",
                )
            view_state = pdk.ViewState(
                longitude=midpoint[1], latitude=midpoint[0], zoom=6, min_zoom=5, max_zoom=15, pitch=0, bearing=-27.36
            )
            r = pdk.Deck(
                map_style=cn.MAPBOX_STYLE,
                layers=[layer],
                initial_view_state=view_state,
                tooltip={
                    "html": "<b>Value:</b> {value} <br/>",
                    "style": {
                        "backgroundColor": "steelblue",
                        "color": "white"}
                }
            )
            st.pydeck_chart(r)
            if value_col:
                self.render_legend(min_val, max_val, cn.MAP_LEGEND_SYMBOL_SIZE)
        else:
            st.warning('Unable to create map: no location data was found')

    def render_legend(self, min_val: float, max_val: float, height: int):
        """
        Renders the map plot blue-green gradient legend showing 2 circles and the corresponding intervals. Eg. values
        go from 100 to 500 in a map. Then values vom 100-349 will be shown in blue shades, 350-500 in green shades.

        :param min_val: minimum value in plot
        :param max_val: maximum value in plot
        :param height: height of circle
        :return: None
        """

        a = round(min_val)
        b = round((max_val - min_val) / 2)
        c = round(max_val)
        legend = """
           <style>
           .bdot {{
           height: {0}px;
           width: {0}px;
           background-color: Blue;
           border-radius: 50%;
           display: inline-block;
           }}
           .gdot {{
           height: {0}px;
           width: {0}px;
           background-color: #4DFF00;
           border-radius: 50%;
           display: inline-block;
           }}
           .rdot {{
           height: {0}px;
           width: {0}px;
           background-color: #FF0000;
           border-radius: 50%;
           display: inline-block;
           }}
           </style>
           <div style="text-align:left">
           <h3>Legend</h3>
           <span class="bdot"></span>  {1} - {2}<br>
           <span class="gdot"></span>  &#62;{2} - {3}<br>
           <span class="rdot"></span>  &#62;{3}
           </div>
           """.format(height, a, b, c)
        st.markdown(legend, unsafe_allow_html=True)

    def plot_time_series(self, title: str, df: pd.DataFrame) -> list:
        """Plots a time series plot. input: title: plot title, df: datafram with the data, ctrl: list of GUI controls"""

        result = []
        x_lab = ''
        y_lab = self.get_label(self.ypar)
        if self.__yax_max == self.__yax_min:
            scy = alt.Scale()
        else:
            scy = alt.Scale(domain=(self.__yax_min, self.__yax_max))

        base = alt.Chart(df, title=title).mark_line(point=self.__parent.has_markers, clip=True).encode(
            x=alt.X('{}:T'.format(cn.SAMPLE_DATE_COLUMN),
                    axis=alt.Axis(title='')),
            y=alt.Y('{}:Q'.format(cn.VALUES_VALUE_COLUMN),
                    scale=scy,
                    axis=alt.Axis(title=y_lab)
                    ),
            color=alt.Color(cn.STATION_NAME_COLUMN,
                            scale=alt.Scale(scheme=cn.color_schema)
                            ),
            tooltip=[cn.STATION_NAME_COLUMN, cn.SAMPLE_DATE_COLUMN, cn.VALUES_VALUE_COLUMN]
        )
        result.append(base)
        result.append(df)
        return result

    def plot_scatter(self, title: str, df: pd.DataFrame) -> list:
        """
        Returns a scatter plot diagram

        :param title: plot title
        :param df: x,y data
        :return: altair scatter plot object
        """

        result = []
        # remove NAN values
        df = tools.get_pivot_data(df, self.marker_group_by)
        df = df.reset_index()
        # verify that both parameter exist as column names
        x_col = self.__parent.parameters.parameters_display[self.xpar]
        y_col = self.__parent.parameters.parameters_display[self.ypar]
        ok = set([x_col, y_col]).issubset(df.columns)
        # filter for NAN values
        if ok:
            df = df[(df[x_col] > 0) & (df[y_col] > 0)]
            ok = len(df) > 0
        if ok:
            df = df.reset_index()
            x_lab = self.get_label(self.xpar)
            y_lab = self.get_label(self.ypar)

            if self.xax_max == self.xax_min:
                scx = alt.Scale()
            else:
                scx = alt.Scale(domain=(self.xax_min, self.xax_max))

            if self.__yax_max == self.__yax_min:
                scy = alt.Scale()
            else:
                scy = alt.Scale(domain=(self.__yax_min, self.__yax_max))

            base = alt.Chart(df, title=title).mark_circle(size=cn.symbol_size, clip=True).encode(
                x=alt.X(x_col + ':Q',
                        scale=scx,
                        axis=alt.Axis(title=x_lab)),
                y=alt.Y(y_col + ':Q',
                        scale=scy,
                        axis=alt.Axis(title=y_lab)),
                color=alt.Color('{}:O'.format(self.marker_group_by),
                                scale=alt.Scale(scheme=cn.color_schema)
                                ),
                tooltip=[cn.STATION_NAME_COLUMN,cn.SAMPLE_DATE_COLUMN, self.marker_group_by, x_col, y_col]
            )
        else:
            empty_df = pd.DataFrame(data={'col1': [1, 2], 'col2': [3, 4]})
            base = alt.Chart(empty_df, title=title).mark_circle(size=cn.symbol_size).encode()
            df = []

        result.append(base)
        result.append(df)
        return result

    def render_controls(self):
        """Renders the stations menu controls.
        :rtype: object
        """

        # def render_time_filter():
        #    """ renders the controls for the time filter to ensure that the user may only filter by 1 time control"""
        #    if not self.__parent.filter.filter_by_season_cb:
        #        self.__parent.filter.filter_by_year_cb = st.sidebar.checkbox('Filter data by year', value=False,
        #                                                                     key=None)
        #    if self.__parent.filter.filter_by_year_cb:
        #        self.__parent.filter.year_slider = st.sidebar.slider('Year', min_value=int(self.__parent.first_year),
        #                                                             max_value=int(self.__parent.last_year),
        #                                                             value=self.__parent.filter.year_slider)

        def render_group_by_controls():
            """Group by controls for plots and markers"""

            tools.log('render_group_by_controls, start')
            st.sidebar.markdown('---')
            st.sidebar.markdown('#### Plot group and marker settings')
            self.plot_groupby = st.sidebar.selectbox('Group plots by', cn.group_by_options,
                                                       format_func=lambda x: cn.group_by_display[x])
            if self.plot_type == 'time series':
                self.marker_group_by = 'station'
            elif self.plot_type == 'map':
                # map markers colors are generated automatically based on the values of the y parameter
                pass
            else:
                self.marker_group_by = st.sidebar.selectbox('Group markers by', cn.group_by_options,
                                                              format_func=lambda x: cn.group_by_display[x], index=2)
            tools.log('render_group_by_controls, end')

        def render_options():
            """Renders plot specific options controls such as pameters or number of bins for histograms."""

            st.sidebar.markdown('---')
            st.sidebar.markdown('#### Plot and axis settings')
            if self.plot_type not in ['time series', 'histogram', 'box plot', 'bar chart', 'map']:
                self.xpar = st.sidebar.selectbox('X-parameter', options=self.__parent.parameters.parameters_options,
                                                   format_func=lambda x: self.__parent.parameters.parameters_display[x])
            self.ypar = st.sidebar.selectbox('Y-parameter',
                                               options=self.__parent.parameters.parameters_options,
                                               format_func=lambda x: self.__parent.parameters.parameters_display[x])

            if self.plot_type == 'histogram':
                self.bin_size = st.sidebar.number_input('Bin width')

            # various plot settings such as axis length, min max on axis etc

            if self.plot_type == 'bar chart':
                self.__direction = st.sidebar.radio('Bars', ['vertical', 'horizontal'])

            if self.plot_type == 'scatter plot':
                self.xax_min = st.sidebar.number_input('Minimum X', value=0.0)
                self.xax_max = st.sidebar.number_input('Maximum X', value=0.0)

            if self.plot_type not in ['map']:
                self.__yax_min = st.sidebar.number_input('Minimum y', value=0.0)
                self.__yax_max = st.sidebar.number_input('Maximum y', value=0.0)

            if self.plot_type not in ['map']:
                self.__define_axis_length = st.sidebar.checkbox('Define axis length', value=False)
                if self.__define_axis_length:
                    self.plot_width = st.sidebar.number_input('Width (pixel)', value=self.plot_width)
                    self.plot_height = st.sidebar.number_input('Height (pixel)', value=self.plot_height)

            self.__show_data_table = st.sidebar.checkbox('Show data table', value=False, key=None)

        self.plot_type = st.sidebar.selectbox('Plot type', cn.plot_type_list, index=0)
        render_group_by_controls()
        render_options()
        self.__parent.filter.render_menu()

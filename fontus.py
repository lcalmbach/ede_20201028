import streamlit as st
import pandas as pd
import config as cn
import tools
import numpy as np
import database as db
import locale
import altair as alt

class Filter:
    ''' This class holds all filter control 
    filter_stations_cb       if set, selected station attributes are shown to build a station filter
    stations_list_selection  a station multi list allowing to select multiple stations
    stations_list_selection
    filter_by_year_cb
    filter_year_slider
    filter_season_list
    x_list_selection            x parameter
    x_list_selection            y parameter
    '''

    def __init__(self, parent):
        self.__parent = parent
        self.filter_stations_cb = True
        self.stations_list_selection = 0
        self.stations_multilist_selection = []
        self.filter_by_year_cb = False
        self.year_slider = []
        self.filter_by_season_cb = False
        self.season_list_selection = 0
        self.filter_parameter_groups_cb = False
        self.parameters_multilist_selection = []

class DataCollection:
    '''
    This class holds data on: 
    - the database connection
    - the available data collection in the database
    - the current data collection
    - the available datasets in the current data collectin
    - the current dataset
    '''
    def __init__(self):
        '''inits the data collection and sets id as the current data collection. if id = 0 then an empty object is created.'''

        db.init()
        locale.setlocale(locale.LC_ALL, '')  # Use '' for auto, or force e.g. to 'en_US.UTF-8'
        self.__menu_selection = 'Info'
        query = 'SELECT * FROM envdata.v_data_collections'
        self.__dfAll_data_collections = db.execute_query(query)
        values = self.__dfAll_data_collections[cn.DATA_COLLECTION_NAME_COLUMN].tolist()
        self.__data_collection_options = self.__dfAll_data_collections['id'].tolist()
        self.__data_collection_display = dict(zip(self.__data_collection_options, values))
        self.__dfAll_data_collections = self.__dfAll_data_collections.set_index('id')
        self.__data_collection_id = 0 #init attribute
        self.__parent_id = cn.DEFAULT_DATA_COLLECTION_ID


    @property
    def menu_selection(self):
        '''menu selection: info, plotting, parameters info, stations info'''

        return self.__menu_selection
    
    @menu_selection.setter
    def menu_selection(self, menuitem):
        '''menu selection: info, plotting, parameters info, stations info'''

        self.__menu_selection = menuitem

    @property
    def filter(self):
        '''object holding all filter settings'''
        return self.__filter

    @property
    def dfAll_data_collections(self):
        '''data frame holding all available data collection in the database'''
        return self.__dfAll_data_collections

    @property
    def data_collection_id(self):
        return self.__data_collection_id

    @data_collection_id.setter
    def data_collection_id(self, id):
        if id != self.__data_collection_id:
            '''sets the attribute data_collection_id and retrieves a dataframe of all datasets belonging to the current datacollection'''
            self.__data_collection_id = id
            query = "SELECT * FROM envdata.v_datasets where data_collection_id = {} order by {}".format(id, cn.DATASET_NAME_COLUMN)
            self.__dfDatasets = db.execute_query(query)
            values = self.__dfDatasets[cn.DATASET_NAME_COLUMN].tolist()
            self.__dataset_options = self.__dfDatasets['id'].tolist()
            self.__dataset_display = dict(zip(self.dataset_options, values))
            self.__google_maps_url = ''
            
            # set the new dataset_id
            query = "SELECT min(id) as id FROM envdata.v_datasets where data_collection_id = {}".format(id)
            df = db.execute_query(query)
            self.dataset_id = df.at[0,'id']

    @property 
    def observations_view(self):
        return self.__observations_view

    @property 
    def dataset_id(self):
        return self.__dataset_id
    
    @property 
    def google_maps_url(self):
        return self.__google_maps_url
    
    def has_google_maps_url(self):
        return self.__google_maps_url is None


    @dataset_id.setter
    def dataset_id(self, id):
        '''sets the dataset_id and retrieves a dataframe of all datasets belonging to the current data collection'''
        if id > 0:
            self.__dataset_id = id
            query = 'SELECT * FROM envdata.v_datasets where id = {}'.format(id)
            self.__dfCurr_dataset = db.execute_query(query)
            self.__dfCurr_dataset = self.__dfCurr_dataset.set_index('id')
            self.__observations_view = self.__dfCurr_dataset.at[id, 'result_view']
            self.__first_year = int(self.__dfCurr_dataset.at[id, 'first_year'])
            self.__last_year = int(self.__dfCurr_dataset.at[id, 'last_year'])
            self.__google_maps_url = self.__dfCurr_dataset.at[id, 'google_maps_url']
            self.__has_markers = self.__dfCurr_dataset.at[id, 'has_markers']

            self.__parameters = Parameters(self)
            self.__stations = Stations(self)
            self.__filter = Filter(self)
            self.__filter.year_slider = [self.__first_year, self.__last_year]
    
    @property
    def first_year(self):
        '''Year of first sample collection'''
        return self.__first_year
    
    @property
    def has_markers(self):
        '''If True data points in plots will be shown as circles'''
        return bool(self.__has_markers == 1)
    
    @property
    def last_year(self):
        '''Year of most recent sample collection'''
        return self.__last_year

    @property
    def dfCurr_data_collection(self):
        '''Dataframe holding current data collection record'''

        return self.__dfCurr_data_collection


    @property
    def data_collection_options(self):
        '''List of ids from data_collection table. the list is used to fill the data collection selection control'''

        return self.__data_collection_options


    @property
    def data_collection_display(self):
        return self.__data_collection_display

    @property
    def dataset_options(self):
        '''List of ids from dataset table. the list is used to fill the dataset selection control'''
        return self.__dataset_options
    
    @property
    def dataset_display(self):
        '''dictionary of dataset id:name pairs for current data collection'''
        return self.__dataset_display

    @property
    def stations(self):
        '''Stations object associated with current data collection'''
        return self.__stations
    
    @property
    def parameters(self):
        '''Parameters object associated with current data collection'''
        return self.__parameters
    
    def show_url_list(self):
        '''In table refererence url references realted to each data collection can be defined and rendered with this function'''

        query = "select html_reference from envdata.v_references where object_type_id = 1 and object_id = {}".format(self.__parent_id)
        refs = db.execute_query(query)['html_reference'].tolist()
        for ref in refs:
            st.markdown('    * {}'.format(ref), unsafe_allow_html=True)

    def read_values(self, criteria):
        ''' Returns a data frame with all values matching the criteria'''

        query = "Select * from {} where {}".format(self.observations_view, criteria)
        result = db.execute_query(query)
        return result

    def render_about_text(self):
        ''' Renders info on the selected data collection composed of: a header image, some explenatory text, a metadatatable for the 
        data collection and metadata for each dataset included in the data collection
        '''

        id = self.__data_collection_id
        df = self.dfAll_data_collections
        st.image('static/images/' + df.at[id, 'about_image'])
        st.write(df.at[id, 'name_long'])
        text = df.at[id, 'about_text']
        st.markdown(text)
        # metadata for 
        st.markdown('### Metadata from data owner:')
        st.markdown('* Publisher: {0}'.format(df.at[id, 'publisher']))
        st.markdown('* Update frequency: {0}'.format(df.at[id, 'update_frequency']))
        st.markdown('* Geographical coverage: {0}'.format(df.at[id, 'geographical_coverage']))
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
            st.markdown('* *Time interval covered*: {} - {}'.format(df.at[dataset, 'first_year'], df.at[dataset, 'last_year']))

class Stations:
    '''Holds all information on the stations related to the current dataset'''

    def __init__(self, parent):
        self.__parent = parent
        query = "SELECT * FROM envdata.v_stations where dataset_id = {0} order by {1};".format(self.__parent.dataset_id, cn.STATION_NAME_COLUMN)
        df = db.execute_query(query)
        values = df[cn.STATION_NAME_COLUMN].tolist()
        self.__stations_options = df['id'].tolist()
        self.__stations_display = dict(zip(self.__stations_options, values))
        self.__dfStations = df.set_index('id')

    @property
    def dfStations(self):
        return self.__dfStations

    @property
    def stations_options(self):
        return self.__stations_options

    @property
    def stations_display(self):
        return self.__stations_display

    def get_table(self):
        if not self.__parent.filter.filter_stations_cb:
            query = 'select * from envdata.v_stations_ds{}_display'.format(self.__parent.dataset_id)
            result = db.execute_query(query)
            return result
        else: 
            result = pd.DataFrame({"Field":[], "Value":[]}) 
            query = "SELECT * FROM envdata.v_stations where id = {0}".format(self.__parent.filter.stations_list_selection)
            df = db.execute_query(query)
            # todo: make this a tools function
            for key, value in df.iteritems():
                df2 = pd.DataFrame({"Field": [key], "Value": [df.iloc[-1][key]]}) 
                result = result.append(df2)
            return result.set_index('Field')

    def get_samples(self, criteria):
        ''' Returns a dataframe of samples as a dataframe where column 0 is the field name and column 1 is its value'''
        
        query = "SELECT * FROM envdata.v_samples_all where {} order by {}".format(criteria, cn.SAMPLE_DATE_COLUMN)
        result = db.execute_query(query)
        return result

    def render_menu(self):
        '''renders the station info menu controls'''

        #sidebar menu
        self.__parent.filter.filter_stations_cb = st.sidebar.checkbox('Filter stations', value = self.__parent.filter.filter_stations_cb, key = None)
        if self.__parent.filter.filter_stations_cb:
            self.__parent.filter.stations_list_selection = st.sidebar.selectbox(label = cn.STATION_WIDGET_NAME, options = self.stations_options, format_func=lambda x: self.stations_display[x]) 
        # content either html table of dataframe
        df = self.get_table()
        #df.reset_index(inplace = True) #needed so station_name can be selected on plotly table
        if self.__parent.filter.filter_stations_cb:
            st.write(df)
            criteria = "{0} = {1} and {2} = {3}".format('station_id', self.__parent.filter.stations_list_selection, 'dataset_id', self.__parent.dataset_id)
            #show samples belonging to sample
            df = self.get_samples(criteria)
            df = df.set_index('id')
            station_name = self.stations_display[self.__parent.filter.stations_list_selection]
            number_of_samples = len(df)
            text = '##### {0} has {1} samples'.format(station_name, number_of_samples)
            st.markdown(text)
            st.write(df)
            #st.write(df.set_index('Field', inplace=True))
        else:  
            st.write(df)
            #column_values = [df[cn.STATION_NAME_COLUMN], df.aquifer_lithology, df.stratigraphy, df.well_depth, df.screen_hole, df.min_sample_year, df.max_sample_year, df.number_of_samples]
            #tools.show_table(df, column_values)
        
        if self.__parent.has_google_maps_url():
            text = r'[View all wells on my google maps]({})'.format(self.__parent.google_maps_url)
            st.markdown(text)

class Parameters:
    def __init__(self, parent):
        self.__parent = parent
        query =  "select id, {0}, {1}, {2} from envdata.parameter where dataset_id = {3} order by {0}".format(cn.PAR_NAME_COLUMN, cn.PAR_LABEL_COLUMN, cn.PAR_UNIT_COLUMN, self.__parent.dataset_id )
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

    def get_table(self):
        if not self.__parent.filter.filter_stations_cb:
            query = 'select t1.parameter_name, t1.formula, t1.unit, t2.min_value, t2.max_value, t2.average_value, t2.number_of_values from envdata.v_parameters'.format(self.__parent.dataset_id)
            result = db.execute_query(query)
        else:
            stations = tools.get_cs_item_list(lst = self.__parent.filter.stations_multilist_selection, separator = ',', quote_string = '')
            query = '''select t1.parameter_name, t1.formula, t1.unit, t2.min_value, t2.max_value, t2.average_value, t2.number_of_values from 
                        envdata.v_parameters t1
                        inner join (select parameter_id, min(calc_value) min_value, max(calc_value) max_value, avg(calc_value) average_value, count(*) as number_of_values from 
                        envdata.v_observations where dataset_id = {} and station_id in ({}) group by parameter_id) t2 on t2.parameter_id = t1.id'''.format(self.__parent.dataset_id, stations)
            result = db.execute_query(query)
        return result

    #def get_sample_parameters(self, station_name):
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
    #def get_parameter_key(self, par_label):
    #    query = "Select * from v_parameters where dataset_id = {} and {} = '{}'".format(db.DATASET_ID, cn.PAR_LABEL_COLUMN, par_label)
    #    df = db.execute_query(query)
    #    return  df.at[0, cn.PAR_NAME_COLUMN]

    def render_menu(self):
        #sidebar menu
        self.__parent.filter.filter_stations_cb = st.sidebar.checkbox('Filter stations', 
            value = self.__parent.filter.filter_stations_cb, key  =None)
        if self.__parent.filter.filter_stations_cb:
            self.__parent.filter.stations_multilist_selection = st.sidebar.multiselect(label = cn.STATION_WIDGET_NAME, 
                default = self.__parent.stations.stations_options[0], options = self.__parent.stations.stations_options, 
                format_func=lambda x: self.__parent.stations.stations_display[x])
        df = self.get_table()
        st.write(df)
        #df = df.set_index(cn.PAR_NAME_COLUMN)
        #df = df[[cn.PAR_NAME_COLUMN, cn.PAR_LABEL_COLUMN, cn.PAR_UNIT_COLUMN]]
        #values = [df[cn.PAR_NAME_COLUMN], df[cn.PAR_LABEL_COLUMN], df[cn.PAR_UNIT_COLUMN]]
        #txt.show_table(df, values)
        #st.write("{} parameters found in stations {}".format(len(df.index), ','.join(ctrl['station_list_multi']) ))
        if not self.__parent.filter.filter_stations_cb:
            text = "This parameter list only includes parameters with at least one occurrence in one of the selected well."
        else:
            text = "This parameter list includes all parameters having been measured in the monitoring network."
        st.markdown(text)

class Charting:
    '''This class is used to generate plots'''

    def __init__(self, parent):
        self.__parent = parent
        self.__plot_groupby = ''
        self.__marker_groupby = ''
        self.__plot_type = 'bar chart'
        self.__orientation = 'vertical'
        self.__show_data_table = False
        self.__plot_width = cn.plot_width
        self.__plot_height = cn.plot_height
        self.__xpar = 0
        self.__ypar = 0
        self.__define_axis_limits = False
        self.__xax_min = 0
        self.__xax_max = 0
        self.__yax_min = 0
        self.__yax_max = 0
        self.__bin_size = 0


    def render_menu(self):
        self.render_controls()
        criteria_base = self.get_criteria_expression()
        if self.plot_groupby == 'none':
            crit = criteria_base
            tit = ''
            self.plot(title = tit, criteria = crit)
            
        elif self.__plot_groupby == 'year':
            year_list = db.get_distinct_values(cn.YEAR_COLUMN, self.__parent.observations_view, self.__parent.dataset_id)
            for group in year_list:
                crit = criteria_base + " AND {0} = '{1}'".format(cn.YEAR_COLUMN, group)
                tit = str(group)
                self.plot(title = tit, criteria = crit)

        elif self.plot_groupby == 'season':
            for group in cn.season_list:
                crit = criteria_base + " AND {0} = '{1}'".format(cn.SEASON_COLUMN, group)
                tit = group
                self.plot(title = tit, criteria = crit)

        elif self.plot_groupby == 'aquifer_type':
            for group in db.get_distinct_values(cn.AQUIFER_TYPE_COLUMN, self.__parent.observations_view, self.__parent.dataset_id):
                crit = criteria_base + " AND {0} = '{1}'".format(cn.AQUIFER_TYPE_COLUMN, group)
                tit = group
                self.plot(title = tit, criteria = crit)

        elif self.plot_groupby == cn.STATION_NAME_COLUMN:
            # if a station filter is set, then loop through these stations otherwise loop through all stations
            if not self.__parent.filter.filter_stations_cb:
                list_of_stations = stations.all_stations_list
            else:
                list_of_stations = self.__parent.filter.stations_multilist_selection

            for group in list_of_stations:
                crit = criteria_base + " AND {0} = {1}".format('station_id', group)
                tit = self.__parent.stations.dfStations.at[group, cn.STATION_NAME_COLUMN]
                self.plot(title = tit, criteria = crit)
                # todo: move to plot def
                #if (len(plot_results[1]) > 0):
                #    st.write(plot_results[0].properties(width = self.__plot_width, height = self.__plot_height))
                #    # if a station has been selected display a link to visit site on google maps
                #    if not filter_stations_cb and len(self.__parent.filter.stations_multilist_selection) == 1:
                #        stations.dfStations.set_index(cn.STATION_NAME_COLUMN, inplace = True)
                #        lat = stations.dfStations.at[self.ctrl['station'],'lat']
                ##        lon = stations.dfStations.at[self.ctrl['station'],'lon']
                #        loc = stations.dfStations.at[self.ctrl['station'],'LOCATION']
                #        lnk = 'Location: {0}. [Visit station on GOOGLE maps](https://www.google.com/maps/search/?api=1&query={1},{2} "open in GOOGLE maps")'.format(loc, lat, lon)
                #        st.markdown(lnk)
                #    if self.__show_data_table:
                #        st.dataframe(plot_results[1])
        else: #map plot
            crit = criteria_base
            tit = 'Map'
            self.plot(title = tit, criteria = crit)
            df = self.__parent.stations.dfStations
            if len(self.__parent.filter.stations_multilist_selection) == 1:
                pass
            elif len(self.__parent.filter.stations_multilist_selection) > 1:
                df = stations.dfStations[(df['id'].isin(self.__parent.filter.stations_multilist_selection))]
                df = df[(df['id'] == self.ctrl['station'])]
            
            if df.shape[0] > 0:
                self.plot_map(df)
                st.write('if map appears empty, use mouse wheel to zoom out, until markers appear.')
            else:
                st.write('Insufficient data')
    
    # returns the label for a given parameter key. 
    def get_label(self, par_id):
        label = self.__parent.parameters.dfParameters.at[par_id, cn.PAR_LABEL_COLUMN]
        unit = self.__parent.parameters.dfParameters.at[par_id, cn.PAR_UNIT_COLUMN]
        return "{} ({})".format(label, unit)

    def plot(self, title, criteria):
        df = self.__parent.read_values(criteria = criteria)

        if (self.__plot_type  == 'scatter plot'):
            plot_results = self.plot_scatter(title, df)
        elif (self.__plot_type == 'time series'):
             plot_results = self.plot_time_series(title, df)
        elif (self.__plot_type == 'histogram'):
             plot_results = self.plot_histogram(title, df)
        elif (self.__plot_type == 'box plot'):
             plot_results = self.plot_boxplot(title, df)
        elif (self.__plot_type == 'schoeller'):
             plot_results = self.plot_schoeller(title, df)
        elif (self.__plot_type == 'bar chart' and self.__direction == 'horizontal'):
             plot_results = self.plot_bar_h(title, df)
        elif (self.__plot_type == 'bar chart' and self.__direction == 'vertical'):
             plot_results = self.plot_bar_v(title, df)
        elif (self.__plot_type == 'map'):
            plot_map(title, df, ctrl)
            plot_results = []
        else:
            plot_results = []
        
        # verify if the result list has items
        if (len(plot_results[1]) > 0):
            st.write(plot_results[0].properties(width = self.__plot_width, height = self.__plot_height))
            if self.__show_data_table:
                st.dataframe(plot_results[1])
        else:
            st.write('Insufficient data')

    def plot_schoeller(self, title, df):
        ''' todo: schoeller plot'''

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

    def plot_boxplot(self, title, df):
        result = []
        y_lab = self.get_label(self.__ypar)
        x_lab = ''
        if self.__yax_max == self.__yax_min:
            scy = alt.Scale()
        else:
            scy = alt.Scale(domain=(self.__yax_min, self.__yax_max))
        base = alt.Chart(df, title = title).mark_boxplot(clip=True).encode(
                alt.X('{}:O'.format(self.__marker_group_by), title = x_lab),  #, axis=alt.Axis(labelAngle=0)
                alt.Y('{}:Q'.format(cn.VALUES_VALUE_COLUMN), title = y_lab, scale = scy)
                )
        result.append(base)
        result.append(df)
        return result

    def plot_histogram(self, title, df):
        result = []
        x_lab =self.get_label(self.__ypar)
        #df = df[(df[cn.PAR_NAME_COLUMN] == self.__ypar) & (df[cn.VALUES_VALUE_COLUMN] > 0)]

        if self.__marker_group_by == 'none':
            df = df[[cn.VALUES_VALUE_COLUMN, cn.STATION_NAME_COLUMN]]
        else:
            df = df[[cn.VALUES_VALUE_COLUMN, self.__marker_group_by]]
        brush = alt.selection(type='interval', encodings=['x'])

        if self.__xax_max == self.__xax_min:
            scx = alt.Scale()
        else:
            scx = alt.Scale(domain=(self.__xax_min, self.__xax_max))
        #use bin width if user defined
        if self.__bin_size > 0:
            bin_def = alt.Bin(step = self.__bin_size)
        else:
            bin_def = alt.Bin()

        if self.__marker_group_by == 'none':
            base = alt.Chart(df, title = title).mark_bar(clip = True).encode(
                alt.X('{}:Q'.format(cn.VALUES_VALUE_COLUMN), bin = bin_def, title = x_lab, scale = scx),
                alt.Y('count()', stack = None),
            )
        else:
            base = alt.Chart(df, title = title).mark_bar(opacity = cn.OPACITY,clip = True).encode(
                alt.X('{}:Q'.format(cn.VALUES_VALUE_COLUMN), bin = bin_def, title = x_lab, scale = scx),
                alt.Y('count()', stack = None),
                alt.Color(self.__marker_group_by)
            )
        result.append(base)
        result.append(df)
        return result

    def plot_bar_h(self, title, df):
        result = []
        y_lab = self.get_label(self.__ypar)
        #df = df[(df[cn.PAR_NAME_COLUMN] == self.__ypar) & (df[cn.VALUES_VALUE_COLUMN] > 0)]
        #brush = alt.selection(type='interval', encodings=['x'])
        if (self.__yax_max == self.__yax_min):
            scy = alt.Scale()
        else:
            scy = alt.Scale(domain = [self.__yax_min, self.__yax_max])

        base = alt.Chart(data = df, title = title).mark_bar().encode(
            alt.Y('{}:O'.format(self.__marker_group_by), title = ''),
            alt.X('mean({0}):Q'.format(cn.VALUES_VALUE_COLUMN), title = y_lab, scale = scy),
        )

        avg = alt.Chart(df).mark_rule(color='red').encode(
            x='mean({0}):Q'.format(cn.VALUES_VALUE_COLUMN)
        )
        
        result.append(base + avg)
        result.append(df)
        return result

    def plot_bar_v(self, title, df):
        result = []
        y_lab = self.get_label(self.__ypar)
        #df = df[(df[cn.PAR_NAME_COLUMN] == self.__ypar) & (df[cn.VALUES_VALUE_COLUMN] > 0)]
        #brush = alt.selection(type='interval', encodings=['x'])
        if (self.__yax_max == self.__yax_min):
            scy = alt.Scale()
        else:
            scy = alt.Scale(domain= [self.__yax_min, self.__yax_max])
        
        base = alt.Chart(data = df, title = title).mark_bar().encode(
            alt.X('{}:O'.format(self.__marker_group_by), title = ''),
            alt.Y('mean({0}):Q'.format(cn.VALUES_VALUE_COLUMN), title = y_lab, scale = scy),
        )

        avg = alt.Chart(df).mark_rule(color='red').encode(
            y = 'mean({0}):Q'.format(cn.VALUES_VALUE_COLUMN)
        )
        
        result.append(base + avg)
        result.append(df)
        return result

    def plot_map(self, df): 
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

    def plot_time_series(self, title, df):
        '''Plots a time series plot. input: title: plot title, df: datafram with the data, ctrl: list of GUI controls'''

        result = []
        x_lab = ''
        y_lab = self.get_label(self.__ypar)
        if self.__yax_max == self.__yax_min:
            scy = alt.Scale()
        else:
            scy = alt.Scale(domain=(self.__yax_min, self.__yax_max))
        
        base = alt.Chart(df, title = title).mark_line(point = self.__parent.has_markers, clip = True).encode(
            x = alt.X('{}:T'.format(cn.SAMPLE_DATE_COLUMN),
                axis = alt.Axis(title = '')),
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

    def plot_scatter(self, title, df):
        ok = False
        result = []

        # remove value < 0
        df = df.reset_index()
        df = df[(df[cn.PAR_NAME_COLUMN].isin([self.__xpar, self.__ypar]))]
        df = get_pivot_data(df, self.__marker_group_by)
        ok = (set([self.__xpar, self.__ypar]).issubset(df.columns))

        #filter for NAN values
        if ok:
            df = df[(df[self.__xpar] > 0) & (df[self.__ypar] > 0)]
            ok = len(df) > 0
        if ok:
            df = df.reset_index()
            x_lab =self.get_label(self.__xpar)
            y_lab =self.get_label(self.__ypar)

            if (self.__xax_max == self.__xax_min):
                scx = alt.Scale()
            else:
                scx = alt.Scale(domain=(self.__xax_min, self.__xax_max))
            
            if self.__yax_max == self.__yax_min:
                scy = alt.Scale()
            else:
                scy = alt.Scale(domain=(self.__yax_min, self.__yax_max))

            base = alt.Chart(df, title = title).mark_circle(size = cn.symbol_size, clip = True).encode(
                x = alt.X(self.__xpar + ':Q',
                    scale = scx,
                    axis = alt.Axis(title = x_lab)),
                y = alt.Y(self.__ypar + ':Q',
                    scale = scy,
                    axis = alt.Axis(title = y_lab)),
                    color = alt.Color('{}:O'.format(self.__marker_group_by),
                        scale=alt.Scale(scheme = cn.color_schema)
                    ),
                tooltip=[cn.SAMPLE_DATE_COLUMN, self.__marker_group_by, self.__xpar, self.__ypar]
            )
        else:
            dfEmpty = pd.DataFrame(data={'col1': [1, 2], 'col2': [3, 4]})
            base = alt.Chart(dfEmpty, title = title).mark_circle(size = cn.symbol_size).encode()
            df = []
            
        result.append(base)
        result.append(df)
        return result

    def render_controls(self):
        def render_time_filter():
            ''' renders the controls for the time filter to ensure that the user may only filter by 1 time control'''
            if not self.__parent.filter.filter_by_season_cb:
                self.__parent.filter.filter_by_year_cb = st.sidebar.checkbox('Filter data by year', value=False, key=None)
            if self.__parent.filter.filter_by_year_cb:
                self.__parent.filter.year_slider = st.sidebar.slider('Year', min_value = int(self.__parent.first_year), max_value = int(self.__parent.last_year), value = self.__parent.filter.year_slider)

            if not self.__parent.filter.filter_by_year_cb:
                self.__parent.filter.filter_by_season_cb = st.sidebar.checkbox('Filter data by season', value=False, key=None)
            if self.__parent.filter.filter_by_season_cb:
                self.__parent.filter.season_list_selection = st.sidebar.selectbox('Season', options = cn.season_list)

        self.__plot_type = st.sidebar.selectbox('Plot type', cn.plot_type_list, index = 0)

        self.plot_groupby = st.sidebar.selectbox('Group plots by', cn.group_by_options, format_func=lambda x: cn.group_by_display[x])
        if self.__plot_type == 'time series':
            self.__marker_group_by = 'station'
        else:
            self.__marker_group_by = st.sidebar.selectbox('Group markers by', cn.group_by_options, format_func=lambda x: cn.group_by_display[x], index = 2)

        if self.__plot_type not in ['time series', 'histogram', 'box plot', 'bar chart', 'map']:
            self.__xpar = st.sidebar.selectbox('X-parameter', options= self.__parent.parameters.parameters_options, format_func = lambda x: self.__parent.parameters.parameters_display[x])
        if self.__plot_type not in ['map']:
            self.__ypar = st.sidebar.selectbox('Y-parameter',
                options= self.__parent.parameters.parameters_options,
                format_func = lambda x: self.__parent.parameters.parameters_display[x])
        
        st.sidebar.markdown('---')
        st.sidebar.markdown('#### Filter')
        # filter for stations
        if self.__plot_type == 'time series':
            self.__parent.filter.filter_stations_cb = True
        else:
            self.__parent.filter.filter_stations_cb = st.sidebar.checkbox('Filter data by station', value=False, key = None)
        
        if self.__parent.filter.filter_stations_cb:
            self.__parent.filter.stations_multilist_selection = st.sidebar.multiselect(label = cn.STATION_WIDGET_NAME,
                default = self.__parent.stations.stations_options[0],
                options = self.__parent.stations.stations_options, 
                format_func=lambda x: self.__parent.stations.stations_display[x])
        
        #filter for month or year, this is hidden for plot type time series
        if self.__plot_type not in ['time series']:
            render_time_filter()
        
        if self.__plot_type == 'histogram':
            self.__bin_size = st.sidebar.number_input('Bin width')

        # various plot settings such as axis length, min max on axis etc
        st.sidebar.markdown('---')
        st.sidebar.markdown('#### Plot settings')
        self.__define_axis_limits = st.sidebar.checkbox('Define axis limits', value=False, key=None)
        if self.__define_axis_limits:
            if self.__plot_type not in ['time series']:
                self.__xax_min = st.sidebar.number_input('Minimum X', value= 0.0)
                self.__xax_max = st.sidebar.number_input('Maximum X', value= 0.0)
            self.__yax_min = st.sidebar.number_input('Minimum y', value= 0.0)
            self.__yax_max = st.sidebar.number_input('Maximum y', value= 0.0)
        if self.__plot_type == 'bar chart':
            self.__direction = st.sidebar.radio('Bars', ['vertical', 'horizontal'])

        self.__define_axis_length = st.sidebar.checkbox('Define axis length', value=False)
        if self.__define_axis_length:
            self.__plot_width = st.sidebar.number_input('Width (pixel)', value = self.__plot_width)
            self.__plot_height = st.sidebar.number_input('Height (pixel)', value = self.__plot_height)
        
        self.__show_data_table = st.sidebar.checkbox('Show detail data', value = False, key = None)
    
    def get_criteria_expression(self):
        '''creates the sql where clause for the set filter controls'''

        result = 'dataset_id = {}'.format(self.__parent.dataset_id)

        if self.__parent.filter.filter_stations_cb:
            selected_stations_list = tools.get_cs_item_list(self.__parent.filter.stations_multilist_selection,separator=',', quote_string = '')
            result += " AND {0} in ({1})".format('station_id', selected_stations_list)
        
        if self.__parent.filter.filter_by_season_cb:
            result += " AND {0} = '{1}'".format(cn.SEASON_COLUMN, self.__parent.filter.season_list_selection)
        
        if self.__parent.filter.filter_by_year_cb:
            if self.__parent.filter.year_slider[0] == self.__parent.filter.year_slider[1]:
                result += " AND {0} = {1}".format(cn.YEAR_COLUMN, self.__parent.filter.year_slider[0])
            else:
                result += " AND ({0} >= {1} AND {0} <= {2})".format(cn.YEAR_COLUMN, self.__parent.filter.year_slider[0], self.__parent.filter.year_slider[1])
        
        if self.__plot_type == 'scatter plot':
            par_list = get_quoted_items_list([self.__xpar, self.__ypar])
            result += " AND {} in ({})".format(cn.PAR_NAME_COLUMN, par_list)
        else:
            result += " AND {} = {}".format('parameter_id', self.__ypar)
        
        return result

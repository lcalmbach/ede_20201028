import streamlit as st
import pandas as pd
import config as cn
import tools
import numpy as np
import database as db
import locale
import altair as alt

class DataCollection:
    '''
    this class holds data on: 
    - the database connection
    - the available data collection in the database
    - the current data collection
    - the available datasets in the current data collectin
    - the current dataset
    '''
    def __init__(self, id):
        '''inits the data collection and sets id as the current data collection. if id = 0 then an empty object is created.'''
        locale.setlocale(locale.LC_ALL, '')  # Use '' for auto, or force e.g. to 'en_US.UTF-8'
        if id > 0:
            self.data_collection_id = id
            values = self.__dfAll_data_collections[cn.DATA_COLLECTION_NAME_COLUMN].tolist()
            self.__data_collection_options = self.__dfAll_data_collections['id'].tolist()
            self.__data_collection_display = dict(zip(self.data_collection_options, values))
            self.__dfAll_data_collections = self.__dfAll_data_collections.set_index('id')
        else:
            pass

    @property
    def dfAll_data_collections(self):
        '''data frame holding all available data collection in the database'''
        return self.__dfAll_data_collections

    @property
    def data_collection_id(self):
        return self.__data_collection_id

    @data_collection_id.setter
    def data_collection_id(self, id):
        '''sets the datacollection_id and retrieves a dataframe of all datasets belonging to the current datacollection'''

        self.__data_collection_id = id
        query = 'SELECT * FROM envdata.v_data_collections'
        self.__dfAll_data_collections = db.execute_query(query)
        
        query = "SELECT * FROM envdata.v_datasets where data_collection_id = {} order by {}".format(id, cn.DATASET_NAME_COLUMN)
        self.__dfDatasets = db.execute_query(query)
        values = self.__dfDatasets[cn.DATASET_NAME_COLUMN].tolist()
        self.__dataset_options = self.__dfDatasets['id'].tolist()
        self.__dataset_display = dict(zip(self.dataset_options, values))

    @property 
    def observations_view(self):
        return self.__observations_view

    @property 
    def dataset_id(self):
        return self.__dataset_id

    @dataset_id.setter
    def dataset_id(self, id):
        '''sets the dataset_id and retrieves a dataframe of all datasets belonging to the current datacollection'''
        if id > 0:
            self.__dataset_id = id
            query = 'SELECT * FROM envdata.v_datasets where id = {}'.format(id)
            self.__dfCurr_dataset = db.execute_query(query)
            self.__dfCurr_dataset = self.__dfCurr_dataset.set_index('id')
            self.__observations_view = self.__dfCurr_dataset.at[id, 'result_view']
            
            self.__parameters = Parameters(id)
            self.__stations = Stations(id)
        else:
            pass
        
    @property
    def dfCurr_data_collection(self):
        ''' dataframe holding current data collection record'''
        return self.__dfCurr_data_collection

    @property
    def data_collection_options(self):
        return self.__data_collection_options
    
    @property
    def data_collection_display(self):
        return self.__data_collection_display

    @property
    def dataset_options(self):
        '''list of dataset ids for current data collection'''
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
        query = "select html_reference from envdata.v_references where object_type_id = 1 and object_id = {}".format(self.data_collection_id)
        refs = db.execute_query(query)['html_reference'].tolist()
        for ref in refs:
            st.markdown('    * {}'.format(ref), unsafe_allow_html=True)

    def read_values(self, criteria):
        ''' Returns a data frame with all values matching the criteria'''
        query = "Select * from {} where {}".format(cn.VALUES_ALL_VIEW, criteria)
        result = db.execute_query(query)
        #result[cn.SAMPLE_DATE_COLUMN] = pd.to_datetime(result[cn.SAMPLE_DATE_COLUMN])
        return result

    def render_about_text(self):
        ''' shows info on the selected datacollection composed of: a header image, some explenatory text, a metadatatable for the data collection and metadata for each dataset included in the data collection'''

        id = self.data_collection_id
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
    def __init__(self, dataset_id):
        query = "SELECT id, {0} FROM envdata.station where dataset_id = {1} order by {0};".format(cn.STATION_NAME_COLUMN, dataset_id)
        df = db.execute_query(query)
        values = df[cn.STATION_NAME_COLUMN].tolist()
        self.__stations_options = df['id'].tolist()
        self.__stations_display = dict(zip(self.__stations_options, values))
        self.__dataset_id = dataset_id

    @property
    def stations_options(self):
        return self.__stations_options

    @property
    def dataset_id(self):
        return self.__dataset_id

    @property
    def stations_display(self):
        return self.__stations_display

    def get_table(self, use_all_stations, sel_station_list):
        global dfStations

        if use_all_stations:
            query = "SELECT * FROM envdata.v_stations_all where dataset_id = {0}".format(db.DATASET_ID)
            result = db.execute_query(query)
        else:
            result = pd.DataFrame({"Field":[], "Value":[]}) 
            query = "SELECT * FROM envdata.v_stations_all where id = {0}".format(sel_station_list)
            df = db.execute_query(query)
            for key, value in df.iteritems():
                df2 = pd.DataFrame({"Field": [key], "Value": [df.iloc[-1][key]]}) 
                result = result.append(df2)
        return result.set_index('Field')

    def get_station_code_list(self, field_name):
        '''retrieves the list of quifer type codes used in the current dataset 
        out: list
        '''
        query = "SELECT {0} FROM envdata.v_stations_all where dataset_id = {1} group by {0} order by {0}".format(field_name, db.DATASET_ID)
        result = db.execute_query(query)
        return result[field_name].tolist()

    def get_all_stations(self):
        query = "SELECT * FROM envdata.v_stations_all where dataset_id = {} order by {}".format(db.DATASET_ID, cn.STATION_NAME_COLUMN)
        result = db.execute_query(query)
        return result

    def get_samples(self, criteria):
        ''' returns a pivoted station record as a dataframe where column 0 is the field name and column1 is the value'''
        
        query = "SELECT * FROM envdata.v_samples_all where {} order by {}".format(criteria, cn.SAMPLE_DATE_COLUMN)
        result = db.execute_query(query)
        #result = result[cn.STATION_NAME_COLUMN].tolist()
        return result

    def render_menu(self, ctrl):
        #sidebar menu
        ctrl['filter_stations_cb'] = st.sidebar.checkbox('All stations', value = False, key = None)
        if not ctrl['filter_stations_cb']:
            ctrl['station_list'] = st.sidebar.selectbox(label = cn.STATION_WIDGET_NAME, options = self.stations_options, format_func=lambda x: self.stations_display[x]) 
        # content either html table of dataframe
        df = self.get_table(ctrl['filter_stations_cb'], ctrl['station_list'])
        #df.reset_index(inplace = True) #needed so station_name can be selected on plotly table
        if not ctrl['filter_stations_cb']:
            st.write(df)
            criteria = "{0} = {1} and {2} = {3}".format('station_id', ctrl['station_list'], 'dataset_id', self.dataset_id)
            #show samples belonging to sample
            df = self.get_samples(criteria)
            df = df.set_index('id')
            text = '##### {0} has {1} samples'.format(self.stations_display[ctrl['station_list']], len(df))
            st.markdown(text)
            st.write(df)
            #st.write(df.set_index('Field', inplace=True))
        else:  
            column_values = [df[cn.STATION_NAME_COLUMN], df.aquifer_lithology, df.stratigraphy, df.well_depth, df.screen_hole, df.min_year, df.max_year, df.number_of_samples]
            tools.show_table(df, column_values)
        
        text = r'[View all wells on my google maps](https://drive.google.com/open?id=12WTf4bepPi9u6rtFDSMXIiBCOOzcz09p&usp=sharing)'
        st.markdown(text)

class Plots:
    def __init__():
        pass
    
    def get_pivot_data(df, group_by):
        if group_by == 'station':
            result = pd.pivot_table(df, values=cn.VALUES_VALUE_COLUMN, index=[cn.SAMPLE_DATE_COLUMN, cn.STATION_NAME_COLUMN, cn.MONTH_COLUMN, cn.YEAR_COLUMN], columns=[cn.PAR_NAME_COLUMN], aggfunc=np.average)
        elif group_by == cn.MONTH_COLUMN:
            result = pd.pivot_table(df, values=cn.VALUES_VALUE_COLUMN, index=[cn.SAMPLE_DATE_COLUMN, cn.MONTH_COLUMN, cn.STATION_NAME_COLUMN,cn.YEAR_COLUMN], columns=[cn.PAR_NAME_COLUMN], aggfunc=np.average)
        else:
            result = pd.pivot_table(df, values=cn.VALUES_VALUE_COLUMN, index=[cn.SAMPLE_DATE_COLUMN, cn.YEAR_COLUMN, ], columns=[cn.PAR_NAME_COLUMN], aggfunc=np.average)
        return result

    # returns the label for a given parameter key. 
    def get_label(par_name):
        df = parameters.dfParameters[(parameters.dfParameters[cn.PAR_LABEL_COLUMN] == par_name)]
        df = parameters.dfParameters.set_index(cn.PAR_NAME_COLUMN)
        return  df.at[par_name, cn.PAR_LABEL_COLUMN]

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
        #df = df[(df[cn.PAR_NAME_COLUMN] == ctrl['ypar']) & (df[cn.VALUES_VALUE_COLUMN] > 0)]
        
        if ctrl['max_y'] == ctrl['min_y']:
            scy = alt.Scale()
        else:
            scy = alt.Scale(domain=(ctrl['min_y'], ctrl['max_y']))
        
        base = alt.Chart(df, title = plt_title).mark_boxplot(clip=True).encode(
                alt.X('{}:O'.format(ctrl['group_by']), title = ctrl['group_by'].capitalize()),  #, axis=alt.Axis(labelAngle=0)
                alt.Y('{}:Q'.format(cn.VALUES_VALUE_COLUMN), title = y_lab, scale = scy)
                )
        result.append(base)
        result.append(df)
        return result

    def plot_histogram(plt_title, df, ctrl):
        result = []
        x_lab = get_label(ctrl['ypar'])
        df = df[(df[cn.PAR_NAME_COLUMN] == ctrl['ypar']) & (df[cn.VALUES_VALUE_COLUMN] > 0)]

        if ctrl['group_by'] == 'none':
            df = df[[cn.VALUES_VALUE_COLUMN, cn.STATION_NAME_COLUMN]]
        else:
            df = df[[cn.VALUES_VALUE_COLUMN, ctrl['group_by']]]
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

        if ctrl['group_by'] == 'none':
            base = alt.Chart(df, title = plt_title).mark_bar(clip = True).encode(
                alt.X('{}:Q'.format(cn.VALUES_VALUE_COLUMN), bin = bin_def, title = x_lab, scale = scx),
                alt.Y('count()', stack = None),
            )
        else:
            base = alt.Chart(df, title = plt_title).mark_bar(opacity = cn.OPACITY,clip = True).encode(
                alt.X('{}:Q'.format(cn.VALUES_VALUE_COLUMN), bin = bin_def, title = x_lab, scale = scx),
                alt.Y('count()', stack = None),
                alt.Color(ctrl['group_by'])
            )
        result.append(base)
        result.append(df)
        return result

    def plot_bar_h(plt_title, df, ctrl):
        result = []
        y_lab = get_label(ctrl['ypar'])
        #df = df[(df[cn.PAR_NAME_COLUMN] == ctrl['ypar']) & (df[cn.VALUES_VALUE_COLUMN] > 0)]
        #brush = alt.selection(type='interval', encodings=['x'])
        if (ctrl['max_y'] == ctrl['min_y']):
            scy = alt.Scale()
        else:
            scy = alt.Scale(domain = [ctrl['min_y'], ctrl['max_y']])

        base = alt.Chart(data = df, title = plt_title).mark_bar().encode(
            alt.Y('{}:O'.format(ctrl['group_by']), title = ''),
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
        #df = df[(df[cn.PAR_NAME_COLUMN] == ctrl['ypar']) & (df[cn.VALUES_VALUE_COLUMN] > 0)]
        #brush = alt.selection(type='interval', encodings=['x'])
        if (ctrl['max_y'] == ctrl['min_y']):
            scy = alt.Scale()
        else:
            scy = alt.Scale(domain= [ctrl['min_y'], ctrl['max_y']])
        
        base = alt.Chart(data = df, title = plt_title).mark_bar().encode(
            alt.X('{}:O'.format(ctrl['group_by']), title = ''),
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
            x = alt.X('{}:T'.format(cn.SAMPLE_DATE_COLUMN),
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

        #filter for NAN values
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
                    color = alt.Color('{}:O'.format(ctrl['group_by']),
                        scale=alt.Scale(scheme = cn.color_schema)
                    ),
                tooltip=[cn.SAMPLE_DATE_COLUMN, ctrl['group_by'], ctrl['xpar'], ctrl['ypar']]
            )
        else:
            dfEmpty = pd.DataFrame(data={'col1': [1, 2], 'col2': [3, 4]})
            base = alt.Chart(dfEmpty, title = plt_title).mark_circle(size = cn.symbol_size).encode()
            df = []
            
        result.append(base)
        result.append(df)
        return result

    def render_time_filter(ctrl):
        if not ctrl['filter_by_season']:
            ctrl['filter_by_year'] = st.sidebar.checkbox('Filter data by year', value=False, key=None)
        if ctrl['filter_by_year']:
            ctrl['filter_year'] = st.sidebar.slider('Year', min_value = int(db.first_year), max_value = int(db.last_year), value = int(db.first_year))

        if not ctrl['filter_by_year']:
            ctrl['filter_by_season'] = st.sidebar.checkbox('Filter data by season', value=False, key=None)
        if ctrl['filter_by_season']:
            ctrl['filter_season'] = st.sidebar.selectbox('Season', options = cn.season_list)

    def render_menu(ctrl):
        ctrl['plot_type'] = st.sidebar.selectbox('Plot type', cn.plot_type_list, index = 0)

        ctrl['plot_group_by'] = st.sidebar.selectbox('Group plots by', cn.group_by_options, format_func=lambda x: cn.group_by_display[x])
        if ctrl['plot_type'] == 'time series':
            ctrl['group_by'] = 'station'
        else:
            ctrl['group_by'] = st.sidebar.selectbox('Group markers by', options = cn.group_by_options, format_func=lambda x: cn.group_by_display[x], index = 2)

        if ctrl['plot_type'] not in ['time series', 'histogram', 'box plot', 'bar chart', 'map']:
            ctrl['xpar'] = st.sidebar.selectbox('X-parameter', parameters.all_parameters_list, index = 0)
        
        if ctrl['plot_type'] not in ['map']:
            ctrl['ypar'] = st.sidebar.selectbox('Y-parameter', parameters.all_parameters_list, index = 0)
        
        st.sidebar.markdown('---')
        st.sidebar.markdown('#### Filter')
        # filter for stations
        if ctrl['plot_type'] == 'time series':
            ctrl['filter_stations_cb'] = True
        else:
            ctrl['filter_stations_cb'] = st.sidebar.checkbox('Filter data by station', value=False, key=None)
        
        if ctrl['filter_stations_cb']:
            ctrl['station_list_multi'] = st.sidebar.multiselect(label = cn.STATION_WIDGET_NAME, default = stations.all_stations_list[0], options = stations.all_stations_list)
        
        #filter for month or year, this is hidden for plot type time series
        if ctrl['plot_type'] not in ['time series']:
            render_time_filter(ctrl)
        
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

class Parameters:
    def __init__(self, dataset_id):
        query =  "select id, {0}, {1} from envdata.parameter where dataset_id = {2} order by {0}".format(cn.PAR_NAME_COLUMN, cn.PAR_LABEL_COLUMN, dataset_id )
        df = db.execute_query(query)
        values = df[cn.PAR_NAME_COLUMN].tolist()
        self.__dataset_id = dataset_id
        self.__parameters_options = df['id'].tolist()
        self.__parameters_display = dict(zip(self.__parameters_options, values))
        self.__dfParameters = df
    
    @property
    def dfParameters(self):
        return self.__dfParameters

    @property
    def dataset_id(self):
        return self.__dataset_id

    @property
    def parameters_options(self):
        return self.__parameters_options

    @property
    def parameters_display(self):
        return self.__parameters_display

    def get_table(self, use_all_stations, sel_stations_list):
        global dfParameters
        global dfValues

        if use_all_stations:
            query = '''select t1.parameter_name, t1.formula, t1.unit, t2.min_value, t2.max_value, t2.average_value, t2.number_of_values from 
                        envdata.v_parameters t1
                        inner join (select parameter_id, min(calc_value) min_value, max(calc_value) max_value, avg(calc_value) average_value, count(*) as number_of_values from 
                        envdata.v_observations where dataset_id = {} group by parameter_id) t2 on t2.parameter_id = t1.id'''.format(self.dataset_id)
            result = db.execute_query(query)
        else:
            stations = tools.get_cs_item_list(lst = sel_stations_list, separator=',', quote_string = '')
            query = '''select t1.parameter_name, t1.formula, t1.unit, t2.min_value, t2.max_value, t2.average_value, t2.number_of_values from 
                        envdata.v_parameters t1
                        inner join (select parameter_id, min(calc_value) min_value, max(calc_value) max_value, avg(calc_value) average_value, count(*) as number_of_values from 
                        envdata.v_observations where dataset_id = {} and station_id in ({}) group by parameter_id) t2 on t2.parameter_id = t1.id'''.format(self.dataset_id, stations)
            result = db.execute_query(query)
        return result

    def get_sample_parameters(self, station_name):
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
    def get_parameter_key(self, par_label):
        query = "Select * from v_parameters where dataset_id = {} and {} = '{}'".format(db.DATASET_ID, cn.PAR_LABEL_COLUMN, par_label)
        df = db.execute_query(query)
        return  df.at[0, cn.PAR_NAME_COLUMN]

    def render_menu(self, ctrl, stations):
        #sidebar menu
        ctrl['filter_stations_cb'] = st.sidebar.checkbox('All stations', value=False, key=None)
        if not ctrl['filter_stations_cb']:
            ctrl['station_list_multi'] = st.sidebar.multiselect(label = cn.STATION_WIDGET_NAME, default = stations.stations_options[0], options = stations.stations_options, format_func=lambda x: stations.stations_display[x]) 
        df = self.get_table(ctrl['filter_stations_cb'], ctrl['station_list_multi'])
        df = df.set_index(cn.PAR_NAME_COLUMN)
        #df = df[[cn.PAR_NAME_COLUMN, cn.PAR_LABEL_COLUMN, cn.PAR_UNIT_COLUMN]]
        #values = [df[cn.PAR_NAME_COLUMN], df[cn.PAR_LABEL_COLUMN], df[cn.PAR_UNIT_COLUMN]]
        #txt.show_table(df, values)
        #st.write("{} parameters found in stations {}".format(len(df.index), ','.join(ctrl['station_list_multi']) ))
        st.write(df)
        if not ctrl['filter_stations_cb']:
            text = "This parameter list only includes parameters with at least one occurrence in one of the selected well."
        else:
            text = "This parameter list includes all parameters having been measured in the monitoring network."
        st.markdown(text)

class Charting:
    def __init__(self, data_collection, ctrl):
        self.__data_collection = data_collection
        self.__ctrl = ctrl
    
    @property
    def data_collection(self):
        return self.__data_collection
    
    @property
    def ctrl(self):
        ''' return the dictionary with all controls'''
        return self.__ctrl

    def render_menu(self):
        self.render_controls()
        criteria_base = tools.get_criteria_expression(self.ctrl)
        if self.ctrl['plot_group_by'] == 'none':
            df = self.data_collection.read_values(criteria_base)
            plot_results_list = self.plot('', df, self.ctrl)
            # verify if the data has rows
            if (len(plot_results_list[1]) > 0):
                st.write(plot_results_list[0].properties(width = ctrl('plot_width'), height = ctrl('plot_height')))
                if ctrl('show_data'):
                    st.dataframe(plot_results_list[1])
            else:
                st.write('Insufficient data')
        elif self.ctrl['plot_group_by'] == 'year':
            pass
        elif self.ctrl['plot_group_by'] == 'season':
            for group in cn.season_list:
                criteria = criteria_base + " AND {0} = '{1}'".format(cn.SEASON_COLUMN, group)
                df = db.read_values(criteria)
                plot_title = group

                plot_results_list = plt.plot(plot_title, df, self.ctrl)
                # verify if the data has rows
                if (len(plot_results_list[1]) > 0):
                    st.write(plot_results_list[0].properties(width = ctrl('plot_width'), height = ctrl('plot_height')))
                    if ctrl('show_data'):
                        st.dataframe(plot_results_list[1])
                else:
                    st.write('Insufficient data for: ' + plot_title)
        elif self.ctrl['plot_group_by'] == 'aquifer_type':
            for group in stations.get_aquifer_types():
                criteria = criteria_base + " AND {0} = '{1}'".format(cn.AQUIFER_TYPE_COLUMN, group)
                df = db.read_values(criteria)
                plot_title = group

                plot_results_list = plt.plot(plot_title, df, self.ctrl)
                # verify if the data has rows
                if (len(plot_results_list[1]) > 0):
                    st.write(plot_results_list[0].properties(width = ctrl('plot_width'), height = ctrl('plot_height')))
                    if ctrl('show_data'):
                        st.dataframe(plot_results_list[1])
                else:
                    st.write('Insufficient data for: ' + plot_title)
        elif self.ctrl['group_by'] == cn.STATION_NAME_COLUMN or self.ctrl['plot_type'] == 'time series':
            # if a station filter is set, then loop through these stations otherwise loop through all stations
            list_of_stations = []
            if not ctrl('filter_stations_cb'):
                list_of_stations = stations.all_stations_list
            else:
                list_of_stations = ctrl('station_list_multi')

            for group in list_of_stations:
                criteria = criteria_base + " AND {0} = '{1}'".format(STATION_NAME_COLUMN, group)
                dfStationValues = db.read_values(criteria)
                plot_title = group
                show_all_stations = True
                
                plot_results_list = plt.plot(plot_title, dfStationValues, self.ctrl)
                # verify if the data has rows
                if (len(plot_results_list[1]) > 0):
                    st.write(plot_results_list[0].properties(width = ctrl('plot_width'), height = ctrl('plot_height')))
                    # if a station has been selected display a link to visit site on google maps
                    if not show_all_stations and len(self.ctrl['station_list_multi']) == 1:
                        stations.dfStations.set_index(cn.STATION_NAME_COLUMN, inplace = True)
                        lat = stations.dfStations.at[self.ctrl['station'],'lat']
                        lon = stations.dfStations.at[self.ctrl['station'],'lon']
                        loc = stations.dfStations.at[self.ctrl['station'],'LOCATION']
                        lnk = 'Location: {0}. [Visit station on GOOGLE maps](https://www.google.com/maps/search/?api=1&query={1},{2} "open in GOOGLE maps")'.format(loc, lat, lon)
                        st.markdown(lnk)
                    if ctrl('show_data'):
                        st.dataframe(plot_results_list[1])
                else:
                    st.write('Insufficient data for: ' + plot_title)
        else:
            show_all_stations = True
            plot_title = 'Map'
            df = stations.dfStations
            if len(ctrl('station_list_multi')) == 1:
                pass
            elif len(ctrl('station_list_multi')) > 1:
                df = stations.dfStations[(stations.dfStations[cn.STATION_NAME_COLUMN].isin(ctrl('station_list_multi')))]
                if not show_all_stations:
                    df = df[(df[cn.STATION_NAME_COLUMN] == ctrl('station'))]
            
            if df.shape[0] > 0:
                plt.plot_map(df, ctrl)
                st.write('if map appears empty, use mouse wheel to zoom out, until markers appear.')
            else:
                st.write('Insufficient data')
    
    # returns the label for a given parameter key. 
    def get_label(self, par_id):
        return self.data_collection.parameters.dfParameters.at[par_id,'label']

    def plot(self, plt_title, df, ctrl):
        if (ctrl['plot_type']  == 'scatter plot'):
            return self.plot_scatter(plt_title, df, ctrl)
        elif (ctrl['plot_type'] == 'time series'):
            return self.plot_time_series(plt_title, df, ctrl)
        elif (ctrl['plot_type'] == 'histogram'):
            return self.plot_histogram(plt_title, df, ctrl)
        elif (ctrl['plot_type'] == 'box plot'):
            return self.plot_boxplot(plt_title, df, ctrl)
        elif (ctrl['plot_type'] == 'schoeller'):
            return self.plot_schoeller(plt_title, df, ctrl)
        elif (ctrl['plot_type'] == 'bar chart' and ctrl['bar_direction'] == 'horizontal'):
            return self.plot_bar_h(plt_title, df, ctrl)
        elif (ctrl['plot_type'] == 'bar chart' and ctrl['bar_direction'] == 'vertical'):
            return self.plot_bar_v(plt_title, df)
        elif (ctrl['plot_type'] == 'map'):
            plot_map(plt_title, df, ctrl)
            return ''
        else:
            return 'invalid plottype'

    def plot_schoeller(self, plt_title, df, ctrl):
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

    def plot_boxplot(self, plt_title, df, ctrl):
        result = []
        y_lab = get_label(ctrl['ypar'])
        x_lab = ''
        #df = df[(df[cn.PAR_NAME_COLUMN] == ctrl['ypar']) & (df[cn.VALUES_VALUE_COLUMN] > 0)]
        
        if ctrl['max_y'] == ctrl['min_y']:
            scy = alt.Scale()
        else:
            scy = alt.Scale(domain=(ctrl['min_y'], ctrl['max_y']))
        
        base = alt.Chart(df, title = plt_title).mark_boxplot(clip=True).encode(
                alt.X('{}:O'.format(ctrl['group_by']), title = ctrl['group_by'].capitalize()),  #, axis=alt.Axis(labelAngle=0)
                alt.Y('{}:Q'.format(cn.VALUES_VALUE_COLUMN), title = y_lab, scale = scy)
                )
        result.append(base)
        result.append(df)
        return result

    def plot_histogram(self, plt_title, df, ctrl):
        result = []
        x_lab = get_label(ctrl['ypar'])
        df = df[(df[cn.PAR_NAME_COLUMN] == ctrl['ypar']) & (df[cn.VALUES_VALUE_COLUMN] > 0)]

        if ctrl['group_by'] == 'none':
            df = df[[cn.VALUES_VALUE_COLUMN, cn.STATION_NAME_COLUMN]]
        else:
            df = df[[cn.VALUES_VALUE_COLUMN, ctrl['group_by']]]
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

        if ctrl['group_by'] == 'none':
            base = alt.Chart(df, title = plt_title).mark_bar(clip = True).encode(
                alt.X('{}:Q'.format(cn.VALUES_VALUE_COLUMN), bin = bin_def, title = x_lab, scale = scx),
                alt.Y('count()', stack = None),
            )
        else:
            base = alt.Chart(df, title = plt_title).mark_bar(opacity = cn.OPACITY,clip = True).encode(
                alt.X('{}:Q'.format(cn.VALUES_VALUE_COLUMN), bin = bin_def, title = x_lab, scale = scx),
                alt.Y('count()', stack = None),
                alt.Color(ctrl['group_by'])
            )
        result.append(base)
        result.append(df)
        return result

    def plot_bar_h(self, plt_title, df, ctrl):
        result = []
        y_lab = self.get_label(ctrl['ypar'])
        #df = df[(df[cn.PAR_NAME_COLUMN] == ctrl['ypar']) & (df[cn.VALUES_VALUE_COLUMN] > 0)]
        #brush = alt.selection(type='interval', encodings=['x'])
        if (self.ctrl['max_y'] == ctrl['min_y']):
            scy = alt.Scale()
        else:
            scy = alt.Scale(domain = [ctrl['min_y'], ctrl['max_y']])

        base = alt.Chart(data = df, title = plt_title).mark_bar().encode(
            alt.Y('{}:O'.format(ctrl['group_by']), title = ''),
            alt.X('mean({0}):Q'.format(cn.VALUES_VALUE_COLUMN), title = y_lab, scale = scy),
        )

        avg = alt.Chart(df).mark_rule(color='red').encode(
            x='mean({0}):Q'.format(cn.VALUES_VALUE_COLUMN)
        )
        
        result.append(base + avg)
        result.append(df)
        return result

    def plot_bar_v(self, plt_title, df):
        result = []
        y_lab = self.get_label(self.ctrl['ypar'])
        #df = df[(df[cn.PAR_NAME_COLUMN] == ctrl['ypar']) & (df[cn.VALUES_VALUE_COLUMN] > 0)]
        #brush = alt.selection(type='interval', encodings=['x'])
        if (self.ctrl['max_y'] == self.ctrl['min_y']):
            scy = alt.Scale()
        else:
            scy = alt.Scale(domain= [self.ctrl['min_y'], self.ctrl['max_y']])
        
        base = alt.Chart(data = df, title = plt_title).mark_bar().encode(
            alt.X('{}:O'.format(self.ctrl['group_by']), title = ''),
            alt.Y('mean({0}):Q'.format(cn.VALUES_VALUE_COLUMN), title = y_lab, scale = scy),
        )

        avg = alt.Chart(df).mark_rule(color='red').encode(
            y = 'mean({0}):Q'.format(cn.VALUES_VALUE_COLUMN)
        )
        
        result.append(base + avg)
        result.append(df)
        return result

    def plot_map(self, df, ctrl): 
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

    def plot_time_series(self, plt_title, df, ctrl):
        result = []
        x_lab = ''
        y_lab = get_label(ctrl['ypar'])
        df = df[(df[cn.PAR_NAME_COLUMN] == ctrl['ypar']) & (df[cn.VALUES_VALUE_COLUMN] > 0)]
        if ctrl['max_y'] == ctrl['min_y']:
            scy = alt.Scale()
        else:
            scy = alt.Scale(domain=(ctrl['min_y'], ctrl['max_y']))
        base = alt.Chart(df, title = plt_title).mark_line(point = True, clip=True).encode(
            x = alt.X('{}:T'.format(cn.SAMPLE_DATE_COLUMN),
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

    def plot_scatter(self, plt_title, df, ctrl):
        ok = False
        result = []

        # remove value < 0
        df = df.reset_index()
        df = df[(df[cn.PAR_NAME_COLUMN].isin([ctrl['xpar'], ctrl['ypar']]))]
        df = get_pivot_data(df, ctrl['group_by'])
        ok = (set([ctrl['xpar'], ctrl['ypar']]).issubset(df.columns))

        #filter for NAN values
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
                    color = alt.Color('{}:O'.format(ctrl['group_by']),
                        scale=alt.Scale(scheme = cn.color_schema)
                    ),
                tooltip=[cn.SAMPLE_DATE_COLUMN, ctrl['group_by'], ctrl['xpar'], ctrl['ypar']]
            )
        else:
            dfEmpty = pd.DataFrame(data={'col1': [1, 2], 'col2': [3, 4]})
            base = alt.Chart(dfEmpty, title = plt_title).mark_circle(size = cn.symbol_size).encode()
            df = []
            
        result.append(base)
        result.append(df)
        return result

    def render_controls(self):
        def render_time_filter():
            ''' renders the controls for the time filter to ensure that the user may only filter by 1 time control'''
            if not self.ctrl['filter_by_season']:
                self.ctrl['filter_by_year'] = st.sidebar.checkbox('Filter data by year', value=False, key=None)
            if self.ctrl['filter_by_year']:
                self.ctrl['filter_year'] = st.sidebar.slider('Year', min_value = int(db.first_year), max_value = int(db.last_year), value = int(db.first_year))

            if not self.ctrl['filter_by_year']:
                self.ctrl['filter_by_season'] = st.sidebar.checkbox('Filter data by season', value=False, key=None)
            if self.ctrl['filter_by_season']:
                self.ctrl['filter_season'] = st.sidebar.selectbox('Season', options = cn.season_list)

        self.ctrl['plot_type'] = st.sidebar.selectbox('Plot type', cn.plot_type_list, index = 0)

        self.ctrl['plot_group_by'] = st.sidebar.selectbox('Group plots by', cn.group_by_options, format_func=lambda x: cn.group_by_display[x])
        if self.ctrl['plot_type'] == 'time series':
            self.ctrl['group_by'] = 'station'
        else:
            self.ctrl['group_by'] = st.sidebar.selectbox('Group markers by', cn.group_by_options, format_func=lambda x: cn.group_by_display[x], index = 2)

        if self.ctrl['plot_type'] not in ['time series', 'histogram', 'box plot', 'bar chart', 'map']:
            self.ctrl['xpar'] = st.sidebar.selectbox('X-parameter', options= self.data_collection.parameters.parameters_options, format_func = lambda x: self.data_collection.parameters.parameters_display[x])
        if self.ctrl['plot_type'] not in ['map']:
            self.ctrl['ypar'] = st.sidebar.selectbox('Y-parameter', options= self.data_collection.parameters.parameters_options, format_func = lambda x: self.data_collection.parameters.parameters_display[x])
        
        st.sidebar.markdown('---')
        st.sidebar.markdown('#### Filter')
        # filter for stations
        if self.ctrl['plot_type'] == 'time series':
            self.ctrl['filter_stations_cb'] = True
        else:
            self.ctrl['filter_stations_cb'] = st.sidebar.checkbox('Filter data by station', value=False, key=None)
        
        if self.ctrl['filter_stations_cb']:
            self.ctrl['station_list_multi'] = st.sidebar.multiselect(label = cn.STATION_WIDGET_NAME, default = stations.all_stations_list[0], options = stations.all_stations_list)
        
        #filter for month or year, this is hidden for plot type time series
        if self.ctrl['plot_type'] not in ['time series']:
            render_time_filter()
        
        if self.ctrl['plot_type'] == 'histogram':
            self.ctrl['bin_size'] = st.sidebar.number_input('Bin width')

        # various plot settings such as axis length, min max on axis etc
        st.sidebar.markdown('---')
        st.sidebar.markdown('#### Plot settings')
        self.ctrl['define_axis_limits'] = st.sidebar.checkbox('Define axis limits', value=False, key=None)
        if self.ctrl['define_axis_limits']:
            if self.ctrl['plot_type'] not in ['time series']:
                self.ctrl['min_x'] = st.sidebar.number_input('Minimum X', value= 0.0)
                self.ctrl['max_x'] = st.sidebar.number_input('Maximum X', value= 0.0)
            self.ctrl['min_y'] = st.sidebar.number_input('Minimum y', value= 0.0)
            self.ctrl['max_y'] = st.sidebar.number_input('Maximum y', value= 0.0)
        if self.ctrl['plot_type'] == 'bar chart':
            self.ctrl['bar_direction'] = st.sidebar.radio('Bars', ['vertical', 'horizontal'])

        self.ctrl['define_axis_length'] = st.sidebar.checkbox('Define axis length', value=False)
        if self.ctrl['define_axis_length']:
            self.ctrl['plot_width'] = st.sidebar.number_input('Width (pixel)', value = self.ctrl['plot_width'])
            self.ctrl['plot_height'] = st.sidebar.number_input('Height (pixel)', value = self.ctrl['plot_height'])
        
        self.ctrl['show_data'] = st.sidebar.checkbox('Show detail data', value = False, key = None)
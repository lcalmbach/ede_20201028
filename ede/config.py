import socket
from enum import Enum


class DataType(Enum):
    chemistry = 1
    precipitation = 2
    water_level = 3


LOCAL_SERVER = 'waterloo'
if socket.gethostname() == LOCAL_SERVER:
    SQL_CONNECT_STRING = 'mysql://root:password@localhost/envdata'
else:
    SQL_CONNECT_STRING = 'mysql://root:password63@terra-1.cxudpg3pe6ie.us-east-2.rds.amazonaws.com/envdata'

dict_menu_filter_type = {
    "Info": 0,
    "Station information": 1,
    "Parameters information": 2,
    "Plotting": 3
}

MAP_LEGEND_SYMBOL_SIZE: int = 10
MAPBOX_STYLE: str = "mapbox://styles/mapbox/light-v10"
GRADIENT: str = 'blue-green'
FILTER_TYPE_STATION: int = 1
FILTER_TYPE_PARAMETER: int = 2
FILTER_TYPE_PLOT: int = 3
USER_MANUAL_LINK: str = 'https://ede.readthedocs.io/en/latest/'
HELP_ICON: str = 'https://img.icons8.com/offices/30/000000/help.png'
YEAR_COLUMN: str = 'year'
MONTH_COLUMN = 'month'
DAY_COLUMN = 'day'
SEASON_COLUMN = 'season'
PAR_NAME_COLUMN = 'parameter_name'
PAR_LABEL_COLUMN = 'label'
PAR_UNIT_COLUMN = 'unit'
SAMPLE_DATE_COLUMN = 'sample_date'
STATION_NAME_COLUMN = 'station_name'
DEPTH_CATEGORY_COLUMN = 'depth_category'
LONGITUDE_COLUMN = 'lon'
LATITUDE_COLUMN = 'lat'
VALUES_VALUE_COLUMN = 'calc_value'
AQUIFER_TYPE_COLUMN = 'aquifer_type'
VALUES_SAMPLENO_COLUMN = 'sample_number'
LOGO_REFERENCE = 'https://github.com/lcalmbach/ede/blob/master/ede/static/images/flask.png?raw=true'
# database settings, parameter and column mapping
STATION_SUMMARY_TABLE_COLUMNS = ['station_name', 'aquifer_lithology', 'stratigraphy', 'well_depth', 'screen_hole',
                                 'first_year', 'last_year', 'number_of_samples']
STATIONS_ALL_VIEW = 'v_stations_all'
SAMPLES_ALL_VIEW = 'v_samples'
VALUES_ALL_VIEW = 'v_values_all'
PARAMETERS_ALL_VIEW = 'v_parameters_all'
OPACITY = 0.3
plot_width = 600
plot_height = 400
text_path = r'static/text/'
images_path = r'static/images/'
css_path = r'static/css/'
data_path = r'static/data/'

chem_data_file = r'chemistry.txt'
parameters_data_file = r'parameters.txt'
precipitation_data_file = r'precipitation.txt'
samples_data_file = r'samples.txt'
water_levels_data_file = r'waterlevels.txt'
stations_data_file = r'PGMN_WELLS_NAD83.txt'

version = '0.0.1'
data_last_modified = r'March 14, 2017'

season_list = ['spring', 'summer', 'autumn', 'winter']
plot_type_list = ['bar chart', 'box plot', 'scatter plot', 'time series', 'histogram', 'map']  # , 'schoeller',
group_by_options = ['none', 'station_name', 'year', 'season', 'aquifer_type', 'depth_category', 'township', 'county']
group_by_display = {'none': 'none', 'station_name': 'station', 'year': 'year', 'season': 'season',
                    'aquifer_type': 'aquifer type', 'depth_category': 'well depth category',
                    'township': 'township', 'county': 'county'}
months_list = ['<all>', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
menu_list = ['Info', 'Station information', 'Parameters information', 'Plotting']  # 'Help', , 'Settings'
color_schema = "set1"  # https://vega.github.io/vega/docs/schemes/#reference
symbol_size = 60
google_link = r'https://drive.google.com/open?id=12WTf4bepPi9u6rtFDSMXIiBCOOzcz09p&usp=sharing'

STATION_WIDGET_NAME = 'Station'

DEFAULT_DATA_COLLECTION_ID = 1  # pgmn
DATA_COLLECTION_NAME_COLUMN = 'name_long'
DATASET_NAME_COLUMN = 'name'

SQL_CONNECT_STRING =  'mysql://root:password@localhost/envdata' 
# SQL_CONNECT_STRING: 'mysql://root:password63@terra-1.cxudpg3pe6ie.us-east-2.rds.amazonaws.com/imp'
YEAR_COLUMN = 'year'
MONTH_COLUMN = 'month'
DAY_COLUMN = 'day'
SEASON_COLUMN = 'season'
PAR_NAME_COLUMN = 'parameter_name'
PAR_LABEL_COLUMN = 'label'
PAR_UNIT_COLUMN = 'unit'
SAMPLE_DATE_COLUMN = 'sample_date'
STATION_NAME_COLUMN = 'station_name'
LONGITUDE_COLUMN = 'lon'
LATITUDE_COLUMN = 'lat'
VALUES_VALUE_COLUMN = 'value'
AQUIFER_TYPE_COLUMN = 'aquifer_type'
VALUES_SAMPLENO_COLUMN = 'sample_number'
DEFAULT_STATION = 'W0000083-1'
LOGO_REFERENCE = 'https://github.com/lcalmbach/ede/blob/master/static/images/flask.png?raw=true'
# database settings, parameter and column mapping
STATION_SUMMARY_TABLE_COLUMNS = ['station_name', 'aquifer_lithology', 'stratigraphy', 'well_depth', 'screen_hole', 'first_year', 'last_year', 'number_of_samples']
STATIONS_ALL_VIEW = 'v_stations_all'
SAMPLES_ALL_VIEW = 'v_samples_all'
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

season_list = ['spring','summer','autumn','winter']
plot_type_list = ['bar chart','box plot','scatter plot','time series','histogram','map'] #, 'schoeller', ,
group_by_list = ['none','station_name','year','month', 'season','aquifer_type']
group_by_list2 = ['station_name','year','season', 'aquifer_type']
plot_group_by_list = ['none','station_name','year','season', 'aquifer_type']
months_list = ['<all>','1','2','3','4','5','6','7','8','9','10','11','12']
menu_list = ['Info','Plotting', 'Station information', 'Parameters information']  # 'Help', , 'Settings'
color_schema = "set1" # https://vega.github.io/vega/docs/schemes/#reference
symbol_size = 60
google_link = r'https://drive.google.com/open?id=12WTf4bepPi9u6rtFDSMXIiBCOOzcz09p&usp=sharing'

STATION_WIDGET_NAME = 'Station'

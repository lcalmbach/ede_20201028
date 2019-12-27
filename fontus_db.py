"""
## Fontus

Fontus is a tool to 

Author: [Lukas Calmbach](mailto:lcalmbach@gmail.com))\n
Source: [Github](https://github.com/lcalmbach)
"""
import streamlit as st
import pandas as pd
import numpy as np
import constants as cn
from sqlalchemy import create_engine
import sqlalchemy as sql
import pymysql
import MySQLdb
import pandas.io.sql as psql

dfValues = pd.DataFrame
dfSamples = pd.DataFrame
dfStations = pd.DataFrame
dfParameters = pd.DataFrame
dfData_collections = pd.DataFrame
dfData_sets = pd.DataFrame

number_of_samples = 0
number_of_stations = 0
number_of_parameters = 0
first_year = 0
last_year = 0
sql_engine = ''

DATA_COLLECTION_LIST = []
DATA_COLLECTION_ID = 0
DATASET_LIST = []
DATASET_ID = 0

def init():
    import app

    global sql_engine
    global DATA_COLLECTION_LIST

    sql_engine = sql.create_engine(cn.SQL_CONNECT_STRING)
    init_data_collection()

    #dfValues = read_values(sql_engine)
    #dfSamples = read_samples(sql_engine, '')
    #dfStations = read_wells(sql_engine)
    #dfParameters = read_parameters(sql_engine)
    
    #number_of_samples = len(dfSamples.index)
    #number_of_stations = len(dfStations.index)
    #number_of_parameters = len(dfParameters.index)
    #first_year = dfSamples[cn.YEAR_COLUMN].min()
    #last_year = dfSamples[cn.YEAR_COLUMN].max()
    #all_parameters_list = dfParameters[cn.PAR_NAME_COLUMN].tolist()
    #DATA_COLLECTION_LIST = ['pgmn', 'pwqmn']
    #DATASET_LIST = ['water chemistry', 'water levels', 'precipitation']


# @st.cache(allow_output_mutation=True)
def init_data_collection():
    global sql_engine
    global DATA_COLLECTION_LIST
    global dfData_collections

    query = "Select * from v_data_collections"
    dfData_collections = pd.read_sql_query(query, sql_engine)   
    DATA_COLLECTION_LIST = dfData_collections['name_short'].tolist()
    dfData_collections = dfData_collections.set_index('name_short')

''' 
retrieves the record for a current dataset using the dataset name (from the selectbox) and returns its id, which will then be
used for querying.
'''
def set_dataset_id(dataset_key):
    global DATASET_ID
    global sql_engine
    global first_year
    global last_year

    query = "Select * from v_dataset_summary where dataset = '{}'".format(dataset_key)
    result = pd.read_sql_query(query, sql_engine)
    DATASET_ID = result.at[0, 'dataset_id']
    first_year = result.at[0, 'min_year']
    last_year = result.at[0, 'max_year']

def get_dataset_list(collection_key):
    global sql_engine
    global DATA_COLLECTION_ID

    # find the collection id
    query = "Select * from v_data_collections where name_short = '{}'".format(collection_key)
    result = pd.read_sql_query(query, sql_engine)
    DATA_COLLECTION_ID = result.at[0, 'id']

    # find associated data sets
    query = "Select * from v_datasets where data_collection_id = '{}'".format(DATA_COLLECTION_ID)
    result = pd.read_sql_query(query, sql_engine)
    result = result['name'].tolist()
    return result

'''
retrieves the table of dataset summary information for the current data collection. also sets 
the index to the dataset_id column, so we can iterate trough rows.
'''
def get_datasets(collection_id):
    global sql_engine

    query = "Select * from v_dataset_summary where data_collection_id = '{}'".format(collection_id)
    result = pd.read_sql_query(query, sql_engine)
    # result = result.set_index('dataset_id')
    return result

# @st.cache(allow_output_mutation=True)
def get_data_collection_id(collection_name):
    global sql_engine
    global DATA_COLLECTION_ID

    query = "Select * from v_dataset where data_collection_id = {}".format(DATA_COLLECTION_ID)
    result = pd.read_sql_query(query, sql_engine)
    DATA_COLLECTION_ID = result.at[0, 'id']
    set.write(result)
    return result

def read_values(criteria):
    global sql_engine

    query = "Select * from {} where {}".format(cn.VALUES_ALL_VIEW, criteria)
    result = pd.read_sql_query(query, sql_engine)
    result[cn.SAMPLE_DATE_COLUMN] = pd.to_datetime(result[cn.SAMPLE_DATE_COLUMN])
    return result

def read_wells(sql_engine):
    #result = pd.read_csv(cn.data_path + cn.stations_data_file, sep='\t', encoding = "ISO-8859-1",)
    query = "select * from " + cn.STATIONS_ALL_VIEW
    result = pd.read_sql_query(query, sql_engine)
    return result

def read_samples(sql_engine, criteria):
    #result = pd.read_csv(cn.data_path + cn.samples_data_file, sep='\t', encoding = "ISO-8859-1",)
    query = "select * from " + cn.VALUES_ALL_VIEW
    if criteria > '':
        query += ' where ' + criteria
    result = pd.read_sql_query(query, sql_engine)
    result[cn.SAMPLE_DATE_COLUMN] = pd.to_datetime(result[cn.SAMPLE_DATE_COLUMN])
    return result

def read_parameters(sql_engine):
    query = "select * from " + cn.PARAMETERS_ALL_VIEW
    result = pd.read_sql_query(query, sql_engine)
    return result

def execute_query(query):
    result = pd.read_sql_query(query, sql_engine)
    return result
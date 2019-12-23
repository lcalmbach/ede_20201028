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

number_of_samples = 0
number_of_stations = 0
number_of_parameters = 0
first_year = 0
last_year = 0
sql_engine = ''

def init():
    import app

    global dfValues
    global dfSamples
    global dfStations
    global dfParameters
    global dfSamples_all
    global number_of_samples
    global number_of_stations
    global number_of_parameters
    global first_year
    global last_year
    global all_parameters_list
    global sql_engine

    sql_engine = sql.create_engine(cn.SQL_CONNECT_STRING)
    #dfValues = read_values(sql_engine)
    dfSamples = read_samples(sql_engine, '')
    dfStations = read_wells(sql_engine)
    dfParameters = read_parameters(sql_engine)
    
    number_of_samples = len(dfSamples.index)
    number_of_stations = len(dfStations.index)
    number_of_parameters = len(dfParameters.index)
    first_year = dfSamples[cn.YEAR_COLUMN].min()
    last_year = dfSamples[cn.YEAR_COLUMN].max()
    all_parameters_list = dfParameters[cn.PAR_NAME_COLUMN].tolist()

def read_values(criteria):
    global sql_engine

    query = "Select * from " + cn.VALUES_ALL_VIEW
    if criteria > '':
        query += ' where ' + criteria
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
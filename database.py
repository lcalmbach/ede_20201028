from sqlalchemy import create_engine
import sqlalchemy as sql
import pymysql
import MySQLdb
#import pandas.io.sql as psql
import pandas as pd
import streamlit as st
import config as cn

def execute_query(query):
    '''executes a query and returns a dataframe with the results'''
    
    global sql_engine

    result = pd.read_sql_query(query, sql_engine)
    return result

def init():
    '''Reads the connection string and sets the sql_engine attribute.'''
    global sql_engine
    
    sql_engine = sql.create_engine(cn.SQL_CONNECT_STRING)

def get_distinct_values(column_name, table_name, dataset_id):
    '''returns a list of unique values from a defined code column'''
    query = "SELECT {0} FROM {1} where dataset_id = {2} group by {0} order by {0}".format(column_name, table_name, dataset_id)
    result = execute_query(query)
    result = result[column_name].tolist()
    return result

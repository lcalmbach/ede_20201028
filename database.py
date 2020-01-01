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

from sqlalchemy import create_engine
import sqlalchemy as sql
import pymysql
import pandas as pd
import constants as cn

def file2table(): # table_name, filename
    table_name = 'pwqmn_chemistry'
    #filename = r'static/data/pwqmn_stations.txt'
    #filename = r'E:\develop\pwqmn\static\data\pwqmn_stations.txt'
    filename = r'E:\Data\Canada\Ontario\pwqmn_rawdata_2016\pwqmn_chemistry_data.txt'
    dataFrame = pd.read_csv(filename, sep='\t', encoding = "ISO-8859-1",)
    
    DB_USER = 'root'
    DB_PASS = 'password'
    DB_HOST = 'localhost'
    DB_PORT = 3306
    DATABASE = 'imp'

    connect_string = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(DB_USER, DB_PASS, DB_HOST, DB_PORT, DATABASE)
    sql_engine = sql.create_engine(connect_string, pool_recycle=3600)
    dbConnection = sql_engine.connect()

    try:
        frame = dataFrame.to_sql(table_name, dbConnection, if_exists='fail');
    except ValueError as vx:
        print(vx)
    except Exception as ex:
        print(ex)
    else:
        print("Table %s created successfully."%table_name);   
    finally:
        dbConnection.close()
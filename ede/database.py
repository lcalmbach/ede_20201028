import mysql.connector as mysql
import pandas as pd
import config as cn

mydb = ''

def execute_query(query):
    """Executes a query and returns a dataframe with the results"""

    result = pd.read_sql_query(query, mydb)
    return result

def init():
    """Reads the connection string and sets the sql_engine attribute."""

    global mydb
    
    mydb = mysql.connect(
        host="localhost",
        # host="terra-1.cxudpg3pe6ie.us-east-2.rds.amazonaws.com",
        user="root",
        passwd="password",
        # passwd="password63",
        database="envdata"
    )

    
def get_distinct_values(column_name, table_name, dataset_id, criteria):
    """Returns a list of unique values from a defined code column."""

    query = "SELECT {0} FROM {1} where dataset_id = {2} {3} {4} group by {0} order by {0}".format(column_name,
        table_name, dataset_id, (' AND ' if criteria > '' else ''), criteria)
    result = execute_query(query)
    result = result[column_name].tolist()
    return result

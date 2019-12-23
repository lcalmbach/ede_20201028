import pandas as pd

merge_path = r'E:\Data\Canada\Ontario\pgmn\merged'

filename = r'E:\Data\Canada\Ontario\pgmn\precipitation\24.csv'
df = pd.read_csv(filename, sep=',',encoding = "ISO-8859-1")
df['READING_DTTM'] = pd.to_datetime(df['READING_DTTM'], errors='coerce')

#add day month year columns
df['day'] = df['READING_DTTM'].dt.day
df['month'] = df['READING_DTTM'].dt.month
df['year'] = df['READING_DTTM'].dt.year
df = df.groupby(['day','month','year'])['AccumulationFinal'].sum()

filename = merge_path + '\\' + 'precipitation.txt'
df.to_csv(filename, header = True, index = True, sep='\t')


import pandas as pd
from os import listdir
from os.path import isfile, join
import zipfile as zip
import datetime as dt

df_merged_files = pd.DataFrame
list_of_frames = []
merge_path = r'E:\Data\Canada\Ontario\pgmn\data\\'
zip_path = r'E:\Data\Canada\Ontario\pgmn\waterlevels\\'
temp_path = r'E:\Data\Canada\Ontario\pgmn\temp\\'

files = [f for f in listdir(zip_path) if isfile(join(zip_path, f))]
"""
for f in files:
    filename = zip_path + f
    print(f)
    with zip.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall(temp_path)
"""
files = [f for f in listdir(temp_path) if isfile(join(temp_path, f))]
for f in files:
    print(f)
    filename = temp_path + f
    df = pd.read_csv(filename, sep=',', encoding = "ISO-8859-1")
    df['READING_DTTM'] = pd.to_datetime(df['READING_DTTM'], errors='coerce')
    df['DAY'] = df["READING_DTTM"].dt.strftime("%Y-%m-%d")
    df = df[['CASING_ID','DAY','Water_Level_Elevation_meter_above_sea_level']]
    df = df.groupby(['CASING_ID','DAY']).mean()
    list_of_frames.append(df)

df_merged_files = pd.concat(list_of_frames, axis=0, join='outer', ignore_index=False, keys=None,
    levels=None, names=None, sort=True,verify_integrity=False, copy=True)

filename = merge_path + '\\' + 'waterlevels.txt'
df_merged_files.to_csv(filename, header = True, index = True, sep='\t')


import pandas as pd
import numpy as np
from os import listdir
from os.path import isfile, join

merged_files = pd.DataFrame
list_of_frames = []
chem_path = r'E:\Data\Canada\Ontario\pgmn\Chemistry'
merge_path = r'E:\Data\Canada\Ontario\pgmn\merged'
files = [f for f in listdir(chem_path) if isfile(join(chem_path, f))]

# generate the merged table using the first file, remove it from the list so
# it is not read twice

for f in files:
    filename = chem_path + '\\' + f
    df = pd.read_csv(filename, sep='\t',encoding = "ISO-8859-1")
    list_of_frames.append(df)

df_merged_files = pd.concat(list_of_frames, axis=0, join='outer', ignore_index=False, keys=None,
    levels=None, names=None, sort=True,verify_integrity=False, copy=True)

filename = merge_path + '\\' + 'all_wells.txt'

# create a list of parameters, then transform it to a dataframe and save it

df = df_merged_files[['ParameterName']]
df = df.drop_duplicates().sort_values(by=['ParameterName']) 
filename = merge_path + '\\' + 'parameters.txt'
df.to_csv(filename, header = True, index = False, sep='\t')

df = df_merged_files[['PGMN_WELL','SampleDate','SampleNumber','LabName','Ionbalance','Comments']]
df = df.drop_duplicates().sort_values(by=['PGMN_WELL','SampleDate'])
filename = merge_path + '\\' + 'samples.txt'
df.to_csv(filename, header = True, index = False, sep='\t')



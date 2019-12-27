import streamlit as st
import pandas as pd
import constants as cn
import fontus_db as db
import plotly.graph_objects as go

dfTexts = pd.DataFrame
help_content = ''
helpfile = 'help.md'
text_file = r"fontus_texts.txt"

def render_about_text(data_collection_name):
    df = db.dfData_collections
    st.image('static/images/' + df.at[data_collection_name, 'about_image'])
    text = df.at[data_collection_name, 'about_text']
    st.markdown(text)
    
    st.markdown('### Metadata from data owner:')
    st.markdown('* Publisher: {0}'.format(df.at[data_collection_name, 'publisher']))
    st.markdown('* Update frequency: {0}'.format(df.at[data_collection_name, 'update_frequency']))
    st.markdown('* Geographical coverage: {0}'.format(df.at[data_collection_name, 'geographical_coverage']))
    st.markdown('* Original data download page: {0}'.format(df.at[data_collection_name, 'origin_url']))
    st.markdown('   ')

    df = db.get_datasets(db.DATA_COLLECTION_ID)
    list_of_dataset_ids = df['dataset_id'].tolist()
    df = df.set_index('dataset_id')
    st.markdown('### Summary of datasets available in the data collection:')
    for dataset in list_of_dataset_ids:
        st.markdown('#### Dataset: {0}'.format(df.at[dataset, 'dataset']))
        st.markdown('* Number of stations: {0}'.format(df.at[dataset, 'number_of_stations']))
        st.markdown('* Number of parameters: {0}'.format(df.at[dataset, 'number_of_parameters']))
        st.markdown('* Number of sampling events: {0}'.format(df.at[dataset, 'number_of_samples']))
        st.markdown('* Time interval covered: {} - {}'.format(df.at[dataset, 'min_year'], df.at[dataset, 'max_year']))

def info_sideboard(key):
    st.sidebar.title("About")
    text = dfTexts.loc[dfTexts.key == key, 'text'].values[0]
    st.sidebar.info(text)

def show_table(df, values):
    fig = go.Figure(data=[go.Table(
    header=dict(values=list(df.columns),
                fill_color='silver',
                line_color='darkslategray',
                align='left'),
    cells=dict(values=values,
               fill_color='white',
               line_color='darkslategray',
               align='left'))
    ])
    st.write(fig)

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
    text = df.at[data_collection_name, 'about_text']
    text = text.replace('%first_year%', df.at[data_collection_name, 'first_year'])
    text = text.replace('%last_year%', df.at[data_collection_name, 'last_year'])
    st.markdown(text)

    st.markdown('### Summary of data available in the data collection:')
    st.markdown('* Number of stations: {0}'.format(1))
    st.markdown('* Number of parameters: {0}'.format(1))
    st.markdown('* Number of sampling events: {0}'.format(1))
    st.markdown('* Data last modified: {0}'.format(1))

    st.markdown('### Metadata from data owner:')
    st.markdown('* Publisher: {}'.format(df.at[data_collection_name, 'publisher'])
    st.markdown('* Ontario Time captured: January 1, 1964 – December 31, 2016')
    st.markdown('* Update frequency: Yearly')
    st.markdown('* Geographical coverage: Ontario')
    st.markdown('* Technical documentation: [Metadata Record](https://www.javacoeapp.lrc.gov.on.ca/geonetwork/srv/en/metadata.show?id=13826)')  

def print_main_about(dfStations, dfParameters, dfSamples):
#to: create a single md file for this!
    st.markdown('![title pic](https://github.com/lcalmbach/pwqmn/raw/master/static/images/river_background.png)')
    text = dfTexts.loc[dfTexts.key == 'PAR001', 'text'].values[0]
    text = text.replace('%first_year%', str(db.first_year))
    st.markdown(text.replace('%last_year%', str(db.last_year)))
    st.markdown(dfTexts.loc[dfTexts.key == 'PAR002', 'text'].values[0])
    st.markdown(dfTexts.loc[dfTexts.key == 'PAR003', 'text'].values[0])
    
    st.markdown('### Summary of data available in the dataset:')
    st.markdown('* Number of stations: {0}'.format(len(dfStations.index)))
    st.markdown('* Number of parameters: {0}'.format(len(dfParameters.index)))
    st.markdown('* Number of sampling events: {0}'.format(db.number_of_samples))
    st.markdown('* Data last modified: {0}'.format(cn.data_last_modified)) 

    st.markdown('### Metadata from data owner:')
    st.markdown('* Publisher: Environment, Conservation and Parks')
    st.markdown('* Ontario Time captured: January 1, 1964 – December 31, 2016')
    st.markdown('* Update frequency: Yearly')
    st.markdown('* Geographical coverage: Ontario')
    st.markdown('* Technical documentation: [Metadata Record](https://www.javacoeapp.lrc.gov.on.ca/geonetwork/srv/en/metadata.show?id=13826)')  

def print_help():
    st.markdown(help_content, unsafe_allow_html=True)

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

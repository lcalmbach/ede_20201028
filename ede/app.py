"""
ede is a Streamlit implementation of an interactive groundwater quality data app.This app allows to explore the
Provincial Groundwater Monitoring Network dataset encompassing over XX years of data. The data can be explored
using various Altair plot types.
Author: Lukas Calmbach lcalmbach@gmail.com
"""

import streamlit as st

import config as cn
from fontus import Fontus
import tools

def info_sideboard():
    """Renders the about text in the sideboard."""

    st.sidebar.subheader("About")
    text = """This app has been developed by [Lukas Calmbach](mailto:lcalmbach@gmail.com) using 
        [Python](https://www.python.org/), [Streamlit](https://streamlit.io/) and [Altair]
        (https://altair-viz.github.io/). All sourcecode is published on [github](https://github.com/lcalmbach/pwqmn).
        """
    st.sidebar.info(text)


def show_menu():
    """Renders the radio button menu in the sidebar and calls selected menu item functions."""

    text = """![logo]({}) <b><span style="color:blue">E</span>nvironmental <span style="color:blue">D</span>ata <span 
        style="color:blue">E</span>xplorer</b>""".format(cn.LOGO_REFERENCE)
    st.sidebar.markdown(text, unsafe_allow_html=True)
    tools.log('session.data_collection_id = st.sidebar, start')
    session.data_collection_id = st.sidebar.selectbox('Select a data collection', session.data_collection_options,
                                                      format_func=lambda x: session.data_collection_display[x])
    # only show the dataset selection of there is more than 1 set
    if len(session.dataset_options) > 1:
        session.dataset_id = st.sidebar.selectbox('Select a dataset', session.dataset_options,
                                                  format_func=lambda x: session.dataset_display[x])
    # now that the dataset id is set init station and parameter lists
    st.sidebar.header('Menu')
    session.menu = st.sidebar.radio('', cn.menu_list)
    st.sidebar.markdown('---')
    if session.menu == 'Info':
        session.render_about_text()
        info_sideboard()
    elif session.menu == 'Station information':
        session.stations.render_menu()
    elif session.menu == 'Parameters information':
        session.parameters.render_menu()
    elif session.menu == 'Plotting':
        session.plots.render_menu()
    session.render_help()


if __name__ == "__main__":
    session = Fontus()
    show_menu()

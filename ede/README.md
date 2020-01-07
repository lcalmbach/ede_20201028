**Environmental Data Explorer (EDE): An interactive analysis tool for environmental data sets**

EDE is designed to import various types of environmental data collections and immiedeately show summary tables and graphs for this data. The current version holds two data collection provided by Ontario.ca:

* [The Provincial (Stream) Water Quality Monitoring Network (PWQMN)](https://www.ontario.ca/data/provincial-stream-water-quality-monitoring-network)
* [Provincial Groundwater Monitoring Network (PGMN)](https://www.severnsound.ca/programs-projects/monitoring/provincial-groundwater-quality-monitoring-network)

The current tool allows us to present this dataset in interactive scatter, time series, boxplots, etc. to better discover patterns and trends. 

EDE is written in python and uses the following two main libraries:
* [streamlit](https://streamlit.io/)
* [Altair](https://altair-viz.github.io/)

A prototype can be visited on [http://18.222.39.57:8501](http://18.222.39.57:8501)

EDE is currently under development; any input is highly appreciated. Please don't hesitate using the issue-section to contribute.
__version__ = '0.1.0'
__author__ = 'G McMullen-Klein, M Lograda, TJG Lassale, JG Tignol'

"""
Covidat
=======

Provides
    1. A way of easily downloading data from the gov.uk covid API 
	(https://coronavirus.data.gov.uk/details/developers-guide)

    2. A number of plotting functions to easily visualize the data

Documentation
-------------
There is extensive documentation included with the package in the
covidat_documentation.ipnb file. This is the best place to find
help. All functions contain docstrings that explain the required
input and expected output.

The package contains two main modules
    1. data.py Containing the class CovidData which interacts with 
       API and controls which data is downloaded
    2. plot.py Containing all of the plotting functions. These 
       functions are not listed here. To see an explanation of
       how they should be used, please read the documentation
    3. geo_data Contains the .shp files required for geographical
		plots.
"""

from covidatx.data import CovidData
from covidatx.plot import *

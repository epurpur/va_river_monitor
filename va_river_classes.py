

import requests
import json
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt


class RiverAPI():
    
    
    def __init__(self, river_name, site_number):
        self.river_name = river_name
        self.site_number = site_number
    

    def get_current_water_level(self):
        """Takes river site id number and makes API request to waterservices.usgs.gov
        Then parses response to get current water level for river and returns it."""
        
        url = f'http://waterservices.usgs.gov/nwis/iv/?format=json&sites={self.site_number}&parameterCd=00060,00065&siteStatus=all'

        response = requests.request("GET", url)
        data = json.loads(response.text)
        
        #parses json response to get only value of current water level for given river
        current_water_level = data['value']['timeSeries'][0]['values'][0]['value'][0]['value']
        
        return current_water_level
    

    @staticmethod
    def prep_current_water_data(river_site_info):
        """Method used in multithreading process.
        Takes in dictionary of river_site_info. Then creates RiverAPI instance.
        Gets current water level for that instance and appends it to list. 
        Returns entire list of data which is current water levels for all rivers."""

        current_data_list = []

        for river_name, site_number in river_site_info.items():
            data = RiverAPI(river_name, site_number)
            current_water_level = data.get_current_water_level()
            current_data_list.append(current_water_level)

        return current_data_list


    def get_historical_river_data(self):
        """Need to read 'river_levels.csv' in order to get historical stats for each river. 
        This includes min, max, and mean (average) water levels for each river  """

        va_river_data = pd.read_csv('river_levels.csv')

        #convert values in dataframe from strings to floats
        va_river_data[self.river_name] = va_river_data[self.river_name].apply(float)
        
        #get min, max, mean water levels for given river
        min_water_level = va_river_data[self.river_name].min()
        max_water_level = va_river_data[self.river_name].max()
        mean_water_level = va_river_data[self.river_name].mean()

        return (min_water_level, max_water_level, mean_water_level)
            

    @staticmethod
    def read_from_and_write_to_csv(current_data_list):
        """Takes current_data_list from main module,
        reads 'river_levels.csv'
        adds current river data as row to dataframe
        writes new, updated dataframe to 'river_levels.csv', overwriting current file
        returns modified dataframe"""
        

        #add current timestamp to current_data_list at 0 index
        current_datetime = datetime.now()
        current_datetime_formatted = current_datetime.strftime("%d-%b-%Y (%H:%M:%S.%f)")
        current_data_list.insert(0, current_datetime_formatted)
 
        #read csv file as pandas dataframe
        va_river_data = pd.read_csv('river_levels.csv')

        #drop unneeded index column (added by pandas)
        columns_to_drop = ['Unnamed: 0']
        va_river_data.drop(columns_to_drop, inplace=True, axis=1)

        #add current_data_list as row at end of dataframe
        #if length of rows is > 100, drop first row of dataframe
        if va_river_data['Time Stamp'].count() > 100:
            va_river_data = va_river_data.drop(va_river_data.index[0])

        new_row = pd.Series(current_data_list, index=va_river_data.columns)
        va_river_data = va_river_data.append(new_row, ignore_index=True)

        #write data to 'rivers_csv' file
        va_river_data.to_csv('river_levels.csv')

        return va_river_data


    @staticmethod
    def make_plots(river_name, values):
        """Makes plot for each river's current water level.
        Min val is lowest recorded value of river. Max val is highest recorded value of river
        Red line depicts median water level
        Returns figure object, which is plotted in main module """

        fig, ax = plt.subplots()

        ax.set_title(river_name)
        ax.set_ylabel('Cubic Feet per Second (cfs)')
        ax.axhline(y=sum(values)/len(values), color='red', linestyle="--", label='Average Water Level')
        ax.legend()

        ax.set_ylim(min(values) * .95, max(values) * 1.05)

        return ax














        
        

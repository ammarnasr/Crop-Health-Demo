import geopandas as gpd
from senHub import SenHub
import rioxarray as rx
from shapely.geometry import Point
from math import isnan
import requests
import utils
from sentinelhub import  SHConfig
import main
import pipline
import process



clients=["FGM","MATO"]
year_list=[2020,2021]
metrics=["CAB","FCOVER","LAI","TRUECOLOR"]

##################################--This is Used to download all availabe data in given years and store them in azure--##################################
'''
TO DO: now it downloads data locally "the path is set inside Download_image_in_given_date() function",
INSTEAD  insert azure configration.

TO DO: make sure what kind of data to be stored? raw only or masked and processed?

'''


def batch_job(clients,year_list,metrics):
    '''
    clints: list of all clients currently.
    year_list: list of years in which data is required.
    metrics: list of the vegation indexes provided by the application.

    '''
    for clientName in clients:
        data_path = f'./clients/{clientName}.geojson'
        src_df = pipline.read_geodataframe(data_path)
        fields = main.get_list_of_fields(src_df)

        for metric in metrics:

            for field in fields:
                dates= main.get_user_selection_dates(field,year_list) 

                for date in dates:
                    process.Download_image_in_given_date(clientName, metric, src_df, field, date)
                    process.mask_downladed_image(clientName, metric, src_df, field, date)
                    process.convert_maske_image_to_geodataframe(clientName, metric, src_df, field, date, src_df.crs)

if __name__ == "__main__":
    batch_job(clients,year_list,metrics)
                







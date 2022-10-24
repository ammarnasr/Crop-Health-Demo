import process
import pipline
import utils
import geopandas as gpd
from datetime import datetime
import os
from senHub import SenHub
from sentinelhub import MimeType
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np



##################################--Set The Main Parameters: Client and dates--##################################
CONFIG = utils.parse_app_config()
clientName = CONFIG['ClientName']
data_path = f'./clients/{clientName}.geojson'
print(data_path)
src_df = pipline.read_geodataframe(data_path)
years_list = [2022, 2021]
start_date = CONFIG['StartDate']
end_date =  datetime.today().strftime('%Y-%m-%d')

##################################--Get Information about the Client--##################################
def get_list_of_fields(df=src_df):
    '''
    Returns a sorted list of field Ids for the client
    '''
    s = sorted(df['Field_Id'].unique())
    return s

def get_user_selection_dates(field_id, src_df = src_df, years_list= years_list, start_date=start_date, end_date=end_date):
    '''
    Return a list of Avilable dates for a specfic field ID
    '''
    dates = process.get_available_dates_for_field(src_df, field_id, start_date=start_date, end_date=end_date)
    return dates

##################################--Get Foluim Map of a vegation index for a field--##################################

def get_metric_for_field_figure(metric, date, field, m=None, vmin=None, vmax=None, cmap=None):
    '''
    Serach for a specfic geojson based on field id, metric and date then return a folium map.
    metric: Vegation index of the target image
    date: The Date in which the image was downloade 
    field: The Id of the field used to mask the image
    m: Optional folium map for the figure created to use it as base map
    '''
    df = get_cuarted_df_for_field(metric, date, field)
    return make_figure(df, metric, date, field, m=m, vmin=vmin,vmax=vmax, cmap=cmap)


def get_cuarted_df_for_field(metric, date, field):
    '''
    Serach for a specfic geojson based on field id, metric and date then retunt it's dataframe.
    metric: Vegation index of the target image
    date: The Date in which the image was downloade 
    field: The Id of the field used to mask the image
    '''
    curated_date_path, is_exist =  utils.get_curated_location_img_path(clientName, metric, date, field)
    if is_exist:
       df = pipline.read_geodataframe(curated_date_path)
       return df
    else:
        process.Download_image_in_given_date(clientName, metric, src_df, field, date)
        process.mask_downladed_image(clientName, metric, src_df, field, date)
        process.convert_maske_image_to_geodataframe(clientName, metric, src_df, field, date, src_df.crs)
        curated_date_path, is_exist =  utils.get_curated_location_img_path(clientName, metric, date, field)
        df = pipline.read_geodataframe(curated_date_path)
        return df

def make_figure(df, metric, date, field, m=None , vmin=None, vmax=None, cmap = None):
    '''
    Make The figure of folium map for the given geodataframe
    df: the data_source (Dataframe) from which the image is taken
    metric: Vegation index of the target image
    date: The Date in which the image was downloade 
    field: The Id of the field used to mask the image
    m: Optional folium map for the figure created to use it as base map
    '''
    title = f'{metric} for selected field no#{field} in {date}'
    if cmap is None:
        cmap = 'RdYlGn'
    print(f'for {metric} the min is {vmin} and max is {vmax} and cmap is {cmap}')
    m  = df.explore(
        column=f'{metric}_{date}',
        cmap=cmap,
        legend=True,
        vmin=vmin,
        vmax=vmax,
        m=m,
        marker_type='circle', marker_kwds={'radius':5.3, 'fill':True})
    return m, title, df
##################################--Get Foluim Map and Metrics for ALL Field--##################################

def get_location_choropleth(df=src_df):
    '''
    Creat a choropleth map for all the fields in the given data source.
    '''
    m = df.explore(
            column="Crop_Type", # make choropleth based on "BoroName" column
            tooltip=["Field_Id", "Crop_Type"], # show "BoroName" value in tooltip (on hover)
            popup=True, # show all values in popup (on click)
            tiles="CartoDB positron", # use "CartoDB positron" tiles
            cmap="Set1", # use "Set1" matplotlib colormap
            style_kwds=dict(color="black", fillOpacity=0.1)) # use black outline)     
    return m    

def get_avg_metric_vals_for_field_in_year(metric, field, year=years_list[0], df=src_df, clientName=clientName):
    '''
    Retruns:
    (1) A list of all the available data for a given year and field
    (2) A list of the avarage reading  for the selected metric and field in all the avilable dates
    df: the data_source (Dataframe) from which the image is taken
    metric: Vegation index of the target image
    date: The Date in which the image was downloade 
    field: The Id of the field used to mask the image
    m: Optional folium map for the figure created to use it as base map
    '''
    date_list = process.get_available_dates_for_field(df, field, year)
    xs = []
    ys = []
    for date in date_list:
        curated_date_path, is_exist =  utils.get_curated_location_img_path(clientName, metric, date, field)
        if is_exist:
            current_df = gpd.read_file(curated_date_path)
            ys.append(current_df[f'{metric}_{date}'].mean())
            xs.append(datetime.strptime(date, '%Y-%m-%d'))
        else:
            process.Download_image_in_given_date(clientName, metric, src_df, field, date)
            process.mask_downladed_image(clientName, metric, src_df, field, date)
            process.convert_maske_image_to_geodataframe(clientName, metric, src_df, field, date, src_df.crs)
            curated_date_path, is_exist2 =  utils.get_curated_location_img_path(clientName, metric, date, field)
            if is_exist2:
                current_df = gpd.read_file(curated_date_path)
                ys.append(current_df[f'{metric}_{date}'].mean())
                xs.append(datetime.strptime(date, '%Y-%m-%d'))


    return xs, ys



##################################--Get True Color Image--##################################

def get_True_color(metric, date, field, m=None, clientName=clientName, df=src_df):

    date_dir = f'./{clientName}/raw/{metric}/{date}/field_{field}/'
    utils.make_dir(f'{date_dir}')
    imagePath = ''
    is_exist = False
    if len(os.listdir(date_dir)) > 0:
        imagePath = f'{date_dir}{os.listdir(date_dir)[0]}/response.png'
        is_exist  = os.path.exists(imagePath)

    img = None
    if is_exist:
       img = img = mpimg.imread(imagePath)
    else:
        config = process.config
        path = f'./{clientName}/raw/{metric}/{date}/field_{field}/'
        bbox = utils.calculate_bbox(df, field)
        evalscript = utils.Scripts[metric]
        sen_obj = SenHub(config, mime_type = MimeType.PNG)
        sen_obj.set_dir(path)
        sen_obj.make_bbox(bbox)
        sen_obj.make_request(evalscript, date)
        img = sen_obj.download_data()
        img = img[0]

    image = img
    factor=3.5 / 255
    clip_range=(0, 1)
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(15, 15))
    ax.imshow(np.clip(image * factor, *clip_range))
    ax.set_xticks([])
    ax.set_yticks([])
    title = f'{metric} for selected field no#{field} in {date}'
    return fig , title

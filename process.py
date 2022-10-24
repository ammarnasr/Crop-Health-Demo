from tracemalloc import start
import geopandas as gpd
from senHub import SenHub
import rioxarray as rx
from shapely.geometry import Point
from math import isnan
import requests
import utils
from sentinelhub import  SHConfig

config = SHConfig()

config.instance_id      = "9dabbb4c-16a0-4d29-8699-90605775bc94"
config.sh_client_id     = "ae10e67d-8ce7-4a94-ae5e-42de12acca14"
config.sh_client_secret = "Ff:R!@OS5<nJrk,*%My%ZX]gy>[v%V,:y|dljVN:"

# config.instance_id      = "cb6710d9-89e6-4805-80e6-56874aa53f34"
# config.sh_client_id     = "c1210371-c926-43c9-bf96-877aa179c37e"
# config.sh_client_secret = "mi9w(#xfPMA>J5m(HeFBN8JHkTq4CRw?BjbwK3+E"

# config.instance_id      = "19e335ae-5825-448f-a6ea-0b5dbe5c6468"
# config.sh_client_id     = "d461cad2-4f66-4b15-92a0-8e5e28612d5e"
# config.sh_client_secret = "viGI~szLboIu)*Rpexo[qbk2uB[-dWX~DzK)W16z"


# config.instance_id      = "19e335ae-5825-448f-a6ea-0b5dbe5c6468"
# config.sh_client_id     = "d461cad2-4f66-4b15-92a0-8e5e28612d5e"
# config.sh_client_secret = "viGI~szLboIu)*Rpexo[qbk2uB[-dWX~DzK)W16z"
#ToDo: Set up the call for secrets so that it only runs once.
# config.instance_id      = utils.getSecret('SentinelHub-instanceid')
# config.sh_client_id     = utils.getSecret('SentinelHub-clientid')
# config.sh_client_secret = utils.getSecret('SentinelHub-clientsecret')

##################################--Getting The Dates--##################################
def get_dates(bbox, token, year=2022, start_date='', end_date=''):
    '''
    Make the request the get availabe dates (when there is sentinal-2 image) for a specific area
    bbox: bounding box of the tragted area
    token: token generated from sentinanlhub API.
    year: which year to get the dates from
    start_date: Optinal date to get the dates from requested day and month ins of the start of year
    end_date: Optinal date to get the dates to a rquested day and month instead of end of the year
    '''
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer '+ token,
    }
    if start_date == '' or end_date == '':
        data = f'{{ "collections": [ "sentinel-2-l2a" ], "datetime": "{year}-01-01T00:00:00Z/{year}-12-31T23:59:59Z", "bbox": {bbox}, "limit": 100, "distinct": "date" }}'
    else:
        print(f'we have {start_date} and {end_date}')
        data = f'{{ "collections": [ "sentinel-2-l2a" ], "datetime": "{start_date}T00:00:00Z/{end_date}T23:59:59Z", "bbox": {bbox}, "limit": 100, "distinct": "date" }}'
    response = requests.post('https://services.sentinel-hub.com/api/v1/catalog/search', headers=headers, data=data)
    return response.json()['features']

def get_available_dates_for_field(df, field, year=2022, start_date='', end_date=''):
    '''
    Get The Available Dates for a specfic field in a specific time period.
    '''
    bbox = utils.calculate_bbox(df, field)
    token = SenHub(config).token
    return get_dates(bbox, token, year, start_date, end_date)

##################################--Downloading The Image--##################################

def Download_image_in_given_date(clientName, metric, df, field, date):
    '''
    Download image of a specific field from the data source in given date.
    clientName: Name of the client for the data source used
    metric: Vegation index of the target image
    df: the data_source (Dataframe) from which the image is taken
    field: The Id of the field used to mask the image
    date: The Date in which the image was downloade 
    '''
    sen_obj = SenHub(config)
    sen_obj = set_download_path(sen_obj,clientName, metric, date, field)
    sen_obj = set_target_bbox(sen_obj, df, field)
    sen_obj = set_download_request(sen_obj, metric, date)
    sen_obj.download_data()
    return sen_obj.download_data()

def set_download_path(sen_obj,clientName, metric, date, field):
    '''
    Set the download path for a senHub Object based on passed parameters.
    sen_obj: The SenHub object.
    clientName: Name of the client for the data source used
    metric: Vegation index of the target image
    date: The Date in which the image was downloade 
    field: The Id of the field used to mask the image
    '''
    path = f'./{clientName}/raw/{metric}/{date}/field_{field}/'
    sen_obj.set_dir(path)
    return sen_obj

def set_target_bbox(sen_obj, df, field):
    '''
    Set the target bounding box for a senHub Object based on passed parameters.
    sen_obj: The SenHub object.
    df: the data_source (Dataframe) from which the image is taken
    field: The Id of the field used to mask the image
    '''
    bbox = utils.calculate_bbox(df, field)
    sen_obj.make_bbox(bbox)
    return sen_obj

def set_download_request(sen_obj, metric, date):
    '''
    Set the download Request for a senHub Object based on passed parameters.
    sen_obj: The SenHub object.
    metric: Vegation index of the target image
    date: The Date in which the image was downloade 
    '''
    evalscript = utils.Scripts[metric]
    sen_obj.make_request(evalscript, date)
    return sen_obj

##################################--Masking The Image--##################################

def mask_downladed_image(clientName, metric, df, field, date):
    '''
    Read, Mask and save the downloaded image based on the actual field in the data_source.
    clientName: Name of the client for the data source used
    metric: Vegation index of the target image
    df: the data_source (Dataframe) from which the image is taken
    field: The Id of the field used to mask the image
    date: The Date in which the image was downloade 
    '''
    download_path = utils.get_downloaded_location_img_path(clientName, metric, date, field)
    im = rx.open_rasterio(download_path)
    clipped = mask_image_as_tiff(im, df, field)
    s = save_masked_image(clipped, clientName, metric, date, field)
    return s

def mask_image_as_tiff(im, df, field):
    '''
    clip a given image based on a given field geometry
    im: Tiff image file as rioxarray
    df : the data_source (Dataframe) from which the image is taken
    field: The Id of the field used to mask the image
    '''
    pol = df.loc[df['Field_Id'] == field]
    clipped = im.rio.clip(pol.geometry, pol.crs, drop=True)
    return clipped

def save_masked_image(im, clientName ,metric, date, field):
    '''
    Save the masked image to disk in path based the parameters passed to the function
    im: Tiff image file as rioxarray
    clientName: Name of the client for the data source used
    metric: Vegation index of the target image
    field: The Id of the field used to mask the image
    date: The Date in which the image was downloade 
    '''
    savePath = f'./{clientName}/processed/{metric}/{date}/field_{field}/'
    utils.make_dir(savePath)
    im.rio.to_raster(savePath + 'masked.tiff')
    return savePath + 'masked.tiff'

##################################--Converting The Masked Image to GeoJSON--##################################

def convert_maske_image_to_geodataframe(clientName, metric, df, field, date, crs):
    '''
    Read, Convert and save the Masked image as geojson file.
    clientName: Name of the client for the data source used
    metric: Vegation index of the target image
    df: the data_source (Dataframe) from which the image is taken
    field: The Id of the field used to mask the image
    date: The Date in which the image was downloade 
    crs: The Refrencing system of concern
    '''
    gdf = sample_masked_image_as_geodataframe(clientName, metric, field, date, crs)
    s = save_masked_geodataframe_as_geojson(gdf,clientName, metric, date, field)
    return s

def tiff_to_geodataframe(im, metric, date, crs):
    ''' 
    Sample Pixles in a given masked image to row in a geodataframe
    im: Tiff image file as rioxarray
    metric: Vegation index of the target image
    date: The Date in which the image was downloade 
    crs: The Refrencing system of concern
    '''
    x_cords = im.coords['x'].values
    y_cords = im.coords['y'].values
    vals = im.values
    dims = vals.shape
    
    points = []
    v_s = []
    for lat in range(dims[1]):
        y = y_cords[lat]
        for lon in range(dims[2]):
            x = x_cords[lon]

            v = vals[:,lat,lon]
            if isnan(v[0]):
                continue
            points.append(Point(x,y))
            v_s.append(v.item())   
    d = {f'{metric}_{date}': v_s, 'geometry': points} 
    df = gpd.GeoDataFrame(d, crs = crs)
    return df

def sample_masked_image_as_geodataframe(clientName, metric, field, date, crs):
    '''
    Read and sample a masked tiff image to geodataframe
    clientName: Name of the client for the data source used
    metric: Vegation index of the target image
    field: The Id of the field used to mask the image
    date: The Date in which the image was downloade 
    crs: The Refrencing system of concern
    '''
    imagePath = utils.get_masked_location_img_path(clientName, metric, date, field)
    im = rx.open_rasterio(imagePath)
    return tiff_to_geodataframe(im, metric, date, crs)

def save_masked_geodataframe_as_geojson(df,clientName, metric, date, field):
    '''
    Save the masked geodataframe as geojson in path based on passed parameters
    df: the data_source (Dataframe) from which the image is taken
    clientName: Name of the client for the data source used
    metric: Vegation index of the target image
    date: The Date in which the image was downloade 
    field: The Id of the field used to mask the image
    '''
    savePath = f'./{clientName}/curated/{metric}/{date}/field_{field}/'
    utils.make_dir(savePath)
    df.to_file(savePath + 'masked.geojson', driver='GeoJSON')
    return savePath + 'masked.geojson'

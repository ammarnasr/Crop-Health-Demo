import os
import matplotlib.pyplot as plt
import folium
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
import confuse

# Initialzie custom basemaps for folium
basemaps = {
    'Google Maps': folium.TileLayer(
        tiles = 'https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
        attr = 'Google',
        name = 'Google Maps',
        overlay = True,
        control = True
    ),
    'Google Satellite': folium.TileLayer(
        tiles = 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr = 'Google',
        name = 'Google Satellite',
        overlay = True,
        control = True
    ),
    'Google Terrain': folium.TileLayer(
        tiles = 'https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}',
        attr = 'Google',
        name = 'Google Terrain',
        overlay = True,
        control = True
    ),
    'Google Satellite Hybrid': folium.TileLayer(
        tiles = 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr = 'Google',
        name = 'Google Satellite',
        overlay = True,
        control = True
    ),
    'Esri Satellite': folium.TileLayer(
        tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr = 'Esri',
        name = 'Esri Satellite',
        overlay = True,
        control = True
    ),
    'openstreetmap': folium.TileLayer('openstreetmap'),
    'cartodbdark_matter': folium.TileLayer('cartodbdark_matter')
}

# Open and Read The Javascripts that will be passed to the SentinelHub API
with open('./scripts/cab.js') as f:
    evalscript_cab = f.read()
with open('./scripts/fcover.js') as f:
    evalscript_fcover = f.read()
with open('./scripts/lai.js') as f:
    evalscript_lai = f.read()
with open('./scripts/truecolor.js') as f:
    evalscript_truecolor = f.read()
with open('./scripts/clp.js') as f:
    evalscript_clp = f.read()

# Dictionry of JavaScript files
Scripts = {
    'CAB': evalscript_cab,
    'FCOVER': evalscript_fcover,
    'LAI': evalscript_lai,
    'TRUECOLOR': evalscript_truecolor,
    'CLP': evalscript_clp
}

def calculate_bbox(df, field):
    '''
    Calculate the bounding box of a specfic field  ID in a  given data frame
    '''
    field = int(field)
    bbox = df.loc[df['Field_Id'] == field].bounds
    r = bbox.iloc[0]
    return [r.minx, r.miny, r.maxx, r.maxy]

def get_downloaded_location_img_path(clientName, metric, date, field):
    '''
    Get the path of the downloaded image in TIFF based on the:
    clientName: The data source of concern
    metric : The vegation index of concern
    date: the date tragted
    field: the id of the field in the specifed data source
    '''
    date_dir = f'./{clientName}/raw/{metric}/{date}/field_{field}/'
    imagePath = f'{date_dir}{os.listdir(date_dir)[0]}/response.tiff'
    return imagePath

def get_masked_location_img_path(clientName, metric, date, field):
    '''
    Get the path of the downloaded image after applying the mask in TIFF based on the:
    clientName: The data source of concern
    metric : The vegation index of concern
    date: the date tragted
    field: the id of the field in the specifed data source
    '''
    date_dir = f'./{clientName}/processed/{metric}/{date}/field_{field}/'
    imagePath = date_dir + 'masked.tiff'
    return imagePath

def get_curated_location_img_path(clientName, metric, date, field):
    '''
    Get the path of the downloaded image after applying the mask and converting it to geojson formay based on the:
    clientName: The data source of concern
    metric : The vegation index of concern
    date: the date tragted
    field: the id of the field in the specifed data source
    '''
    date_dir = f'./{clientName}/curated/{metric}/{date}/field_{field}/'
    imagePath = date_dir + 'masked.geojson'

    return imagePath, os.path.exists(imagePath)

def make_dir(path):
    '''
    Make a directory in the specified path
    '''
    os.makedirs(path, exist_ok=True)

def make_figure(h, w, rows, cols):
    '''
    Make a figure base on :
    h: height of figure
    w: width of figure
    rows: number of subplots in the figure
    cols: number of columns in the figure
    '''
    fig,ax = plt.subplots(rows, cols, figsize=(w, h))
    return fig, ax

def getSecret(secretName):
    '''
    Get a secret Value from the Azure Valut
    '''
    keyVaultName = os.environ["KEY_VAULT_NAME"]
    KVUri = f"https://{keyVaultName}.vault.azure.net"
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=KVUri, credential=credential)
    retrived_secret = client.get_secret(secretName)
    return retrived_secret._value

def parse_app_config(path=r'config-fgm-dev.yaml'):
    config = confuse.Configuration('CropHealth', __name__)
    config.set_file(path)
    return config
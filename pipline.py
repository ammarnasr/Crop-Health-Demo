import geopandas as gpd
import rioxarray as rx
import process


def read_geodataframe(imagePath):
    """
    Read geodataframe from a given path.
    """
    return gpd.read_file(imagePath)

def read_downloade_tiff_image(imagePath):
    """
    Read tiff file from a given path.
    """
    im = rx.open_rasterio(imagePath)
    return im

def download_image(metric, df, field, date):
    '''
    Download image of a specific field from the data source in given date.
    metric: Vegation index of the target image
    df: the data_source (Dataframe) from which the image is taken
    field: The Id of the field used to mask the image
    date: The Date in which the image was downloade 
    '''
    process.Download_image_in_given_date(metric, df, field, date)

def create_masked_tiff(metric, df, field, date):
    '''
    Mask a Downloaded TIFF image of a specific field from the data source in given date.
    metric: Vegation index of the target image
    df: the data_source (Dataframe) from which the image is taken
    field: The Id of the field used to mask the image
    date: The Date in which the image was downloade 
    '''
    imgPath = process.get_downloaded_location_img_path(metric, date, field)
    im = read_downloade_tiff_image(imgPath)
    im_masked = process.mask_image_as_tiff(im, df, field)
    process.save_masked_image(im_masked, metric, date, field)

def create_masked_geojson(metric, df, field, date):
    '''
    Convert a Masked TIFF image of a specific field from the data source in given date to GeoJSON format.
    metric: Vegation index of the target image
    df: the data_source (Dataframe) from which the image is taken
    field: The Id of the field used to mask the image
    date: The Date in which the image was downloade 
    '''
    metric_gdf = process.sample_masked_image_as_geodataframe(metric, field, date, df.crs)
    process.save_masked_geodataframe_as_geojson(metric_gdf, metric, date, field)

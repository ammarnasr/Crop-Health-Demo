import pipline
import main
import process
import utils
from datetime import datetime

##################################--Set The Main Parameters: Clients, metrics and year--##################################

current_year = [datetime.today().year]
clients =["sugar", "FGM",  "MATO", "qadarif"]
metrics =["LAI", "FCOVER","CLP", "CAB" ]


def daily_job(clients, current_year, metrics):
    '''
    Daily checks to see whether a new image of a field is available for any of the clients, and if so, downloads, masks, and converts it
    clients: a list of all the current clients
    current_year: Ongoing year, will be utilized to obtain all the dates for which a field image is available during that year
    metrics: Vegation indices of the target image

    '''
    for clientName in clients:

        data_path= f'./clients/{clientName}.geojson'
        src_df= pipline.read_geodataframe(data_path)
        fields= main.get_list_of_fields(src_df)
        
        for metric in metrics: 

            for field in fields:
                
                dates= main.get_user_selection_dates(field, src_df, current_year)
                today= datetime.today().strftime("%Y-%m-%d")

##################################--Checks if the current date belongs to the list of dates in which that particular field has an image--##################################

                if today in dates:
                    process.Download_image_in_given_date(clientName, metric, src_df, field, today)
                    process.mask_downladed_image(clientName, metric, src_df, field, today)
                    process.convert_maske_image_to_geodataframe(clientName, metric, src_df, field, today, src_df.crs)
                else:
                    print(f"No image found for client ({clientName}) under date {today}, field {field} and metric {metric}")

if __name__ == "__main__":    
    daily_job(clients, current_year, metrics)



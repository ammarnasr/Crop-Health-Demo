import streamlit as st
from streamlit_folium import st_folium
import main 
import utils
import pipline
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from scipy import signal
from datetime import datetime
import os
from zipfile import ZipFile



CONFIG = utils.parse_app_config()
##################################--Set & Calculate The LAI Parameters--##################################
metric = 'LAI'
Data_Path = main.data_path
src_df = pipline.read_geodataframe(Data_Path)
field_id_map = {}
field_name_map = {}
for i in range(len(src_df)):
    field_id_map[str(i)] =  src_df.iloc[i].Field_Id
    field_name_map[str(i)] =  src_df.iloc[i].Crop_Type
choropleth_map = main.get_location_choropleth()

def app():
    f_id = -1
    
    @st.cache()
    def get_and_cache_available_dates(field_id, Data_Path, today):
        print(f'Caching Dates for {field_id} in {Data_Path} on {today}')
        dates = main.get_user_selection_dates(field_id)
        dates.append(-1)
        return dates



    

##################################--Initlize The Page--##################################
    st.title(f"{metric} Analysis")
    with st.sidebar:
        st.title(f'{CONFIG["APP"]["Name"].get()}')
        report_caption = f'''
        {CONFIG["Client"]["Name"].get()} Dashboard v{CONFIG["appSemanticVersion"].get()}
        '''
        st.image(CONFIG["Client"]["Logo"].get(), caption=report_caption)
        st.image(CONFIG["APP"]["LAI"].get())
    col1, col2 = st.columns(2)
    with col1:
        utils.basemaps['openstreetmap'].add_to(choropleth_map)
        st_data = st_folium(choropleth_map, width = 500, height = 200)
    with col2:
        field_names = list(field_name_map.values())
        keys_list = list(field_name_map.keys())
        field_names.append('None')
        field_name = st.selectbox("Check Field (or click on the map)",field_names, index=len(field_names)-1)

        if field_name != 'None':
            a = keys_list[field_names.index(field_name)]
            f_id = field_id_map[a]
            st.write(f'You selected {field_name}')
    
    
##################################--Select A Field and a date--##################################
    date = -1
    if (st_data['last_active_drawing'] != None):
        f_id = st_data['last_active_drawing']['id']
        f_id = field_id_map[f_id]
        st.write(f"Field Selected : {f_id}")
        today =  datetime.today().strftime('%Y-%m-%d')
        dates = get_and_cache_available_dates(f_id, Data_Path, today)
        date = st.selectbox('Select Observation Date: ', dates, index=len(dates)-1)
        st.write('You selected:', date)
    elif f_id != -1 :
        st.write(f"Field Selected : {f_id}")
        today =  datetime.today().strftime('%Y-%m-%d')
        dates = get_and_cache_available_dates(f_id, Data_Path, today)
        date = st.selectbox('Select Observation Date: ', dates, index=len(dates)-1)
        st.write('You selected:', date)
    else:
        st.write('Please Select A Field')

##################################--Plot  A Field map and add download links--##################################
    if (date != -1) and (f_id != -1):   
        fig, title, df_Metric = main.get_metric_for_field_figure(metric, date, f_id)
        
        clp_df = main.get_cuarted_df_for_field('CLP', date, f_id)
        avg_clp = clp_df[f'CLP_{date}'].mean() *100

        if avg_clp > 80:
            st.warning(f'⚠️ The Avarage Cloud Cover is {avg_clp}%')
            st.info('Please Select A Different Date')
        else:
            st.write(title)
            utils.basemaps['Google Satellite'].add_to(fig)
            # st.pyplot(fig, width = 725)
            a = df_Metric.columns[0]
            x = df_Metric[a].describe()
            
            col1, col2 = st.columns([1,3])
            with col1:
                st.write(x)
            with col2:
                st_folium(fig, width = 725)



            if len(df_Metric) > 0:
                col1, col2 = st.columns(2)
                with col1:
                    shapefilename = f"{f_id}_{metric}"
                    extension = 'shp'
                    path = f'./shapefiles/{f_id}/{metric}/{extension}'
                    utils.make_dir(path)
                    df_Metric.to_file(f'{path}/{shapefilename}.{extension}')
                    files = []
                    for i in os.listdir(path):
                        if os.path.isfile(os.path.join(path,i)):
                            if i[0:len(shapefilename)] == shapefilename:
                                files.append(os.path.join(path,i))
                    zipFileName = f'{path}/data.zip'
                    zipObj = ZipFile(zipFileName, 'w')
                    for file in files:
                        zipObj.write(file)
                    zipObj.close()
                    with open(zipFileName, 'rb') as f:
                        st.download_button('Download as ShapeFile', f,file_name=zipFileName)

                with col2:
                    filename = utils.get_masked_location_img_path(main.clientName, metric, date, f_id)
                    donwnload_filename = f'{metric}_{f_id}_{date}.tiff'
                    with open(filename, 'rb') as f:
                        st.download_button('Download as Tiff File', f,file_name=donwnload_filename)

##################################--Expriment--##################################

    

##################################--Plot Historic Avarages--##################################
    options_list = ['YES', 'NO']
    display_historic_avgs = st.selectbox('Do you want to show Historic avrages? : ', options_list, index=1)
    selected_f_ids = []
    
    if display_historic_avgs == 'YES':
        options = st.multiselect('Select Field(s) For Historic Comparison', field_names)
        if len(options) > 0:
            for o in options:
                a= keys_list[field_names.index(o)]
                selected_f_ids.append(field_id_map[a])
        
        done = st.checkbox('Click Here when done')
        if done:
            my_bar2 = st.progress(0)
            status_text = st.empty()

            my_bar = st.progress(0)
            today =  datetime.today().strftime('%Y-%m-%d')
            historic_avarage_plot = make_subplots(specs=[[{"secondary_y": True}]])
            status_text_date = st.empty()

            
            for row_fid in selected_f_ids:
                status_text.text(f'Calculating Value for Field {row_fid}')
                xs, ys = [],[]
                dates = get_and_cache_available_dates(row_fid, Data_Path, today)
                
                for i in range(len(dates)-1):
                    status_text_date.text(f'{dates[i]}...')
                    current_df = main.get_cuarted_df_for_field(metric, dates[i], row_fid)
                    avg_val = current_df[f'{metric}_{dates[i]}'].mean()
                    xs.append(dates[i])
                    ys.append(avg_val)
                    my_bar.progress((i + 1)/(len(dates)-1))
                ys = signal.savgol_filter(ys,7, 3)
                historic_avarage_plot.add_trace(go.Scatter(x=xs, y=ys, name=f"Field {row_fid} data"), secondary_y=True)
                my_bar2.progress((selected_f_ids.index(row_fid)+ 1)/(len(selected_f_ids)))

            st.plotly_chart(historic_avarage_plot, use_container_width=True)


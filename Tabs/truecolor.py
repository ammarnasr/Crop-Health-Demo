import streamlit as st
from streamlit_folium import st_folium
import main 
import pipline
import os
import utils
from datetime import datetime



CONFIG = utils.parse_app_config()
###################################--Set & Calculate The TRUECOLOR Parameters--##################################
metric = 'TRUECOLOR'
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
    @st.cache_data()
    def get_and_cache_available_dates(field_id, Data_Path, today):
        print(f'Caching Dates for {field_id} in {Data_Path} on {today}')
        dates = main.get_user_selection_dates(field_id)
        dates.append(-1)
        return dates


    

##################################--Initlize The Page--##################################
    st.title(f"TRUECOLOR Analysis")
    with st.sidebar:
        st.title(f'{CONFIG["APP"]["Name"].get()}')
        report_caption = f'''
        {CONFIG["Client"]["Name"].get()} Dashboard v{CONFIG["appSemanticVersion"].get()}
        '''
        st.image(CONFIG["Client"]["Logo"].get(), caption=report_caption)
        st.image(CONFIG["APP"]["LAI"].get())
        
    col1, col2 = st.columns(2)
    with col1:
        # utils.basemaps['openstreetmap'].add_to(choropleth_map)
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
        fig, title = main.get_True_color(metric, date, f_id)
        st.write(title)
        st.pyplot(fig)
        date_dir = f'./{main.clientName}/raw/{metric}/{date}/field_{f_id}/'
        donwnload_filename = f'{date_dir}{os.listdir(date_dir)[0]}/response.png'
        with open(donwnload_filename, 'rb') as f:
            st.download_button('Download as PNG File', f,file_name=donwnload_filename)
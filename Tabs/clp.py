import streamlit as st
from streamlit_folium import st_folium
import main 
import utils
import pipline


m = main.get_location_choropleth()
metric = 'CLP'
src_df = pipline.read_geodataframe(main.data_path)
temp_map = {}
for i in range(len(src_df)):
    temp_map[str(i)] =  src_df.iloc[i].Field_Id


def app():
    date = -1
    st.title(f"CLP Analysis")
    with st.sidebar:
        st.title(f'CLP')
    
    st_data = st_folium(m, width = 500, height = 200)
    if st_data['last_active_drawing'] != None :
        f_id = st_data['last_active_drawing']['id']
        f_id = temp_map[f_id]
        st.write(f"Field Selected : {f_id}")
        dates = main.get_user_selection_dates(f_id)
        dates.append(-1)
        date = st.selectbox('Select Observation Date: ', dates, index=len(dates)-1)
        st.write('You selected:', date)
    else:
        st.write('Please Select A Field')

    if (date != -1) and (f_id != -1):
        
        
        fig, title = main.get_metric_for_field_figure(metric, date, f_id)
        st.write(title)
        # utils.basemaps['Google Satellite'].add_to(fig)
        st_folium(fig, width = 725)

        
        filename = utils.get_masked_location_img_path(main.clientName, metric, date, f_id)
        donwnload_filename = f'{metric}_{f_id}_{date}.tiff'
        with open(filename, 'rb') as f:
            st.download_button('Download as Tiff File', f,file_name=donwnload_filename)
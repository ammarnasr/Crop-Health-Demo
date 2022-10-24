import streamlit as st
from streamlit_folium import st_folium
from main import get_location_choropleth, data_path
import utils
import pipline



CONFIG = utils.parse_app_config()
choropleth_map = get_location_choropleth()
src_df = pipline.read_geodataframe(data_path)
utils.basemaps['Google Satellite'].add_to(choropleth_map)
def app():
    st.title("Crop Monitoring")  
    with st.container():
        st_data = st_folium(choropleth_map, width = 725, height = 450)
    with st.sidebar:
        st.title(f'{CONFIG["APP"]["Name"].get()}')
        report_caption = f'''
        {CONFIG["Client"]["Name"].get()} Dashboard v{CONFIG["appSemanticVersion"].get()}
        '''
        st.image(CONFIG["Client"]["Logo"].get(), caption=report_caption)
        # src_df.columns = ['Location','Year', 'Crop Type', 'Field ID', 'Geometry']
    st.write(src_df)
    
        
        
    
  
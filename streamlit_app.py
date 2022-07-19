from turtle import width
import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_assets.components import User

# PAGE SETUP
st.set_page_config(
    page_title="SpotiMy",
    layout="wide",
    page_icon="streamlit_assets/assets/app_logo.png",

)


# From https://discuss.streamlit.io/t/how-to-center-images-latex-header-title-etc/1946/4
with open("streamlit_assets/style.css") as f:
    st.markdown("""<link href='http://fonts.googleapis.com/css?family=Roboto:400,100,100italic,300,300italic,400italic,500,500italic,700,700italic,900italic,900' rel='stylesheet' type='text/css'>""", unsafe_allow_html=True)
    st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)


left_column, center_column1, center_column2, right_column = st.columns([1,1,1,1])

with left_column:
    st.info("Project using streamlit")
with right_column:
    st.write("##### Authors\nThis tool has been developed by [Emile D. Esmaili](https://github.com/emileDesmaili)")
with center_column1:
    st.image("streamlit_assets/assets/app_logo.png", width=120)
with center_column2:
    st.markdown('# SpotiMy')



st.sidebar.write(f'# Welcome')

page_container = st.sidebar.container()
with page_container:
    page = option_menu("Menu", ["Top Tracks", "Playlists"], 
    icons=['reddit','dpad'], menu_icon="cast", default_index=0, orientation="vertical")


user = User()
user.get_playlists()

selection = st.selectbox('Select Playlist',user.playlists.keys())
selected_playlist = user.playlists[selection]

df = user.get_playlist_df(selected_playlist)
col1, col2 = st.columns(2)
with col1:
    user.plot_radar(df)
with col2:
    user.get_wordcloud(df)
    metric = st.selectbox('Select metric',['danceability','energy','speechiness','acousticness','instrumentalness','liveness','valence','mode'])
    user.plot_tracks(df,metric)


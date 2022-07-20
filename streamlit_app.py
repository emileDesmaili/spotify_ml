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
    icons=['spotify','skip-end-circle'], menu_icon="cast", default_index=0, orientation="vertical")

if page == 'Top Tracks':
    user = User()
    df = user.get_playlist_df(playlist_id='top tracks')

    col1, col2 = st.columns(2)
    with col1:
        st.write('### Playlist Audio Features')
        user.plot_radar(df)
    with col2:
        st.write('### Artists')
        user.get_wordcloud(df)

    col3, col4 = st.columns([1,2])
    with col3:
        st.write('### Songs Visualizer')
        metric = st.selectbox('Select metric',['danceability','energy','speechiness','acousticness','instrumentalness','liveness','valence','mode'])
        k = st.slider('Select number of clusters',1,10,step=1,value=5)
    with col4:
        user.plot_tracks(df,metric,k)

if page == 'Playlists':

    user = User()
    user.get_playlists()

    selection = st.selectbox('Select Playlist',user.playlists.keys())
    selected_playlist = user.playlists[selection]
    if selected_playlist not in st.session_state:
    #     session_str = 'df'+selected_playlist
        st.session_state[selected_playlist] = user.get_playlist_df(selected_playlist)

    df = st.session_state[selected_playlist].copy()



    col1, col2 = st.columns(2)
    with col1:
        st.write('### Playlist Audio Features')
        user.plot_radar(df)
    with col2:
        st.write('### Artists')
        user.get_wordcloud(df)

    col3, col4 = st.columns([1,2])
    with col3:
        st.write('### Songs Visualizer')
        metric = st.selectbox('Select metric',['danceability','energy','speechiness','acousticness','instrumentalness','liveness','valence','mode'])
        k = st.slider('Select number of clusters',1,10,step=1,value=5)
    with col4:
        user.plot_tracks(df,metric,k)


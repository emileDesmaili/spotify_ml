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
    page = option_menu("Menu", ["Top Tracks", "Playlists","Recommendations"], 
    icons=['speaker','skip-end-circle','lightbulb'], menu_icon="spotify", default_index=0, orientation="vertical")

if page == 'Top Tracks':
    user = User()
    time_dict = {"Short Term":'short_term',"Medium Term":'medium_term','Long Term':'long_term'}
    selection= st.selectbox('Select time range',time_dict.keys())
    time_range = time_dict[selection]
    df = user.get_playlist_df(playlist_id='top tracks', time_range=time_range)
    st.write('# Your Top Tracks')
    user.display_tracks(df,n=6)

    user.display_metrics(df)

if page == 'Playlists':

    user = User()
    user.get_playlists()

    selection = st.selectbox('Select Playlist',user.playlists.keys())
    selected_playlist = user.playlists[selection]
    if selected_playlist not in st.session_state:
    #     session_str = 'df'+selected_playlist
        st.session_state[selected_playlist] = user.get_playlist_df(selected_playlist)

    df = st.session_state[selected_playlist].copy()

    user.display_metrics(df)


if page =='Recommendations':

    user = User()
    user.get_playlists()
    bases = user.playlists
    bases['Top Tracks'] ='top tracks'
    selection = st.selectbox('Base my recommendations on: ',bases.keys())
    base = bases[selection]

    df = user.get_recos_df(base)
    st.write('# Your Recommendations')
    n=6
    user.display_tracks(df,n=n)
    user.display_tracks(df[n:],n=n)

    user.display_metrics(df)





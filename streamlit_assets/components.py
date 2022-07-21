import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import streamlit as st
import concurrent.futures
import streamlit.components.v1 as components

class User:

    def __init__(self):
        self.client_id = 'aa3b040fe8a14f47babd5211bc20f4c8' 
        self.secret_id = '7274e34729fc407d9f0bef405fd24805'
        self.redirect_uri = 'http://localhost:8000/callback'
        self.scope = "user-library-read, playlist-read-private, user-read-private, user-read-playback-state, user-top-read, user-follow-read, user-read-currently-playing, user-read-recently-played"
        self.auth_manager = SpotifyOAuth(client_id=self.client_id, client_secret=self.secret_id, redirect_uri=self.redirect_uri, scope=self.scope, open_browser=False)
        self.auth_url = self.auth_manager.get_authorize_url()
        
        st.write(f'<h2><a href="{self.auth_url}">Sign in</a></h2>', unsafe_allow_html=True)
        
        self.sp = spotipy.Spotify(auth_manager=self.auth_manager)
    
    @staticmethod
    def get_wordcloud(df):
        text = " ".join(i for i in df['artist'].str.replace(' ',''))
        stopwords = list(set(STOPWORDS))
        wordcloud = WordCloud(stopwords=stopwords, background_color=None,mode='RGBA', colormap='cool', width=600, height=300,
                     font_path='streamlit_assets/fonts/BRITANIC.ttf').generate(text)
        st.image(wordcloud.to_array())
    
    def get_playlists(self):
        playlists = self.sp.current_user_playlists()
        playlist_names = []
        playlist_ids = []
        for pl in playlists['items']:
            playlist_ids.append(pl['id'])
            playlist_names.append(pl['name'])
        self.playlists = dict(zip(playlist_names,playlist_ids))
    
    def get_features(self, item):     
        track = item['name']
        uri = item['uri']
        artist = item['artists'][0]['name']
        album_cover = item['album']['images'][1]['url']
        preview = item['preview_url']
        popularity = item['popularity']
        features = self.sp.audio_features(uri)[0]
        danceability = features['danceability']
        energy = (features['energy'])
        key = (features['key'])
        loudness= (features['loudness'])
        mode = (features['mode'])
        speechiness = (features['speechiness'])
        acousticness = (features['acousticness'])
        instrumentalness = (features['instrumentalness'])
        liveness = (features['liveness'])
        valence = (features['valence'])
        tempo = (features['tempo'])
        return list([uri,track,artist,album_cover, preview, popularity,danceability,energy,key,loudness,mode,speechiness,acousticness,instrumentalness,liveness,valence,tempo])
    

    def get_playlist_df(self, playlist_id, time_range='short_term', seed_tracks=None):
        
        if playlist_id =='top tracks': 
            tracks = self.sp.current_user_top_tracks(limit=50, time_range=time_range)
            tracklist = []
            for idx, item in enumerate(tracks['items']):
                tracklist.append(item)
        elif playlist_id =='recos':
            tracks = self.sp.recommendations(seed_tracks=seed_tracks, limit=20)
            tracklist = []
            for idx, item in enumerate(tracks['tracks']):
                tracklist.append(item)
        else:
            tracks = self.sp.playlist(playlist_id)
            tracklist = []
            for idx, item in enumerate(tracks['tracks']['items']):
                tracklist.append(item['track'])

        
        MAX_THREADS = 100
        threads = min(MAX_THREADS, len(tracklist))

        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            features = executor.map(self.get_features, tracklist)

        df = pd.DataFrame(features, columns=['id','name','artist','album_cover','preview','popularity' ,
                                        'danceability','energy','key','loudness','mode','speechiness','acousticness',
                                        'instrumentalness','liveness','valence', 'tempo'])
        return df

    def get_recos_df(self,base):
        base_df = self.get_playlist_df(playlist_id=base)
        seed_tracks = list(base_df['id'].values)[:4]
        df = self.get_playlist_df(playlist_id='recos', seed_tracks=seed_tracks)
        return df

    
    def plot_radar(self,df):
        mean_df = df.mean(axis=0)
        radar_df = mean_df.filter(items=['danceability','energy','speechiness','acousticness','instrumentalness','liveness','valence','mode',])
        fig = px.bar_polar(radar_df, r=radar_df.values, theta=radar_df.index, 
                        range_r = [], color=radar_df.index,
                        color_discrete_sequence=px.colors.qualitative.Plotly,
                        template='plotly_dark')
        fig.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)")

        st.plotly_chart(fig)
    
    def plot_tracks(self, df,size,k):
        X = np.array(df.drop(['id','name','artist','preview','album_cover','popularity','key','mode'], axis=1))

        kmeans = KMeans(n_clusters=k, random_state=42)
        df['cluster'] = kmeans.fit_predict(X)

        X_proj = TSNE(n_components=2, learning_rate='auto',
                        init='random', random_state=42).fit_transform(X)

        df['X'] = [item[0] for item in X_proj]
        df['Y'] = [item[1] for item in X_proj]

        #plots
        df['cluster_str'] = df['cluster'].astype(str)
        df['track_str'] = df['name'] + " - " + df['artist']

        hover_dict = {'X':False,'Y':False,'cluster':False,size:False, 'cluster_str':False}

        fig = px.scatter(df,x='X',y='Y',color='cluster_str',size=size, template='plotly_dark', hover_name="track_str", hover_data=hover_dict,
                        color_discrete_sequence=px.colors.qualitative.Plotly)
        #legend
        fig.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)")
        #x axis
        fig.update_xaxes(visible=False)

        #y axis    
        fig.update_yaxes(visible=False)
        st.plotly_chart(fig, use_container_width=True)
    
    def display_tracks(self,df,n=5):
        
        columns = st.columns(n)
        for a, x in enumerate(columns):
            with x:
                name = df['name'].iloc[a]
                artist = df['artist'].iloc[a]
                cover = df['album_cover'].iloc[a]
                preview = df['preview'].iloc[a]
                st.write(f'**{name}**' +" - " +artist)
                st.image(cover)
                st.audio(preview, format='audio/ogg')

    def display_metrics(self,df):
        col1, col2 = st.columns(2)
        with col1:
            st.write('### Audio Features')
            self.plot_radar(df)
        with col2:
            pop = str(round(df['popularity'].mean()))
            st.write('#### Average Popularity: ' + f'{pop}')
            st.write('### Artists')
            self.get_wordcloud(df)
            

        col3, col4 = st.columns([1,3])
        with col3:
            st.write('### Songs Visualizer')
            metric = st.selectbox('Select metric',['danceability','energy','speechiness','acousticness','instrumentalness','liveness','valence'])
            k = st.slider('Select number of clusters',1,10,step=1,value=5)
        with col4:
            self.plot_tracks(df,metric,k)






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

class User:

    def __init__(self):
        self.client_id = 'aa3b040fe8a14f47babd5211bc20f4c8' 
        self.secret_id = '7274e34729fc407d9f0bef405fd24805'
        self.redirect_uri = 'http://localhost:3005/callback/'
        self.scope = "user-library-read, playlist-read-private, user-read-private, user-read-playback-state, user-top-read, user-follow-read, user-read-currently-playing, user-read-recently-played"
        self.auth_manager = SpotifyOAuth(client_id=self.client_id, client_secret=self.secret_id, redirect_uri=self.redirect_uri, scope=self.scope)
        self.sp = spotipy.Spotify(auth_manager=self.auth_manager)
    
    @staticmethod
    def get_wordcloud(df):
        text = " ".join(i for i in df['artist'].str.replace(' ',''))
        stopwords = list(set(STOPWORDS))
        wordcloud = WordCloud(stopwords=stopwords, background_color=None,mode='RGBA', colormap='spring', width=600, height=300,
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
    

    def get_playlist_df(self, playlist_id):
        playlist = self.sp.playlist(playlist_id)
        artists = []
        track_names = []
        track_ids = []
        danceability = []
        energy = []
        key = []
        loudness = []
        mode = []
        speechiness = []
        acousticness = []
        instrumentalness = []
        liveness = []
        valence = []
        tempo = []
        
        for idx, item in enumerate(playlist['tracks']['items']):
            track = item['track']['name']
            id = item['track']['id']
            artist = item['track']['artists'][0]['name']
            
            artists.append(artist)
            track_names.append(track)
            track_ids.append(id)
            features = self.sp.audio_features(id)[0]
            danceability.append(features['danceability'])
            energy.append(features['energy'])
            key.append(features['key'])
            loudness.append(features['loudness'])
            mode.append(features['mode'])
            speechiness.append(features['speechiness'])
            acousticness.append(features['acousticness'])
            instrumentalness.append(features['instrumentalness'])
            liveness.append(features['liveness'])
            valence.append(features['valence'])
            tempo.append(features['tempo'])

        df = pd.DataFrame(list(zip(track_ids,track_names,artists, 
                            danceability,energy,key,loudness,mode,speechiness,acousticness,instrumentalness,liveness, valence, tempo)), 
                            columns=['id','name','artist', 'danceability','energy','key','loudness','mode','speechiness','acousticness',
                            'instrumentalness','liveness','valence', 'tempo'])
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
        X = np.array(df.drop(['id','name','artist'], axis=1))

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








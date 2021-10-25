#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import folium
import streamlit as st
from streamlit_folium import folium_static
from pandas import json_normalize


# In[2]:


datavelobordeaux_url=("https://data.bordeaux-metropole.fr/geojson?key=17AEIIMYZZ&typename=ci_vcub_p")
datavelobordeaux=pd.read_json(datavelobordeaux_url)
dfvelobordeaux = json_normalize(datavelobordeaux['features'])
lat, long = [], []
for i in range(len(dfvelobordeaux)):
    lat.append(dfvelobordeaux['geometry.coordinates'][i][1])
    long.append(dfvelobordeaux['geometry.coordinates'][i][0])
dfvelobordeaux['Lat'] = lat
dfvelobordeaux['Long'] = long
col_suppr=['type', 'geometry.type', 'properties.gid',
           'properties.geom_o', 'properties.geom_err', 'properties.ident',
           'properties.cdate', 'properties.mdate', 'geometry.coordinates']
dfvelobordeaux.drop(col_suppr, axis=1, inplace=True)
dfvelobordeaux = dfvelobordeaux.rename(columns={'properties.type':'type', 'properties.nom':'nom', 'properties.etat':'etat',
       'properties.nbplaces':'nbplaces', 'properties.nbvelos':'nbvelos', 'properties.nbelec':'nbelec',
       'properties.nbclassiq':'nbclassiq'})


# In[3]:


dfadrBOD=pd.read_csv('./adresses_BOD.csv')


# In[4]:


st.set_page_config(page_title=' Vélos libre-service ', page_icon=None, layout='wide', initial_sidebar_state='auto')
st.title('Vélos libre-service Bordeaux')
st.write('Sélectionner votre adresse')
choix = st.slider(label='Choisissez le nombre de stations à afficher', min_value=1, max_value=10, value=3)
commune = st.selectbox(label='Choisissez la commune', options=dfadrBOD['commune'].sort_values().unique())
voie = st.selectbox(label='Choisissez le type de voie', options=dfadrBOD[dfadrBOD['commune']==commune]['Voie'].sort_values().unique())
rue = st.selectbox(label='Choisissez le nom de la voie', options=dfadrBOD[(dfadrBOD['commune']==commune) & (dfadrBOD['Voie']==voie)]['nom_voie'].sort_values().unique())
numero = st.selectbox(label='Choisissez le numéro dans la voie', options=dfadrBOD[(dfadrBOD['commune']==commune) & (dfadrBOD['nom_voie']==rue)]['numero'].sort_values().unique())

indice=dfadrBOD[(dfadrBOD['commune']==commune) & (dfadrBOD['nom_voie']==rue) & (dfadrBOD['numero']==numero)].index[0]
LAT=dfadrBOD['Lat'][indice] 
LONG=dfadrBOD['Long'][indice]


# In[5]:


### CALCUL DE LA DISTANCE AUX STATIONS
dist=[]
for i in range(len(dfvelobordeaux)):
    dist.append(np.sqrt((LAT-dfvelobordeaux['Lat'][i])**2 + (LONG-dfvelobordeaux['Long'][i])**2))
dfvelobordeaux['DISTANCE']=dist


# In[6]:


dfvelofin=dfvelobordeaux.sort_values(by='DISTANCE')
index=range(len(dfvelobordeaux))
dfvelofin['index']=index
dfvelofin = dfvelofin.set_index('index')


# In[7]:


map = folium.Map([LAT, LONG], zoom_start=16) # carte centrée sur la commune
folium.Marker(location = [LAT,LONG],
              popup = 'Ma Position',
              icon=folium.Icon(color="green")).add_to(map) # Mon emplacement

for i in range(choix):
    folium.Marker(location=[dfvelofin['Lat'][i], dfvelofin['Long'][i]],
              popup = str(dfvelofin['nbelec'][i])+' velos electriques, '+str(dfvelofin['nbclassiq'][i])+' velos classiques et '+str(dfvelofin['nbplaces'][i])+' places libres').add_to(map)
    # emplacement des n(=choix) plus proches stations
    
folium_static(map) # Affichage de la carte


# In[ ]:





# Libraries
#from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

# bibliotecas necessárias
import folium
import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image

from streamlit_folium import folium_static

st.set_page_config(page_title = "Visão Entregadores", page_icon='🛵')

# Import dataset
df_raw = pd.read_csv('train.csv')

df1 = df_raw.copy()

# Limpeza
# Coluna ID - remover espaço final string
df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()

# Coluna Delivery_person_ID - remover espaço final string
df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()

# Coluna Delivery person age - removendo NaN e convertendo para tipo int
df1 = df1.loc[df1['Delivery_person_Age'] != 'NaN ',:]
df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

# Coluna Delivery person ratings - convertendo para float
df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

# Coluna Order date - convertendo para datetime
df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

# Coluna Time orderd - removendo NaN
df1 = df1.loc[df1['Time_Orderd'] != 'NaN ',:]

# Coluna Weatherconditions - removendo NaN e espaços e transformando para lowcase
df1['Weatherconditions'] = df1['Weatherconditions'].apply(lambda x: x.replace("conditions ", "").lower())
df1 = df1.loc[df1['Weatherconditions'] != 'NaN',:]

# Coluna multiple deliveries - removendo NaN
df1 = df1.loc[df1['multiple_deliveries'] != 'NaN ',:]

# Coluna Road traffic density - removendo espaços e transformando para lowcase
df1['Road_traffic_density'] = df1['Road_traffic_density'].apply(lambda x: x.strip().lower())

# Coluna Type_of_order - removendo espaços e transformando para lowcase
df1['Type_of_order'] = df1['Type_of_order'].apply(lambda x: x.strip().lower())

# Coluna Type_of_vehicle - removendo espaços e transformando para lowcase
df1['Type_of_vehicle'] = df1['Type_of_vehicle'].apply(lambda x: x.strip().lower())

# Coluna Festival - removendo espaços e transformando para lowcase
df1 = df1.loc[df1['Festival'] != 'NaN ',:]
df1['Festival'] = df1['Festival'].apply(lambda x: x.strip().lower())

# Coluna City - removendo espaços e transformando para lowcase
df1 = df1.loc[df1['City'] != 'NaN ',:]
df1['City'] = df1['City'].apply(lambda x: x.strip().lower())

#Time taken
df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.replace("(min) ", "")).astype(int)

# =================================
# Sidebar
# =================================

image_path = 'logo.png'
image = Image.open(image_path)
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Food Place')
st.sidebar.markdown('## The best choices for your meal')
st.sidebar.markdown("""---""")

#st.sidebar.markdown('Seleciona uma data limite')
value_order_date = df1['Order_Date'].max()
date_slider = st.sidebar.slider(
    'Selecione uma data limite',
    value = pd.datetime(value_order_date.year, value_order_date.month, value_order_date.day),
    max_value = df1['Order_Date'].max(),
    min_value = df1['Order_Date'].min(),
    format = "DD-MM-YYYY"
)

st.sidebar.markdown("""---""")
traffic_option = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    df1['Road_traffic_density'].unique(),
    default = df1['Road_traffic_density'].unique()
)

st.sidebar.markdown("""---""")
city_option = st.sidebar.multiselect(
    'Quais as cidades',
    df1['City'].unique(),
    default = df1['City'].unique()
)

st.sidebar.markdown("""---""")
weather_option = st.sidebar.multiselect(
    'Quais as condições climáticas',
    df1['Weatherconditions'].unique(),
    default = df1['Weatherconditions'].unique()
)

st.sidebar.markdown("""---""")
st.sidebar.markdown("Feito por Gabriel Alves - Comunidade DS")

# Filtro de data
filtro_data = df1['Order_Date'] < date_slider
df1 = df1.loc[filtro_data, :]

# Filtro de transito
filtro_transito = df1['Road_traffic_density'].isin(traffic_option)
df1 = df1.loc[filtro_transito, :]

# Filtro de cidade
filtro_cidade = df1['City'].isin(city_option)
df1 = df1.loc[filtro_cidade, :]

# Filtro de condicao climatica
filtro_clima = df1['Weatherconditions'].isin(weather_option)
df1 = df1.loc[filtro_clima, :]

# =================================
# Layout principal
# =================================

#Titulo
st.header('Marketplace - Visão Entregadores')

with st.container():
    st.markdown("""---""")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        col1.metric(label='Mais velho', value=df1['Delivery_person_Age'].max())
    
    with col2:
        col2.metric(label='Mais novo', value=df1['Delivery_person_Age'].min())

    with col3:
        col3.metric(label='Melhor condição de veículo', value=df1['Vehicle_condition'].max())

    with col4:
        col4.metric(label='Pior condição de veículo', value=df1['Vehicle_condition'].min())

with st.container():
    st.markdown("""---""")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('### Avaliação média por entregador')
        cols = ['Delivery_person_ID', 'Delivery_person_Ratings']

        df_aux = df1.loc[:, cols].groupby('Delivery_person_ID').mean()

        st.dataframe(df_aux, use_container_width=False)

    with col2:
        with st.container():
            st.markdown('### Avaliação média por trânsito')
            cols = ['Delivery_person_Ratings', 'Road_traffic_density']

            df_aux = df1.loc[:, cols].groupby(cols[1]).agg({cols[0]: ['mean', 'std'] })
            df_aux.columns = ['ratings_mean', 'ratings_std']

            st.dataframe(df_aux, use_container_width=False)
            
        with st.container():
            st.markdown('### Avaliação média por condição de clima')
            cols = ['Delivery_person_Ratings', 'Weatherconditions']

            df_aux = df1.loc[:, cols].groupby(cols[1]).agg( {cols[0]: ['mean', 'std']})
            df_aux.columns = ['ratings_mean', 'ratings_std']

            st.dataframe(df_aux, use_container_width=False)

with st.container():
    st.markdown("""---""")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('### Top 10 Entregadores mais rápidos')

        cols = ['Delivery_person_ID', 'Time_taken(min)', 'City']

        df_aux = df1.loc[:, cols].groupby([cols[2], cols[0]]).mean().reset_index().sort_values([cols[2], cols[1]])

        df_aux1 = df_aux.loc[(df_aux['City'] == 'metropolitian'), :].head(10)
        df_aux2 = df_aux.loc[(df_aux['City'] == 'urban'), :].head(10)
        df_aux3 = df_aux.loc[(df_aux['City'] == 'semi-urban'), :].head(10)

        df_aux4 = pd.concat([df_aux1, df_aux2, df_aux3])

        st.dataframe(df_aux4, use_container_width=True)

    with col2: 
        st.markdown('### Top 10 Entregadores mais lentos')

        cols = ['Delivery_person_ID', 'Time_taken(min)', 'City']

        df_aux = df1.loc[:, cols].groupby([cols[2], cols[0]]).mean().reset_index().sort_values([cols[2], cols[1]], ascending=False)

        df_aux1 = df_aux.loc[(df_aux['City'] == 'metropolitian'), :].head(10)
        df_aux2 = df_aux.loc[(df_aux['City'] == 'urban'), :].head(10)
        df_aux3 = df_aux.loc[(df_aux['City'] == 'semi-urban'), :].head(10)

        df_aux4 = pd.concat([df_aux1, df_aux2, df_aux3])

        st.dataframe(df_aux4, use_container_width=True)
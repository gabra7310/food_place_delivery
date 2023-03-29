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
from geopy.distance      import geodesic

st.set_page_config(page_title = "Visão Restaurantes", page_icon='👨‍🍳', layout='wide')

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

df2 = df1.copy()

# =================================
# Layout principal
# =================================

#Titulo
st.header('Marketplace - Visão Restaurantes')

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '-', '-'])

with st.container():
    #st.markdown("""---""")
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            col1.metric(label='Entregadores únicos', value=df2['Delivery_person_ID'].nunique())
        
        with col2:
            cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
            df2['distance'] = 0
            df2['distance'] = df2.loc[:, cols].apply(lambda x: geodesic((x[cols[0]], x[cols[1]]), (x[cols[2]], x[cols[3]])).km, axis=1)

            col2.metric(label='Distância média', value=np.round(df2['distance'].mean(),2))

        with col3:
            cols = ['Time_taken(min)', 'Festival']

            df_aux = df2.loc[:, cols].groupby(cols[1]).agg({cols[0]: ['mean', 'std'] })
            df_aux.columns = ['time_mean', 'time_std']
            df_aux = df_aux.reset_index()

            cond = df_aux['Festival'] == 'yes'
            np.round(df_aux.loc[cond,'time_mean'],2)

            col3.metric(label='Tempo médio (com festival)', value=np.round(df_aux.loc[cond,'time_mean'],2))

        with col4:
            cols = ['Time_taken(min)', 'Festival']

            df_aux = df2.loc[:, cols].groupby(cols[1]).agg({cols[0]: ['mean', 'std'] })
            df_aux.columns = ['time_mean', 'time_std']
            df_aux = df_aux.reset_index()

            cond = df_aux['Festival'] == 'yes'
            np.round(df_aux.loc[cond,'time_mean'],2)

            col4.metric(label='Desvio padrão (com festival)', value=np.round(df_aux.loc[cond,'time_std'],2))


    with st.container():
        col5, col6 = st.columns(2)

        with col5:
            cols = ['Time_taken(min)', 'Festival']

            df_aux = df2.loc[:, cols].groupby(cols[1]).agg({cols[0]: ['mean', 'std'] })
            df_aux.columns = ['time_mean', 'time_std']
            df_aux = df_aux.reset_index()

            cond = df_aux['Festival'] == 'no'
            np.round(df_aux.loc[cond,'time_mean'],2)

            col5.metric(label='Tempo médio (com festival)', value=np.round(df_aux.loc[cond,'time_mean'],2))

        with col6:
            cols = ['Time_taken(min)', 'Festival']

            df_aux = df2.loc[:, cols].groupby(cols[1]).agg({cols[0]: ['mean', 'std'] })
            df_aux.columns = ['time_mean', 'time_std']
            df_aux = df_aux.reset_index()

            cond = df_aux['Festival'] == 'no'
            np.round(df_aux.loc[cond,'time_mean'],2)

            col6.metric(label='Desvio padrão (sem festival)', value=np.round(df_aux.loc[cond,'time_std'],2))

    
    with st.container():
        st.markdown("""---""")
        st.markdown('### Distribuição da distância média por Cidade')

        cols = ['distance', 'City']
        df_aux = df2.loc[:, cols].groupby(cols[1]).mean().reset_index()

        fig = px.bar(df_aux, x="City", y="distance", color="City")

        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown("""---""")
        col1, col2 = st.columns(2)

        with col1:
            cols = ['Time_taken(min)', 'City']
            df_aux = df2.loc[:, cols].groupby(cols[1]).mean().reset_index()

            fig = px.bar(df_aux, x="City", y="Time_taken(min)", color="City")

            st.plotly_chart(fig, use_container_width=True)    
        
        with col2:
            cols = ['Time_taken(min)', 'City', 'Road_traffic_density']

            df_aux = df2.loc[:, cols].groupby(cols[1:]).mean().reset_index()

            fig = px.bar(df_aux, x='City', y="Time_taken(min)", color="Road_traffic_density", barmode='group')

            st.plotly_chart(fig, use_container_width=True) 
            
            #st.dataframe(df_aux, use_container_width=True)



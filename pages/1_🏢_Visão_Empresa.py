# Libraries
#from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

# bibliotecas necessárias
import folium
import pandas as pd
import streamlit as st
from PIL import Image

from streamlit_folium import folium_static

st.set_page_config(page_title = "Visão Empresa", page_icon='🏢', layout='wide')

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

st.sidebar.markdown('Seleciona uma data limite')
value_order_date = df1['Order_Date'].max()
date_slider = st.sidebar.slider(
    'Selecione uma data',
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

# =================================
# Layout principal
# =================================

#Titulo
st.header('Marketplace - Visão Cliente')

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        st.markdown('## Quantidade de pedidos por dia')

        cols = ['Order_Date', 'ID']
        df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()
        fig = px.bar(df_aux, x='Order_Date', y='ID')

        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('## Volume de pedidos por tipo de tráfego')

            cols = ['ID', 'Road_traffic_density']
            df_aux = df1.loc[:, cols].groupby('Road_traffic_density').count().reset_index().sort_values(by='ID', ascending=False)
            fig = px.bar(df_aux, x='Road_traffic_density', y='ID')

            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown('## Volume de pedidos por tipo de tráfego e cidade')

            cols = ['ID', 'City', 'Road_traffic_density']
            df_aux = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).count().reset_index()
            fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')

            st.plotly_chart(fig, use_container_width=True)


with tab2:
    with st.container():
        st.markdown("## Quantidade de pedidos por semana")

        df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')

        df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
        #fig = px.line(df_aux, x='week_of_year', y='ID')
        fig = px.bar(df_aux, x='week_of_year', y='ID')

        st.plotly_chart(fig, use_container_width=True)
    
    with st.container():
        st.markdown("## Quantidade de pedidos por entregador por semana")

        df_aux1 = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
        df_aux2 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()

        df_aux = pd.merge(df_aux1, df_aux2, how='inner', on='week_of_year')
        df_aux['order_by_delivers'] = df_aux['ID'] / df_aux['Delivery_person_ID']

        fig = px.line(df_aux, x='week_of_year', y='order_by_delivers')

        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("## Mapa com entregas por tipo de tráfego")
    cols = ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df_aux = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).median().reset_index()

    map = folium.Map()

    for index, location_info in df_aux.iterrows():
        folium.Marker(
            [ location_info['Delivery_location_latitude'], location_info['Delivery_location_longitude'] ],
            popup = location_info[['City', 'Road_traffic_density']] ).add_to(map)

    folium_static(map, width=1024, height=600)


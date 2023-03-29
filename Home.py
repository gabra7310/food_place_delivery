import streamlit as st
from PIL import Image

st.set_page_config(
    page_title = "🏠 Home",
    page_icon = "🎲",
    layout='wide'
)

image = Image.open('logo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Food Place')
st.sidebar.markdown('## The best choices for your meal')
st.sidebar.markdown("""---""")


st.sidebar.markdown("Feito por Gabriel Alves - Comunidade DS")

st.write('# Food Place - Company Growth Dashboard')

st.markdown(""" 
Este dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.

### Como utilizar este dashborad?
- Visão Empresa:
	- Visão Gerencial: Métricas gerais de comportamento
	- Visão Tática: Indicadores semanasi de crescimento
	- Visão Geográfica: Insights de geolocalização

- Visão Entregador:
	- Acompanhamento dos indicadores semanais de crescimento

- Visão Restaurante:
	- Indicadores semanais de crescimento dos restaurantes

""")

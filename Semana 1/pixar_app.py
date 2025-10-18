import pandas as pd
import streamlit as st
import plotly.express as px
import requests

# Configuración de la página
st.set_page_config(page_title="Pixar Dashboard", layout="wide")

# 
# 1. Cargar datos de la API
# 
@st.cache_data
def load_data():
    personajes = []
    for page in range(1, 6):  # puedes aumentar este número si quieres más datos
        url = f"https://api.disneyapi.dev/character?page={page}"
        r = requests.get(url).json()
        for p in r["data"]:
            if p["films"]:  # solo personajes con películas
                personajes.append({
                    "Nombre": p["name"],
                    "Películas": ", ".join(p["films"]),
                    "Series": ", ".join(p["tvShows"]) if p["tvShows"] else "Ninguna",
                    "Imagen": p["imageUrl"]
                })
    return pd.DataFrame(personajes)

df = load_data()

# 
# 2. Título
# 
st.title("🎬 Pixar Dashboard (Disney API)")

# 
# 3. Filtros
# 
st.sidebar.header("Filtros")

lista_peliculas = sorted(set(", ".join(df["Películas"]).split(", ")))
lista_series = sorted(set(", ".join(df["Series"]).split(", ")))

peliculas_sel = st.sidebar.multiselect("Películas", options=lista_peliculas, default=lista_peliculas)
series_sel = st.sidebar.multiselect("Series", options=lista_series, default=lista_series)

filtro = df[
    df["Películas"].apply(lambda x: any(p in x for p in peliculas_sel)) &
    df["Series"].apply(lambda x: any(s in x for s in series_sel))
]

# 
# 4. KPIs
# 
col1, col2, col3 = st.columns(3)
col1.metric("Total de personajes", len(filtro))
col2.metric("Películas únicas", len(set(", ".join(filtro["Películas"]).split(", "))))
col3.metric("Series únicas", len(set(", ".join(filtro["Series"]).split(", "))) if len(filtro) > 0 else 0)

# 
# 5. Gráficos
# 
col1, col2 = st.columns(2)

# 📊 Gráfico de personajes por película
with col1:
    film_counts = filtro["Películas"].str.split(", ").explode().value_counts().reset_index()
    film_counts.columns = ["Película", "Personajes"]
    fig1 = px.bar(film_counts, x="Película", y="Personajes", title="Personajes por película")
    fig1.update_layout(xaxis={'categoryorder':'total descending'})
    st.plotly_chart(fig1, use_container_width=True)

# 🥧 Gráfico circular por series
with col2:
    show_counts = filtro["Series"].str.split(", ").explode().value_counts().reset_index()
    show_counts.columns = ["Serie", "Personajes"]
    fig2 = px.pie(show_counts, names="Serie", values="Personajes", title="Distribución por series")
    st.plotly_chart(fig2, use_container_width=True)

# 
# 6. Tabla de datos
# 
st.subheader("📊 Datos completos")
st.dataframe(filtro[["Nombre", "Películas", "Series"]].head(20), use_container_width=True)

# 
# 7. Imágenes destacadas
# 
st.subheader("✨ Personajes destacados")
cols = st.columns(4)
for i, row in enumerate(filtro.head(4).itertuples()):
    with cols[i]:
        st.image(row.Imagen, caption=row.Nombre, use_container_width=True)

import boto3
import pandas as pd
import json
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

# Configuración de página
st.set_page_config(page_title="Server Status Dashboard", layout="wide")

# ----------------------
# Helpers
# ----------------------
s3 = boto3.client("s3")
bucket_name = "xideralaws-curso-benjamin2"
prefix = "raw/"

@st.cache_data(show_spinner=False)
def actualizar() -> pd.DataFrame:
    """
    Trae todos los JSON del bucket y devuelve un DataFrame concatenado.
    """
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    data_frames = []

    for obj in response.get("Contents", []):
        key = obj["Key"]
        if key.endswith(".json"):
            file_obj = s3.get_object(Bucket=bucket_name, Key=key)
            content = file_obj["Body"].read().decode("utf-8")
            json_data = json.loads(content)
            df_temp = pd.json_normalize(json_data)
            data_frames.append(df_temp)

    if data_frames:
        df = pd.concat(data_frames, ignore_index=True)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["fecha"] = df["timestamp"].dt.date
        return df
    else:
        return pd.DataFrame()

def contar_status(df: pd.DataFrame) -> pd.DataFrame:
    """
    Devuelve un DataFrame con conteo de OK, WARN y ERROR por servidor.
    """
    return df.groupby(['server_id', 'status']).size().unstack(fill_value=0)

# ----------------------
# Sidebar
# ----------------------
st.sidebar.title("🎛️ Controles")
fecha_inicio = st.sidebar.date_input("Fecha inicio")
fecha_fin = st.sidebar.date_input("Fecha fin")
region_filter = st.sidebar.multiselect("Filtrar por región", options=[], default=[])

# ----------------------
# Main
# ----------------------
st.title("🖥️ Server Status Dashboard")

df = actualizar()
if df.empty:
    st.warning("No hay datos disponibles en S3.")
    st.stop()

# Filtros dinámicos
region_options = sorted(df['region'].unique())
if not region_filter:
    region_filter = region_options
df = df[df['region'].isin(region_filter)]
df = df[(df['fecha'] >= fecha_inicio) & (df['fecha'] <= fecha_fin)]

# ----------------------
# KPIs
# ----------------------
left, mid, right = st.columns(3)
with left:
    st.metric("Total registros", f"{len(df):,}")
with mid:
    st.metric("Servidores únicos", df['server_id'].nunique())
with right:
    st.metric("Regiones", len(df['region'].unique()))

st.markdown("---")

# ----------------------
# Tab: Conteo de status
# ----------------------
tab1, tab2, tab3 = st.tabs(["📊 Conteo por servidor", "📈 Tendencias por fecha", "⚠️ WARN/ERROR"])

with tab1:
    st.subheader("Conteo de status por servidor")
    conteo = contar_status(df)
    st.dataframe(conteo)

    # Gráfico de barras apiladas
    conteo_reset = conteo.reset_index().melt(id_vars='server_id', var_name='status', value_name='count')
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=conteo_reset, x='server_id', y='count', hue='status', ci=None, palette="Set2", ax=ax)
    ax.set_title("Estado de servidores (OK / WARN / ERROR)")
    st.pyplot(fig, clear_figure=True)

with tab2:
    st.subheader("Tendencia de status por fecha")
    tendencia = df.groupby(['fecha', 'status']).size().unstack()


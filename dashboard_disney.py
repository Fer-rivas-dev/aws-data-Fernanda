import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import boto3
import json
from datetime import datetime

# ==================== CONFIGURACIÓN ====================
st.set_page_config(
    page_title="Disney Movies Analytics",
    page_icon="🎬",
    layout="wide"
)

# ==================== CONEXIÓN S3 Y LAMBDA ====================
@st.cache_data(ttl=300)
def get_lambda_stats():
    """Obtiene estadísticas desde Lambda"""
    try:
        lambda_client = boto3.client('lambda', region_name='us-west-1')
        
        response = lambda_client.invoke(
            FunctionName='xideralaws-fernanda',
            InvocationType='RequestResponse',
            Payload=json.dumps({})
        )
        
        result = json.loads(response['Payload'].read())
        if result['statusCode'] == 200:
            return json.loads(result['body'])
        else:
            st.warning("Lambda no retornó datos válidos")
            return None
    except Exception as e:
        st.warning(f"No se pudo invocar Lambda: {str(e)}")
        return None

@st.cache_data(ttl=300)
def load_data_from_s3():
    """Carga datos desde S3"""
    try:
        s3 = boto3.client('s3')
        bucket = 'xideralaws-curso-fernanda'
        
        # Leer CSVs
        files = {
            'movies': 'disney-project/final/movies_spark.csv',
            'segment': 'disney-project/final/agg_segment.csv',
            'temporal': 'disney-project/final/agg_temporal.csv',
            'decade': 'disney-project/final/agg_decade.csv'
        }
        
        data = {}
        for key, file_path in files.items():
            try:
                obj = s3.get_object(Bucket=bucket, Key=file_path)
                data[key] = pd.read_csv(obj['Body'])
            except Exception as e:
                st.warning(f"No se pudo cargar {key}: {file_path}")
                data[key] = pd.DataFrame()  # DataFrame vacío como fallback
        
        return data
    except Exception as e:
        st.error(f"Error cargando datos: {str(e)}")
        return None

def get_col(df, possible_names):
    """Busca una columna por varios nombres posibles"""
    for name in possible_names:
        if name in df.columns:
            return name
    return None

# ==================== HEADER ====================
st.title("🎬 Disney Movies Analytics Dashboard")
st.markdown("---")

# CONFIGURACIÓN: Cambiar a False si no tienes permisos Lambda
USE_LAMBDA = False  # ← Cambiar a True cuando tengas permisos

# Intentar obtener stats de Lambda
lambda_stats = None
if USE_LAMBDA:
    lambda_stats = get_lambda_stats()

if lambda_stats:
    st.success("✅ Conectado a Lambda para estadísticas en tiempo real")
    
    # Mostrar stats de Lambda en un expander
    with st.expander("📊 Estadísticas desde Lambda"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Películas (Lambda)", lambda_stats['summary']['total_movies'])
            st.metric("Revenue Total", f"${lambda_stats['revenue']['total']/1e9:.2f}B")
        
        with col2:
            st.metric("Revenue Promedio", f"${lambda_stats['revenue']['average']/1e6:.1f}M")
            st.metric("Rating Promedio", f"{lambda_stats['ratings']['average']:.2f} ⭐")
        
        with col3:
            st.metric("Marca Principal", lambda_stats.get('top_brand', 'N/A'))
            st.metric("Películas con Revenue", lambda_stats['summary']['movies_with_revenue'])
elif USE_LAMBDA:
    st.info("ℹ️ Lambda no disponible - usando datos de S3 directamente")

# Cargar datos
data = load_data_from_s3()

if data is None:
    st.stop()

movies_df = data['movies']
segment_df = data['segment']
temporal_df = data['temporal']
decade_df = data['decade']

# Detectar columnas clave con nombres alternativos
revenue_col = get_col(movies_df, ['box_office_revenue_clean', 'revenue', 'box_office_revenue', 'total_gross'])
rating_col = get_col(movies_df, ['imdb_score', 'imdb_rating', 'rating', 'score'])  # ← CORRECCIÓN: imdb_score primero
year_col = get_col(movies_df, ['release_year', 'year', 'Year'])
title_col = get_col(movies_df, ['film_title', 'title', 'movie_title', 'name'])
brand_col = get_col(movies_df, ['brand', 'studio', 'franchise'])
segment_col = get_col(movies_df, ['segment', 'category', 'type'])
chars_col = get_col(movies_df, ['character_count', 'characters', 'cast_count'])
decade_col = get_col(movies_df, ['decade', 'period'])
rating_cat_col = get_col(movies_df, ['rating_category', 'rating_cat', 'category'])

# Debug info - Solo en sidebar (colapsado por defecto)
if st.sidebar.checkbox("🔍 Mostrar Info Debug", value=False):
    st.sidebar.write("**Columnas Detectadas:**")
    st.sidebar.caption(f"Revenue: `{revenue_col}`")
    st.sidebar.caption(f"Rating: `{rating_col}`")
    st.sidebar.caption(f"Year: `{year_col}`")
    st.sidebar.caption(f"Brand: `{brand_col}`")
    st.sidebar.caption(f"Segment: `{segment_col}`")

# ==================== SIDEBAR FILTROS ====================
st.sidebar.header("🔍 Filtros")

# Filtro por años
if year_col:
    min_year = int(movies_df[year_col].min())
    max_year = int(movies_df[year_col].max())
    year_range = st.sidebar.slider(
        "Rango de Años",
        min_year, max_year, (min_year, max_year)
    )
    movies_filtered = movies_df[
        (movies_df[year_col] >= year_range[0]) & 
        (movies_df[year_col] <= year_range[1])
    ]
else:
    movies_filtered = movies_df

# Filtro por marca
if brand_col:
    brands = ['Todas'] + sorted(movies_filtered[brand_col].dropna().unique().tolist())
    selected_brand = st.sidebar.selectbox("Marca Disney", brands)
    if selected_brand != 'Todas':
        movies_filtered = movies_filtered[movies_filtered[brand_col] == selected_brand]

# Filtro por segmento
if segment_col:
    segments = ['Todos'] + sorted(movies_filtered[segment_col].dropna().unique().tolist())
    selected_segment = st.sidebar.selectbox("Segmento", segments)
    if selected_segment != 'Todos':
        movies_filtered = movies_filtered[movies_filtered[segment_col] == selected_segment]

# ==================== TABS ====================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview", 
    "📈 Análisis Temporal", 
    "🏆 Rankings", 
    "👥 Personajes",
    "💡 Insights"
])

# ==================== TAB 1: OVERVIEW ====================
with tab1:
    st.header("Resumen General")
    
    # KPIs principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_movies = len(movies_filtered)
        st.metric("Total Películas", f"{total_movies:,}")
    
    with col2:
        if revenue_col:
            total_revenue = movies_filtered[revenue_col].sum()
            st.metric("Revenue Total", f"${total_revenue/1e9:.2f}B")
        else:
            st.metric("Revenue Total", "N/A")
    
    with col3:
        if rating_col:
            avg_rating = movies_filtered[rating_col].mean()
            st.metric("Rating Promedio", f"{avg_rating:.2f} ⭐")
        else:
            st.metric("Rating Promedio", "N/A")
    
    with col4:
        if chars_col:
            total_chars = movies_filtered[chars_col].sum()
            st.metric("Total Personajes", f"{int(total_chars):,}")
        else:
            st.metric("Total Personajes", "N/A")
    
    st.markdown("---")
    
    # Gráficos principales
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Revenue por Marca")
        if 'brand' in movies_filtered.columns and 'box_office_revenue_clean' in movies_filtered.columns:
            brand_revenue = movies_filtered.groupby('brand')['box_office_revenue_clean'].sum().reset_index()
            brand_revenue = brand_revenue.sort_values('box_office_revenue_clean', ascending=False)
            
            fig = px.bar(
                brand_revenue,
                x='brand',
                y='box_office_revenue_clean',
                title="Revenue Total por Marca Disney",
                labels={'box_office_revenue_clean': 'Revenue ($)', 'brand': 'Marca'},
                color='box_office_revenue_clean',
                color_continuous_scale='Blues'
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Columnas 'brand' o 'revenue' no disponibles")
    
    with col2:
        st.subheader("Distribución de Ratings")
        if 'rating_category' in movies_filtered.columns:
            rating_dist = movies_filtered['rating_category'].value_counts().reset_index()
            rating_dist.columns = ['Categoría', 'Cantidad']
            
            fig = px.pie(
                rating_dist,
                names='Categoría',
                values='Cantidad',
                title="Distribución por Categoría de Rating",
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Columna 'rating_category' no disponible")
    
    # Segmentación
    st.subheader("Segmentación de Películas")
    if 'segment' in movies_filtered.columns:
        segment_counts = movies_filtered['segment'].value_counts().reset_index()
        segment_counts.columns = ['Segmento', 'Cantidad']
        
        fig = px.bar(
            segment_counts,
            x='Segmento',
            y='Cantidad',
            title="Películas por Segmento de Éxito",
            color='Cantidad',
            color_continuous_scale='Greens'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Columna 'segment' no disponible")

# ==================== TAB 2: ANÁLISIS TEMPORAL ====================
with tab2:
    st.header("Análisis Temporal")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Evolución de Revenue")
        if 'release_year' in movies_filtered.columns and 'box_office_revenue_clean' in movies_filtered.columns:
            yearly_revenue = movies_filtered.groupby('release_year')['box_office_revenue_clean'].sum().reset_index()
            
            fig = px.line(
                yearly_revenue,
                x='release_year',
                y='box_office_revenue_clean',
                title="Revenue Anual",
                labels={'release_year': 'Año', 'box_office_revenue_clean': 'Revenue ($)'},
                markers=True
            )
            fig.update_traces(line_color='#0066CC', line_width=3)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Datos de año o revenue no disponibles")
    
    with col2:
        st.subheader("Películas por Año")
        if 'release_year' in movies_filtered.columns:
            yearly_count = movies_filtered.groupby('release_year').size().reset_index(name='count')
            
            fig = px.bar(
                yearly_count,
                x='release_year',
                y='count',
                title="Producción Anual",
                labels={'release_year': 'Año', 'count': 'Cantidad'},
                color='count',
                color_continuous_scale='Oranges'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Columna 'release_year' no disponible")
    
    # Análisis por década
    st.subheader("Análisis por Década")
    if 'decade' in movies_filtered.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            decade_count = movies_filtered.groupby('decade').size().reset_index(name='Películas')
            fig = px.bar(
                decade_count,
                x='decade',
                y='Películas',
                title="Películas por Década",
                color='Películas',
                color_continuous_scale='Purples'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'box_office_revenue_clean' in movies_filtered.columns:
                decade_revenue = movies_filtered.groupby('decade')['box_office_revenue_clean'].mean().reset_index()
                decade_revenue.columns = ['Década', 'Revenue Promedio']
                
                fig = px.line(
                    decade_revenue,
                    x='Década',
                    y='Revenue Promedio',
                    title="Revenue Promedio por Década",
                    markers=True
                )
                fig.update_traces(line_color='#FF6B6B', line_width=3)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Columna 'revenue' no disponible")
    else:
        st.info("Columna 'decade' no disponible")

# ==================== TAB 3: RANKINGS ====================
with tab3:
    st.header("Rankings y Top Películas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 Top 10 por Revenue")
        if revenue_col and title_col and year_col:
            top_revenue = movies_filtered.nlargest(10, revenue_col)[
                [title_col, revenue_col, year_col]
            ].copy()
            top_revenue['Revenue ($M)'] = (top_revenue[revenue_col] / 1e6).round(2)
            top_revenue = top_revenue.rename(columns={title_col: 'Película', year_col: 'Año'})
            st.dataframe(
                top_revenue[['Película', 'Año', 'Revenue ($M)']],
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("Columnas necesarias no disponibles")
    
    with col2:
        st.subheader("⭐ Top 10 por Rating")
        if rating_col and title_col and year_col:
            top_rating = movies_filtered.nlargest(10, rating_col)[
                [title_col, rating_col, year_col]
            ].copy()
            top_rating = top_rating.rename(columns={
                title_col: 'Película',
                rating_col: 'Rating',
                year_col: 'Año'
            })
            st.dataframe(
                top_rating[['Película', 'Año', 'Rating']],
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("Columnas necesarias no disponibles")
    
    # Gráfico: Rating vs Revenue
    st.subheader("Relación Rating vs Revenue")
    if rating_col and revenue_col:
        scatter_data = movies_filtered[[rating_col, revenue_col]].copy()
        
        # Agregar columnas opcionales para el hover
        hover_cols = [title_col, year_col]
        hover_data_dict = {}
        for col in hover_cols:
            if col and col in movies_filtered.columns:
                scatter_data = pd.concat([scatter_data, movies_filtered[[col]]], axis=1)
                hover_data_dict[col] = True
        
        fig = px.scatter(
            scatter_data,
            x=rating_col,
            y=revenue_col,
            color=brand_col if brand_col and brand_col in scatter_data.columns else None,
            size=chars_col if chars_col and chars_col in scatter_data.columns else None,
            hover_data=hover_data_dict if hover_data_dict else None,
            title="Correlación entre Rating IMDb y Revenue",
            labels={
                rating_col: 'Rating IMDb',
                revenue_col: 'Revenue ($)',
                brand_col: 'Marca' if brand_col else None
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Datos de rating o revenue no disponibles")

# ==================== TAB 4: PERSONAJES ====================
with tab4:
    st.header("Análisis de Personajes")
    
    if 'character_count' in movies_filtered.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Top 10 Películas con Más Personajes")
            top_chars = movies_filtered.nlargest(10, 'character_count')[
                ['film_title', 'character_count', 'release_year']
            ].copy()
            top_chars = top_chars.rename(columns={
                'film_title': 'Película',
                'character_count': 'Personajes',
                'release_year': 'Año'
            })
            
            fig = px.bar(
                top_chars,
                x='Personajes',
                y='Película',
                orientation='h',
                title="Películas con Mayor Cantidad de Personajes",
                color='Personajes',
                color_continuous_scale='Teal'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Promedio de Personajes por Década")
            if 'decade' in movies_filtered.columns:
                decade_chars = movies_filtered.groupby('decade')['character_count'].mean().reset_index()
                decade_chars.columns = ['Década', 'Promedio Personajes']
                
                fig = px.line(
                    decade_chars,
                    x='Década',
                    y='Promedio Personajes',
                    title="Evolución del Promedio de Personajes",
                    markers=True
                )
                fig.update_traces(line_color='#9B59B6', line_width=3)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Columna 'decade' no disponible")
        
        # Tabla detallada
        st.subheader("Detalle de Películas")
        display_cols = []
        if title_col: display_cols.append(title_col)
        if year_col: display_cols.append(year_col)
        if chars_col: display_cols.append(chars_col)
        if rating_col: display_cols.append(rating_col)
        if revenue_col: display_cols.append(revenue_col)
        
        if display_cols:
            detail_df = movies_filtered[display_cols].copy()
            if chars_col:
                detail_df = detail_df.sort_values(chars_col, ascending=False).head(20)
            st.dataframe(detail_df, hide_index=True, use_container_width=True)
    else:
        st.info("Columna 'character_count' no disponible")

# ==================== TAB 5: INSIGHTS ====================
with tab5:
    st.header("💡 Insights Clave")
    
    # Métricas avanzadas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'box_office_revenue_clean' in movies_filtered.columns:
            revenue_per_movie = movies_filtered['box_office_revenue_clean'].mean()
            st.metric(
                "Revenue Promedio por Película",
                f"${revenue_per_movie/1e6:.1f}M"
            )
    
    with col2:
        if 'character_count' in movies_filtered.columns:
            chars_per_movie = movies_filtered['character_count'].mean()
            st.metric(
                "Personajes Promedio",
                f"{chars_per_movie:.1f}"
            )
    
    with col3:
        if 'segment' in movies_filtered.columns:
            success_rate = (movies_filtered['segment'].str.contains('Éxito', na=False).sum() / len(movies_filtered) * 100)
            st.metric(
                "Tasa de Éxito",
                f"{success_rate:.1f}%"
            )
    
    st.markdown("---")
    
    # Insights textuales
    st.subheader("📊 Hallazgos Principales")
    
    insights = []
    
    # Insight 1: Marca más exitosa
    if 'brand' in movies_filtered.columns and 'box_office_revenue_clean' in movies_filtered.columns:
        top_brand = movies_filtered.groupby('brand')['box_office_revenue_clean'].sum().idxmax()
        top_brand_revenue = movies_filtered.groupby('brand')['box_office_revenue_clean'].sum().max()
        insights.append(f"🏆 **{top_brand}** es la marca más exitosa con ${top_brand_revenue/1e9:.2f}B en revenue total")
    
    # Insight 2: Década dorada
    if 'decade' in movies_filtered.columns:
        decade_counts = movies_filtered['decade'].value_counts()
        top_decade = decade_counts.idxmax()
        insights.append(f"🎬 La **década de {top_decade}** fue la más productiva con {decade_counts.max()} películas")
    
    # Insight 3: Rating vs Revenue
    if rating_col and revenue_col:
        corr_data = movies_filtered[[rating_col, revenue_col]].dropna()
        if len(corr_data) > 0:
            correlation = corr_data[rating_col].corr(corr_data[revenue_col])
            if correlation > 0.5:
                insights.append(f"⭐ Fuerte correlación positiva ({correlation:.2f}) entre rating y revenue")
            elif correlation < 0:
                insights.append(f"📉 Correlación negativa ({correlation:.2f}) entre rating y revenue")
            else:
                insights.append(f"➡️ Correlación moderada ({correlation:.2f}) entre rating y revenue")
    
    # Insight 4: Personajes
    if chars_col and revenue_col:
        char_data = movies_filtered[[chars_col, revenue_col]].dropna()
        if len(char_data) > 0:
            char_corr = char_data[chars_col].corr(char_data[revenue_col])
            if char_corr > 0.3:
                insights.append(f"👥 Mayor cantidad de personajes se asocia con mayor revenue (correlación: {char_corr:.2f})")
    
    for insight in insights:
        st.markdown(f"- {insight}")
    
    # Comparación de segmentos
    if 'segment' in movies_filtered.columns and 'box_office_revenue_clean' in movies_filtered.columns:
        st.subheader("Comparación por Segmento")
        
        # Construir dict de agregación dinámicamente
        agg_dict = {
            'film_title': 'count',
            'box_office_revenue_clean': 'mean'
        }
        
        # Solo agregar imdb_rating si existe
        if 'imdb_rating' in movies_filtered.columns:
            agg_dict['imdb_rating'] = 'mean'
        
        segment_analysis = movies_filtered.groupby('segment').agg(agg_dict).reset_index()
        
        # Renombrar columnas
        new_cols = ['Segmento', 'Películas', 'Revenue Promedio']
        if 'imdb_rating' in movies_filtered.columns:
            new_cols.append('Rating Promedio')
        
        segment_analysis.columns = new_cols
        st.dataframe(segment_analysis, hide_index=True, use_container_width=True)

# ==================== FOOTER ====================
st.markdown("---")
st.caption(f"📅 Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 🎬 Disney Data Pipeline Project")
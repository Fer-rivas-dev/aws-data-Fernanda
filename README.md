# 🎬 Disney Data Pipeline - AWS Cloud Analytics

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![AWS](https://img.shields.io/badge/AWS-Cloud-orange.svg)](https://aws.amazon.com/)
[![PySpark](https://img.shields.io/badge/PySpark-3.x-red.svg)](https://spark.apache.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red.svg)](https://streamlit.io/)

Pipeline de datos end-to-end para análisis de películas Disney utilizando servicios AWS, PySpark y visualización con Streamlit.

## 🎯 Descripción

Este proyecto implementa un pipeline de datos completo para procesar, transformar y visualizar información sobre películas Disney. El sistema ingesta datos desde múltiples fuentes (Kaggle y API Disney), los procesa con PySpark, y genera visualizaciones interactivas.

### Características Principales

✅ **Ingesta de Datos Multi-Fuente**
- Dataset de Kaggle: 116 películas Disney
- Disney API: 1,419 personajes

✅ **Procesamiento Distribuido**
- PySpark para análisis de Big Data
- Transformaciones y agregaciones complejas

✅ **Arquitectura Cloud**
- Almacenamiento en S3 (Raw, Cleaned, Final)
- Procesamiento en EC2
- Lambda para análisis en tiempo real

✅ **Visualización Interactiva**
- Dashboard Streamlit con 5 tabs
- Gráficos interactivos con Plotly
- Filtros dinámicos

## 🏗️ Arquitectura
┌─────────────────────────────────────────────────────────┐
│ AWS Cloud (us-west-1) │
├─────────────────────────────────────────────────────────┤
│ │
│ Kaggle + API → EC2 (Ingesta) → S3 Raw │
│ │
│ S3 Raw → EC2 (Limpieza) → S3 Cleaned │
│ │
│ S3 Cleaned → EC2 (Spark) → S3 Final │
│ │
│ S3 Final → Lambda → Streamlit Dashboard │
│ │
└─────────────────────────────────────────────────────────┘

text

### Componentes del Pipeline

| Componente | Tecnología | Función |
|------------|------------|---------|
| **Ingesta** | EC2 + Jupyter | Extracción de datos desde Kaggle y API Disney |
| **Almacenamiento** | S3 Buckets | Almacenamiento en capas: Raw, Cleaned, Final |
| **Procesamiento** | PySpark | Transformaciones y agregaciones distribuidas |
| **Análisis** | AWS Lambda | Generación de métricas en tiempo real |
| **Visualización** | Streamlit | Dashboard interactivo con filtros dinámicos |

## 🛠️ Tecnologías

### Cloud & Infrastructure
- **AWS S3**: Almacenamiento de datos en capas
- **AWS EC2**: Instancias para procesamiento
- **AWS Lambda**: Análisis serverless

### Processing & Analytics
- **Python 3.11**: Lenguaje principal
- **PySpark 3.x**: Procesamiento distribuido
- **Pandas**: Manipulación de datos
- **NumPy**: Cálculos numéricos

### Visualization
- **Streamlit**: Framework de aplicaciones web
- **Plotly**: Gráficos interactivos
- **Matplotlib/Seaborn**: Visualizaciones estáticas

### Data Sources
- **Kaggle API**: Dataset de películas Disney
- **Disney API**: Información de personajes

## 📁 Estructura del Proyecto

disney-pipeline-project/
│
├── notebooks/
│ ├── 01_ingesta_datos.ipynb # Fase 1: Ingesta desde Kaggle y API
│ ├── 02_limpieza_transformacion.ipynb # Fase 2: Limpieza y transformación
│ └── 03b_procesamiento_spark.ipynb # Fase 3: Procesamiento con PySpark
│
├── data/
│ ├── raw/
│ │ ├── kaggle/
│ │ │ └── disney_movies.csv
│ │ └── api/
│ │ └── disney_characters.json
│ │
│ ├── cleaned/
│ │ ├── movies_cleaned.csv
│ │ ├── characters_cleaned.csv
│ │ └── relations.csv
│ │
│ └── final/
│ ├── movies_spark.csv
│ ├── agg_segment.csv
│ ├── agg_temporal.csv
│ └── agg_decade.csv
│
├── spark_output/
│ ├── movies_enriched.parquet
│ ├── agg_segment.parquet
│ ├── agg_temporal.parquet
│ └── agg_decade.parquet
│
├── lambda/
│ └── lambda_function.py # Función Lambda para análisis
│
├── dashboard_disney.py # Dashboard Streamlit
├── datos_fase1.pkl # Checkpoint Fase 1
├── datos_fase2.pkl # Checkpoint Fase 2
├── datos_fase3.pkl # Checkpoint Fase 3
├── .env.example # Plantilla de variables de entorno
├── .gitignore
├── requirements.txt
└── README.md

import streamlit as st
import os

# 1. Configuración Global
st.set_page_config(
    page_title="Herramientas Ingenieria",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Definición de Páginas

# -- Página de Inicio --
pg_inicio = st.Page("inicio.py", title="Inicio", icon="🏠", default=True)

# -- Planeación --
pg_proyecciones = st.Page("pages/1_Proyecciones/1_proyecciones.py", title="Proyección Población", icon="📈")
pg_caudal = st.Page("pages/2_Caudal/2_Calculos_Adicionales.py", title="Cálculo Caudal", icon="💧")

# -- Sedimentación --
paginas_sedimentacion = [
    st.Page("pages/4_Sedimentacion/0_Menu_Sedimentacion.py", title="Menú Sedimentación", icon="⏳"),
    st.Page("pages/4_Sedimentacion/1_Sedimentacion.py", title="Sedimentador Alta Tasa", icon="👌"),
    st.Page("pages/4_Sedimentacion/2_Velocidad_asentamiento_ejemplo5-21-1.py", title="Velocidad Asentamiento", icon="📉"),
    st.Page("pages/4_Sedimentacion/3_Flujo_horizontal_5-21-2.py", title="Flujo Horizontal", icon="➡️")
]

# Agregar archivos adicionales de sedimentación si existen
archivos_sedimentacion_extra = [
    "pages/4_Sedimentacion/4_Dos_sedimentadores.py",
    "pages/4_Sedimentacion/5_Calcular_Diametro.py", 
    "pages/4_Sedimentacion/6_Sedimentador_opera.py"
]

for ruta in archivos_sedimentacion_extra:
    if os.path.exists(ruta):
        nombre = os.path.basename(ruta).replace('.py', '').replace('_', ' ').title()
        icono = "📝"  # Icono por defecto
        paginas_sedimentacion.append(st.Page(ruta, title=nombre, icon=icono))

# -- EJERCICIOS DEL LIBRO --
paginas_ejercicios_libro = []

# Menú principal de ejercicios del libro
if os.path.exists("pages/5_Ejercicios_Libro/0_Menu_Ejercicios_Libro.py"):
    paginas_ejercicios_libro.append(
        st.Page("pages/5_Ejercicios_Libro/0_Menu_Ejercicios_Libro.py", title="Menú Ejercicios Libro", icon="📚")
    )

# Ejercicios individuales del libro
ejercicios_libro = [
    ("1_Flujo_Horizontal_5_12.py", "🌊"),
    ("2_Parametros_Basicos_5_13.py", "⚙️"),
    ("3_Duplicar_Capacidad_5_15.py", "📈"),
    ("4_Remosion_Total_Solidos_5_16.py", "🧹"),
    ("5_Diseño_Sedimentador_Convencional_3a1.py","👌"),
    ("6_Sedimentador_Flujo_Horizontal_5_19.py", "🏗️"),
    ("7_Repotenciacion_Placas_Inclinadas.py", "🏗️"),
    ]

for archivo, icono in ejercicios_libro:
    ruta = f"pages/5_Ejercicios_Libro/{archivo}"
    if os.path.exists(ruta):
        nombre = archivo.replace('.py', '').replace('_', ' ').title()
        paginas_ejercicios_libro.append(st.Page(ruta, title=nombre, icon=icono))

# -- Otros módulos --
pg_aireador = st.Page("pages/3_Aireadores/3_Diseno_Aireador.py", title="Diseño Aireador", icon="🌊")
pg_filtracion = st.Page("pages/5_Filtracion/1_Filtracion.py", title="Diseño Filtración", icon="🧪")

# 3. Configuración del Menú de Navegación
navigation_config = {
    "Principal": [pg_inicio],
    "Planeación y Demanda": [pg_proyecciones, pg_caudal],
    "Sedimentación": paginas_sedimentacion,
    "Potabilización": [pg_aireador, pg_filtracion]
}

# Agregar sección de ejercicios del libro solo si hay archivos
if paginas_ejercicios_libro:
    navigation_config["📚 Ejercicios Libro"] = paginas_ejercicios_libro

# 4. Ejecutar la aplicación
pg = st.navigation(navigation_config)
pg.run()
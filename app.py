import streamlit as st
import os

# 1. Configuración Global
st.set_page_config(
    page_title="Herramientas Ingenieria",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Definición de Páginas - SOLO ARCHIVOS QUE EXISTEN

# -- Página de Inicio --
pg_inicio = st.Page("inicio.py", title="Inicio", icon="🏠", default=True)

# -- Planeación --
pg_proyecciones = st.Page("pages/1_Proyecciones/1_proyecciones.py", title="Proyección Población", icon="📈")
pg_caudal = st.Page("pages/2_Caudal/2_Calculos_Adicionales.py", title="Cálculo Caudal", icon="💧")

# -- Sedimentación --
pg_menu_sedimentacion = st.Page("pages/4_Sedimentacion/0_Menu_Sedimentacion.py", title="Menú Sedimentación", icon="⏳")
pg_sedimentador = st.Page("pages/4_Sedimentacion/1_Sedimentacion.py", title="Sedimentador Alta Tasa", icon="💧")
pg_velocidad_asentamiento = st.Page(
    "pages/4_Sedimentacion/2_Velocidad_asentamiento_ejemplo5-21-1.py", 
    title="Velocidad Asentamiento", 
    icon="📉"
)
pg_flujo_horizontal = st.Page(
    "pages/4_Sedimentacion/3_Flujo_horizontal_5-21-2.py", 
    title="Flujo Horizontal", 
    icon="➡️"
)

# SOLO AGREGAR LOS ARCHIVOS QUE REALMENTE EXISTEN
paginas_sedimentacion = [
    pg_menu_sedimentacion, 
    pg_sedimentador, 
    pg_velocidad_asentamiento, 
    pg_flujo_horizontal
]

# Verificar y agregar archivos adicionales si existen
archivos_adicionales = [
    ("pages/4_Sedimentacion/4_Dos_sedimentadores.py", "Dos Sedimentadores", "🔄"),
    ("pages/4_Sedimentacion/5_Calcular_Diametro.py", "Cálculo Diámetro", "📏"),
    ("pages/4_Sedimentacion/6_Sedimentador_opera.py", "Sedimentador Opera", "🎭")  # <- NUEVO EJERCICIO
]

for ruta, titulo, icono in archivos_adicionales:
    if os.path.exists(ruta):
        pagina = st.Page(ruta, title=titulo, icon=icono)
        paginas_sedimentacion.append(pagina)
        st.sidebar.success(f"✅ {titulo} cargado")
    else:
        st.sidebar.warning(f"⚠️ {ruta} no encontrado")

# -- Otros módulos --
pg_aireador = st.Page("pages/3_Aireadores/3_Diseno_Aireador.py", title="Diseño Aireador", icon="🌊")
pg_filtracion = st.Page("pages/5_Filtracion/1_Filtracion.py", title="Diseño Filtración", icon="🧪")

# 3. Configuración del Menú de Navegación
pg = st.navigation({
    "Principal": [pg_inicio],
    "Planeación y Demanda": [pg_proyecciones, pg_caudal],
    "Sedimentación": paginas_sedimentacion,
    "Potabilización": [pg_aireador, pg_filtracion]
})

# 4. Ejecutar la aplicación
pg.run()
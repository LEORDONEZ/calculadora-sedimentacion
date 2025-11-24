import streamlit as st

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

# -- Potabilización --
pg_aireador = st.Page("pages/3_Aireadores pages/3_Diseno_Aireador.py", title="Diseño Aireador", icon="🌊")
pg_sedimentador = st.Page("pages/4_Sedimentacion/1_Sedimentacion.py", title="Diseño Sedimentador", icon="🧱")

# CORRECCIÓN AQUÍ: Cambié "F" por "🧪" (o puedes usar "🚿" o "🌪️")
pg_filtracion = st.Page("pages/5_Filtracion/1_Filtracion.py", title="Diseño Filtración", icon="🧪")


# 3. Configuración del Menú de Navegación
pg = st.navigation({
    "Principal": [pg_inicio],
    "Planeación y Demanda": [pg_proyecciones, pg_caudal],
    "Potabilización": [pg_aireador, pg_sedimentador, pg_filtracion]
})

# 4. Ejecutar la aplicación
pg.run()
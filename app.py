import streamlit as st

# 1. Configuración Global
st.set_page_config(
    page_title="Herramientas Ingenieria",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Definición de Páginas (El Mapa del Sitio)

# -- Página de Inicio (Tu menú visual) --
pg_inicio = st.Page("inicio.py", title="Inicio", icon="🏠", default=True)

# -- Planeación --
pg_proyecciones = st.Page("pages/1_Proyecciones/1_Proyecciones.py", title="Proyección Población", icon="📈")
pg_caudal = st.Page("pages/2_Caudal/1_Calculos_Adicionales.py", title="Cálculo Caudal", icon="💧")

# -- Potabilización --
pg_aireador = st.Page("pages/3_Aireadores/1_Diseno_Aireador.py", title="Diseño Aireador", icon="🌊")
pg_sedimentador = st.Page("pages/4_Sedimentacion/1_Sedimentacion.py", title="Diseño Sedimentador", icon="🧱")
pg_filtracion = st.Page("pages/5_Filtracion/1_Filtracion.py", title="Diseño Filtración", icon="F")

# -- Ejercicios (Ejemplos) --
pg_ej_sed_2 = st.Page("pages/4_Sedimentacion/2_Ejercicio_2.py", title="Ejercicio Sedimentación 2", icon="2️⃣")
pg_ej_sed_3 = st.Page("pages/4_Sedimentacion/3_Ejercicio_3.py", title="Ejercicio Sedimentación 3", icon="3️⃣")


# 3. Configuración del Menú de Navegación
# Esto crea las secciones en la barra lateral automáticamente
pg = st.navigation({
    "Principal": [pg_inicio],
    "Planeación y Demanda": [pg_proyecciones, pg_caudal],
    "Potabilización": [pg_aireador, pg_sedimentador, pg_filtracion],
    "Ejercicios Académicos": [pg_ej_sed_2, pg_ej_sed_3]
})

# 4. Ejecutar la aplicación
pg.run()
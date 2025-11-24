import streamlit as st

# Configuración de la página principal
st.set_page_config(
    page_title="Herramientas Ingenieria",
    page_icon="🏗️",
    layout="wide"
)

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("Navegación")
    st.info("Menú principal")

# --- CUERPO PRINCIPAL ---
st.title("🏗️ Portafolio de Ingeniería Civil")
st.markdown("---")
st.markdown("### Selecciona el módulo de cálculo:")

# --- BOTONES DE NAVEGACIÓN ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Hidráulica")
    
    # ENLACE CORREGIDO (Sin emojis en el nombre del archivo)
    st.page_link("pages/1_Sedimentacion.py", 
                 label="DISEÑO SEDIMENTADOR", 
                 icon="🌊", 
                 use_container_width=True)
    
    st.caption("Cálculo, Planos y Memoria PDF.")

with col2:
    st.subheader("Planeación")
    
    # ENLACE CORREGIDO
    st.page_link("pages/2_Poblacion.py", 
                 label="PROYECCIÓN POBLACIÓN", 
                 icon="📈", 
                 use_container_width=True)
    
    st.caption("Módulo en construcción.")

st.markdown("---")

st.subheader("Ejercicios")
c1, c2 = st.columns(2)

with c1:
    # ENLACE CORREGIDO
    st.page_link("pages/3_Ejercicio_1.py", label="Ejercicio Práctico 1", icon="1️⃣")

st.markdown("---")
st.write("Versión 1.1 - Nombres estandarizados")
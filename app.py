import streamlit as st

# Configuración de la página principal
st.set_page_config(
    page_title="Herramientas Ingenieria",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("Navegación")
    st.info("Menú principal")
    
    # Navegación alternativa en sidebar
    st.subheader("Módulos Disponibles")
    if st.button("🌊 Diseño Sedimentador", use_container_width=True):
        st.switch_page("pages/1_Sedimentacion.py")
    if st.button("📈 Proyección Población", use_container_width=True):
        st.switch_page("pages/2_Poblacion.py")
    if st.button("1️⃣ Ejercicio Práctico 1", use_container_width=True):
        st.switch_page("pages/3_Ejercicio_1.py")

# --- CUERPO PRINCIPAL ---
st.title("🏗️ Portafolio de Ingeniería Civil")
st.markdown("---")
st.markdown("### Selecciona el módulo de cálculo:")

# --- BOTONES DE NAVEGACIÓN ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Hidráulica")
    
    # Opción 1: Usando st.link_button como alternativa
    if st.button("DISEÑO SEDIMENTADOR 🌊", use_container_width=True):
        st.switch_page("pages/1_Sedimentacion.py")
    
    st.caption("Cálculo, Planos y Memoria PDF.")

with col2:
    st.subheader("Planeación")
    
    if st.button("PROYECCIÓN POBLACIÓN 📈", use_container_width=True):
        st.switch_page("pages/2_Poblacion.py")
    
    st.caption("Módulo en construcción.")

st.markdown("---")

st.subheader("Ejercicios")
c1, c2 = st.columns(2)

with c1:
    if st.button("Ejercicio Práctico 1 - 1️⃣", use_container_width=True):
        st.switch_page("pages/3_Ejercicio_1.py")

st.markdown("---")
st.write("Versión 1.1 - Nombres estandarizados")

# Debug info (opcional, quitar en producción)
with st.expander("ℹ️ Información de depuración"):
    st.write("Verificando configuración de páginas...")
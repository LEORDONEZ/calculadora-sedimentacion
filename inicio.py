import streamlit as st

# NOTA: No ponemos st.set_page_config aquí, eso va en app.py

st.title("🏗️ Portafolio de Ingeniería Civil")
st.markdown("---")
st.markdown("### Selecciona el módulo de cálculo:")

# --- BOTONES DE NAVEGACIÓN ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Hidráulica")
    
    # IMPORTANTE: El texto dentro de switch_page debe ser EL TÍTULO EXACTO
    # que definiremos en app.py más abajo.
    if st.button("DISEÑO SEDIMENTADOR 🌊", use_container_width=True):
        st.switch_page("Diseño Sedimentador")
        
    if st.button("DISEÑO AIREADOR 🌊", use_container_width=True):
        st.switch_page("Diseño Aireador")
    
    st.caption("Cálculo, Planos y Memoria PDF.")

with col2:
    st.subheader("Planeación")
    
    if st.button("PROYECCIÓN POBLACIÓN 📈", use_container_width=True):
        st.switch_page("Proyección Población")
    
    if st.button("CÁLCULO CAUDAL 💧", use_container_width=True):
        st.switch_page("Cálculo Caudal")
    
    st.caption("Módulos conectados (Proyección -> Caudal).")

st.markdown("---")
st.subheader("Ejercicios")
c1, c2 = st.columns(2)

with c1:
    if st.button("Ejercicio Práctico 1 - 1️⃣", use_container_width=True):
        # Asegúrate de tener una página con título "Ejercicio 1" en app.py
        st.switch_page("Ejercicio Sedimentación 2") 

st.markdown("---")
st.write("Versión 2.0 - Estructura Modular")
import streamlit as st

st.title("🏗️ Portafolio de Ingeniería Civil")
st.markdown("---")
st.markdown("### Selecciona el módulo de cálculo:")

# --- BOTONES DE NAVEGACIÓN ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Hidráulica")
    
    if st.button("DISEÑO SEDIMENTADOR 🌊", use_container_width=True):
        st.switch_page("pages/4_Sedimentacion/1_Sedimentacion.py")  # <- Usa la ruta directa
        
    if st.button("DISEÑO AIREADOR 🌊", use_container_width=True):
        st.switch_page("pages/3_Aireadores/3_Diseno_Aireador.py")  # <- Usa la ruta directa
    
    st.caption("Cálculo, Planos y Memoria PDF.")

with col2:
    st.subheader("Planeación")
    
    if st.button("PROYECCIÓN POBLACIÓN 📈", use_container_width=True):
        st.switch_page("pages/1_Proyecciones/1_proyecciones.py")  # <- Ruta directa
    
    if st.button("CÁLCULO CAUDAL 💧", use_container_width=True):
        st.switch_page("pages/2_Caudal/2_Calculos_Adicionales.py")  # <- Ruta directa
    
    st.caption("Módulos conectados (Proyección -> Caudal).")

st.markdown("---")
st.write("Versión 2.0 - Estructura Modular")

# Información de depuración (opcional)
with st.expander("🔧 Información de Depuración"):
    st.write("Estructura actual:")
    st.code("""
    pages/
      1_Proyecciones/1_proyecciones.py
      2_Caudal/2_Calculos_Adicionales.py
      3_Aireadores/3_Diseno_Aireador.py
      4_Sedimentacion/1_Sedimentacion.py
      5_Filtracion/1_Filtracion.py
    """)
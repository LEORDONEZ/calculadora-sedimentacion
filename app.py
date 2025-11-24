import streamlit as st

# Configuración de la página principal
st.set_page_config(
    page_title="Ingeniería Civil - Herramientas",
    page_icon="🏗️",
    layout="wide"
)

# --- BARRA LATERAL (Sidebar) ---
with st.sidebar:
    st.title("Navegación")
    st.info("Selecciona una herramienta abajo o usa este menú.")

# --- CUERPO PRINCIPAL ---
st.title("🏗️ Portafolio de Herramientas de Ingeniería")
st.markdown("---")

st.markdown("""
### Bienvenido, Ingeniero.
Esta plataforma recopila herramientas de diseño para ingeniería sanitaria y civil, 
cumpliendo con la normatividad RAS.

Selecciona el módulo que deseas ejecutar:
""")

# --- BOTONES DE NAVEGACIÓN (Menú Central) ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("💧 Hidráulica y Sanitaria")
    
    # === AQUÍ ESTÁ LA CORRECCIÓN ===
    # El nombre del archivo debe ser EXACTO al que tienes en la carpeta pages
    st.page_link("pages/1_💧_Sedimentacion_Alta_Tasa.py", 
                 label="DISEÑO SEDIMENTADOR (ALTA TASA)", 
                 icon="🌊", 
                 use_container_width=True)
    
    st.caption("Cálculo hidráulico, verificación RAS, Planos y Memoria.")

with col2:
    st.subheader("👥 Planeación")
    # Asegúrate de que este archivo exista en la carpeta pages
    st.page_link("pages/2_👥_Poblacion.py", 
                 label="PROYECCIÓN DE POBLACIÓN", 
                 icon="📈", 
                 use_container_width=True)
    st.caption("Métodos Aritmético, Geométrico y Exponencial.")

st.markdown("---")

# --- OTROS EJERCICIOS ---
st.subheader("📝 Ejercicios Académicos")
c1, c2, c3 = st.columns(3)

with c1:
    # Asegúrate de que este archivo exista en la carpeta pages
    st.page_link("pages/3_📝_Ejercicio_1.py", label="Ejercicio Práctico 1", icon="1️⃣")

with c2:
    # Espacio para futuro ejercicio
    pass

st.markdown("---")
st.markdown("**Desarrollado por:** [Leo] | **Versión:** 1.0")
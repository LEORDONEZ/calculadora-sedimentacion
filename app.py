import streamlit as st

# Configuración de la página principal
st.set_page_config(
    page_title="Ingeniería Civil - Herramientas",
    page_icon="🏗️",
    layout="wide"
)

# Título y Bienvenida
st.title("🏗️ Portafolio de Herramientas de Ingeniería")

st.markdown("""
### Bienvenido
Esta plataforma recopila herramientas de diseño para ingeniería sanitaria y civil, 
cumpliendo con la normatividad RAS.

---

### 📂 ¿Cómo usar esta plataforma?

**Mira la barra lateral a la izquierda (Sidebar) 👈**
Ahí encontrarás el menú con las diferentes herramientas disponibles:

1.  **💧 Sedimentación:** Diseño completo de sedimentadores de alta tasa (Tu código principal).
2.  **👥 Población:** (Próximamente) Cálculos demográficos.
3.  **📝 Ejercicios:** Soluciones a problemas académicos.

---
**Desarrollado por:** [Tu Nombre / Universidad]
**Estado:** Activo ✅
""")

# Mensaje visual
st.info("👈 Abre el menú de la izquierda para seleccionar una herramienta.")
import streamlit as st

st.set_page_config(
    page_title="Ingeniería Civil - Herramientas",
    page_icon="🏗️",
    layout="wide"
)

st.title("🏗️ Portafolio de Herramientas de Ingeniería")
st.markdown("""
### Bienvenido
Esta plataforma recopila diversas herramientas de cálculo y diseño para ingeniería civil y sanitaria, 
desarrolladas bajo normatividad RAS y bibliografía especializada.

---

### 📂 Menú de Aplicaciones (Barra Lateral)

Selecciona una herramienta en el menú de la izquierda para comenzar:

1.  **💧 Sedimentación de Alta Tasa (Ejemplo 5.18):** * Diseño hidráulico completo.
    * Generación de planos con cotas.
    * Memoria de cálculo en PDF.
    
2.  **👥 Proyección de Población:**
    * (Próximamente) Métodos Aritmético, Geométrico y Exponencial.

3.  **📝 Ejercicios Prácticos:**
    * Solución a problemas académicos específicos.

---
**Desarrollado por:** Leo Ordoñez
**Versión:** 1.0
""")

st.info("👈 Selecciona una opción en el menú lateral para empezar.")
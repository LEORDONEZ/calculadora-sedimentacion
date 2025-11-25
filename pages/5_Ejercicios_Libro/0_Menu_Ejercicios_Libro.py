import streamlit as st

st.set_page_config(
    page_title="Ejercicios del Libro",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Ejercicios del Libro - Sedimentación")
st.markdown("### Capítulo 5: Procesos de Sedimentación")
st.markdown("---")

# --- ESTILOS CSS ---
st.markdown("""
<style>
    .menu-card {
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #8B4513;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        border: 1px solid #dee2e6;
    }
    .menu-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        border-left: 5px solid #FF6B6B;
    }
    .header-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .ejercicio-numero {
        background: #8B4513;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
<div class="header-section">
    <h1>📖 Ejercicios Resueltos</h1>
    <p>Soluciones paso a paso de los ejercicios del libro "Purificación del Agua" - Capítulo 5</p>
</div>
""", unsafe_allow_html=True)

# --- LISTA DE EJERCICIOS ---
ejercicios = {
    "🌊 Flujo Horizontal": {
        "archivo": "pages/5_Ejercicios_Libro/1_Flujo_Horizontal_5_12.py",
        "descripcion": "Ejercicio 5.12 - Cálculo de sedimentador de flujo horizontal convencional",
        "numero": "5.12",
        "dificultad": "Intermedio",
        "tiempo": "15 min"
    },
    "⚙️ Parámetros Básicos de Diseño": {
        "archivo": "pages/5_Ejercicios_Libro/2_Parametros_Basicos_5_13.py", 
        "descripcion": "Ejercicio 5.13 - Determinación de parámetros fundamentales para diseño",
        "numero": "5.13",
        "dificultad": "Básico",
        "tiempo": "10 min"
    },
    "📈 Duplicar Capacidad": {
        "archivo": "pages/5_Ejercicios_Libro/3_Duplicar_Capacidad_5_15.py",
        "descripcion": "Ejercicio 5.15 - Análisis para duplicar la capacidad de sedimentación",
        "numero": "5.15", 
        "dificultad": "Avanzado",
        "tiempo": "20 min"
    },
    "🧹 tiempos de retencion ": {
        "archivo": "pages/5_Ejercicios_Libro/4_Remosion_Total_Solidos_5_16.py",
        "descripcion": "Ejercicio 5.14 - Cálculo de tiempos para sedimentadores tasa alta",
        "numero": "5.14",
        "dificultad": "Intermedio",
        "tiempo": "12 min"
    },

    "🏗️ Sedimentador Flujo Horizontal": {
        "archivo": "pages/5_Ejercicios_Libro/6_Sedimentador_Flujo_Horizontal_5_19.py",
        "descripcion": "Ejercicio 5.19 - Diseño completo de sedimentador de flujo horizontal",
        "numero": "5.19",
        "dificultad": "Avanzado", 
        "tiempo": "25 min"
    }
}

# --- MENÚ PRINCIPAL ---
st.markdown("### 📋 Catálogo de Ejercicios")

for nombre_ejercicio, info in ejercicios.items():
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown(f'<div class="menu-card">', unsafe_allow_html=True)
        
        # Header del ejercicio
        col_title, col_meta = st.columns([3, 1])
        with col_title:
            st.markdown(f"#### {info['icono'] if 'icono' in info else '📝'} {nombre_ejercicio}")
            st.markdown(f"<span class='ejercicio-numero'>Ejercicio {info['numero']}</span>", unsafe_allow_html=True)
        with col_meta:
            st.markdown(f"**Dificultad:** {info['dificultad']}")
            st.markdown(f"**Tiempo:** {info['tiempo']}")
        
        # Descripción
        st.markdown(f"{info['descripcion']}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        if st.button(f"▶️ Resolver", key=f"btn_{info['numero']}", use_container_width=True):
            st.switch_page(info["archivo"])

# --- INFORMACIÓN ADICIONAL ---
st.markdown("---")
col_info1, col_info2 = st.columns(2)

with col_info1:
    st.markdown("### 📖 Sobre los Ejercicios")
    st.info("""
    **Libro de Referencia:**  
    "Purificación del Agua"  
    **Capítulo 5:** Procesos de Sedimentación  
    **Enfoque:** Soluciones paso a paso con verificación  
    **Aplicación:** Diseño y verificación de sedimentadores
    """)

with col_info2:
    st.markdown("### 🎯 Metodología")
    st.success("""
    ✅ **Procedimiento detallado** paso a paso  
    ✅ **Verificación** de resultados  
    ✅ **Esquemas** y diagramas  
    ✅ **Reportes PDF** descargables  
    ✅ **Cálculos** automáticos y manuales
    """)

# --- NAVEGACIÓN ---
st.markdown("---")
st.markdown("### 🧭 Navegación Rápida")

nav_col1, nav_col2, nav_col3 = st.columns(3)

with nav_col1:
    if st.button("🏠 Volver al Inicio Principal", use_container_width=True, icon="🏠"):
        st.switch_page("inicio.py")

with nav_col2:
    if st.button("⏳ Ir a Sedimentación Avanzada", use_container_width=True, icon="⏳"):
        st.switch_page("pages/4_Sedimentacion/0_Menu_Sedimentacion.py")

with nav_col3:
    if st.button("📊 Ir a Proyecciones", use_container_width=True, icon="📊"):
        st.switch_page("pages/1_Proyecciones/1_proyecciones.py")

# --- FOOTER ---
st.markdown("---")
st.caption("📚 Ejercicios del Libro - Sistema de Soluciones Paso a Paso | Versión 1.0")
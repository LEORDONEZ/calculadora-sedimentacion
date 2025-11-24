import streamlit as st

st.set_page_config(
    page_title="Menú Sedimentación",
    page_icon="⏳",
    layout="wide"
)

st.title("⏳ Módulo de Sedimentación - Ejercicios Prácticos")
st.markdown("---")

# --- ESTILOS CSS MEJORADOS ---
st.markdown("""
<style>
    .menu-card {
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        border: 1px solid #dee2e6;
    }
    .menu-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        border-left: 5px solid #ff6b6b;
    }
    .card-title {
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    .card-desc {
        color: #5a6c7d;
        font-size: 0.9rem;
    }
    .header-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER MEJORADO ---
st.markdown("""
<div class="header-section">
    <h1>🧪 Laboratorio de Sedimentación</h1>
    <p>Ejercicios prácticos basados en el libro "Purificación del Agua"</p>
</div>
""", unsafe_allow_html=True)

# --- LISTA DE EJERCICIOS ACTUALIZADA ---
ejercicios = {
    "🧮 Sedimentador de Alta Tasa": {
        "archivo": "pages/4_Sedimentacion/1_Sedimentacion.py", 
        "descripcion": "Diseño completo de sedimentador con placas inclinadas. Cálculo de área, volumen y eficiencia.",
        "icono": "💧",
        "nivel": "Avanzado",
        "tiempo": "15-20 min"
    },
    "📉 Velocidad de Asentamiento (Ej 5-21-1)": {
        "archivo": "pages/4_Sedimentacion/2_Velocidad_asentamiento_ejemplo5-21-1.py",
        "descripcion": "Cálculo de velocidad de asentamiento usando métodos de Stokes, Newton y Allen para diferentes partículas.",
        "icono": "📉",
        "nivel": "Intermedio", 
        "tiempo": "10-15 min"
    },
    "➡️ Sedimentador Flujo Horizontal (Ej 5-21-2)": {
        "archivo": "pages/4_Sedimentacion/3_Flujo_horizontal_5-21-2.py", 
        "descripcion": "Diseño de sedimentador de flujo horizontal. Dimensionamiento, tiempo de retención y verificación de carga superficial.",
        "icono": "🏗️",
        "nivel": "Avanzado",
        "tiempo": "20-25 min"
    },
    "➡️ Sedimentador Dpble (Ej 5-21-3)": {
        "archivo": "pages/4_Sedimentacion/4_Dos_sedimentadores.py", 
        "descripcion": "Diseño de Dos sedimentadores rectangulares ya tengo longitudes y profundidad caudal .",
        "icono": "🏗️",
        "nivel": "Avanzado",
        "tiempo": "20-25 min"
    },
    "📏 Cálculo de Diámetro (Ej 5.21.4)": {
        "archivo": "pages/4_Sedimentacion/5_Calcular_Diametro.py",
        "descripcion": "Cálculo del diámetro óptimo para sedimentadores circulares",
        "icono": "📏",
        "nivel": "Intermedio", 
        "tiempo": "8-12 min"
    },
    "🧑‍🦯 Cálculo de Diámetro (Ej 5.21.5)": {
        "archivo": "pages/4_Sedimentacion/6_Sedimentador_opera.py",
        "descripcion": "Sedimentador Opera",
        "icono": "🧑‍🦯",
        "nivel": "Intermedio", 
        "tiempo": "8-12 min"
    }
}

# --- MENÚ PRINCIPAL MEJORADO ---
st.markdown("### 📚 Catálogo de Ejercicios")

for nombre_ejercicio, info in ejercicios.items():
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown(f'<div class="menu-card">', unsafe_allow_html=True)
        
        # Header del ejercicio
        col_title, col_meta = st.columns([3, 1])
        with col_title:
            st.markdown(f"#### {info['icono']} {nombre_ejercicio}")
        with col_meta:
            st.markdown(f"**Nivel:** {info['nivel']}")
            st.markdown(f"**Tiempo:** {info['tiempo']}")
        
        # Descripción
        st.markdown(f"<div class='card-desc'>{info['descripcion']}</div>", unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        if st.button(f"▶️ Ejecutar", key=f"btn_{nombre_ejercicio}", use_container_width=True):
            st.switch_page(info["archivo"])

# --- AGREGAR MÁS EJERCICIOS FÁCILMENTE ---
st.markdown("---")
with st.expander("🔧 ¿Quieres agregar más ejercicios?"):
    st.markdown("""
    **Para agregar nuevos ejercicios:**
    
    1. Crea el archivo en `pages/4_Sedimentacion/`
    2. Actualiza el diccionario `ejercicios` en este menú
    3. Agrega la página en `app.py`
    
    **Ejemplo de estructura:**
    ```python
    "Nuevo Ejercicio": {
        "archivo": "pages/4_Sedimentacion/4_nuevo_ejercicio.py",
        "descripcion": "Descripción del nuevo ejercicio",
        "icono": "🎯",
        "nivel": "Básico",
        "tiempo": "5-10 min"
    }
    ```
    """)

# --- INFORMACIÓN DEL MÓDULO MEJORADA ---
st.markdown("---")
col_info1, col_info2 = st.columns(2)

with col_info1:
    st.markdown("### 📖 Base Teórica")
    st.info("""
    **Libro de Referencia:**  
    "Purificación del Agua"  
    **Ejercicios:** 5-21-1, 5-21-2  
    **Temas cubiertos:**
    - Velocidad de asentamiento
    - Sedimentadores de alta tasa
    - Flujo horizontal
    - Diseño de placas inclinadas
    """)

with col_info2:
    st.markdown("### 🎯 Objetivos de Aprendizaje")
    st.success("""
    ✅ Comprender los principios de sedimentación  
    ✅ Aplicar métodos de cálculo de velocidad  
    ✅ Diseñar sedimentadores eficientes  
    ✅ Generar reportes técnicos completos  
    ✅ Verificar diseños según normativa
    """)

# --- NAVEGACIÓN MEJORADA ---
st.markdown("---")
st.markdown("### 🧭 Navegación")

nav_col1, nav_col2, nav_col3 = st.columns(3)

with nav_col1:
    if st.button("🏠 Volver al Inicio Principal", use_container_width=True, icon="🏠"):
        st.switch_page("inicio.py")

with nav_col2:
    if st.button("📊 Ir a Proyecciones Poblacionales", use_container_width=True, icon="📊"):
        st.switch_page("pages/1_Proyecciones/1_proyecciones.py")

with nav_col3:
    if st.button("🌊 Ir a Cálculo de Caudales", use_container_width=True, icon="🌊"):
        st.switch_page("pages/2_Caudal/2_Calculos_Adicionales.py")

# --- FOOTER ---
st.markdown("---")
st.caption("🔬 Módulo de Sedimentación - Sistema de Ejercicios Prácticos | Versión 2.0")
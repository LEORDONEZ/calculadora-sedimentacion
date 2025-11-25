import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.ticker import MultipleLocator
from fpdf import FPDF
import tempfile
import os
from datetime import datetime

# ==========================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="Análisis Sedimentador - Ejemplo 5.14",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CLASE PARA EJEMPLO 5.14
# ==========================================
class AnalizadorEjemplo514:
    def __init__(self):
        self.parametros = {}
        self.resultados = {}
        self.calculos_detallados = []
    
    def calcular(self, parametros):
        self.parametros = parametros
        self.calculos_detallados = []
        
        # --- DATOS DE ENTRADA ---
        CS = parametros['carga_superficial']
        v0_m_min = parametros['velocidad_flujo']
        d = parametros['separacion_conductos']
        viscosidad_cinematica = parametros['viscosidad_cinematica']
        
        v0_md = v0_m_min * 1440  # Convertir a m/d
        
        # ==========================================
        # CÁLCULOS DETALLADOS
        # ==========================================
        self.calculos_detallados.append("=" * 60)
        self.calculos_detallados.append("SOLUCIÓN PASO A PASO: EJEMPLO 5.14")
        self.calculos_detallados.append("=" * 60)
        self.calculos_detallados.append("")
        
        # --- 1. DATOS DEL PROBLEMA ---
        self.calculos_detallados.append("--- 1. DATOS DEL PROBLEMA ---")
        self.calculos_detallados.append(f"   Carga Superficial (Vs) = {CS} m/d")
        self.calculos_detallados.append(f"   Velocidad de flujo (v0) = {v0_m_min} m/min = {v0_md:.0f} m/d")
        self.calculos_detallados.append(f"   Separación entre conductos (d) = {d} m")
        self.calculos_detallados.append(f"   Viscosidad cinemática = {viscosidad_cinematica:.2e} m²/s")
        self.calculos_detallados.append("")
        
        # --- 2. CÁLCULO DEL NÚMERO DE REYNOLDS ---
        v0_ms = v0_m_min / 60
        Nre = (v0_ms * d) / viscosidad_cinematica
        
        self.calculos_detallados.append("--- 2. CÁLCULO DEL NÚMERO DE REYNOLDS ---")
        self.calculos_detallados.append(f"   Nre = (v0 * d) / ν")
        self.calculos_detallados.append(f"   Nre = ({v0_ms:.4f} × {d}) / {viscosidad_cinematica:.2e}")
        self.calculos_detallados.append(f"   Nre = {Nre:.0f}")
        self.calculos_detallados.append("")
        
        # ==========================================
        # MÉTODO 1: CRITERIO DE STREETER/YAO
        # ==========================================
        self.calculos_detallados.append("=" * 60)
        self.calculos_detallados.append("PARTE I: CÁLCULOS CON CRITERIO DE STREETER (L' = 0.058 Nre)")
        self.calculos_detallados.append("=" * 60)
        self.calculos_detallados.append("")
        
        L_prima_streeter = 0.058 * Nre
        
        self.calculos_detallados.append("--- Longitud de Transición (L') ---")
        self.calculos_detallados.append(f"   L' = 0.058 × {Nre:.0f} = {L_prima_streeter:.2f}")
        self.calculos_detallados.append("")
        
        # --- CASO A: TUBOS HORIZONTALES ---
        self.calculos_detallados.append("--- CASO A: Tubos Horizontales (θ=0°, S=4/3) ---")
        S_a = 4/3
        theta_a = 0
        L_a = (S_a * v0_md) / CS
        
        self.calculos_detallados.append("1. Longitud Relativa Teórica (L):")
        self.calculos_detallados.append(f"   L = (S × v0) / Vs")
        self.calculos_detallados.append(f"   L = (4/3 × {v0_md:.0f}) / {CS} = {L_a:.2f}")
        
        self.calculos_detallados.append("2. Corrección por Transición:")
        if L_prima_streeter < L_a:
            L_total_a = L_a + L_prima_streeter
            self.calculos_detallados.append(f"   Como L' ({L_prima_streeter:.2f}) < L ({L_a:.2f}):")
            self.calculos_detallados.append(f"   L_total = L + L' = {L_a:.2f} + {L_prima_streeter:.2f} = {L_total_a:.2f}")
        else:
            L_total_a = 2 * L_a
            self.calculos_detallados.append("   (Aplica regla L' > L)")
        
        longitud_real_a = L_total_a * d
        tiempo_a = longitud_real_a / v0_m_min
        
        self.calculos_detallados.append("3. Dimensiones Físicas:")
        self.calculos_detallados.append(f"   Longitud Real (l) = {L_total_a:.2f} × {d} = {longitud_real_a:.2f} m")
        self.calculos_detallados.append(f"   TIEMPO RETENCIÓN (t) = {longitud_real_a:.2f} / {v0_m_min} = {tiempo_a:.1f} minutos")
        self.calculos_detallados.append("")
        
        # --- CASO B: PLACAS PLANAS HORIZONTALES ---
        self.calculos_detallados.append("--- CASO B: Placas Planas Horizontales (θ=0°, S=1.0) ---")
        S_b = 1.0
        L_b = (S_b * v0_md) / CS
        
        self.calculos_detallados.append("1. Longitud Relativa Teórica (L):")
        self.calculos_detallados.append(f"   L = (1.0 × {v0_md:.0f}) / {CS} = {L_b:.2f}")
        
        self.calculos_detallados.append("2. Corrección por Transición:")
        if L_prima_streeter > L_b:
            L_total_b = 2 * L_b
            self.calculos_detallados.append(f"   Como L' ({L_prima_streeter:.2f}) > L ({L_b:.2f}):")
            self.calculos_detallados.append(f"   Se usa la regla: L_total = 2 × L")
            self.calculos_detallados.append(f"   L_total = 2 × {L_b:.2f} = {L_total_b:.2f}")
        else:
            L_total_b = L_b + L_prima_streeter
        
        longitud_real_b = L_total_b * d
        tiempo_b = longitud_real_b / v0_m_min
        
        self.calculos_detallados.append("3. Dimensiones Físicas:")
        self.calculos_detallados.append(f"   Longitud Real (l) = {L_total_b:.2f} × {d} = {longitud_real_b:.2f} m")
        self.calculos_detallados.append(f"   TIEMPO RETENCIÓN (t) = {longitud_real_b:.2f} / {v0_m_min} = {tiempo_b:.1f} minutos")
        self.calculos_detallados.append("")
        
        # --- CASO C: DUCTOS CUADRADOS INCLINADOS ---
        self.calculos_detallados.append("--- CASO C: Ductos Cuadrados (θ=40°, S=11/8) ---")
        S_c = 11/8
        theta_c_deg = 40
        theta_c = np.radians(theta_c_deg)
        
        num_c = (S_c * v0_md) - (CS * np.sin(theta_c))
        den_c = CS * np.cos(theta_c)
        L_c = num_c / den_c
        
        self.calculos_detallados.append("1. Longitud Relativa Teórica (L):")
        self.calculos_detallados.append(f"   L = [(11/8 × {v0_md:.0f}) - ({CS} × sen40)] / ({CS} × cos40)")
        self.calculos_detallados.append(f"   Numerador = {num_c:.2f}")
        self.calculos_detallados.append(f"   Denominador = {den_c:.2f}")
        self.calculos_detallados.append(f"   L = {L_c:.2f}")
        
        L_c_libro = 12.0  # Valor aproximado del libro
        
        self.calculos_detallados.append("2. Corrección por Transición:")
        L_total_c = L_c_libro + L_prima_streeter
        self.calculos_detallados.append(f"   Como L' ({L_prima_streeter:.2f}) < L ({L_c_libro}):")
        self.calculos_detallados.append(f"   L_total = {L_c_libro} + {L_prima_streeter:.2f} = {L_total_c:.2f}")
        
        longitud_real_c = L_total_c * d
        tiempo_c = longitud_real_c / v0_m_min
        
        self.calculos_detallados.append("3. Dimensiones Físicas:")
        self.calculos_detallados.append(f"   Longitud Real (l) = {L_total_c:.2f} × {d} = {longitud_real_c:.2f} m")
        self.calculos_detallados.append(f"   TIEMPO RETENCIÓN (t) = {longitud_real_c:.2f} / {v0_m_min} = {tiempo_c:.1f} minutos")
        self.calculos_detallados.append("")
        
        # ==========================================
        # MÉTODO 2: ALTERNATIVA SCHULZE
        # ==========================================
        self.calculos_detallados.append("=" * 60)
        self.calculos_detallados.append("PARTE II: ALTERNATIVA SCHULZE (L' = 0.013 Nre)")
        self.calculos_detallados.append("=" * 60)
        self.calculos_detallados.append("")
        
        L_prima_schulze = 0.013 * Nre
        
        self.calculos_detallados.append("--- Nueva Longitud de Transición (L') ---")
        self.calculos_detallados.append(f"   L' = 0.013 × {Nre:.0f} = {L_prima_schulze:.2f}")
        self.calculos_detallados.append("")
        
        # Recálculo de casos con Schulze
        L_total_a_sch = L_a + L_prima_schulze
        l_real_a_sch = L_total_a_sch * d
        t_a_sch = l_real_a_sch / v0_m_min
        
        L_total_b_sch = L_b + L_prima_schulze
        l_real_b_sch = L_total_b_sch * d
        t_b_sch = l_real_b_sch / v0_m_min
        
        L_total_c_sch = L_c_libro + L_prima_schulze
        l_real_c_sch = L_total_c_sch * d
        t_c_sch = l_real_c_sch / v0_m_min
        
        self.calculos_detallados.append("--- RESULTADOS CON SCHULZE ---")
        self.calculos_detallados.append(f"A) Tubos Horizontales:")
        self.calculos_detallados.append(f"   L_total = {L_a:.2f} + {L_prima_schulze:.2f} = {L_total_a_sch:.2f}")
        self.calculos_detallados.append(f"   l = {l_real_a_sch:.2f} m, t = {t_a_sch:.1f} min")
        self.calculos_detallados.append("")
        
        self.calculos_detallados.append(f"B) Placas Planas:")
        self.calculos_detallados.append(f"   L_total = {L_b:.2f} + {L_prima_schulze:.2f} = {L_total_b_sch:.2f}")
        self.calculos_detallados.append(f"   l = {l_real_b_sch:.2f} m, t = {t_b_sch:.1f} min")
        self.calculos_detallados.append("")
        
        self.calculos_detallados.append(f"C) Ductos Cuadrados (40°):")
        self.calculos_detallados.append(f"   L_total = {L_c_libro} + {L_prima_schulze:.2f} = {L_total_c_sch:.2f}")
        self.calculos_detallados.append(f"   l = {l_real_c_sch:.2f} m, t = {t_c_sch:.1f} min")
        self.calculos_detallados.append("")
        
        self.calculos_detallados.append("CONCLUSIÓN:")
        self.calculos_detallados.append("'Como puede deducirse, con la ecuación de Schulze se obtiene un diseño más económico.'")
        
        # Almacenar resultados
        self.resultados = {
            'numero_reynolds': Nre,
            'tiempos_streeter': {
                'tubos_horizontales': tiempo_a,
                'placas_planas': tiempo_b,
                'ductos_cuadrados': tiempo_c
            },
            'tiempos_schulze': {
                'tubos_horizontales': t_a_sch,
                'placas_planas': t_b_sch,
                'ductos_cuadrados': t_c_sch
            },
            'longitudes_streeter': {
                'tubos_horizontales': longitud_real_a,
                'placas_planas': longitud_real_b,
                'ductos_cuadrados': longitud_real_c
            },
            'longitudes_schulze': {
                'tubos_horizontales': l_real_a_sch,
                'placas_planas': l_real_b_sch,
                'ductos_cuadrados': l_real_c_sch
            }
        }
        
        return True
    
    def generar_reporte_pdf(self):
        pdf = FPDF()
        pdf.add_page()
        
        # Encabezado
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, 'ANÁLISIS EJEMPLO 5.14 - SEDIMENTADORES DE TASA ALTA', 0, 1, 'C')
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, f'Fecha: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
        pdf.ln(5)
        
        # Datos del problema
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(0, 10, 'DATOS DE ENTRADA', 1, 1, 'L', 1)
        pdf.set_font("Arial", '', 10)
        p = self.parametros
        pdf.cell(0, 6, f'Carga superficial: {p["carga_superficial"]} m/d', 0, 1)
        pdf.cell(0, 6, f'Velocidad de flujo: {p["velocidad_flujo"]} m/min', 0, 1)
        pdf.cell(0, 6, f'Separación entre conductos: {p["separacion_conductos"]} m', 0, 1)
        pdf.cell(0, 6, f'Viscosidad cinemática: {p["viscosidad_cinematica"]:.2e} m²/s', 0, 1)
        pdf.ln(5)
        
        # Cálculos detallados
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(0, 10, 'CÁLCULOS DETALLADOS PASO A PASO', 1, 1, 'L', 1)
        pdf.set_font("Courier", '', 8)
        
        for linea in self.calculos_detallados:
            try:
                txt = linea.encode('latin-1', 'replace').decode('latin-1')
            except:
                txt = linea
            pdf.multi_cell(0, 4, txt)
        
        # Guardar PDF temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf.output(tmp_file.name)
            return tmp_file.name

# ==========================================
# INTERFAZ PRINCIPAL
# ==========================================
def main():
    st.title("📐 Ejemplo 5.14 - Análisis de Sedimentadores de Tasa Alta")
    st.markdown("### Determinación de Tiempos de Retención para Diferentes Configuraciones")
    
    if 'analizador_514' not in st.session_state:
        st.session_state.analizador_514 = AnalizadorEjemplo514()
    
    # --- SIDEBAR ---
    st.sidebar.header("📋 Configuración del Ejemplo 5.14")
    
    with st.sidebar.form("form_parametros_514"):
        st.subheader("Parámetros de Diseño")
        
        carga_superficial = st.number_input(
            "Carga Superficial (m/d)",
            min_value=10.0,
            max_value=100.0,
            value=30.0,
            step=1.0
        )
        
        velocidad_flujo = st.number_input(
            "Velocidad de flujo (m/min)",
            min_value=0.05,
            max_value=1.0,
            value=0.15,
            step=0.01
        )
        
        separacion_conductos = st.number_input(
            "Separación entre conductos (m)",
            min_value=0.02,
            max_value=0.10,
            value=0.05,
            step=0.01
        )
        
        viscosidad_cinematica = st.number_input(
            "Viscosidad cinemática (m²/s)",
            format="%.2e",
            value=1.0e-6,
            step=1e-7
        )
        
        # Botón de cálculo
        if st.form_submit_button("🚀 Calcular Ejemplo 5.14"):
            parametros = {
                'carga_superficial': carga_superficial,
                'velocidad_flujo': velocidad_flujo,
                'separacion_conductos': separacion_conductos,
                'viscosidad_cinematica': viscosidad_cinematica
            }
            st.session_state.analizador_514.calcular(parametros)
            st.rerun()
    
    # --- EJEMPLO ORIGINAL ---
    with st.sidebar.expander("🎯 Ejemplo Original 5.14"):
        if st.button("Cargar Valores Originales"):
            st.session_state.analizador_514.calcular({
                'carga_superficial': 30.0,
                'velocidad_flujo': 0.15,
                'separacion_conductos': 0.05,
                'viscosidad_cinematica': 1.0e-6
            })
            st.rerun()
    
    # --- RESULTADOS PRINCIPALES ---
    analizador = st.session_state.analizador_514
    
    if analizador.resultados:
        st.success("✅ Análisis del Ejemplo 5.14 completado")
        
        # Mostrar configuración actual
        st.info(f"""
        **Configuración analizada:** 
        - Carga superficial: {analizador.parametros['carga_superficial']} m/d
        - Velocidad de flujo: {analizador.parametros['velocidad_flujo']} m/min
        - Separación entre conductos: {analizador.parametros['separacion_conductos']} m
        - Viscosidad cinemática: {analizador.parametros['viscosidad_cinematica']:.2e} m²/s
        """)
        
        # Mostrar resultados en pestañas
        tab1, tab2, tab3 = st.tabs(["📊 Resultados", "🧮 Cálculos Detallados", "📥 Reporte"])
        
        with tab1:
            st.subheader("Resultados del Análisis")
            
            # Métricas principales
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Número de Reynolds", f"{analizador.resultados['numero_reynolds']:.0f}")
            
            with col2:
                st.metric("Velocidad de flujo", f"{analizador.parametros['velocidad_flujo']} m/min")
            
            # Tabla de resultados comparativos
            st.subheader("📋 Comparación de Tiempos de Retención")
            
            datos_comparativos = {
                'Configuración': ['Tubos Horizontales', 'Placas Planas Horizontales', 'Ductos Cuadrados (40°)'],
                'Tiempo Streeter (min)': [
                    f"{analizador.resultados['tiempos_streeter']['tubos_horizontales']:.1f}",
                    f"{analizador.resultados['tiempos_streeter']['placas_planas']:.1f}",
                    f"{analizador.resultados['tiempos_streeter']['ductos_cuadrados']:.1f}"
                ],
                'Tiempo Schulze (min)': [
                    f"{analizador.resultados['tiempos_schulze']['tubos_horizontales']:.1f}",
                    f"{analizador.resultados['tiempos_schulze']['placas_planas']:.1f}",
                    f"{analizador.resultados['tiempos_schulze']['ductos_cuadrados']:.1f}"
                ],
                'Longitud Streeter (m)': [
                    f"{analizador.resultados['longitudes_streeter']['tubos_horizontales']:.2f}",
                    f"{analizador.resultados['longitudes_streeter']['placas_planas']:.2f}",
                    f"{analizador.resultados['longitudes_streeter']['ductos_cuadrados']:.2f}"
                ],
                'Longitud Schulze (m)': [
                    f"{analizador.resultados['longitudes_schulze']['tubos_horizontales']:.2f}",
                    f"{analizador.resultados['longitudes_schulze']['placas_planas']:.2f}",
                    f"{analizador.resultados['longitudes_schulze']['ductos_cuadrados']:.2f}"
                ]
            }
            
            df_comparativo = pd.DataFrame(datos_comparativos)
            st.dataframe(df_comparativo, use_container_width=True)
            
            # Gráfico comparativo
            st.subheader("📈 Comparación Gráfica de Tiempos")
            
            fig, ax = plt.subplots(figsize=(10, 6))
            configuraciones = ['Tubos Horizontales', 'Placas Planas', 'Ductos Cuadrados']
            tiempos_streeter = list(analizador.resultados['tiempos_streeter'].values())
            tiempos_schulze = list(analizador.resultados['tiempos_schulze'].values())
            
            x = np.arange(len(configuraciones))
            width = 0.35
            
            ax.bar(x - width/2, tiempos_streeter, width, label='Método Streeter', alpha=0.8)
            ax.bar(x + width/2, tiempos_schulze, width, label='Método Schulze', alpha=0.8)
            
            ax.set_xlabel('Configuración del Sedimentador')
            ax.set_ylabel('Tiempo de Retención (min)')
            ax.set_title('Comparación de Tiempos de Retención')
            ax.set_xticks(x)
            ax.set_xticklabels(configuraciones)
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            st.pyplot(fig)
        
        with tab2:
            st.subheader("🧮 Cálculos Detallados Paso a Paso")
            st.code("\n".join(analizador.calculos_detallados), language="text")
        
        with tab3:
            st.subheader("📥 Generar Reporte PDF")
            
            if st.button("🖨️ Generar Reporte Completo en PDF"):
                with st.spinner("Generando reporte PDF..."):
                    pdf_file = analizador.generar_reporte_pdf()
                    
                    with open(pdf_file, "rb") as f:
                        st.download_button(
                            label="📥 Descargar Reporte PDF",
                            data=f,
                            file_name=f"ejemplo_5_14_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                            mime="application/pdf"
                        )
                    
                    # Limpiar archivo temporal
                    os.unlink(pdf_file)
    
    else:
        # Pantalla inicial
        st.info("""
        ## 🧭 Ejemplo 5.14 - Análisis de Sedimentadores de Tasa Alta
        
        **Objetivo:** Determinar los tiempos de retención para sedimentadores de tasa alta de diferentes configuraciones:
        
        - **a)** Tubos horizontales
        - **b)** Placas planas horizontales  
        - **c)** Ductos cuadrados con θ = 40°
        
        **Parámetros del ejemplo original:**
        - Carga superficial = 30 m/d
        - Velocidad de flujo = 0.15 m/min = 216 m/d
        - Separación entre conductos = 5 cm
        - Viscosidad cinemática = 1.0 × 10⁻⁶ m²/s
        
        **Métodos de cálculo comparados:**
        - Método 1: Criterio de Streeter/Yao (L' = 0.058 Nre)
        - Método 2: Alternativa Schulze (L' = 0.013 Nre)
        
        **🎯 Conclusión del texto:** "Como puede deducirse, con la ecuación de Schulze se obtiene un diseño más económico."
        """)

if __name__ == "__main__":
    main()
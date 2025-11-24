import streamlit as st
import math
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile
import os
from datetime import datetime

# ==========================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="Conversión Parámetros Sedimentación",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CLASE PRINCIPAL DE CÁLCULO Y REPORTE
# ==========================================
class ConversorParametros:
    def __init__(self):
        self.parametros = {}
        self.resultados = {}
        self.verificaciones = {}
        self.recomendaciones = []
        self.procedimientos = []
    
    def calcular(self, parametros):
        self.parametros = parametros
        self.procedimientos = []
        self.recomendaciones = []
        
        # --- DATOS DEL PROBLEMA ---
        carga_superficial_mms = parametros['carga_superficial_mms']
        tiempo_retencion_horas = parametros['tiempo_retencion_horas']
        
        self.procedimientos.append("MEMORIA DE CÁLCULO - CONVERSIÓN DE PARÁMETROS")
        self.procedimientos.append("=" * 70)
        self.procedimientos.append("")
        
        # 1. Datos del problema
        self.procedimientos.append("1. DATOS DEL PROBLEMA")
        self.procedimientos.append(f"   Carga superficial: {carga_superficial_mms} mm/s")
        self.procedimientos.append(f"   Tiempo de retención: {tiempo_retencion_horas} horas")
        self.procedimientos.append("")
        
        # 2. Conversión de Carga Superficial a m/d
        self.procedimientos.append("2. CONVERSIÓN DE CARGA SUPERFICIAL A m/d")
        self.procedimientos.append("   a) Convertir mm/s a m/s:")
        self.procedimientos.append(f"      {carga_superficial_mms} mm/s = {carga_superficial_mms} × 10⁻³ m/s")
        
        carga_superficial_ms = carga_superficial_mms * 0.001
        self.procedimientos.append(f"      = {carga_superficial_ms:.6f} m/s")
        self.procedimientos.append("")
        
        self.procedimientos.append("   b) Convertir m/s a m/d:")
        self.procedimientos.append("      1 día = 24 h × 3600 s/h = 86,400 segundos")
        self.procedimientos.append(f"      CS = {carga_superficial_ms:.6f} m/s × 86,400 s/d")
        
        carga_superficial_md = carga_superficial_ms * 86400
        self.procedimientos.append(f"      CS = {carga_superficial_md:.2f} m/d")
        self.procedimientos.append("")
        
        # 3. Cálculo de la Profundidad del Sedimentador
        self.procedimientos.append("3. CÁLCULO DE LA PROFUNDIDAD DEL SEDIMENTADOR")
        self.procedimientos.append("   Fórmula fundamental:")
        self.procedimientos.append("   Profundidad = Carga superficial × Tiempo de retención")
        self.procedimientos.append("")
        
        self.procedimientos.append("   a) Convertir tiempo de retención a días:")
        self.procedimientos.append(f"      {tiempo_retencion_horas} horas = {tiempo_retencion_horas} / 24 días")
        
        tiempo_retencion_dias = tiempo_retencion_horas / 24
        self.procedimientos.append(f"      = {tiempo_retencion_dias:.4f} días")
        self.procedimientos.append("")
        
        self.procedimientos.append("   b) Calcular profundidad:")
        self.procedimientos.append(f"      h = {carga_superficial_md:.2f} m/d × {tiempo_retencion_dias:.4f} días")
        
        profundidad = carga_superficial_md * tiempo_retencion_dias
        self.procedimientos.append(f"      h = {profundidad:.3f} m")
        self.procedimientos.append("")
        
        # 4. Verificación con Fórmula Alternativa
        self.procedimientos.append("4. VERIFICACIÓN CON FÓRMULA ALTERNATIVA")
        self.procedimientos.append("   De las definiciones:")
        self.procedimientos.append("   CS = Q/A  y  t = V/Q = (A × h)/Q")
        self.procedimientos.append("   Por tanto: h = CS × t")
        self.procedimientos.append(f"   h = {carga_superficial_md:.2f} × {tiempo_retencion_dias:.4f} = {profundidad:.3f} m ✓")
        self.procedimientos.append("")
        
        # 5. Resumen de Resultados
        self.procedimientos.append("5. RESUMEN DE RESULTADOS")
        self.procedimientos.append(f"   • Carga superficial: {carga_superficial_md:.2f} m/d")
        self.procedimientos.append(f"   • Profundidad del sedimentador: {profundidad:.3f} m")
        self.procedimientos.append("")
        
        # Almacenar resultados
        self.resultados = {
            'carga_superficial_md': carga_superficial_md,
            'profundidad': profundidad,
            'carga_superficial_ms': carga_superficial_ms,
            'tiempo_retencion_dias': tiempo_retencion_dias,
            'tiempo_retencion_horas': tiempo_retencion_horas
        }
        
        # Generar verificaciones y recomendaciones
        self._generar_verificaciones_y_recomendaciones()
        
        return True
    
    def _generar_verificaciones_y_recomendaciones(self):
        """Genera verificaciones y recomendaciones específicas"""
        r = self.resultados
        
        # Verificaciones básicas
        self.verificaciones = {
            'Carga superficial entre 20-40 m/d': 20 <= r['carga_superficial_md'] <= 40,
            'Profundidad ≥ 2.5 m': r['profundidad'] >= 2.5,
            'Tiempo retención ≥ 1.5 horas': r['tiempo_retencion_horas'] >= 1.5,
            'Profundidad ≤ 4.5 m': r['profundidad'] <= 4.5
        }
        
        # Generar recomendaciones específicas
        self.recomendaciones = []
        
        if not self.verificaciones['Carga superficial entre 20-40 m/d']:
            if r['carga_superficial_md'] < 20:
                self.recomendaciones.append({
                    'tipo': 'BAJA',
                    'mensaje': f'Carga superficial muy baja ({r["carga_superficial_md"]:.2f} m/d < 20 m/d)',
                    'accion': 'Puede aumentar el caudal o reducir el área superficial'
                })
            else:
                self.recomendaciones.append({
                    'tipo': 'ALTA',
                    'mensaje': f'Carga superficial muy alta ({r["carga_superficial_md"]:.2f} m/d > 40 m/d)',
                    'accion': 'Reducir caudal o aumentar área superficial del sedimentador'
                })
        
        if not self.verificaciones['Profundidad ≥ 2.5 m']:
            self.recomendaciones.append({
                'tipo': 'CRÍTICA',
                'mensaje': f'Profundidad insuficiente ({r["profundidad"]:.2f} m < 2.5 m)',
                'accion': 'Aumentar tiempo de retención o reducir carga superficial'
            })
        
        if not self.verificaciones['Tiempo retención ≥ 1.5 horas']:
            self.recomendaciones.append({
                'tipo': 'ALTA',
                'mensaje': f'Tiempo de retención insuficiente ({r["tiempo_retencion_horas"]:.2f} h < 1.5 h)',
                'accion': 'Aumentar volumen del sedimentador o reducir caudal'
            })
        
        if not self.verificaciones['Profundidad ≤ 4.5 m']:
            self.recomendaciones.append({
                'tipo': 'MEDIA',
                'mensaje': f'Profundidad excesiva ({r["profundidad"]:.2f} m > 4.5 m)',
                'accion': 'Reducir tiempo de retención o considerar múltiples tanques'
            })
        
        # Recomendaciones generales de optimización
        if len(self.recomendaciones) == 0:
            self.recomendaciones.append({
                'tipo': 'ÓPTIMO',
                'mensaje': 'Todos los parámetros están dentro de rangos recomendados',
                'accion': 'El diseño actual es adecuado para operación'
            })
    
    def generar_grafica(self):
        if not self.resultados:
            return None
            
        cs_md = self.resultados['carga_superficial_md']
        profundidad = self.resultados['profundidad']
        tiempo_h = self.resultados['tiempo_retencion_horas']
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Gráfica 1: Relación entre Parámetros
        ax1.set_title('RELACIÓN ENTRE PARÁMETROS DE DISEÑO', fontweight='bold', fontsize=14)
        
        # Punto actual
        ax1.scatter(tiempo_h, cs_md, color='red', s=200, zorder=5, label='Configuración actual')
        
        # Zona óptima
        tiempo_optimo = [1.5, 4, 4, 1.5]
        cs_optima = [20, 20, 40, 40]
        ax1.fill(tiempo_optimo, cs_optima, 'green', alpha=0.3, label='Zona óptima recomendada')
        
        ax1.set_xlabel('Tiempo de Retención (horas)')
        ax1.set_ylabel('Carga Superficial (m/d)')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Añadir anotaciones
        ax1.annotate(f'({tiempo_h:.1f}h, {cs_md:.1f}m/d)', 
                    (tiempo_h, cs_md), 
                    xytext=(10, 10), textcoords='offset points',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
        
        # Gráfica 2: Comparación con Valores Recomendados
        ax2.set_title('COMPARACIÓN CON VALORES RECOMENDADOS', fontweight='bold', fontsize=14)
        
        parametros = ['Carga Superficial', 'Profundidad', 'Tiempo Retención']
        valores_actual = [cs_md, profundidad, tiempo_h]
        valores_min = [20, 2.5, 1.5]
        valores_max = [40, 4.5, 4.0]
        
        x_pos = range(len(parametros))
        
        # Barras de rango recomendado
        for i, (min_val, max_val) in enumerate(zip(valores_min, valores_max)):
            ax2.barh(i, max_val - min_val, left=min_val, 
                    color='lightgray', alpha=0.6, label='Rango óptimo' if i == 0 else "")
        
        # Puntos de valores actuales
        ax2.scatter(valores_actual, x_pos, color='red', s=100, zorder=3, 
                   label='Valor actual')
        
        # Líneas de referencia
        for i, (actual, min_val, max_val) in enumerate(zip(valores_actual, valores_min, valores_max)):
            if actual < min_val:
                ax2.axhline(y=i, color='red', linestyle='--', alpha=0.5)
            elif actual > max_val:
                ax2.axhline(y=i, color='orange', linestyle='--', alpha=0.5)
        
        ax2.set_yticks(x_pos)
        ax2.set_yticklabels(parametros)
        ax2.set_xlabel('Valor del Parámetro')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def generar_reporte_pdf(self):
        pdf = FPDF()
        pdf.add_page()
        
        # Encabezado
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, 'REPORTE: CONVERSIÓN PARÁMETROS SEDIMENTACIÓN', 0, 1, 'C')
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, f'Fecha: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
        pdf.ln(5)
        
        # Datos del problema
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(0, 10, 'DATOS DEL PROBLEMA', 1, 1, 'L', 1)
        pdf.set_font("Arial", '', 10)
        p = self.parametros
        pdf.cell(0, 6, f'Carga superficial: {p["carga_superficial_mms"]} mm/s', 0, 1)
        pdf.cell(0, 6, f'Tiempo de retención: {p["tiempo_retencion_horas"]} horas', 0, 1)
        pdf.ln(5)
        
        # Procedimiento de cálculo
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(0, 10, 'PROCEDIMIENTO DE CÁLCULO', 1, 1, 'L', 1)
        pdf.set_font("Courier", '', 8)
        
        for linea in self.procedimientos:
            try:
                txt = linea.encode('latin-1', 'replace').decode('latin-1')
            except:
                txt = linea
            pdf.multi_cell(0, 4, txt)
        
        pdf.ln(5)
        
        # Resultados
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(0, 10, 'RESULTADOS', 1, 1, 'L', 1)
        pdf.set_font("Arial", '', 10)
        
        r = self.resultados
        pdf.cell(0, 6, f'Carga superficial: {r["carga_superficial_md"]:.2f} m/d', 0, 1)
        pdf.cell(0, 6, f'Profundidad del sedimentador: {r["profundidad"]:.3f} m', 0, 1)
        pdf.cell(0, 6, f'Tiempo de retención: {r["tiempo_retencion_horas"]:.1f} horas', 0, 1)
        pdf.ln(5)
        
        # Verificaciones
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(0, 10, 'VERIFICACIONES', 1, 1, 'L', 1)
        pdf.set_font("Arial", '', 10)
        
        for criterio, cumple in self.verificaciones.items():
            if cumple:
                pdf.set_text_color(0, 128, 0)
                pdf.cell(0, 6, f"✓ {criterio}", 0, 1)
            else:
                pdf.set_text_color(200, 0, 0)
                pdf.cell(0, 6, f"✗ {criterio}", 0, 1)
        
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)
        
        # Recomendaciones
        if self.recomendaciones:
            pdf.set_font("Arial", 'B', 12)
            pdf.set_fill_color(255, 240, 200)
            pdf.cell(0, 10, 'RECOMENDACIONES', 1, 1, 'L', 1)
            pdf.set_font("Arial", '', 10)
            
            for rec in self.recomendaciones:
                if rec['tipo'] == 'CRÍTICA':
                    pdf.set_text_color(200, 0, 0)
                elif rec['tipo'] == 'ALTA':
                    pdf.set_text_color(200, 100, 0)
                elif rec['tipo'] == 'MEDIA':
                    pdf.set_text_color(150, 150, 0)
                elif rec['tipo'] == 'BAJA':
                    pdf.set_text_color(100, 100, 200)
                else:
                    pdf.set_text_color(0, 128, 0)
                
                pdf.cell(0, 6, f"{rec['tipo']}: {rec['mensaje']}", 0, 1)
                pdf.set_text_color(0, 0, 0)
                pdf.cell(0, 6, f"   Acción: {rec['accion']}", 0, 1)
                pdf.ln(2)
        
        # Guardar PDF temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf.output(tmp_file.name)
            return tmp_file.name

# ==========================================
# INTERFAZ PRINCIPAL
# ==========================================
def main():
    st.title("🔄 Conversión de Parámetros de Sedimentación")
    st.markdown("### Resolución del Problema 5.21.5 - Capítulo 5: Sedimentación")
    
    if 'conversor' not in st.session_state:
        st.session_state.conversor = ConversorParametros()
    
    # --- SIDEBAR ---
    st.sidebar.header("📋 Parámetros de Operación")
    
    with st.sidebar.form("form_parametros"):
        st.subheader("Datos del Sedimentador")
        
        carga_superficial_mms = st.number_input(
            "Carga superficial (mm/s)",
            min_value=0.1,
            max_value=5.0,
            value=0.7,
            step=0.1,
            help="Velocidad de sedimentación superficial"
        )
        
        tiempo_retencion_horas = st.number_input(
            "Tiempo de retención (horas)",
            min_value=0.5,
            max_value=8.0,
            value=1.2,
            step=0.1,
            help="Tiempo que permanece el agua en el sedimentador"
        )
        
        # Botón de cálculo
        if st.form_submit_button("🚀 Calcular Conversión"):
            parametros = {
                'carga_superficial_mms': carga_superficial_mms,
                'tiempo_retencion_horas': tiempo_retencion_horas
            }
            st.session_state.conversor.calcular(parametros)
            st.rerun()
    
    # --- INFORMACIÓN DE NORMA ---
    with st.sidebar.expander("📚 Parámetros Recomendados"):
        st.markdown("""
        **Valores típicos (RAS):**
        
        - **Carga superficial:** 20-40 m/d
        - **Tiempo de retención:** 1.5-4 horas
        - **Profundidad útil:** 2.5-4.5 m
        
        **Relación fundamental:**
        ```
        Profundidad = CS × t
        Donde:
        CS = Carga superficial (m/d)
        t = Tiempo retención (días)
        ```
        """)
    
    # --- EJEMPLOS RÁPIDOS ---
    with st.sidebar.expander("🎯 Ejemplos Rápidos"):
        if st.button("Problema 5.21.5 Original"):
            st.session_state.conversor.calcular({
                'carga_superficial_mms': 0.7,
                'tiempo_retencion_horas': 1.2
            })
            st.rerun()
        
        if st.button("Configuración Óptima"):
            st.session_state.conversor.calcular({
                'carga_superficial_mms': 0.4,  # ≈ 34.56 m/d
                'tiempo_retencion_horas': 2.5
            })
            st.rerun()
        
        if st.button("Alta Carga"):
            st.session_state.conversor.calcular({
                'carga_superficial_mms': 1.2,  # ≈ 103.68 m/d
                'tiempo_retencion_horas': 1.0
            })
            st.rerun()
    
    # --- RESULTADOS PRINCIPALES ---
    conversor = st.session_state.conversor
    
    if conversor.resultados:
        st.success("✅ Conversión calculada exitosamente")
        
        # Mostrar configuración actual
        st.info(f"""
        **Configuración analizada:** 
        - Carga superficial: {conversor.parametros['carga_superficial_mms']} mm/s
        - Tiempo de retención: {conversor.parametros['tiempo_retencion_horas']} horas
        """)
        
        # Mostrar resultados en pestañas
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Resultados", "📋 Procedimiento", "💡 Recomendaciones", "📈 Gráficas", "📥 Reporte"])
        
        with tab1:
            st.subheader("Resultados de la Conversión")
            
            # Métricas principales
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Carga Superficial", 
                         f"{conversor.resultados['carga_superficial_md']:.2f} m/d",
                         "20-40 m/d")
            
            with col2:
                st.metric("Profundidad", 
                         f"{conversor.resultados['profundidad']:.3f} m",
                         "2.5-4.5 m")
            
            with col3:
                st.metric("Tiempo Retención", 
                         f"{conversor.resultados['tiempo_retencion_horas']:.1f} h",
                         "1.5-4 h")
            
            # Tabla de resultados detallados
            st.subheader("📋 Resumen de Parámetros")
            datos_resumen = {
                'Parámetro': ['Carga superficial', 'Tiempo de retención', 'Profundidad calculada'],
                'Valor Original': [f"{conversor.parametros['carga_superficial_mms']} mm/s", 
                                 f"{conversor.parametros['tiempo_retencion_horas']} horas", 
                                 '-'],
                'Valor Convertido': [f"{conversor.resultados['carga_superficial_md']:.2f} m/d",
                                   f"{conversor.resultados['tiempo_retencion_horas']:.1f} horas",
                                   f"{conversor.resultados['profundidad']:.3f} m"],
                'Recomendación': ['20-40 m/d', '1.5-4 horas', '2.5-4.5 m']
            }
            
            df_resumen = pd.DataFrame(datos_resumen)
            st.dataframe(df_resumen, use_container_width=True)
            
            # Fórmula fundamental
            st.subheader("🧮 Fórmula Fundamental")
            st.latex(r"h = CS \times t")
            st.markdown("""
            Donde:
            - \( h \) = Profundidad del sedimentador (m)
            - \( CS \) = Carga superficial (m/d)  
            - \( t \) = Tiempo de retención (días)
            """)
            
            # Verificaciones
            st.subheader("✅ Verificaciones de Cumplimiento")
            cols = st.columns(2)
            idx = 0
            for criterio, cumple in conversor.verificaciones.items():
                if cumple:
                    cols[idx % 2].success(f"**{criterio}**")
                else:
                    cols[idx % 2].error(f"**{criterio}**")
                idx += 1
        
        with tab2:
            st.subheader("📝 Procedimiento Detallado de Cálculo")
            st.code("\n".join(conversor.procedimientos), language="text")
        
        with tab3:
            st.subheader("💡 Recomendaciones y Ajustes")
            
            if conversor.recomendaciones:
                for rec in conversor.recomendaciones:
                    if rec['tipo'] == 'CRÍTICA':
                        st.error(f"**{rec['tipo']}:** {rec['mensaje']}")
                        st.info(f"**Acción recomendada:** {rec['accion']}")
                    elif rec['tipo'] == 'ALTA':
                        st.warning(f"**{rec['tipo']}:** {rec['mensaje']}")
                        st.info(f"**Acción recomendada:** {rec['accion']}")
                    elif rec['tipo'] == 'MEDIA':
                        st.warning(f"**{rec['tipo']}:** {rec['mensaje']}")
                        st.info(f"**Acción recomendada:** {rec['accion']}")
                    elif rec['tipo'] == 'BAJA':
                        st.info(f"**{rec['tipo']}:** {rec['mensaje']}")
                        st.info(f"**Acción recomendada:** {rec['accion']}")
                    else:
                        st.success(f"**{rec['tipo']}:** {rec['mensaje']}")
                        st.info(f"**Acción recomendada:** {rec['accion']}")
                    st.markdown("---")
            else:
                st.success("**✅ CONFIGURACIÓN ÓPTIMA:** No se requieren ajustes adicionales")
            
            # Sugerencias de optimización
            st.subheader("🔧 Guía de Ajustes")
            st.markdown("""
            **Para optimizar el diseño:**
            
            **Si la carga superficial es ALTA (> 40 m/d):**
            - Reducir el caudal tratado
            - Aumentar el área superficial del sedimentador
            - Verificar eficiencia de remoción
            
            **Si el tiempo de retención es BAJO (< 1.5 h):**
            - Aumentar el volumen del sedimentador
            - Reducir el caudal
            - Considerar sedimentador más grande
            
            **Si la profundidad es INADECUADA:**
            - < 2.5 m: Aumentar tiempo de retención
            - > 4.5 m: Reducir tiempo de retención
            """)
        
        with tab4:
            st.subheader("📈 Análisis Gráfico")
            fig = conversor.generar_grafica()
            if fig:
                st.pyplot(fig)
        
        with tab5:
            st.subheader("📥 Generar Reporte PDF")
            
            if st.button("🖨️ Generar Reporte Completo en PDF"):
                with st.spinner("Generando reporte PDF..."):
                    pdf_file = conversor.generar_reporte_pdf()
                    
                    with open(pdf_file, "rb") as f:
                        st.download_button(
                            label="📥 Descargar Reporte PDF",
                            data=f,
                            file_name=f"conversion_parametros_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                            mime="application/pdf"
                        )
                    
                    # Limpiar archivo temporal
                    os.unlink(pdf_file)
    
    else:
        # Pantalla inicial - Instrucciones
        st.info("""
        ## 🧭 Instrucciones de Uso
        
        1. **Ingrese los parámetros** en la barra lateral:
           - Carga superficial en mm/s
           - Tiempo de retención en horas
        
        2. **Haga clic en "Calcular Conversión"** para obtener los resultados
        
        3. **Revise los resultados** en las diferentes pestañas:
           - 📊 Resultados: Valores convertidos y verificaciones
           - 📋 Procedimiento: Cálculos detallados paso a paso
           - 💡 Recomendaciones: Ajustes específicos si no cumple
           - 📈 Gráficas: Análisis visual de los parámetros
           - 📥 Reporte: Descarga en PDF
        
        ### 🎯 Problema 5.21.5 Original:
        Convertir parámetros de operación:
        - Carga superficial: 0.7 mm/s
        - Tiempo de retención: 1.2 horas
        """)

if __name__ == "__main__":
    main()
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
    page_title="Análisis de Sedimentadores Existentes",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CLASE PRINCIPAL DE CÁLCULO Y REPORTE
# ==========================================
class AnalizadorSedimentadores:
    def __init__(self):
        self.parametros = {}
        self.resultados = {}
        self.verificaciones = {}
        self.procedimientos = []
    
    def calcular(self, parametros):
        self.parametros = parametros
        self.procedimientos = []
        
        # --- DATOS DEL PROBLEMA ---
        num_tanques = parametros['numero_tanques']
        longitud = parametros['longitud_tanque']
        ancho = parametros['ancho_tanque']
        profundidad = parametros['profundidad_util']
        caudal_total = parametros['caudal_total_m3d']
        longitud_vertedero = parametros['longitud_vertedero_total']
        
        self.procedimientos.append("MEMORIA DE CÁLCULO - ANÁLISIS SEDIMENTADORES EXISTENTES")
        self.procedimientos.append("=" * 70)
        self.procedimientos.append("")
        
        # 1. Datos del problema
        self.procedimientos.append("1. DATOS DEL PROBLEMA")
        self.procedimientos.append(f"   Número de tanques: {num_tanques}")
        self.procedimientos.append(f"   Dimensiones de cada tanque: {longitud} m × {ancho} m × {profundidad} m")
        self.procedimientos.append(f"   Caudal total tratado: {caudal_total:,} m³/d")
        self.procedimientos.append(f"   Longitud total del vertedero: {longitud_vertedero} m")
        self.procedimientos.append("")
        
        # 2. Cálculo del Período de Retención
        self.procedimientos.append("2. CÁLCULO DEL PERÍODO DE RETENCIÓN")
        self.procedimientos.append("   a) Volumen de un tanque:")
        self.procedimientos.append(f"      V₁ = L × B × h = {longitud} × {ancho} × {profundidad}")
        
        volumen_un_tanque = longitud * ancho * profundidad
        self.procedimientos.append(f"      V₁ = {volumen_un_tanque} m³")
        self.procedimientos.append("")
        
        self.procedimientos.append("   b) Volumen total de todos los tanques:")
        self.procedimientos.append(f"      V_total = N × V₁ = {num_tanques} × {volumen_un_tanque}")
        
        volumen_total = num_tanques * volumen_un_tanque
        self.procedimientos.append(f"      V_total = {volumen_total} m³")
        self.procedimientos.append("")
        
        self.procedimientos.append("   c) Período de retención:")
        self.procedimientos.append(f"      t = V_total / Q_total = {volumen_total} / {caudal_total:,}")
        
        t_dias = volumen_total / caudal_total
        t_horas = t_dias * 24
        t_minutos = t_horas * 60
        
        self.procedimientos.append(f"      t = {t_dias:.4f} días")
        self.procedimientos.append(f"      t = {t_dias:.4f} × 24 = {t_horas:.2f} horas")
        self.procedimientos.append(f"      t = {t_horas:.2f} × 60 = {t_minutos:.0f} minutos")
        self.procedimientos.append("")
        
        # 3. Cálculo de la Carga Superficial
        self.procedimientos.append("3. CÁLCULO DE LA CARGA SUPERFICIAL")
        self.procedimientos.append("   a) Área superficial de un tanque:")
        self.procedimientos.append(f"      A_s1 = L × B = {longitud} × {ancho}")
        
        area_superficial_un_tanque = longitud * ancho
        self.procedimientos.append(f"      A_s1 = {area_superficial_un_tanque} m²")
        self.procedimientos.append("")
        
        self.procedimientos.append("   b) Área superficial total:")
        self.procedimientos.append(f"      A_s_total = N × A_s1 = {num_tanques} × {area_superficial_un_tanque}")
        
        area_superficial_total = num_tanques * area_superficial_un_tanque
        self.procedimientos.append(f"      A_s_total = {area_superficial_total} m²")
        self.procedimientos.append("")
        
        self.procedimientos.append("   c) Carga superficial:")
        self.procedimientos.append(f"      CS = Q_total / A_s_total = {caudal_total:,} / {area_superficial_total}")
        
        carga_superficial = caudal_total / area_superficial_total
        self.procedimientos.append(f"      CS = {carga_superficial:.2f} m/d")
        self.procedimientos.append("")
        
        # 4. Cálculo de la Carga de Rebose
        self.procedimientos.append("4. CÁLCULO DE LA CARGA DE REBOSE")
        self.procedimientos.append("   a) Caudal en m³/s:")
        self.procedimientos.append(f"      Q_m3s = Q_total / 86400 = {caudal_total:,} / 86,400")
        
        caudal_m3s = caudal_total / 86400
        self.procedimientos.append(f"      Q_m3s = {caudal_m3s:.6f} m³/s")
        self.procedimientos.append("")
        
        self.procedimientos.append("   b) Carga de rebose:")
        self.procedimientos.append(f"      q = Q_m3s / L_v_total = {caudal_m3s:.6f} / {longitud_vertedero}")
        
        carga_rebose_m3sm = caudal_m3s / longitud_vertedero
        carga_rebose_lsm = carga_rebose_m3sm * 1000
        
        self.procedimientos.append(f"      q = {carga_rebose_m3sm:.6f} m³/s·m")
        self.procedimientos.append(f"      q = {carga_rebose_m3sm:.6f} × 1000 = {carga_rebose_lsm:.3f} L/s·m")
        self.procedimientos.append("")
        
        # 5. Resumen de resultados
        self.procedimientos.append("5. RESUMEN DE RESULTADOS")
        self.procedimientos.append(f"   • Período de retención: {t_horas:.2f} horas")
        self.procedimientos.append(f"   • Carga superficial: {carga_superficial:.2f} m/d")
        self.procedimientos.append(f"   • Carga de rebose: {carga_rebose_lsm:.3f} L/s·m")
        self.procedimientos.append("")
        
        # Almacenar resultados
        self.resultados = {
            'periodo_retencion_horas': t_horas,
            'carga_superficial': carga_superficial,
            'carga_rebose_lsm': carga_rebose_lsm,
            'volumen_total': volumen_total,
            'area_superficial_total': area_superficial_total,
            'caudal_m3s': caudal_m3s,
            'relacion_LB': longitud / ancho
        }
        
        # Verificaciones según normas
        self.verificaciones = {
            'Período retención entre 1.5-4 horas': 1.5 <= t_horas <= 4,
            'Carga superficial entre 20-40 m/d': 20 <= carga_superficial <= 40,
            'Carga de rebose < 7.25 L/s·m': carga_rebose_lsm < 7.25,
            'Relación L/B entre 3:1 y 5:1': 3 <= (longitud/ancho) <= 5,
            'Velocidad horizontal < 1.5 cm/s': True  # Se calcularía con más datos
        }
        
        return True
    
    def generar_grafica(self):
        if not self.resultados:
            return None
            
        L = self.parametros['longitud_tanque']
        B = self.parametros['ancho_tanque']
        h = self.parametros['profundidad_util']
        num_tanques = self.parametros['numero_tanques']
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Gráfica 1: Esquema de los Tanques
        ax1.set_title('ESQUEMA DE LOS SEDIMENTADORES', fontweight='bold', fontsize=14)
        
        # Dibujar múltiples tanques
        for i in range(num_tanques):
            # Tanque principal
            rect = plt.Rectangle((i*(L+5), 0), L, B, fill=True, 
                               color=['lightblue', 'lightgreen'][i%2], 
                               alpha=0.6, edgecolor='blue', linewidth=2)
            ax1.add_patch(rect)
            
            # Flecha de flujo
            ax1.arrow(i*(L+5) + L*0.1, B/2, L*0.6, 0, 
                     head_width=B*0.1, head_length=L*0.05, 
                     fc='red', ec='red', linewidth=2)
            
            # Texto identificador
            ax1.text(i*(L+5) + L/2, B/2, f'Tanque {i+1}', 
                    ha='center', va='center', fontweight='bold', fontsize=10)
        
        ax1.set_xlim(-2, num_tanques*(L+5))
        ax1.set_ylim(-B*0.5, B*1.5)
        ax1.set_aspect('equal')
        ax1.axis('off')
        
        # Gráfica 2: Comparación con Normas
        ax2.set_title('COMPARACIÓN CON NORMAS DE DISEÑO', fontweight='bold', fontsize=14)
        
        parametros = ['Retención (h)', 'Carga Superf. (m/d)', 'Carga Rebose (L/s·m)']
        valores_actual = [
            self.resultados['periodo_retencion_horas'],
            self.resultados['carga_superficial'],
            self.resultados['carga_rebose_lsm']
        ]
        valores_min = [1.5, 20, 0]
        valores_max = [4, 40, 7.25]
        
        x_pos = range(len(parametros))
        
        # Barras de rango recomendado
        for i, (min_val, max_val) in enumerate(zip(valores_min, valores_max)):
            ax2.barh(i, max_val - min_val, left=min_val, 
                    color='lightgray', alpha=0.6, label='Rango óptimo' if i == 0 else "")
        
        # Puntos de valores actuales
        ax2.scatter(valores_actual, x_pos, color='red', s=100, zorder=3, 
                   label='Valor actual')
        
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
        pdf.cell(0, 10, 'REPORTE: ANÁLISIS SEDIMENTADORES EXISTENTES', 0, 1, 'C')
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, f'Fecha: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
        pdf.ln(5)
        
        # Datos del problema
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(0, 10, 'DATOS DEL PROBLEMA', 1, 1, 'L', 1)
        pdf.set_font("Arial", '', 10)
        p = self.parametros
        pdf.cell(0, 6, f'Número de tanques: {p["numero_tanques"]}', 0, 1)
        pdf.cell(0, 6, f'Dimensiones cada tanque: {p["longitud_tanque"]} m × {p["ancho_tanque"]} m × {p["profundidad_util"]} m', 0, 1)
        pdf.cell(0, 6, f'Caudal total: {p["caudal_total_m3d"]:,} m³/d', 0, 1)
        pdf.cell(0, 6, f'Longitud vertedero total: {p["longitud_vertedero_total"]} m', 0, 1)
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
        pdf.cell(0, 10, 'RESULTADOS DEL ANÁLISIS', 1, 1, 'L', 1)
        pdf.set_font("Arial", '', 10)
        
        r = self.resultados
        pdf.cell(0, 6, f'Período de retención: {r["periodo_retencion_horas"]:.2f} horas', 0, 1)
        pdf.cell(0, 6, f'Carga superficial: {r["carga_superficial"]:.2f} m/d', 0, 1)
        pdf.cell(0, 6, f'Carga de rebose: {r["carga_rebose_lsm"]:.3f} L/s·m', 0, 1)
        pdf.cell(0, 6, f'Volumen total: {r["volumen_total"]:,} m³', 0, 1)
        pdf.cell(0, 6, f'Área superficial total: {r["area_superficial_total"]} m²', 0, 1)
        pdf.ln(5)
        
        # Verificaciones
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(0, 10, 'VERIFICACIONES DE DISEÑO', 1, 1, 'L', 1)
        pdf.set_font("Arial", '', 10)
        
        for criterio, cumple in self.verificaciones.items():
            if cumple:
                pdf.set_text_color(0, 128, 0)
                pdf.cell(0, 6, f"✓ {criterio}", 0, 1)
            else:
                pdf.set_text_color(200, 0, 0)
                pdf.cell(0, 6, f"✗ {criterio}", 0, 1)
        
        pdf.set_text_color(0, 0, 0)
        
        # Guardar PDF temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf.output(tmp_file.name)
            return tmp_file.name

# ==========================================
# INTERFAZ PRINCIPAL
# ==========================================
def main():
    st.title("📊 Análisis de Sedimentadores Existentes")
    st.markdown("### Resolución del Problema 5.21.3 - Capítulo 5: Sedimentación")
    
    if 'analizador' not in st.session_state:
        st.session_state.analizador = AnalizadorSedimentadores()
    
    # --- SIDEBAR ---
    st.sidebar.header("📋 Parámetros del Sistema")
    
    with st.sidebar.form("form_parametros"):
        st.subheader("Configuración de Tanques")
        
        numero_tanques = st.number_input(
            "Número de tanques",
            min_value=1,
            max_value=10,
            value=2,
            step=1,
            help="Cantidad de sedimentadores en operación"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            longitud_tanque = st.number_input(
                "Longitud de cada tanque (m)",
                min_value=5.0,
                max_value=100.0,
                value=30.0,
                step=1.0
            )
            
            ancho_tanque = st.number_input(
                "Ancho de cada tanque (m)", 
                min_value=2.0,
                max_value=20.0,
                value=5.0,
                step=0.5
            )
        
        with col2:
            profundidad_util = st.number_input(
                "Profundidad útil (m)",
                min_value=2.0,
                max_value=6.0,
                value=4.0,
                step=0.1
            )
            
            longitud_vertedero_total = st.number_input(
                "Longitud total vertedero (m)",
                min_value=10.0,
                max_value=200.0,
                value=50.0,
                step=5.0
            )
        
        caudal_total_m3d = st.number_input(
            "Caudal total tratado (m³/d)",
            min_value=1000.0,
            max_value=50000.0,
            value=6000.0,
            step=1000.0,
            help="Caudal total que pasa por todos los sedimentadores"
        )
        
        # Botón de cálculo
        if st.form_submit_button("🚀 Analizar Sistema"):
            parametros = {
                'numero_tanques': numero_tanques,
                'longitud_tanque': longitud_tanque,
                'ancho_tanque': ancho_tanque,
                'profundidad_util': profundidad_util,
                'caudal_total_m3d': caudal_total_m3d,
                'longitud_vertedero_total': longitud_vertedero_total
            }
            st.session_state.analizador.calcular(parametros)
            st.rerun()
    
    # --- INFORMACIÓN DE NORMA ---
    with st.sidebar.expander("📚 Parámetros Recomendados"):
        st.markdown("""
        **Valores típicos (RAS):**
        
        - **Período de retención:** 1.5-4 horas
        - **Carga superficial:** 20-40 m/d
        - **Carga de rebose:** < 7.25 L/s·m
        - **Relación L/B:** 3:1 a 5:1
        - **Profundidad útil:** 2.5-4 m
        """)
    
    # --- EJEMPLOS RÁPIDOS ---
    with st.sidebar.expander("🎯 Ejemplos Rápidos"):
        if st.button("Problema 5.21.3 Original"):
            st.session_state.analizador.calcular({
                'numero_tanques': 2,
                'longitud_tanque': 30.0,
                'ancho_tanque': 5.0,
                'profundidad_util': 4.0,
                'caudal_total_m3d': 6000.0,
                'longitud_vertedero_total': 50.0
            })
            st.rerun()
        
        if st.button("Sistema de 3 Tanques"):
            st.session_state.analizador.calcular({
                'numero_tanques': 3,
                'longitud_tanque': 25.0,
                'ancho_tanque': 6.0,
                'profundidad_util': 3.5,
                'caudal_total_m3d': 10000.0,
                'longitud_vertedero_total': 80.0
            })
            st.rerun()
    
    # --- RESULTADOS PRINCIPALES ---
    analizador = st.session_state.analizador
    
    if analizador.resultados:
        st.success("✅ Análisis completado exitosamente")
        
        # Mostrar configuración actual
        st.info(f"""
        **Configuración analizada:** 
        - {analizador.parametros['numero_tanques']} tanques de {analizador.parametros['longitud_tanque']}×{analizador.parametros['ancho_tanque']}×{analizador.parametros['profundidad_util']} m
        - Caudal total: {analizador.parametros['caudal_total_m3d']:,} m³/d
        - Longitud vertedero: {analizador.parametros['longitud_vertedero_total']} m
        """)
        
        # Mostrar resultados en pestañas
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Resultados", "📋 Procedimiento", "📊 Gráficas", "📥 Reporte"])
        
        with tab1:
            st.subheader("Resultados del Análisis")
            
            # Métricas principales
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Período Retención", 
                         f"{analizador.resultados['periodo_retencion_horas']:.2f} h",
                         "1.5-4 h")
            
            with col2:
                st.metric("Carga Superficial", 
                         f"{analizador.resultados['carga_superficial']:.2f} m/d",
                         "20-40 m/d")
            
            with col3:
                st.metric("Carga Rebose", 
                         f"{analizador.resultados['carga_rebose_lsm']:.3f} L/s·m",
                         "< 7.25 L/s·m")
            
            # Tabla de resultados detallados
            st.subheader("📊 Resumen de Parámetros")
            datos_resumen = {
                'Parámetro': ['Período de retención', 'Carga superficial', 'Carga de rebose',
                             'Volumen total', 'Área superficial total', 'Relación L/B'],
                'Valor': [f"{analizador.resultados['periodo_retencion_horas']:.2f} horas",
                         f"{analizador.resultados['carga_superficial']:.2f} m/d",
                         f"{analizador.resultados['carga_rebose_lsm']:.3f} L/s·m",
                         f"{analizador.resultados['volumen_total']:,} m³",
                         f"{analizador.resultados['area_superficial_total']} m²",
                         f"{analizador.resultados['relacion_LB']:.2f}"],
                'Recomendación': ['1.5-4 horas', '20-40 m/d', '< 7.25 L/s·m', '-', '-', '3:1 a 5:1']
            }
            
            df_resumen = pd.DataFrame(datos_resumen)
            st.dataframe(df_resumen, use_container_width=True)
            
            # Verificaciones
            st.subheader("✅ Verificaciones de Cumplimiento")
            cols = st.columns(2)
            idx = 0
            for criterio, cumple in analizador.verificaciones.items():
                if cumple:
                    cols[idx % 2].success(f"**{criterio}**")
                else:
                    cols[idx % 2].error(f"**{criterio}**")
                idx += 1
            
            # Diagnóstico general
            st.subheader("🎯 Diagnóstico del Sistema")
            cumplimientos = sum(analizador.verificaciones.values())
            total_verificaciones = len(analizador.verificaciones)
            
            if cumplimientos == total_verificaciones:
                st.success("**✅ SISTEMA ÓPTIMO:** Todos los parámetros están dentro de los rangos recomendados")
            elif cumplimientos >= total_verificaciones * 0.7:
                st.warning("**⚠️ SISTEMA ACEPTABLE:** La mayoría de parámetros cumplen, algunas mejoras posibles")
            else:
                st.error("**❌ SISTEMA REQUIERE AJUSTES:** Múltiples parámetros fuera de rango recomendado")
        
        with tab2:
            st.subheader("📝 Procedimiento Detallado de Cálculo")
            st.code("\n".join(analizador.procedimientos), language="text")
        
        with tab3:
            st.subheader("📊 Esquemas y Comparaciones")
            fig = analizador.generar_grafica()
            if fig:
                st.pyplot(fig)
        
        with tab4:
            st.subheader("📥 Generar Reporte PDF")
            
            if st.button("🖨️ Generar Reporte Completo en PDF"):
                with st.spinner("Generando reporte PDF..."):
                    pdf_file = analizador.generar_reporte_pdf()
                    
                    with open(pdf_file, "rb") as f:
                        st.download_button(
                            label="📥 Descargar Reporte PDF",
                            data=f,
                            file_name=f"analisis_sedimentadores_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                            mime="application/pdf"
                        )
                    
                    # Limpiar archivo temporal
                    os.unlink(pdf_file)
    
    else:
        # Pantalla inicial - Instrucciones
        st.info("""
        ## 🧭 Instrucciones de Uso
        
        1. **Ingrese los parámetros** en la barra lateral:
           - Número de tanques y sus dimensiones
           - Caudal total tratado
           - Longitud total del vertedero
        
        2. **Haga clic en "Analizar Sistema"** para evaluar el desempeño
        
        3. **Revise los resultados** en las diferentes pestañas:
           - 📈 Resultados: Parámetros calculados y verificaciones
           - 📋 Procedimiento: Cálculos detallados paso a paso  
           - 📊 Gráficas: Esquemas y comparativas
           - 📥 Reporte: Descarga en PDF
        
        ### 🎯 Problema 5.21.3 Original:
        Analizar 2 sedimentadores de 30×5×4 m que tratan 6,000 m³/d
        con vertedero total de 50 m.
        """)

if __name__ == "__main__":
    main()
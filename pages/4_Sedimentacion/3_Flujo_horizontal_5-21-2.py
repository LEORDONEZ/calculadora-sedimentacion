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
    page_title="Diseño de Sedimentador Horizontal ejercicio 5.21.2 libro purificacion de aguas",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CLASE PRINCIPAL DE CÁLCULO Y REPORTE
# ==========================================
class DiseñoSedimentador:
    def __init__(self):
        self.parametros = {}
        self.resultados = {}
        self.verificaciones = {}
        self.procedimientos = []
    
    def calcular(self, parametros):
        self.parametros = parametros
        self.procedimientos = []
        
        # --- DATOS DEL PROBLEMA ---
        Q_m3d = parametros['caudal_m3d']
        h = parametros['profundidad_util']
        CS = parametros['carga_superficial']
        V_h_cms = parametros['velocidad_horizontal_cms']
        q_vertedero = parametros['carga_vertedero_lsm']
        
        self.procedimientos.append("MEMORIA DE CÁLCULO - DISEÑO SEDIMENTADOR HORIZONTAL")
        self.procedimientos.append("=" * 70)
        self.procedimientos.append("")
        
        # 1. Datos del problema
        self.procedimientos.append("1. DATOS DEL PROBLEMA")
        self.procedimientos.append(f"   Caudal (Q) = {Q_m3d:,} m³/d")
        self.procedimientos.append(f"   Profundidad útil (h) = {h} m")
        self.procedimientos.append(f"   Carga superficial (CS) = {CS} m/d")
        self.procedimientos.append(f"   Velocidad horizontal = {V_h_cms} cm/s")
        self.procedimientos.append(f"   Carga sobre vertedero = {q_vertedero} L/s·m")
        self.procedimientos.append("")
        
        # 2. Conversión de unidades
        Q_m3s = Q_m3d / 86400
        V_h_ms = V_h_cms / 100
        q_vertedero_m3sm = q_vertedero / 1000
        
        self.procedimientos.append("2. CONVERSIÓN DE UNIDADES")
        self.procedimientos.append(f"   Q = {Q_m3d:,} m³/d = {Q_m3s:.6f} m³/s")
        self.procedimientos.append(f"   V_h = {V_h_cms} cm/s = {V_h_ms:.3f} m/s")
        self.procedimientos.append(f"   q_vertedero = {q_vertedero} L/s·m = {q_vertedero_m3sm:.3f} m³/s·m")
        self.procedimientos.append("")
        
        # 3. Cálculo del Ancho (B)
        self.procedimientos.append("3. CÁLCULO DEL ANCHO DEL TANQUE (B)")
        self.procedimientos.append("   Fórmula: Q = A × V_h = (B × h) × V_h")
        self.procedimientos.append(f"   {Q_m3s:.6f} = B × {h} × {V_h_ms:.3f}")
        self.procedimientos.append(f"   B = {Q_m3s:.6f} / ({h} × {V_h_ms:.3f})")
        
        B = Q_m3s / (h * V_h_ms)
        self.procedimientos.append(f"   B = {B:.2f} m")
        self.procedimientos.append("")
        
        # 4. Cálculo de la Longitud (L)
        self.procedimientos.append("4. CÁLCULO DE LA LONGITUD DEL TANQUE (L)")
        self.procedimientos.append("   Fórmula: CS = Q / (B × L)")
        self.procedimientos.append(f"   {CS} = {Q_m3d:,} / ({B:.2f} × L)")
        self.procedimientos.append(f"   L = {Q_m3d:,} / ({B:.2f} × {CS})")
        
        L = Q_m3d / (B * CS)
        self.procedimientos.append(f"   L = {L:.2f} m")
        self.procedimientos.append("")
        
        # 5. Cálculo del Tiempo de Retención (t)
        self.procedimientos.append("5. CÁLCULO DEL TIEMPO DE RETENCIÓN (t)")
        self.procedimientos.append("   Fórmula: t = V / Q = (B × L × h) / Q")
        self.procedimientos.append(f"   V = {B:.2f} × {L:.2f} × {h} = {B*L*h:.0f} m³")
        self.procedimientos.append(f"   t = {B*L*h:.0f} / {Q_m3d:,}")
        
        t_dias = (B * L * h) / Q_m3d
        t_horas = t_dias * 24
        t_minutos = t_horas * 60
        
        self.procedimientos.append(f"   t = {t_dias:.4f} días = {t_horas:.2f} horas = {t_minutos:.0f} minutos")
        self.procedimientos.append("")
        
        # 6. Cálculo de la Longitud del Vertedero (L_v)
        self.procedimientos.append("6. CÁLCULO DE LA LONGITUD DEL VERTEDERO (L_v)")
        self.procedimientos.append("   Fórmula: Q = q_vertedero × L_v")
        self.procedimientos.append(f"   {Q_m3s:.6f} = {q_vertedero_m3sm:.3f} × L_v")
        self.procedimientos.append(f"   L_v = {Q_m3s:.6f} / {q_vertedero_m3sm:.3f}")
        
        L_v = Q_m3s / q_vertedero_m3sm
        self.procedimientos.append(f"   L_v = {L_v:.2f} m")
        self.procedimientos.append("")
        
        # 7. Verificaciones de diseño
        self.procedimientos.append("7. VERIFICACIONES DE DISEÑO")
        
        # Relación L/B
        relacion_LB = L / B
        self.procedimientos.append(f"   Relación L/B = {L:.2f} / {B:.2f} = {relacion_LB:.2f}")
        
        # Velocidad horizontal en cm/s
        V_h_verificacion = V_h_cms
        self.procedimientos.append(f"   Velocidad horizontal = {V_h_verificacion} cm/s")
        
        # Carga superficial
        CS_verificacion = CS
        self.procedimientos.append(f"   Carga superficial = {CS_verificacion} m/d")
        
        # Tiempo de retención
        self.procedimientos.append(f"   Tiempo de retención = {t_horas:.2f} horas")
        
        # Almacenar resultados
        self.resultados = {
            'ancho_B': B,
            'longitud_L': L,
            'tiempo_retencion_horas': t_horas,
            'longitud_vertedero': L_v,
            'volumen': B * L * h,
            'relacion_LB': relacion_LB,
            'area_superficial': B * L
        }
        
        # Verificaciones según normas típicas
        self.verificaciones = {
            'Relación L/B entre 3:1 y 5:1': 3 <= relacion_LB <= 5,
            'Velocidad horizontal < 1.5 cm/s': V_h_verificacion < 1.5,
            'Tiempo retención > 1.5 horas': t_horas >= 1.5,
            'Carga superficial típica (20-40 m/d)': 20 <= CS_verificacion <= 40,
            'Longitud vertedero suficiente': L_v <= (2 * B + 2 * L)  # Máximo perímetro disponible
        }
        
        return True
    
    def generar_grafica(self):
        if not self.resultados:
            return None
            
        B = self.resultados['ancho_B']
        L = self.resultados['longitud_L']
        h = self.parametros['profundidad_util']
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Gráfica 1: Vista en Planta
        ax1.set_title('VISTA EN PLANTA (COTAS EN METROS)', fontweight='bold', fontsize=14)
        
        # Dibujar rectángulo del tanque
        rect = plt.Rectangle((0, 0), L, B, fill=True, color='lightblue', alpha=0.6, edgecolor='blue', linewidth=2)
        ax1.add_patch(rect)
        
        # Flecha de flujo
        ax1.arrow(L*0.1, B/2, L*0.6, 0, head_width=B*0.1, head_length=L*0.05, 
                 fc='red', ec='red', linewidth=2)
        
        # Cotas
        ax1.plot([0, 0], [-B*0.1, -B*0.05], 'k-', lw=1)
        ax1.plot([L, L], [-B*0.1, -B*0.05], 'k-', lw=1)
        ax1.plot([0, L], [-B*0.075, -B*0.075], 'k-', lw=1)
        ax1.text(L/2, -B*0.15, f'L = {L:.1f} m', ha='center', va='top', fontweight='bold')
        
        ax1.plot([-L*0.05, -L*0.02], [0, 0], 'k-', lw=1)
        ax1.plot([-L*0.05, -L*0.02], [B, B], 'k-', lw=1)
        ax1.plot([-L*0.035, -L*0.035], [0, B], 'k-', lw=1)
        ax1.text(-L*0.1, B/2, f'B = {B:.1f} m', ha='center', va='center', 
                rotation=90, fontweight='bold')
        
        ax1.set_xlim(-L*0.2, L*1.1)
        ax1.set_ylim(-B*0.3, B*1.1)
        ax1.set_aspect('equal')
        ax1.axis('off')
        
        # Gráfica 2: Vista Transversal
        ax2.set_title('VISTA TRANSVERSAL (COTAS EN METROS)', fontweight='bold', fontsize=14)
        
        # Dibujar sección transversal
        rect2 = plt.Rectangle((0, 0), B, h, fill=True, color='lightgreen', alpha=0.6, edgecolor='green', linewidth=2)
        ax2.add_patch(rect2)
        
        # Línea de agua
        ax2.axhline(y=h, color='blue', linestyle='--', alpha=0.7, label='Nivel de agua')
        
        # Cotas
        ax2.plot([-B*0.05, -B*0.02], [0, 0], 'k-', lw=1)
        ax2.plot([-B*0.05, -B*0.02], [h, h], 'k-', lw=1)
        ax2.plot([-B*0.035, -B*0.035], [0, h], 'k-', lw=1)
        ax2.text(-B*0.1, h/2, f'h = {h} m', ha='center', va='center', 
                rotation=90, fontweight='bold')
        
        ax2.plot([0, B], [-h*0.1, -h*0.1], 'k-', lw=1)
        ax2.text(B/2, -h*0.2, f'B = {B:.1f} m', ha='center', va='top', fontweight='bold')
        
        ax2.set_xlim(-B*0.2, B*1.1)
        ax2.set_ylim(-h*0.3, h*1.2)
        ax2.legend()
        ax2.set_aspect('equal')
        ax2.axis('off')
        
        plt.tight_layout()
        return fig
    
    def generar_reporte_pdf(self):
        pdf = FPDF()
        pdf.add_page()
        
        # Encabezado
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, 'REPORTE: DISEÑO SEDIMENTADOR HORIZONTAL', 0, 1, 'C')
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, f'Fecha: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
        pdf.ln(5)
        
        # Datos del problema
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(0, 10, 'DATOS DEL PROBLEMA', 1, 1, 'L', 1)
        pdf.set_font("Arial", '', 10)
        p = self.parametros
        pdf.cell(0, 6, f'Caudal: {p["caudal_m3d"]:,} m³/d', 0, 1)
        pdf.cell(0, 6, f'Profundidad útil: {p["profundidad_util"]} m', 0, 1)
        pdf.cell(0, 6, f'Carga superficial: {p["carga_superficial"]} m/d', 0, 1)
        pdf.cell(0, 6, f'Velocidad horizontal: {p["velocidad_horizontal_cms"]} cm/s', 0, 1)
        pdf.cell(0, 6, f'Carga vertedero: {p["carga_vertedero_lsm"]} L/s·m', 0, 1)
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
        pdf.cell(0, 10, 'RESULTADOS DEL DISEÑO', 1, 1, 'L', 1)
        pdf.set_font("Arial", '', 10)
        
        r = self.resultados
        pdf.cell(0, 6, f'Ancho del tanque (B): {r["ancho_B"]:.2f} m', 0, 1)
        pdf.cell(0, 6, f'Longitud del tanque (L): {r["longitud_L"]:.2f} m', 0, 1)
        pdf.cell(0, 6, f'Relación L/B: {r["relacion_LB"]:.2f}', 0, 1)
        pdf.cell(0, 6, f'Volumen: {r["volumen"]:.0f} m³', 0, 1)
        pdf.cell(0, 6, f'Tiempo de retención: {r["tiempo_retencion_horas"]:.2f} horas', 0, 1)
        pdf.cell(0, 6, f'Longitud del vertedero: {r["longitud_vertedero"]:.2f} m', 0, 1)
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
    st.title("🏗️ Diseño de Sedimentador Horizontal")
    st.markdown("### Resolución del Problema 5.21.2 - Capítulo 5: Sedimentación")
    
    if 'diseñador' not in st.session_state:
        st.session_state.diseñador = DiseñoSedimentador()
    
    # --- SIDEBAR ---
    st.sidebar.header("📊 Parámetros de Diseño")
    
    with st.sidebar.form("form_parametros"):
        st.subheader("Datos del Proyecto")
        
        caudal_m3d = st.number_input(
            "Caudal de diseño (m³/d)",
            min_value=1000.0,
            max_value=100000.0,
            value=20000.0,
            step=1000.0,
            help="Caudal máximo que debe tratar la planta"
        )
        
        profundidad_util = st.number_input(
            "Profundidad útil (m)",
            min_value=2.0,
            max_value=5.0,
            value=3.0,
            step=0.1,
            help="Profundidad del agua en el sedimentador"
        )
        
        carga_superficial = st.number_input(
            "Carga superficial (m/d)",
            min_value=10.0,
            max_value=60.0,
            value=40.0,
            step=1.0,
            help="Carga hidráulica superficial típica: 20-40 m/d"
        )
        
        velocidad_horizontal_cms = st.number_input(
            "Velocidad horizontal (cm/s)",
            min_value=0.1,
            max_value=2.0,
            value=0.5,
            step=0.1,
            help="Velocidad recomendada: 0.3-1.5 cm/s"
        )
        
        carga_vertedero_lsm = st.number_input(
            "Carga sobre vertedero (L/s·m)",
            min_value=1.0,
            max_value=10.0,
            value=3.0,
            step=0.1,
            help="Carga típica: 2-5 L/s·m"
        )
        
        # Botón de cálculo
        if st.form_submit_button("🚀 Calcular Diseño"):
            parametros = {
                'caudal_m3d': caudal_m3d,
                'profundidad_util': profundidad_util,
                'carga_superficial': carga_superficial,
                'velocidad_horizontal_cms': velocidad_horizontal_cms,
                'carga_vertedero_lsm': carga_vertedero_lsm
            }
            st.session_state.diseñador.calcular(parametros)
            st.rerun()
    
    # --- INFORMACIÓN DE DISEÑO ---
    with st.sidebar.expander("📚 Normas de Diseño"):
        st.markdown("""
        **Parámetros Recomendados (RAS):**
        
        - **Carga superficial:** 20-40 m/d
        - **Velocidad horizontal:** 0.3-1.5 cm/s
        - **Tiempo retención:** 1.5-4 horas
        - **Relación L/B:** 3:1 a 5:1
        - **Profundidad útil:** 2.5-4 m
        - **Carga vertedero:** 2-5 L/s·m
        """)
    
    # --- EJEMPLOS RÁPIDOS ---
    with st.sidebar.expander("🎯 Ejemplos Rápidos"):
        if st.button("Problema 5.21.2 Original"):
            st.session_state.diseñador.calcular({
                'caudal_m3d': 20000.0,
                'profundidad_util': 3.0,
                'carga_superficial': 40.0,
                'velocidad_horizontal_cms': 0.5,
                'carga_vertedero_lsm': 3.0
            })
            st.rerun()
        
        if st.button("Planta Mediana (10,000 m³/d)"):
            st.session_state.diseñador.calcular({
                'caudal_m3d': 10000.0,
                'profundidad_util': 3.0,
                'carga_superficial': 35.0,
                'velocidad_horizontal_cms': 0.4,
                'carga_vertedero_lsm': 2.5
            })
            st.rerun()
    
    # --- RESULTADOS PRINCIPALES ---
    diseñador = st.session_state.diseñador
    
    if diseñador.resultados:
        st.success("✅ Diseño calculado exitosamente")
        
        # Mostrar configuración actual
        st.info(f"""
        **Configuración del proyecto:** 
        - Caudal: {diseñador.parametros['caudal_m3d']:,} m³/d
        - Profundidad útil: {diseñador.parametros['profundidad_util']} m
        - Carga superficial: {diseñador.parametros['carga_superficial']} m/d
        - Velocidad horizontal: {diseñador.parametros['velocidad_horizontal_cms']} cm/s
        """)
        
        # Mostrar resultados en pestañas
        tab1, tab2, tab3, tab4 = st.tabs(["📐 Resultados", "📋 Procedimiento", "📊 Esquemas", "📥 Reporte"])
        
        with tab1:
            st.subheader("Resultados del Diseño")
            
            # Métricas principales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Ancho (B)", f"{diseñador.resultados['ancho_B']:.2f} m")
            
            with col2:
                st.metric("Longitud (L)", f"{diseñador.resultados['longitud_L']:.2f} m")
            
            with col3:
                st.metric("Tiempo Retención", f"{diseñador.resultados['tiempo_retencion_horas']:.2f} h")
            
            with col4:
                st.metric("Volumen", f"{diseñador.resultados['volumen']:.0f} m³")
            
            # Tabla de resultados detallados
            st.subheader("📊 Resumen de Dimensiones")
            datos_resumen = {
                'Parámetro': ['Ancho del tanque (B)', 'Longitud del tanque (L)', 'Relación L/B', 
                             'Área superficial', 'Volumen', 'Tiempo de retención', 'Longitud vertedero'],
                'Valor': [f"{diseñador.resultados['ancho_B']:.2f} m", 
                         f"{diseñador.resultados['longitud_L']:.2f} m",
                         f"{diseñador.resultados['relacion_LB']:.2f}",
                         f"{diseñador.resultados['area_superficial']:.0f} m²",
                         f"{diseñador.resultados['volumen']:.0f} m³",
                         f"{diseñador.resultados['tiempo_retencion_horas']:.2f} horas",
                         f"{diseñador.resultados['longitud_vertedero']:.2f} m"],
                'Recomendación': ['-', '-', '3:1 a 5:1', '-', '-', '1.5-4 horas', 'Suficiente para caudal']
            }
            
            df_resumen = pd.DataFrame(datos_resumen)
            st.dataframe(df_resumen, use_container_width=True)
            
            # Verificaciones
            st.subheader("✅ Verificaciones de Diseño")
            cols = st.columns(2)
            idx = 0
            for criterio, cumple in diseñador.verificaciones.items():
                if cumple:
                    cols[idx % 2].success(f"**{criterio}**")
                else:
                    cols[idx % 2].error(f"**{criterio}**")
                idx += 1
        
        with tab2:
            st.subheader("📝 Procedimiento Detallado de Cálculo")
            st.code("\n".join(diseñador.procedimientos), language="text")
        
        with tab3:
            st.subheader("📊 Esquemas del Sedimentador")
            fig = diseñador.generar_grafica()
            if fig:
                st.pyplot(fig)
                
                # Información adicional
                st.subheader("💡 Recomendaciones de Construcción")
                st.markdown(f"""
                - **Forma recomendada:** Rectangular con relación L/B = {diseñador.resultados['relacion_LB']:.2f}
                - **Sistema de entrada:** Pantalla difusora para distribución uniforme
                - **Sistema de salida:** Vertederos con longitud total de {diseñador.resultados['longitud_vertedero']:.2f} m
                - **Remoción de lodos:** Mecanismos de rastrilleo o tolvas en el fondo
                - **Borde libre:** Adicionar 0.3-0.5 m sobre el nivel de agua
                """)
        
        with tab4:
            st.subheader("📥 Generar Reporte PDF")
            
            if st.button("🖨️ Generar Reporte Completo en PDF"):
                with st.spinner("Generando reporte PDF..."):
                    pdf_file = diseñador.generar_reporte_pdf()
                    
                    with open(pdf_file, "rb") as f:
                        st.download_button(
                            label="📥 Descargar Reporte PDF",
                            data=f,
                            file_name=f"diseno_sedimentador_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                            mime="application/pdf"
                        )
                    
                    # Limpiar archivo temporal
                    os.unlink(pdf_file)
    
    else:
        # Pantalla inicial - Instrucciones
        st.info("""
        ## 🧭 Instrucciones de Uso
        
        1. **Ingrese los parámetros** en la barra lateral:
           - Caudal de diseño (m³/d)
           - Profundidad útil del tanque (m)
           - Carga superficial (m/d)
           - Velocidad horizontal (cm/s)
           - Carga sobre el vertedero (L/s·m)
        
        2. **Haga clic en "Calcular Diseño"** para obtener las dimensiones
        
        3. **Revise los resultados** en las diferentes pestañas:
           - 📐 Resultados: Dimensiones y verificaciones
           - 📋 Procedimiento: Cálculos detallados paso a paso
           - 📊 Esquemas: Diagramas del sedimentador
           - 📥 Reporte: Descarga en PDF
        
        ### 🎯 Problema 5.21.2 Original:
        Diseñar sedimentador para 20,000 m³/d con:
        - Profundidad: 3 m
        - Carga superficial: 40 m/d  
        - Velocidad: 0.5 cm/s
        - Carga vertedero: 3 L/s·m
        """)

if __name__ == "__main__":
    main()
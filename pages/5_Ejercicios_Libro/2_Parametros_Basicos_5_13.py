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
    page_title="Análisis Sedimentador con Placas Inclinadas",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CLASE PRINCIPAL - ANÁLISIS DE PLACAS INCLINADAS
# ==========================================
class AnalizadorPlacasInclinadas:
    def __init__(self):
        self.parametros = {}
        self.resultados = {}
        self.verificaciones = {}
        self.procedimientos = []
        self.calculos_detallados = []
    
    def calcular(self, parametros):
        self.parametros = parametros
        self.procedimientos = []
        self.calculos_detallados = []
        
        # --- DATOS DE ENTRADA ---
        Q_ls = parametros['caudal_ls']
        L_tanque = parametros['longitud_tanque']
        l_placa = parametros['longitud_placa']
        e_placa = parametros['espesor_placa']
        d_espacio = parametros['separacion_placas']
        theta_grados = parametros['angulo_inclinacion']
        viscosidad_cinematica = parametros['viscosidad_cinematica']
        
        theta = np.radians(theta_grados)
        
        # ==========================================
        # NUEVO FORMATO DE CÁLCULOS DETALLADOS
        # ==========================================
        self.calculos_detallados.append("=" * 60)
        self.calculos_detallados.append("REPORTE DE CÁLCULOS - SEDIMENTADOR CON PLACAS")
        self.calculos_detallados.append("=" * 60)
        self.calculos_detallados.append("")
        
        # --- 1. CÁLCULO DE VELOCIDADES ---
        self.calculos_detallados.append("--- 1. CÁLCULO DE VELOCIDADES ---")
        
        # Carga Superficial (CS)
        ancho_tanque = 2.35  # Asumido del ejemplo
        Q_m3d = (Q_ls / 1000) * 86400
        A_tanque = L_tanque * ancho_tanque
        CS = Q_m3d / A_tanque
        
        self.calculos_detallados.append("Carga Superficial (CS):")
        self.calculos_detallados.append(f"   CS = Q / A = ({Q_ls}/1000 × 86.400) / ({L_tanque} × {ancho_tanque})")
        self.calculos_detallados.append(f"   CS = {CS:.0f} m/d")
        
        # Velocidad promedio (v0)
        v0_md = CS / np.sin(theta)
        v0_m_min = v0_md / 1440
        
        self.calculos_detallados.append("Velocidad promedio (v0):")
        self.calculos_detallados.append(f"   v0 = {CS:.0f} / sen {theta_grados}")
        self.calculos_detallados.append(f"   v0 = {v0_md:.1f} m/d = {v0_m_min:.2f} m/min")
        self.calculos_detallados.append("")
        
        # --- 2. LONGITUDES RELATIVAS ---
        self.calculos_detallados.append("--- 2. LONGITUDES RELATIVAS ---")
        
        # Longitud relativa (L)
        L_rel = l_placa / d_espacio
        
        self.calculos_detallados.append("Longitud relativa (L):")
        self.calculos_detallados.append(f"   L = l / d = {l_placa} / {d_espacio}")
        self.calculos_detallados.append(f"   L = {L_rel:.0f}")
        
        # Longitud de transición (L')
        L_trans = (0.013 * (v0_m_min/60) * d_espacio) / viscosidad_cinematica
        
        self.calculos_detallados.append("Longitud de transición (L'):")
        self.calculos_detallados.append(f"   L' = (0.013 × {v0_m_min:.2f} × {d_espacio}) / (60 × {viscosidad_cinematica:.3e})")
        self.calculos_detallados.append(f"   L' = {L_trans:.1f}")
        self.calculos_detallados.append(f"   Verificación: {L_trans:.1f} < {L_rel:.0f} ({'OK' if L_trans < L_rel else 'NO CUMPLE'})")
        
        # Longitud relativa efectiva (Le)
        L_efectiva = L_rel - L_trans
        
        self.calculos_detallados.append("Longitud relativa efectiva (Le):")
        self.calculos_detallados.append(f"   Le = L - L' = {L_rel:.0f} - {L_trans:.1f}")
        self.calculos_detallados.append(f"   Le = {L_efectiva:.1f}")
        self.calculos_detallados.append("")
        
        # --- 3. VELOCIDAD CRÍTICA (DISEÑO) ---
        self.calculos_detallados.append("--- 3. VELOCIDAD CRÍTICA (DISEÑO) ---")
        
        # Velocidad Crítica (Vsc) - Ecuación de Yao
        numerador = 1.0 * v0_md
        denominador = np.sin(theta) + (L_efectiva * np.cos(theta))
        Vsc = numerador / denominador
        
        self.calculos_detallados.append("Velocidad Crítica (Vsc) - Ecuación de Yao:")
        self.calculos_detallados.append(f"   Vsc = (1 × {v0_md:.1f}) / (sen {theta_grados} + {L_efectiva:.1f} cos {theta_grados})")
        self.calculos_detallados.append(f"   Vsc = {Vsc:.1f} m/d")
        
        # Verificación del rango típico
        if 14 <= Vsc <= 22:
            self.calculos_detallados.append("   Nota: Valor comparable con carga convencional (14-22 m/d).")
        else:
            self.calculos_detallados.append("   Nota: Valor fuera del rango típico convencional.")
        self.calculos_detallados.append("")
        
        # --- 4. NÚMERO DE REYNOLDS ---
        self.calculos_detallados.append("--- 4. NÚMERO DE REYNOLDS ---")
        
        Nre = (v0_md * d_espacio) / (86400 * viscosidad_cinematica)
        
        self.calculos_detallados.append("Número de Reynolds (Nre):")
        self.calculos_detallados.append(f"   Nre = ({v0_md:.1f} × {d_espacio}) / (86.400 × {viscosidad_cinematica:.3e})")
        self.calculos_detallados.append(f"   Nre = {Nre:.0f}")
        self.calculos_detallados.append("")
        
        # --- 5. TIEMPOS DE RETENCIÓN ---
        self.calculos_detallados.append("--- 5. TIEMPOS DE RETENCIÓN ---")
        
        # Tiempo en las placas
        t_placas_min = l_placa / v0_m_min
        
        self.calculos_detallados.append("Tiempo en las placas:")
        self.calculos_detallados.append(f"   t = {l_placa} / {v0_m_min:.2f}")
        self.calculos_detallados.append(f"   t = {t_placas_min:.1f} min")
        
        # Tiempo en el tanque de sedimentación
        profundidad_tanque = 3.30  # Asumido del ejemplo
        volumen_tanque = L_tanque * ancho_tanque * profundidad_tanque
        Q_m3_min = (Q_ls / 1000) * 60
        t_tanque_min = volumen_tanque / Q_m3_min
        
        self.calculos_detallados.append("Tiempo en el tanque de sedimentación:")
        self.calculos_detallados.append(f"   t = ({L_tanque} × {ancho_tanque} × {profundidad_tanque}) / ({Q_ls}/1000 × 60)")
        self.calculos_detallados.append(f"   t = {t_tanque_min:.0f} min")
        self.calculos_detallados.append("")
        
        # --- 6. NÚMERO DE PLACAS (N) ---
        self.calculos_detallados.append("--- 6. NÚMERO DE PLACAS (N) ---")
        
        # Fórmula geométrica exacta
        paso_horizontal = (d_espacio + e_placa) / np.sin(theta)
        lx = l_placa * np.cos(theta)
        N_calc = (L_tanque - lx) / paso_horizontal
        N_placas = int(N_calc) + 1
        
        self.calculos_detallados.append("Fórmula geométrica:")
        self.calculos_detallados.append(f"   N = (L - l cos {theta_grados}) sen {theta_grados} / (d + e)")
        self.calculos_detallados.append(f"   N = ({L_tanque} - {l_placa} cos {theta_grados}) sen {theta_grados} / ({d_espacio} + {e_placa})")
        self.calculos_detallados.append(f"   N = {N_calc:.2f} -> Se adoptan {N_placas} placas")
        
        # Almacenar resultados para uso en otras partes
        self.resultados = {
            'numero_placas': N_placas,
            'proyeccion_horizontal': lx,
            'proyeccion_vertical': l_placa * np.sin(theta),
            'paso_horizontal': paso_horizontal,
            'vs_critica_md': Vsc,
            'numero_reynolds': Nre,
            'longitud_efectiva': L_efectiva,
            'carga_superficial': CS,
            'velocidad_promedio': v0_md,
            'tiempo_placas': t_placas_min,
            'tiempo_tanque': t_tanque_min,
            'caudal_m3d': Q_m3d
        }
        
        # Verificaciones
        self.verificaciones = {
            'Nre < 500 (Flujo laminar)': Nre < 500,
            'Longitud efectiva > 0': L_efectiva > 0,
            'Número placas > 0': N_placas > 0,
            'Vs crítica razonable (14-22 m/d)': 14 <= Vsc <= 22,
            'Tiempo en placas adecuado (5-15 min)': 5 <= t_placas_min <= 15
        }
        
        return True
    
    def generar_grafica_mejorada(self):
        if not self.resultados:
            return None
            
        r = self.resultados
        p = self.parametros
        
        # Crear figura con subplots
        fig = plt.figure(figsize=(16, 14))
        gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.2])
        
        ax_detalle = fig.add_subplot(gs[0, :])
        ax_tanque = fig.add_subplot(gs[1, :])
        
        theta = np.radians(p['angulo_inclinacion'])
        lx = r['proyeccion_horizontal']
        ly = r['proyeccion_vertical']
        
        # ==========================================
        # GRÁFICO 1: DETALLE GEOMÉTRICO CON MEDIDAS
        # ==========================================
        ax_detalle.set_title("ZOOM: Detalle Constructivo (Metros)", 
                           fontsize=14, fontweight='bold', pad=20)
        ax_detalle.set_aspect('equal')
        
        # Origen local para el detalle
        x0, y0 = 0.2, 0.2
        
        def dibujar_placa_poligono(ax, x_inicio, y_inicio):
            p1 = np.array([x_inicio, y_inicio])
            p2 = p1 + np.array([lx, ly])
            v_perp = np.array([-np.sin(theta), np.cos(theta)])
            p3 = p2 + v_perp * p['espesor_placa']
            p4 = p1 + v_perp * p['espesor_placa']
            
            poly = patches.Polygon([p1, p2, p3, p4], closed=True, 
                                 facecolor='#B0BEC5', edgecolor='black', alpha=0.9, lw=1)
            ax.add_patch(poly)
            return p1, p2, p3, p4

        # Dibujar dos placas para mostrar las dimensiones
        p1_a, p2_a, p3_a, p4_a = dibujar_placa_poligono(ax_detalle, x0 + r['paso_horizontal'], y0)
        p1_b, p2_b, p3_b, p4_b = dibujar_placa_poligono(ax_detalle, x0, y0)
        
        # Acotaciones detalladas
        # 1. Longitud l
        ax_detalle.annotate('', xy=p2_a, xytext=p1_a,
                          arrowprops=dict(arrowstyle='<->', color='blue', lw=2))
        ax_detalle.text(x0 + r['paso_horizontal'] + lx/2 + 0.05, y0 + ly/2, 
                      f'l = {p["longitud_placa"]} m', 
                      color='blue', rotation=np.degrees(theta), fontsize=12, fontweight='bold')

        # 2. Separación d
        mid_l = p['longitud_placa'] / 3
        base_pt = p1_b + np.array([np.cos(theta), np.sin(theta)]) * mid_l
        normal_vec = np.array([np.sin(theta), -np.cos(theta)])
        
        ax_detalle.annotate('', 
                          xy=(base_pt[0] + normal_vec[0]*p['separacion_placas'], 
                              base_pt[1] + normal_vec[1]*p['separacion_placas']), 
                          xytext=(base_pt[0], base_pt[1]),
                          arrowprops=dict(arrowstyle='<|-|>', color='#D32F2F', lw=2))
        ax_detalle.text(base_pt[0] + 0.02, base_pt[1], 
                      f'd = {p["separacion_placas"]} m', 
                      color='#D32F2F', fontsize=12, fontweight='bold')

        # 3. Espesor e
        ax_detalle.annotate('', xy=p3_b, xytext=p2_b,
                          arrowprops=dict(arrowstyle='<|-|>', color='green', lw=1.5))
        ax_detalle.text(p2_b[0] - 0.08, p2_b[1] + 0.01, 
                      f'e = {p["espesor_placa"]} m', color='green', fontsize=10)

        # 4. Ángulo theta
        len_arc = 0.2
        arc = patches.Arc((x0, y0), len_arc*2, len_arc*2, angle=0, 
                        theta1=0, theta2=p['angulo_inclinacion'], color='black', lw=1.5)
        ax_detalle.add_patch(arc)
        ax_detalle.text(x0 + 0.25, y0 + 0.05, f'θ = {p["angulo_inclinacion"]}°', fontsize=12)

        # Ejes y rejilla para el detalle
        ax_detalle.set_xlabel("Distancia Horizontal (m)", fontsize=12)
        ax_detalle.set_ylabel("Altura (m)", fontsize=12)
        ax_detalle.set_xlim(0, x0 + r['paso_horizontal'] + lx + 0.2)
        ax_detalle.set_ylim(0, y0 + ly + 0.2)
        ax_detalle.xaxis.set_major_locator(MultipleLocator(0.1))
        ax_detalle.yaxis.set_major_locator(MultipleLocator(0.1))
        ax_detalle.grid(True, which='major', color='#90A4AE', linestyle='-', alpha=0.5)

        # ==========================================
        # GRÁFICO 2: VISTA GENERAL DEL TANQUE
        # ==========================================
        ax_tanque.set_title(f"VISTA GENERAL: Distribución en Tanque L={p['longitud_tanque']}m", 
                          fontsize=14, fontweight='bold', pad=20)
        
        # Dibujar Caja del Tanque
        H_tanque = ly + 0.5
        rect = patches.Rectangle((0, 0), p['longitud_tanque'], H_tanque, 
                              lw=3, edgecolor='#37474F', facecolor='#E1F5FE')
        ax_tanque.add_patch(rect)
        
        # Dibujar todas las placas
        x_offset = 0.1
        y_offset = 0.2
        
        for i in range(r['numero_placas']):
            x_pos = x_offset + i * r['paso_horizontal']
            if x_pos + lx > p['longitud_tanque']:
                break
            ax_tanque.plot([x_pos, x_pos + lx], [y_offset, y_offset + ly], 'k-', lw=1)
        
        # Acotaciones generales
        ax_tanque.annotate('', xy=(0, -0.15), xytext=(p['longitud_tanque'], -0.15),
                         arrowprops=dict(arrowstyle='|-|', lw=2, color='black'), 
                         annotation_clip=False)
        ax_tanque.text(p['longitud_tanque']/2, -0.4, f'Largo Total = {p["longitud_tanque"]} m', 
                     ha='center', fontsize=12, fontweight='bold')

        # Caja de resultados mejorada
        texto_resultados = (
            f"RESULTADOS DE DISEÑO:\n"
            f"---------------------\n"
            f"Vel. Crítica = {r['vs_critica_md']:.1f} m/d\n"
            f"Reynolds = {int(r['numero_reynolds'])}\n"
            f"Total Placas = {r['numero_placas']}\n"
            f"Inclinación = {p['angulo_inclinacion']}°\n"
            f"Long. Efectiva = {r['longitud_efectiva']:.2f} m"
        )
        props = dict(boxstyle='round', facecolor='white', alpha=1.0, edgecolor='black')
        ax_tanque.text(p['longitud_tanque'] * 0.02, H_tanque * 0.7, texto_resultados, 
                     bbox=props, zorder=10, fontsize=11)

        # Ejes y rejilla para el tanque
        ax_tanque.set_xlabel("Longitud del Sedimentador (m)", fontsize=12)
        ax_tanque.set_ylabel("Profundidad (m)", fontsize=12)
        ax_tanque.set_xlim(-0.2, p['longitud_tanque'] + 0.2)
        ax_tanque.set_ylim(-0.5, H_tanque + 0.2)
        ax_tanque.set_aspect('equal')
        ax_tanque.xaxis.set_major_locator(MultipleLocator(0.5))
        ax_tanque.yaxis.set_major_locator(MultipleLocator(0.5))
        ax_tanque.grid(True, which='major', color='gray', linestyle='--', alpha=0.5)

        plt.tight_layout()
        return fig
    
    def generar_reporte_pdf(self):
        pdf = FPDF()
        pdf.add_page()
        
        # Encabezado
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, 'ANÁLISIS SEDIMENTADOR CON PLACAS INCLINADAS', 0, 1, 'C')
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, f'Fecha: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
        pdf.ln(5)
        
        # Datos del problema
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(0, 10, 'DATOS DE ENTRADA', 1, 1, 'L', 1)
        pdf.set_font("Arial", '', 10)
        p = self.parametros
        pdf.cell(0, 6, f'Caudal: {p["caudal_ls"]} L/s', 0, 1)
        pdf.cell(0, 6, f'Longitud tanque: {p["longitud_tanque"]} m', 0, 1)
        pdf.cell(0, 6, f'Longitud placa: {p["longitud_placa"]} m', 0, 1)
        pdf.cell(0, 6, f'Separación placas: {p["separacion_placas"]} m', 0, 1)
        pdf.cell(0, 6, f'Espesor placa: {p["espesor_placa"]} m', 0, 1)
        pdf.cell(0, 6, f'Ángulo inclinación: {p["angulo_inclinacion"]}°', 0, 1)
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
        
        pdf.ln(5)
        
        # Resultados
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(0, 10, 'RESULTADOS', 1, 1, 'L', 1)
        pdf.set_font("Arial", '', 10)
        
        r = self.resultados
        pdf.cell(0, 6, f'Número de placas: {r["numero_placas"]}', 0, 1)
        pdf.cell(0, 6, f'Velocidad crítica: {r["vs_critica_md"]:.2f} m/d', 0, 1)
        pdf.cell(0, 6, f'Número Reynolds: {r["numero_reynolds"]:.2f}', 0, 1)
        pdf.cell(0, 6, f'Longitud efectiva: {r["longitud_efectiva"]:.2f} m', 0, 1)
        pdf.cell(0, 6, f'Paso horizontal: {r["paso_horizontal"]:.3f} m', 0, 1)
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
        
        # Guardar PDF temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf.output(tmp_file.name)
            return tmp_file.name

# ==========================================
# INTERFAZ PRINCIPAL
# ==========================================
def main():
    st.title("📐 Análisis de Sedimentador con Placas Inclinadas")
    st.markdown("### Análisis Geométrico y Hidráulico - Versión Mejorada")
    
    if 'analizador_placas' not in st.session_state:
        st.session_state.analizador_placas = AnalizadorPlacasInclinadas()
    
    # --- SIDEBAR ---
    st.sidebar.header("📋 Configuración del Sistema")
    
    with st.sidebar.form("form_parametros"):
        st.subheader("Datos del Sedimentador")
        
        caudal_ls = st.number_input(
            "Caudal (L/s)",
            min_value=1.0,
            max_value=1000.0,
            value=22.0,
            step=1.0
        )
        
        longitud_tanque = st.number_input(
            "Longitud disponible del tanque (m)",
            min_value=1.0,
            max_value=20.0,
            value=5.0,
            step=0.5
        )
        
        st.subheader("Configuración de Placas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            longitud_placa = st.number_input(
                "Longitud placa (m)",
                min_value=0.5,
                max_value=3.0,
                value=1.2,
                step=0.1
            )
            
            separacion_placas = st.number_input(
                "Separación entre placas (m)",
                min_value=0.02,
                max_value=0.2,
                value=0.06,
                step=0.01
            )
        
        with col2:
            espesor_placa = st.number_input(
                "Espesor placa (m)",
                min_value=0.005,
                max_value=0.05,
                value=0.01,
                step=0.005
            )
            
            angulo_inclinacion = st.slider(
                "Ángulo inclinación (°)",
                min_value=45,
                max_value=75,
                value=60
            )
        
        viscosidad_cinematica = st.number_input(
            "Viscosidad cinemática (m²/s)",
            format="%.2e",
            value=1.139e-6,
            step=1e-7
        )
        
        # Botón de cálculo
        if st.form_submit_button("🚀 Analizar Sistema"):
            parametros = {
                'caudal_ls': caudal_ls,
                'longitud_tanque': longitud_tanque,
                'longitud_placa': longitud_placa,
                'espesor_placa': espesor_placa,
                'separacion_placas': separacion_placas,
                'angulo_inclinacion': angulo_inclinacion,
                'viscosidad_cinematica': viscosidad_cinematica
            }
            st.session_state.analizador_placas.calcular(parametros)
            st.rerun()
    
    # --- EJEMPLOS RÁPIDOS ---
    with st.sidebar.expander("🎯 Ejemplos Rápidos"):
        if st.button("Ejemplo 5.13 Original"):
            st.session_state.analizador_placas.calcular({
                'caudal_ls': 22.0,
                'longitud_tanque': 5.0,
                'longitud_placa': 1.2,
                'espesor_placa': 0.01,
                'separacion_placas': 0.06,
                'angulo_inclinacion': 60,
                'viscosidad_cinematica': 1.139e-6
            })
            st.rerun()
    
    # --- RESULTADOS PRINCIPALES ---
    analizador = st.session_state.analizador_placas
    
    if analizador.resultados:
        st.success("✅ Análisis completado exitosamente")
        
        # Mostrar configuración actual
        st.info(f"""
        **Configuración analizada:** 
        - Caudal: {analizador.parametros['caudal_ls']} L/s
        - Longitud tanque: {analizador.parametros['longitud_tanque']} m
        - Placas: {analizador.parametros['longitud_placa']} m, {analizador.parametros['angulo_inclinacion']}°
        - Separación: {analizador.parametros['separacion_placas']} m
        """)
        
        # Mostrar resultados en pestañas
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Resultados", "🧮 Cálculos Detallados", "📈 Gráficas", "📥 Reporte"])
        
        with tab1:
            st.subheader("Resultados del Análisis")
            
            # Métricas principales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Número de Placas", 
                         f"{analizador.resultados['numero_placas']}")
            
            with col2:
                st.metric("Velocidad Crítica", 
                         f"{analizador.resultados['vs_critica_md']:.1f} m/d")
            
            with col3:
                st.metric("Número Reynolds", 
                         f"{analizador.resultados['numero_reynolds']:.0f}")
            
            with col4:
                st.metric("Longitud Efectiva", 
                         f"{analizador.resultados['longitud_efectiva']:.2f} m")
            
            # Tabla de resultados detallados
            st.subheader("📋 Parámetros Calculados")
            datos_resumen = {
                'Parámetro': ['Carga Superficial', 'Velocidad promedio', 'Tiempo en placas',
                             'Tiempo en tanque', 'Paso horizontal', 'Caudal diario'],
                'Valor': [f"{analizador.resultados['carga_superficial']:.0f} m/d",
                         f"{analizador.resultados['velocidad_promedio']:.1f} m/d",
                         f"{analizador.resultados['tiempo_placas']:.1f} min",
                         f"{analizador.resultados['tiempo_tanque']:.0f} min",
                         f"{analizador.resultados['paso_horizontal']:.3f} m",
                         f"{analizador.resultados['caudal_m3d']:.0f} m³/d"],
                'Descripción': ['CS = Q/A', 'v0 = CS/senθ', 't = l/v0',
                               't = V/Q', 'Paso = (d+e)/senθ', 'Q diario total']
            }
            
            df_resumen = pd.DataFrame(datos_resumen)
            st.dataframe(df_resumen, use_container_width=True)
            
            # Verificaciones
            st.subheader("✅ Verificaciones de Diseño")
            cols = st.columns(2)
            idx = 0
            for criterio, cumple in analizador.verificaciones.items():
                if cumple:
                    cols[idx % 2].success(f"**{criterio}**")
                else:
                    cols[idx % 2].error(f"**{criterio}**")
                idx += 1
        
        with tab2:
            st.subheader("🧮 Cálculos Detallados Paso a Paso")
            st.code("\n".join(analizador.calculos_detallados), language="text")
        
        with tab3:
            st.subheader("📈 Análisis Gráfico Mejorado")
            fig = analizador.generar_grafica_mejorada()
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
                            file_name=f"analisis_placas_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                            mime="application/pdf"
                        )
                    
                    # Limpiar archivo temporal
                    os.unlink(pdf_file)
    
    else:
        # Pantalla inicial
        st.info("""
        ## 🧭 Análisis de Sedimentadores con Placas Inclinadas - VERSIÓN MEJORADA
        
        **Nuevas características:**
        - ✅ **Cálculos paso a paso detallados** con todas las operaciones
        - ✅ **Gráficas profesionales** con ejes y rejillas de medición
        - ✅ **Zoom geométrico** con acotaciones precisas
        - ✅ **Vista general del tanque** con reglas de medición
        - ✅ **Verificaciones de diseño** mejoradas
        
        **🎯 Ejemplo 5.13 Original incluido:**
        - Caudal: 22 L/s
        - Longitud tanque: 5.0 m
        - Placas: 1.2 m de longitud, 60° inclinación
        - Separación: 6 cm entre placas
        - Espesor: 1 cm
        
        **📊 Salidas mejoradas:**
        - Todos los cálculos intermedios mostrados
        - Gráficas con escalas en metros
        - Rejillas de medición cada 10cm/50cm
        - Acotaciones profesionales
        """)

if __name__ == "__main__":
    main()
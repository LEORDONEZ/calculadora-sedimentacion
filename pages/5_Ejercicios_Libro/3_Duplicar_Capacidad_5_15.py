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
    page_title="Ejemplo 5.15 - Duplicación Capacidad con Placas",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CLASE PARA EJEMPLO 5.15
# ==========================================
class AnalizadorEjemplo515:
    def __init__(self):
        self.parametros = {}
        self.resultados = {}
        self.calculos_detallados = []
    
    def calcular(self, parametros):
        self.parametros = parametros
        self.calculos_detallados = []
        
        # --- DATOS DE ENTRADA ---
        Q_total_actual = parametros['caudal_total_actual']
        num_tanques = parametros['numero_tanques']
        L_tanque = parametros['longitud_tanque']
        ancho_tanque = parametros['ancho_tanque']
        prof_tanque = parametros['profundidad_tanque']
        l_placa = parametros['longitud_placa']
        w_placa = parametros['ancho_placa']
        e_placa = parametros['espesor_placa']
        d_espacio = parametros['separacion_placas']
        theta_grad = parametros['angulo_inclinacion']
        viscosidad_cinematica = parametros['viscosidad_cinematica']
        
        theta = np.radians(theta_grad)
        
        # ==========================================
        # CÁLCULOS DETALLADOS
        # ==========================================
        self.calculos_detallados.append("=" * 60)
        self.calculos_detallados.append("SOLUCIÓN PASO A PASO: EJEMPLO 5.15")
        self.calculos_detallados.append("=" * 60)
        self.calculos_detallados.append("")
        
        # --- 1. DATOS DEL PROBLEMA ---
        self.calculos_detallados.append("--- 1. DATOS DEL PROBLEMA ---")
        self.calculos_detallados.append(f"   Objetivo: DUPLICAR la capacidad de sedimentación")
        self.calculos_detallados.append(f"   Caudal total actual: {Q_total_actual} m³/d")
        self.calculos_detallados.append(f"   Número de tanques: {num_tanques}")
        self.calculos_detallados.append(f"   Dimensiones tanque: {L_tanque}m × {ancho_tanque}m × {prof_tanque}m")
        self.calculos_detallados.append(f"   Placas: {l_placa}m largo × {w_placa}m ancho × {e_placa}m espesor")
        self.calculos_detallados.append(f"   Separación entre placas: {d_espacio}m")
        self.calculos_detallados.append(f"   Ángulo inclinación: {theta_grad}°")
        self.calculos_detallados.append("")
        
        # Cálculo caudal por tanque después de duplicar capacidad
        Q_tanque_m3d = Q_total_actual / num_tanques
        
        self.calculos_detallados.append("--- CAUDAL POR TANQUE (Después de duplicar) ---")
        self.calculos_detallados.append(f"   Q por tanque = {Q_total_actual} / {num_tanques} = {Q_tanque_m3d} m³/d")
        self.calculos_detallados.append("")
        
        # --- PASO A: CARGA SUPERFICIAL ACTUAL ---
        CS_base = Q_total_actual / (num_tanques * L_tanque * ancho_tanque)
        
        self.calculos_detallados.append("--- A) CARGA SUPERFICIAL BASE (Calidad a mantener) ---")
        self.calculos_detallados.append(f"   CS = Q_actual / Área_total")
        self.calculos_detallados.append(f"   CS = {Q_total_actual} / ({num_tanques} × {L_tanque} × {ancho_tanque})")
        self.calculos_detallados.append(f"   CS = {CS_base:.1f} m/d")
        self.calculos_detallados.append("")
        
        # --- PASO B: ÁREA DE SEDIMENTACIÓN DE ALTA TASA ---
        L_rel = l_placa / d_espacio
        S = 1.0
        
        term_geo = np.sin(theta) + (L_rel * np.cos(theta))
        denominador = CS_base * np.sin(theta) * term_geo
        Area_req = (S * Q_tanque_m3d) / denominador
        
        self.calculos_detallados.append("--- B) ÁREA DE ALTA TASA REQUERIDA (Por Tanque) ---")
        self.calculos_detallados.append(f"   Longitud relativa L = l / d = {l_placa} / {d_espacio} = {L_rel:.0f}")
        self.calculos_detallados.append(f"   Término geométrico = sen{theta_grad} + {L_rel:.0f}cos{theta_grad} = {term_geo:.2f}")
        self.calculos_detallados.append(f"   A = (S × Q) / [CS × senθ × (senθ + Lcosθ)]")
        self.calculos_detallados.append(f"   A = (1 × {Q_tanque_m3d}) / [{CS_base:.1f} × sen{theta_grad} × {term_geo:.2f}]")
        self.calculos_detallados.append(f"   A = {Area_req:.0f} m²")
        self.calculos_detallados.append("")
        
        # Cálculo de la Longitud de la Zona
        num_filas_placas = 3
        ancho_modulos = num_filas_placas * w_placa
        L_zona_calc = Area_req / ancho_modulos
        
        self.calculos_detallados.append("--- DIMENSIONES DE LA ZONA DE ALTA TASA ---")
        self.calculos_detallados.append(f"   Ancho efectivo módulos = {num_filas_placas} filas × {w_placa}m = {ancho_modulos:.1f} m")
        self.calculos_detallados.append(f"   Longitud zona calculada = Área / Ancho = {Area_req:.0f} / {ancho_modulos:.1f} = {L_zona_calc:.1f} m")
        
        # Se adopta L_zona = 6.0 m (como en el libro)
        L_zona = 6.0
        self.calculos_detallados.append(f"   -> Se adopta L_zona = {L_zona} m")
        self.calculos_detallados.append("")
        
        # --- PASO C: NÚMERO DE PLACAS ---
        numerador_N = (L_zona * np.sin(theta)) + d_espacio
        denominador_N = d_espacio + e_placa
        N_filas = numerador_N / denominador_N
        N_filas_entero = int(N_filas)
        
        self.calculos_detallados.append("--- C) NÚMERO DE PLACAS ---")
        self.calculos_detallados.append(f"   Fórmula: N = (L_zona × senθ + d) / (d + e)")
        self.calculos_detallados.append(f"   N = ({L_zona} × sen{theta_grad} + {d_espacio}) / ({d_espacio} + {e_placa})")
        self.calculos_detallados.append(f"   N = {N_filas:.1f} → Se adopta {N_filas_entero} placas por fila")
        
        total_placas = N_filas_entero * num_filas_placas * num_tanques
        self.calculos_detallados.append(f"   Total placas = {N_filas_entero} × {num_filas_placas} × {num_tanques} = {total_placas} placas")
        self.calculos_detallados.append("")
        
        # --- PASO D: VERIFICACIÓN HIDRÁULICA ---
        area_zona_real = ancho_tanque * L_zona
        v0_real_md = Q_tanque_m3d / (area_zona_real * np.sin(theta))
        
        self.calculos_detallados.append("--- D) VERIFICACIÓN HIDRÁULICA (Alta Tasa) ---")
        self.calculos_detallados.append(f"   Área zona real = Ancho × L_zona = {ancho_tanque} × {L_zona} = {area_zona_real} m²")
        self.calculos_detallados.append(f"   v0 = Q / (A_planta × senθ)")
        self.calculos_detallados.append(f"   v0 = {Q_tanque_m3d} / ({area_zona_real} × sen{theta_grad})")
        self.calculos_detallados.append(f"   v0 = {v0_real_md:.0f} m/d")
        self.calculos_detallados.append("")
        
        # Número de Reynolds
        v0_real_ms = v0_real_md / 86400
        Nre = (v0_real_ms * d_espacio) / viscosidad_cinematica
        
        self.calculos_detallados.append("--- NÚMERO DE REYNOLDS ---")
        self.calculos_detallados.append(f"   Nre = (v0 × d) / ν")
        self.calculos_detallados.append(f"   Nre = ({v0_real_md:.0f} × {d_espacio}) / (86400 × {viscosidad_cinematica:.2e})")
        self.calculos_detallados.append(f"   Nre = {Nre:.0f}")
        
        if Nre < 500:
            self.calculos_detallados.append("   ✓ Flujo laminar (Nre < 500) - CONDICIÓN CUMPLIDA")
        else:
            self.calculos_detallados.append("   ✗ Flujo no laminar (Nre > 500) - CONDICIÓN NO CUMPLIDA")
        self.calculos_detallados.append("")
        
        # --- PASO E: TIEMPOS DE RETENCIÓN ---
        v0_min = v0_real_md / 1440
        t_placas = l_placa / v0_min
        
        self.calculos_detallados.append("--- E) TIEMPOS DE RETENCIÓN ---")
        self.calculos_detallados.append("   En las placas:")
        self.calculos_detallados.append(f"   t_placas = l / v0 = {l_placa} / {v0_min:.3f}")
        self.calculos_detallados.append(f"   t_placas = {t_placas:.1f} min")
        
        # Tiempo en tanque completo
        vol_tanque = L_tanque * ancho_tanque * prof_tanque
        t_tanque = vol_tanque / (Q_tanque_m3d / 1440)
        
        self.calculos_detallados.append("   En el tanque completo:")
        self.calculos_detallados.append(f"   Volumen tanque = {L_tanque} × {ancho_tanque} × {prof_tanque} = {vol_tanque:.0f} m³")
        self.calculos_detallados.append(f"   t_tanque = Volumen / (Q/1440) = {vol_tanque:.0f} / ({Q_tanque_m3d}/1440)")
        self.calculos_detallados.append(f"   t_tanque = {t_tanque:.0f} min")
        self.calculos_detallados.append("")
        
        # --- PASO F: VERIFICACIÓN FINAL CON SCHULZE ---
        L_trans = 0.013 * Nre
        L_eff = L_rel - L_trans
        
        self.calculos_detallados.append("--- F) VERIFICACIÓN FINAL DE EFICIENCIA (Método Schulze) ---")
        self.calculos_detallados.append(f"   Longitud transición L' = 0.013 × Nre = 0.013 × {Nre:.0f} = {L_trans:.2f}")
        self.calculos_detallados.append(f"   Longitud efectiva Le = L - L' = {L_rel:.0f} - {L_trans:.2f} = {L_eff:.2f}")
        
        # Velocidad crítica real
        denom_real = np.sin(theta) + (L_eff * np.cos(theta))
        Vsc_real = (1.0 * v0_real_md) / denom_real
        
        self.calculos_detallados.append("   Velocidad crítica real:")
        self.calculos_detallados.append(f"   Vsc = (1 × v0) / (senθ + Le × cosθ)")
        self.calculos_detallados.append(f"   Vsc = (1 × {v0_real_md:.0f}) / (sen{theta_grad} + {L_eff:.2f} × cos{theta_grad})")
        self.calculos_detallados.append(f"   Vsc = {Vsc_real:.1f} m/d")
        
        if Vsc_real <= CS_base:
            self.calculos_detallados.append(f"   ✓ DISEÑO ACEPTABLE: Vsc_real ({Vsc_real:.1f} m/d) ≤ CS_base ({CS_base:.1f} m/d)")
            self.calculos_detallados.append("   Se mantienen las mismas condiciones de sedimentación")
        else:
            self.calculos_detallados.append(f"   ✗ DISEÑO NO ACEPTABLE: Vsc_real > CS_base")
        self.calculos_detallados.append("")
        
        # Almacenar resultados
        self.resultados = {
            'carga_superficial_base': CS_base,
            'area_requerida': Area_req,
            'longitud_zona': L_zona,
            'numero_placas_por_fila': N_filas_entero,
            'total_placas': total_placas,
            'velocidad_flujo': v0_real_md,
            'numero_reynolds': Nre,
            'tiempo_placas': t_placas,
            'tiempo_tanque': t_tanque,
            'velocidad_critica_real': Vsc_real,
            'diseño_aceptable': Vsc_real <= CS_base
        }
        
        return True
    
    def generar_grafica_esquema(self):
        if not self.resultados:
            return None
            
        p = self.parametros
        L_zona = self.resultados['longitud_zona']
        l_placa = p['longitud_placa']
        d_espacio = p['separacion_placas']
        e_placa = p['espesor_placa']
        theta_grad = p['angulo_inclinacion']
        
        theta = np.radians(theta_grad)
        paso_h = (d_espacio + e_placa) / np.sin(theta)
        lx = l_placa * np.cos(theta)
        ly = l_placa * np.sin(theta)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        ax.set_title(f"Figura 5.35: Dimensiones Sedimentador con Placas\nEjemplo 5.15 - Duplicación de Capacidad", 
                   fontsize=14, fontweight='bold', pad=15)
        
        # Altura visual para el gráfico
        H_visual = ly + 0.5
        
        # Dibujar Caja Límite de la Zona
        rect = patches.Rectangle((0, 0), L_zona, H_visual, lw=3, 
                               edgecolor='#424242', facecolor='white')
        ax.add_patch(rect)
        
        # Dibujar Placas (número reducido para claridad)
        N_dibujo = min(20, self.resultados['numero_placas_por_fila'])
        x_start = 0.2
        y_start = 0.2
        
        for i in range(N_dibujo):
            x = x_start + i * paso_h * 2.5  # Factor para espaciar visualmente
            if x + lx > L_zona - 0.2: 
                break
            
            # Placa como polígono
            p1 = np.array([x, y_start])
            p2 = p1 + np.array([lx, ly])
            v_norm = np.array([-np.sin(theta), np.cos(theta)]) * e_placa
            p3 = p2 + v_norm
            p4 = p1 + v_norm
            
            poly = patches.Polygon([p1, p2, p3, p4], closed=True, 
                                 facecolor='#B0BEC5', edgecolor='black', alpha=0.8)
            ax.add_patch(poly)
            
            # Acotación en la primera placa
            if i == 2:
                # Cota longitud l
                ax.annotate('', xy=p2, xytext=p1,
                          arrowprops=dict(arrowstyle='<->', color='blue', lw=2))
                ax.text(x + lx/2 - 0.3, y_start + ly/2, f'l = {l_placa}m', 
                      color='blue', rotation=theta_grad, fontweight='bold')
        
        # Cota General L
        ax.annotate('', xy=(0, -0.2), xytext=(L_zona, -0.2),
                  arrowprops=dict(arrowstyle='|-|', lw=2, color='black'), 
                  annotation_clip=False)
        ax.text(L_zona/2, -0.4, f'Longitud Zona Alta Tasa = {L_zona} m', 
               ha='center', fontweight='bold', fontsize=12)
        
        # Cota d (separación)
        xc = x_start + 8 * paso_h * 2.5
        yc = y_start + ly/2
        ax.annotate('', 
                  xy=(xc + np.sin(theta)*0.2, yc - np.cos(theta)*0.2), 
                  xytext=(xc, yc),
                  arrowprops=dict(arrowstyle='|-|', color='red', lw=2))
        ax.text(xc + 0.1, yc - 0.1, f'd = {d_espacio}m', 
               color='red', fontweight='bold')

        # Ángulo
        ax.text(x_start + 0.5, y_start + 0.1, f'θ = {theta_grad}°', fontsize=12)
        
        # Configuración Ejes
        ax.set_xlim(-0.5, L_zona + 0.5)
        ax.set_ylim(-0.5, H_visual + 0.5)
        ax.set_aspect('equal')
        ax.set_xlabel("Longitud (m)")
        ax.set_ylabel("Altura (m)")
        
        ax.xaxis.set_major_locator(MultipleLocator(1.0))
        ax.grid(True, linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        return fig
    
    def generar_reporte_pdf(self):
        pdf = FPDF()
        pdf.add_page()
        
        # Encabezado
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, 'EJEMPLO 5.15 - DUPLICACIÓN CAPACIDAD CON PLACAS', 0, 1, 'C')
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, f'Fecha: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
        pdf.ln(5)
        
        # Datos del problema
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(0, 10, 'DATOS DE ENTRADA', 1, 1, 'L', 1)
        pdf.set_font("Arial", '', 10)
        p = self.parametros
        pdf.cell(0, 6, f'Caudal total actual: {p["caudal_total_actual"]} m³/d', 0, 1)
        pdf.cell(0, 6, f'Número de tanques: {p["numero_tanques"]}', 0, 1)
        pdf.cell(0, 6, f'Dimensiones tanque: {p["longitud_tanque"]}m × {p["ancho_tanque"]}m × {p["profundidad_tanque"]}m', 0, 1)
        pdf.cell(0, 6, f'Placas: {p["longitud_placa"]}m × {p["ancho_placa"]}m × {p["espesor_placa"]}m', 0, 1)
        pdf.cell(0, 6, f'Separación placas: {p["separacion_placas"]}m', 0, 1)
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
        
        # Resultados
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(0, 10, 'RESULTADOS FINALES', 1, 1, 'L', 1)
        pdf.set_font("Arial", '', 10)
        
        r = self.resultados
        pdf.cell(0, 6, f'Carga superficial base: {r["carga_superficial_base"]:.1f} m/d', 0, 1)
        pdf.cell(0, 6, f'Área requerida por tanque: {r["area_requerida"]:.0f} m²', 0, 1)
        pdf.cell(0, 6, f'Longitud zona alta tasa: {r["longitud_zona"]} m', 0, 1)
        pdf.cell(0, 6, f'Número total de placas: {r["total_placas"]}', 0, 1)
        pdf.cell(0, 6, f'Velocidad crítica real: {r["velocidad_critica_real"]:.1f} m/d', 0, 1)
        pdf.cell(0, 6, f'Diseño aceptable: {"SÍ" if r["diseño_aceptable"] else "NO"}', 0, 1)
        
        # Guardar PDF temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf.output(tmp_file.name)
            return tmp_file.name

# ==========================================
# INTERFAZ PRINCIPAL
# ==========================================
def main():
    st.title("📐 Ejemplo 5.15 - Duplicación de Capacidad con Placas")
    st.markdown("### Análisis de Sedimentadores Existentes con Módulos de Placas")
    
    if 'analizador_515' not in st.session_state:
        st.session_state.analizador_515 = AnalizadorEjemplo515()
    
    # --- SIDEBAR ---
    st.sidebar.header("📋 Configuración del Ejemplo 5.15")
    
    with st.sidebar.form("form_parametros_515"):
        st.subheader("Datos de la Planta Existente")
        
        caudal_total_actual = st.number_input(
            "Caudal total actual (m³/d)",
            min_value=1000.0,
            max_value=50000.0,
            value=10000.0,
            step=1000.0
        )
        
        numero_tanques = st.number_input(
            "Número de tanques existentes",
            min_value=1,
            max_value=10,
            value=2,
            step=1
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            longitud_tanque = st.number_input(
                "Longitud tanque (m)",
                min_value=5.0,
                max_value=50.0,
                value=24.0,
                step=1.0
            )
            
            ancho_tanque = st.number_input(
                "Ancho tanque (m)",
                min_value=2.0,
                max_value=20.0,
                value=8.0,
                step=1.0
            )
        
        with col2:
            profundidad_tanque = st.number_input(
                "Profundidad tanque (m)",
                min_value=1.0,
                max_value=10.0,
                value=3.0,
                step=0.5
            )
        
        st.subheader("Configuración de Placas")
        
        col3, col4 = st.columns(2)
        
        with col3:
            longitud_placa = st.number_input(
                "Longitud placa (m)",
                min_value=0.5,
                max_value=3.0,
                value=1.2,
                step=0.1
            )
            
            ancho_placa = st.number_input(
                "Ancho placa (m)",
                min_value=1.0,
                max_value=5.0,
                value=2.4,
                step=0.1
            )
        
        with col4:
            espesor_placa = st.number_input(
                "Espesor placa (m)",
                min_value=0.005,
                max_value=0.05,
                value=0.01,
                step=0.005
            )
            
            separacion_placas = st.number_input(
                "Separación entre placas (m)",
                min_value=0.02,
                max_value=0.15,
                value=0.06,
                step=0.01
            )
        
        angulo_inclinacion = st.slider(
            "Ángulo de inclinación (°)",
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
        if st.form_submit_button("🚀 Calcular Ejemplo 5.15"):
            parametros = {
                'caudal_total_actual': caudal_total_actual,
                'numero_tanques': numero_tanques,
                'longitud_tanque': longitud_tanque,
                'ancho_tanque': ancho_tanque,
                'profundidad_tanque': profundidad_tanque,
                'longitud_placa': longitud_placa,
                'ancho_placa': ancho_placa,
                'espesor_placa': espesor_placa,
                'separacion_placas': separacion_placas,
                'angulo_inclinacion': angulo_inclinacion,
                'viscosidad_cinematica': viscosidad_cinematica
            }
            st.session_state.analizador_515.calcular(parametros)
            st.rerun()
    
    # --- EJEMPLO ORIGINAL ---
    with st.sidebar.expander("🎯 Ejemplo Original 5.15"):
        if st.button("Cargar Valores Originales"):
            st.session_state.analizador_515.calcular({
                'caudal_total_actual': 10000.0,
                'numero_tanques': 2,
                'longitud_tanque': 24.0,
                'ancho_tanque': 8.0,
                'profundidad_tanque': 3.0,
                'longitud_placa': 1.2,
                'ancho_placa': 2.4,
                'espesor_placa': 0.01,
                'separacion_placas': 0.06,
                'angulo_inclinacion': 60,
                'viscosidad_cinematica': 1.139e-6
            })
            st.rerun()
    
    # --- RESULTADOS PRINCIPALES ---
    analizador = st.session_state.analizador_515
    
    if analizador.resultados:
        st.success("✅ Análisis del Ejemplo 5.15 completado")
        
        # Mostrar configuración actual
        st.info(f"""
        **Configuración analizada:** 
        - Objetivo: Duplicar capacidad manteniendo eficiencia
        - Caudal total actual: {analizador.parametros['caudal_total_actual']} m³/d
        - Tanques: {analizador.parametros['numero_tanques']} unidades
        - Placas: {analizador.parametros['longitud_placa']}m, {analizador.parametros['angulo_inclinacion']}°
        """)
        
        # Mostrar resultados en pestañas
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Resultados", "🧮 Cálculos Detallados", "📈 Esquema", "📥 Reporte"])
        
        with tab1:
            st.subheader("Resultados del Análisis")
            
            # Métricas principales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Carga Superficial Base", f"{analizador.resultados['carga_superficial_base']:.1f} m/d")
            
            with col2:
                st.metric("Total Placas", f"{analizador.resultados['total_placas']}")
            
            with col3:
                st.metric("Número Reynolds", f"{analizador.resultados['numero_reynolds']:.0f}")
            
            with col4:
                status_color = "🟢" if analizador.resultados['diseño_aceptable'] else "🔴"
                st.metric("Diseño Aceptable", f"{status_color} {'SÍ' if analizador.resultados['diseño_aceptable'] else 'NO'}")
            
            # Tabla de resultados detallados
            st.subheader("📋 Parámetros Calculados")
            
            datos_resumen = {
                'Parámetro': [
                    'Área requerida por tanque',
                    'Longitud zona alta tasa', 
                    'Placas por fila',
                    'Velocidad de flujo',
                    'Tiempo en placas',
                    'Tiempo en tanque',
                    'Velocidad crítica real'
                ],
                'Valor': [
                    f"{analizador.resultados['area_requerida']:.0f} m²",
                    f"{analizador.resultados['longitud_zona']} m",
                    f"{analizador.resultados['numero_placas_por_fila']}",
                    f"{analizador.resultados['velocidad_flujo']:.0f} m/d",
                    f"{analizador.resultados['tiempo_placas']:.1f} min",
                    f"{analizador.resultados['tiempo_tanque']:.0f} min",
                    f"{analizador.resultados['velocidad_critica_real']:.1f} m/d"
                ],
                'Descripción': [
                    'Área para módulos de placas',
                    'Longitud adoptada para zona',
                    'Número de placas por fila',
                    'Velocidad promedio en placas',
                    'Tiempo de retención en placas',
                    'Tiempo total en tanque',
                    'Velocidad crítica calculada'
                ]
            }
            
            df_resumen = pd.DataFrame(datos_resumen)
            st.dataframe(df_resumen, use_container_width=True)
            
            # Verificación final
            st.subheader("✅ Verificación Final")
            if analizador.resultados['diseño_aceptable']:
                st.success(f"""
                **DISEÑO ACEPTABLE** ✓
                
                La velocidad crítica real ({analizador.resultados['velocidad_critica_real']:.1f} m/d) es menor o igual 
                que la carga superficial base ({analizador.resultados['carga_superficial_base']:.1f} m/d), por lo que 
                se mantienen las mismas condiciones de sedimentación mientras se duplica la capacidad.
                """)
            else:
                st.error(f"""
                **DISEÑO NO ACEPTABLE** ✗
                
                La velocidad crítica real ({analizador.resultados['velocidad_critica_real']:.1f} m/d) excede 
                la carga superficial base ({analizador.resultados['carga_superficial_base']:.1f} m/d). 
                Se requiere revisar el diseño.
                """)
        
        with tab2:
            st.subheader("🧮 Cálculos Detallados Paso a Paso")
            st.code("\n".join(analizador.calculos_detallados), language="text")
        
        with tab3:
            st.subheader("📈 Esquema del Sedimentador con Placas")
            fig = analizador.generar_grafica_esquema()
            if fig:
                st.pyplot(fig)
                st.caption("Figura 5.35: Esquema de la disposición de placas en la zona de alta tasa")
        
        with tab4:
            st.subheader("📥 Generar Reporte PDF")
            
            if st.button("🖨️ Generar Reporte Completo en PDF"):
                with st.spinner("Generando reporte PDF..."):
                    pdf_file = analizador.generar_reporte_pdf()
                    
                    with open(pdf_file, "rb") as f:
                        st.download_button(
                            label="📥 Descargar Reporte PDF",
                            data=f,
                            file_name=f"ejemplo_5_15_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                            mime="application/pdf"
                        )
                    
                    # Limpiar archivo temporal
                    os.unlink(pdf_file)
    
    else:
        # Pantalla inicial
        st.info("""
        ## 🧭 Ejemplo 5.15 - Duplicación de Capacidad con Módulos de Placas
        
        **Objetivo:** Duplicar la capacidad de sedimentación de una planta existente manteniendo la misma eficiencia, 
        mediante la instalación de módulos de placas inclinadas en los sedimentadores actuales.
        
        **Problema original del libro:**
        - Planta trata 10,000 m³/d (116 L/s) con 2 sedimentadores
        - Dimensiones: 24m × 8m × 3m cada uno
        - Se desea duplicar capacidad a 20,000 m³/d
        - Solución: Instalar placas de 1.2m × 2.4m × 0.01m a 60°
        
        **Metodología de cálculo:**
        1. Determinar carga superficial base actual
        2. Calcular área requerida para módulos de placas
        3. Determinar número de placas necesarias
        4. Verificar condiciones hidráulicas (Reynolds)
        5. Calcular tiempos de retención
        6. Verificar eficiencia con método Schulze
        
        **🎯 Resultado esperado:** Diseño que permite duplicar el caudal manteniendo la misma calidad de sedimentación.
        """)

if __name__ == "__main__":
    main()
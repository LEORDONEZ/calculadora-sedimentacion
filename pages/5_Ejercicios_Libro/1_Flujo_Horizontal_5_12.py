import streamlit as st
import numpy as np
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
    page_title="Análisis Sedimentador con Módulos",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CLASE PRINCIPAL - ESTILO MEJORADO
# ==========================================
class AnalizadorSedimentadorMejorado:
    def __init__(self):
        self.parametros = {}
        self.resultados = {}
        self.verificaciones = {}
        self.procedimientos = []
    
    def calcular(self, parametros):
        self.parametros = parametros
        self.procedimientos = []
        
        # --- DATOS DE ENTRADA ---
        Q_total_m3d = parametros['caudal_total_m3d']
        num_tanques = parametros['numero_tanques']
        L_tanque = parametros['longitud_tanque']
        Ancho_tanque = parametros['ancho_tanque']
        Prof_tanque = parametros['profundidad_tanque']
        L_zona_modulos = parametros['longitud_zona_modulos']
        d_tubo = parametros['diametro_tubo']
        L_tubo_real = parametros['longitud_tubo']
        theta_grados = parametros['angulo_inclinacion']
        viscosidad_cinematica = parametros['viscosidad_cinematica']
        
        theta_rad = np.radians(theta_grados)
        
        self.procedimientos.append("ANÁLISIS SEDIMENTADOR CON MÓDULOS DE ALTA TASA")
        self.procedimientos.append("=" * 70)
        self.procedimientos.append("")
        
        # 1. Carga Superficial Actual (Sin módulos)
        self.procedimientos.append("1. CARGA SUPERFICIAL CONVENCIONAL (Sin módulos)")
        self.procedimientos.append(f"   Área Total = {num_tanques} × {L_tanque} × {Ancho_tanque}")
        
        area_total_actual = num_tanques * L_tanque * Ancho_tanque
        CS_actual = Q_total_m3d / area_total_actual
        
        self.procedimientos.append(f"   Área Total = {area_total_actual:.2f} m²")
        self.procedimientos.append(f"   CS Actual = {Q_total_m3d:,} / {area_total_actual:.2f}")
        self.procedimientos.append(f"   CS Actual = {CS_actual:.2f} m/d")
        self.procedimientos.append("")
        
        # 2. Configuración de Módulos
        self.procedimientos.append("2. CONFIGURACIÓN DE MÓDULOS DE ALTA TASA")
        self.procedimientos.append(f"   Área cubierta = {num_tanques} × {L_zona_modulos} × {Ancho_tanque}")
        
        area_cubierta = num_tanques * L_zona_modulos * Ancho_tanque
        self.procedimientos.append(f"   Área cubierta = {area_cubierta:.2f} m²")
        self.procedimientos.append(f"   Tipo: Tubos cuadrados de {d_tubo*100:.1f} cm")
        self.procedimientos.append(f"   Longitud tubo: {L_tubo_real:.2f} m")
        self.procedimientos.append(f"   Ángulo inclinación: {theta_grados}°")
        self.procedimientos.append("")
        
        # 3. Hidráulica en los Tubos
        self.procedimientos.append("3. HIDRÁULICA EN LOS TUBOS")
        self.procedimientos.append("   Velocidad en tubos: v₀ = Q / (A × senθ)")
        self.procedimientos.append(f"   v₀ = {Q_total_m3d:,} / ({area_cubierta:.2f} × sen{theta_grados}°)")
        
        v0_m_d = Q_total_m3d / (area_cubierta * np.sin(theta_rad))
        v0_m_s = v0_m_d / 86400
        
        self.procedimientos.append(f"   v₀ = {v0_m_d:.2f} m/d = {v0_m_s:.6f} m/s")
        self.procedimientos.append("")
        
        # 4. Número de Reynolds
        self.procedimientos.append("4. NÚMERO DE REYNOLDS")
        self.procedimientos.append("   Nre = (v × d) / ν")
        self.procedimientos.append(f"   Nre = ({v0_m_s:.6f} × {d_tubo}) / {viscosidad_cinematica:.2e}")
        
        Nre = (v0_m_s * d_tubo) / viscosidad_cinematica
        self.procedimientos.append(f"   Nre = {Nre:.2f}")
        self.procedimientos.append("")
        
        # 5. Longitudes Relativas
        self.procedimientos.append("5. LONGITUDES RELATIVAS")
        self.procedimientos.append(f"   L = longitud / diámetro = {L_tubo_real} / {d_tubo}")
        
        L_relativa = L_tubo_real / d_tubo
        self.procedimientos.append(f"   L = {L_relativa:.2f}")
        
        self.procedimientos.append("   L' = 0.013 × Nre (Schulze)")
        self.procedimientos.append(f"   L' = 0.013 × {Nre:.2f}")
        
        L_prima = 0.013 * Nre
        self.procedimientos.append(f"   L' = {L_prima:.2f}")
        
        self.procedimientos.append("   L_efectiva = L - L'")
        self.procedimientos.append(f"   L_efectiva = {L_relativa:.2f} - {L_prima:.2f}")
        
        L_efectiva_rel = L_relativa - L_prima
        self.procedimientos.append(f"   L_efectiva = {L_efectiva_rel:.2f}")
        self.procedimientos.append("")
        
        # 6. Velocidad Crítica de Sedimentación (Modelo de Yao)
        self.procedimientos.append("6. VELOCIDAD CRÍTICA DE SEDIMENTACIÓN (Modelo de Yao)")
        self.procedimientos.append("   Para tubos cuadrados: S = 11/8 = 1.375")
        
        S_factor = 11/8
        
        self.procedimientos.append("   Vs = (S × v₀) / (senθ + L_efectiva × cosθ)")
        self.procedimientos.append(f"   Vs = ({S_factor:.3f} × {v0_m_d:.2f}) / (sen{theta_grados}° + {L_efectiva_rel:.2f} × cos{theta_grados}°)")
        
        numerador = S_factor * v0_m_d
        denominador = np.sin(theta_rad) + (L_efectiva_rel * np.cos(theta_rad))
        Vs_critica = numerador / denominador
        
        self.procedimientos.append(f"   Vs = {Vs_critica:.2f} m/d")
        self.procedimientos.append("")
        
        # 7. Tiempos de Retención
        self.procedimientos.append("7. TIEMPOS DE RETENCIÓN")
        
        # Tiempo en tubos
        t_tubos_min = (L_tubo_real / v0_m_s) / 60
        self.procedimientos.append(f"   Tiempo en tubos = {L_tubo_real} / {v0_m_s:.6f} = {t_tubos_min:.1f} min")
        
        # Tiempo total en tanque
        volumen_total = num_tanques * L_tanque * Ancho_tanque * Prof_tanque
        Q_m3s = Q_total_m3d / 86400
        t_total_min = (volumen_total / Q_m3s) / 60
        self.procedimientos.append(f"   Tiempo total = {volumen_total:.0f} / {Q_m3s:.4f} = {t_total_min:.1f} min")
        
        # Velocidad promedio
        area_transversal = num_tanques * Ancho_tanque * Prof_tanque
        v_promedio_cms = (Q_m3s / area_transversal) * 100
        self.procedimientos.append(f"   Velocidad promedio = {v_promedio_cms:.2f} cm/s")
        self.procedimientos.append("")
        
        # 8. Resumen Comparativo
        self.procedimientos.append("8. RESUMEN COMPARATIVO")
        self.procedimientos.append(f"   • CS convencional: {CS_actual:.1f} m/d")
        self.procedimientos.append(f"   • CS con módulos: {Vs_critica:.1f} m/d")
        mejora_porcentaje = ((CS_actual - Vs_critica) / CS_actual) * 100
        self.procedimientos.append(f"   • Mejora teórica: {mejora_porcentaje:.1f}%")
        self.procedimientos.append("")
        
        # Almacenar resultados
        self.resultados = {
            'cs_convencional': CS_actual,
            'cs_modulos': Vs_critica,
            'mejora_porcentaje': mejora_porcentaje,
            'area_total': area_total_actual,
            'area_cubierta': area_cubierta,
            'v0_m_d': v0_m_d,
            'v0_m_s': v0_m_s,
            'Nre': Nre,
            'L_relativa': L_relativa,
            'L_prima': L_prima,
            'L_efectiva': L_efectiva_rel,
            't_tubos_min': t_tubos_min,
            't_total_min': t_total_min,
            'v_promedio_cms': v_promedio_cms,
            'volumen_total': volumen_total
        }
        
        # Verificaciones
        self.verificaciones = {
            'Nre < 500 (Flujo laminar)': Nre < 500,
            'Tiempo tubos 3-6 min': 3 <= t_tubos_min <= 6,
            'Velocidad < 1.5 cm/s': v_promedio_cms < 1.5,
            'Mejora > 20%': mejora_porcentaje > 20,
            'L_efectiva > 0': L_efectiva_rel > 0
        }
        
        return True
    
    def generar_grafica(self):
        if not self.resultados:
            return None
            
        r = self.resultados
        p = self.parametros
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Gráfica 1: Comparación de Cargas Superficiales
        categorias = ['Convencional', 'Con Módulos']
        valores = [r['cs_convencional'], r['cs_modulos']]
        
        bars = ax1.bar(categorias, valores, color=['lightblue', 'lightgreen'], alpha=0.7)
        ax1.set_title('COMPARACIÓN CARGA SUPERFICIAL', fontweight='bold', fontsize=12)
        ax1.set_ylabel('Carga Superficial (m/d)')
        ax1.grid(True, alpha=0.3)
        
        # Añadir valores en las barras
        for bar, valor in zip(bars, valores):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{valor:.1f}', ha='center', va='bottom', fontweight='bold')
        
        # Gráfica 2: Parámetros Hidráulicos
        parametros_hid = ['v₀ (m/d)', 'Nre', 'L_efectiva', 't_tubos (min)']
        valores_hid = [r['v0_m_d'], r['Nre'], r['L_efectiva'], r['t_tubos_min']]
        
        bars2 = ax2.bar(parametros_hid, valores_hid, color='orange', alpha=0.7)
        ax2.set_title('PARÁMETROS HIDRÁULICOS', fontweight='bold', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        # Añadir valores en las barras
        for bar, valor in zip(bars2, valores_hid):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(valores_hid)*0.05,
                    f'{valor:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=9)
        
        # Gráfica 3: Esquema del Sistema
        ax3.set_title('ESQUEMA DEL SISTEMA', fontweight='bold', fontsize=12)
        
        # Dibujar tanque
        tanque = plt.Rectangle((0, 0), p['longitud_tanque'], p['ancho_tanque'], 
                             fill=True, color='lightblue', alpha=0.5, edgecolor='blue')
        ax3.add_patch(tanque)
        
        # Zona de módulos
        modulos = plt.Rectangle((p['longitud_tanque']-p['longitud_zona_modulos'], 0), 
                              p['longitud_zona_modulos'], p['ancho_tanque'],
                              fill=True, color='red', alpha=0.3, edgecolor='red')
        ax3.add_patch(modulos)
        
        ax3.text(p['longitud_tanque']/2, p['ancho_tanque']/2, 'Zona Convencional', 
                ha='center', va='center', fontweight='bold')
        ax3.text(p['longitud_tanque']-p['longitud_zona_modulos']/2, p['ancho_tanque']/2, 
                'Módulos Alta Tasa', ha='center', va='center', fontweight='bold', color='red')
        
        ax3.set_xlim(0, p['longitud_tanque'] + 5)
        ax3.set_ylim(0, p['ancho_tanque'] + 5)
        ax3.set_aspect('equal')
        ax3.set_xlabel('Longitud (m)')
        ax3.set_ylabel('Ancho (m)')
        
        # Gráfica 4: Verificaciones
        ax4.set_title('VERIFICACIONES DE DISEÑO', fontweight='bold', fontsize=12)
        
        verificaciones = list(self.verificaciones.keys())
        estados = list(self.verificaciones.values())
        colores = ['green' if estado else 'red' for estado in estados]
        
        bars4 = ax4.barh(verificaciones, [1]*len(verificaciones), color=colores, alpha=0.7)
        ax4.set_xlim(0, 1)
        ax4.set_xticks([])
        
        # Añadir texto de verificación
        for i, (bar, estado) in enumerate(zip(bars4, estados)):
            ax4.text(0.5, bar.get_y() + bar.get_height()/2, 
                    '✓ CUMPLE' if estado else '✗ NO CUMPLE',
                    ha='center', va='center', fontweight='bold', fontsize=9)
        
        plt.tight_layout()
        return fig
    
    def generar_reporte_pdf(self):
        pdf = FPDF()
        pdf.add_page()
        
        # Encabezado
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, 'ANÁLISIS SEDIMENTADOR CON MÓDULOS ALTA TASA', 0, 1, 'C')
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, f'Fecha: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
        pdf.ln(5)
        
        # Datos del problema
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(0, 10, 'DATOS DE ENTRADA', 1, 1, 'L', 1)
        pdf.set_font("Arial", '', 10)
        p = self.parametros
        pdf.cell(0, 6, f'Caudal total: {p["caudal_total_m3d"]:,} m³/d', 0, 1)
        pdf.cell(0, 6, f'Tanques: {p["numero_tanques"]} de {p["longitud_tanque"]}×{p["ancho_tanque"]}×{p["profundidad_tanque"]} m', 0, 1)
        pdf.cell(0, 6, f'Zona módulos: {p["longitud_zona_modulos"]} m', 0, 1)
        pdf.cell(0, 6, f'Tubos: {p["diametro_tubo"]*100:.1f} cm × {p["longitud_tubo"]} m, {p["angulo_inclinacion"]}°', 0, 1)
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
        pdf.cell(0, 6, f'CS convencional: {r["cs_convencional"]:.2f} m/d', 0, 1)
        pdf.cell(0, 6, f'CS con módulos: {r["cs_modulos"]:.2f} m/d', 0, 1)
        pdf.cell(0, 6, f'Mejora: {r["mejora_porcentaje"]:.1f}%', 0, 1)
        pdf.cell(0, 6, f'Número Reynolds: {r["Nre"]:.2f}', 0, 1)
        pdf.cell(0, 6, f'Tiempo en tubos: {r["t_tubos_min"]:.1f} min', 0, 1)
        pdf.cell(0, 6, f'Velocidad promedio: {r["v_promedio_cms"]:.2f} cm/s', 0, 1)
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
    st.title("📐 Análisis de Sedimentador con Módulos de Alta Tasa")
    st.markdown("### Adaptación del Ejemplo 5.12 - Mejorado")
    
    if 'analizador_mejorado' not in st.session_state:
        st.session_state.analizador_mejorado = AnalizadorSedimentadorMejorado()
    
    # --- SIDEBAR ---
    st.sidebar.header("📋 Configuración del Sistema")
    
    with st.sidebar.form("form_parametros"):
        st.subheader("Datos del Sedimentador")
        
        caudal_total_m3d = st.number_input(
            "Caudal total (m³/d)",
            min_value=10000.0,
            max_value=500000.0,
            value=114000.0,
            step=1000.0
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            numero_tanques = st.number_input(
                "Número de tanques",
                min_value=1,
                max_value=10,
                value=2,
                step=1
            )
            
            longitud_tanque = st.number_input(
                "Longitud tanque (m)",
                min_value=10.0,
                max_value=100.0,
                value=24.4,
                step=1.0
            )
        
        with col2:
            ancho_tanque = st.number_input(
                "Ancho tanque (m)",
                min_value=5.0,
                max_value=50.0,
                value=18.3,
                step=1.0
            )
            
            profundidad_tanque = st.number_input(
                "Profundidad tanque (m)",
                min_value=2.0,
                max_value=6.0,
                value=3.7,
                step=0.1
            )
        
        st.subheader("Configuración de Módulos")
        
        col3, col4 = st.columns(2)
        
        with col3:
            longitud_zona_modulos = st.number_input(
                "Longitud zona módulos (m)",
                min_value=5.0,
                max_value=50.0,
                value=12.2,
                step=1.0
            )
            
            diametro_tubo = st.number_input(
                "Diámetro tubo (m)",
                min_value=0.01,
                max_value=0.2,
                value=0.051,
                step=0.001,
                format="%.3f"
            )
        
        with col4:
            longitud_tubo = st.number_input(
                "Longitud tubo (m)",
                min_value=0.1,
                max_value=2.0,
                value=0.61,
                step=0.01
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
                'caudal_total_m3d': caudal_total_m3d,
                'numero_tanques': numero_tanques,
                'longitud_tanque': longitud_tanque,
                'ancho_tanque': ancho_tanque,
                'profundidad_tanque': profundidad_tanque,
                'longitud_zona_modulos': longitud_zona_modulos,
                'diametro_tubo': diametro_tubo,
                'longitud_tubo': longitud_tubo,
                'angulo_inclinacion': angulo_inclinacion,
                'viscosidad_cinematica': viscosidad_cinematica
            }
            st.session_state.analizador_mejorado.calcular(parametros)
            st.rerun()
    
    # --- EJEMPLOS RÁPIDOS ---
    with st.sidebar.expander("🎯 Ejemplos Rápidos"):
        if st.button("Ejemplo 5.12 Original"):
            st.session_state.analizador_mejorado.calcular({
                'caudal_total_m3d': 114000.0,
                'numero_tanques': 2,
                'longitud_tanque': 24.4,
                'ancho_tanque': 18.3,
                'profundidad_tanque': 3.7,
                'longitud_zona_modulos': 12.2,
                'diametro_tubo': 0.051,
                'longitud_tubo': 0.61,
                'angulo_inclinacion': 60,
                'viscosidad_cinematica': 1.139e-6
            })
            st.rerun()
    
    # --- RESULTADOS PRINCIPALES ---
    analizador = st.session_state.analizador_mejorado
    
    if analizador.resultados:
        st.success("✅ Análisis completado exitosamente")
        
        # Mostrar configuración actual
        st.info(f"""
        **Configuración analizada:** 
        - {analizador.parametros['numero_tanques']} tanques de {analizador.parametros['longitud_tanque']}×{analizador.parametros['ancho_tanque']}×{analizador.parametros['profundidad_tanque']} m
        - Caudal: {analizador.parametros['caudal_total_m3d']:,} m³/d
        - Módulos en últimos {analizador.parametros['longitud_zona_modulos']} m
        """)
        
        # Mostrar resultados en pestañas
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Resultados", "📋 Procedimiento", "📈 Gráficas", "📥 Reporte"])
        
        with tab1:
            st.subheader("Resultados del Análisis")
            
            # Métricas principales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("CS Convencional", 
                         f"{analizador.resultados['cs_convencional']:.1f} m/d")
            
            with col2:
                st.metric("CS con Módulos", 
                         f"{analizador.resultados['cs_modulos']:.1f} m/d")
            
            with col3:
                st.metric("Mejora", 
                         f"{analizador.resultados['mejora_porcentaje']:.1f}%")
            
            with col4:
                st.metric("Número Reynolds", 
                         f"{analizador.resultados['Nre']:.0f}")
            
            # Tabla de resultados detallados
            st.subheader("📋 Parámetros Calculados")
            datos_resumen = {
                'Parámetro': ['Área total', 'Área con módulos', 'Velocidad en tubos (v₀)',
                             'Longitud relativa (L/d)', 'Longitud transición (L\')', 
                             'Longitud efectiva (Le)', 'Tiempo en tubos', 'Velocidad promedio'],
                'Valor': [f"{analizador.resultados['area_total']:.0f} m²",
                         f"{analizador.resultados['area_cubierta']:.0f} m²",
                         f"{analizador.resultados['v0_m_d']:.0f} m/d",
                         f"{analizador.resultados['L_relativa']:.2f}",
                         f"{analizador.resultados['L_prima']:.2f}",
                         f"{analizador.resultados['L_efectiva']:.2f}",
                         f"{analizador.resultados['t_tubos_min']:.1f} min",
                         f"{analizador.resultados['v_promedio_cms']:.2f} cm/s"],
                'Referencia': ['-', '-', '295 m/d (texto)', '12', '1.99 (texto)', 
                              '10.01 (texto)', '3-6 min', '< 1.5 cm/s']
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
            st.subheader("📝 Procedimiento Detallado")
            st.code("\n".join(analizador.procedimientos), language="text")
        
        with tab3:
            st.subheader("📈 Análisis Gráfico")
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
                            file_name=f"analisis_modulos_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                            mime="application/pdf"
                        )
                    
                    # Limpiar archivo temporal
                    os.unlink(pdf_file)
    
    else:
        # Pantalla inicial
        st.info("""
        ## 🧭 Análisis de Sedimentadores con Módulos de Alta Tasa
        
        **Características del análisis:**
        - Cálculo preciso según modelo de Yao para tubos cuadrados
        - Verificación de flujo laminar (Número de Reynolds)
        - Cálculo de longitud efectiva considerando transición
        - Comparación carga superficial con/sin módulos
        - Verificación de tiempos de retención
        
        **🎯 Ejemplo 5.12 Original:**
        - 2 tanques de 24.4×18.3×3.7 m
        - Caudal: 114,000 m³/d  
        - Módulos en últimos 12.2 m
        - Tubos cuadrados de 5.1 cm × 61 cm a 60°
        """)

if __name__ == "__main__":
    main()
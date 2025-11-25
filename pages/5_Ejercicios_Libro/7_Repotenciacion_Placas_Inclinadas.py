import streamlit as st
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import datetime
from fpdf import FPDF
import tempfile
import os

# ==========================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="Repotenciación con Placas Inclinadas",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CLASE PRINCIPAL DE LÓGICA Y REPORTE
# ==========================================
class RepotenciacionPlacas:
    def __init__(self):
        self.parametros = {}
        self.resultados = {}
        self.calculos_detallados = []
    
    def calcular(self, parametros):
        self.parametros = parametros
        self.calculos_detallados = []
        
        # --- DATOS DE ENTRADA ---
        Q_total_ls = parametros['caudal_total_ls']
        N_tanques = parametros['numero_tanques']
        L_tanque = parametros['largo_tanque']
        B_tanque = parametros['ancho_tanque']
        factor_ampliacion = parametros['factor_ampliacion']
        L_placa = parametros['largo_placa']
        theta_deg = parametros['angulo_inclinacion']
        L_rel = parametros['longitud_relativa']
        viscosidad = parametros['viscosidad']
        
        self.calculos_detallados.append("=" * 60)
        self.calculos_detallados.append("REPOTENCIACIÓN CON PLACAS INCLINADAS - MEMORIA DE CÁLCULO")
        self.calculos_detallados.append("=" * 60)
        self.calculos_detallados.append("")
        
        # ==========================================
        # 1. DIAGNÓSTICO ACTUAL
        # ==========================================
        self.calculos_detallados.append("--- 1. DIAGNÓSTICO DE LA PLANTA ACTUAL ---")
        
        # Caudal por tanque
        Q_tanque_ls = Q_total_ls / N_tanques
        Q_tanque_m3d = (Q_tanque_ls * 86400) / 1000
        
        self.calculos_detallados.append("1.1 CAUDAL ACTUAL POR TANQUE")
        self.calculos_detallados.append(f"   Fórmula: Q = Q_total / N")
        self.calculos_detallados.append(f"   Sustitución: {Q_total_ls} / {N_tanques}")
        self.calculos_detallados.append(f"   Resultado: {Q_tanque_ls:.1f} L/s ({Q_tanque_m3d:.1f} m³/d)")
        self.calculos_detallados.append("")
        
        # Carga Superficial Actual
        Area_tanque = L_tanque * B_tanque
        CS_actual = Q_tanque_m3d / Area_tanque
        
        self.calculos_detallados.append("1.2 CARGA SUPERFICIAL EXISTENTE (CS)")
        self.calculos_detallados.append(f"   Fórmula: CS = Q_tanque / (L × B)")
        self.calculos_detallados.append(f"   Sustitución: {Q_tanque_m3d:.1f} / ({L_tanque} × {B_tanque})")
        self.calculos_detallados.append(f"   Resultado: {CS_actual:.2f} m³/m²·d (o m/d)")
        self.calculos_detallados.append("")
        
        # ==========================================
        # 2. NUEVAS CONDICIONES DE DISEÑO
        # ==========================================
        self.calculos_detallados.append("--- 2. CONDICIONES DE AMPLIACIÓN ---")
        
        # Nuevo Caudal
        Q_nuevo_ls = Q_tanque_ls * factor_ampliacion
        Q_nuevo_m3d = (Q_nuevo_ls * 86400) / 1000
        
        self.calculos_detallados.append("2.1 CAUDAL OBJETIVO (NUEVO)")
        self.calculos_detallados.append(f"   Fórmula: Q_nuevo = Q_actual × Factor")
        self.calculos_detallados.append(f"   Sustitución: {Q_tanque_ls:.1f} × {factor_ampliacion}")
        self.calculos_detallados.append(f"   Resultado: {Q_nuevo_ls:.1f} L/s ({Q_nuevo_m3d:.1f} m³/d)")
        self.calculos_detallados.append("")
        
        # Velocidad de Flujo entre Placas (v0)
        theta_rad = math.radians(theta_deg)
        sen_t = math.sin(theta_rad)
        cos_t = math.cos(theta_rad)
        
        term_parentesis = sen_t + (L_rel * cos_t)
        v0_md = CS_actual * term_parentesis
        v0_cms = v0_md / (86400 / 100)  # Convertir m/d a cm/s
        
        self.calculos_detallados.append("2.2 VELOCIDAD DE FLUJO EN MÓDULOS (v0)")
        self.calculos_detallados.append(f"   Fórmula: v0 = CS × (senθ + L_rel × cosθ)")
        self.calculos_detallados.append(f"   Sustitución: {CS_actual:.1f} × (sen{theta_deg} + {L_rel} × cos{theta_deg})")
        self.calculos_detallados.append(f"   Resultado: {v0_md:.2f} m/d ({v0_cms:.3f} cm/s)")
        self.calculos_detallados.append("")
        
        # ==========================================
        # 3. DIMENSIONAMIENTO DE MÓDULOS
        # ==========================================
        self.calculos_detallados.append("--- 3. DIMENSIONAMIENTO DE MÓDULOS ---")
        
        # Área de sedimentación laminar requerida
        A_lam = Q_nuevo_m3d / (v0_md * sen_t)
        
        self.calculos_detallados.append("3.1 ÁREA DE SEDIMENTACIÓN ACELERADA")
        self.calculos_detallados.append(f"   Fórmula: A_lam = Q_nuevo / (v0 × senθ)")
        self.calculos_detallados.append(f"   Sustitución: {Q_nuevo_m3d:.1f} / ({v0_md:.2f} × {sen_t:.3f})")
        self.calculos_detallados.append(f"   Resultado: {A_lam:.2f} m²")
        self.calculos_detallados.append("")
        
        # Longitud cubierta en el tanque
        L_cubierta = A_lam / B_tanque
        
        self.calculos_detallados.append("3.2 LONGITUD DE TANQUE A CUBRIR CON PLACAS")
        self.calculos_detallados.append(f"   Fórmula: L_cub = A_lam / Ancho_Tanque")
        self.calculos_detallados.append(f"   Sustitución: {A_lam:.2f} / {B_tanque}")
        self.calculos_detallados.append(f"   Resultado: {L_cubierta:.2f} m")
        self.calculos_detallados.append("")
        
        # ==========================================
        # 4. DETALLES CONSTRUCTIVOS
        # ==========================================
        self.calculos_detallados.append("--- 4. DETALLES CONSTRUCTIVOS ---")
        
        # Separación entre placas (e)
        e_m = L_placa / L_rel
        e_cm = e_m * 100
        
        self.calculos_detallados.append("4.1 SEPARACIÓN ENTRE PLACAS (e)")
        self.calculos_detallados.append(f"   Fórmula: e = Largo_Placa / L_rel")
        self.calculos_detallados.append(f"   Sustitución: {L_placa} / {L_rel}")
        self.calculos_detallados.append(f"   Resultado: {e_m:.3f} m ({e_cm:.1f} cm)")
        self.calculos_detallados.append("")
        
        # Número de Reynolds
        Re = (v0_cms * e_cm) / viscosidad
        estado_flujo = "LAMINAR" if Re < 500 else "TURBULENTO"
        
        self.calculos_detallados.append("4.2 VERIFICACIÓN REYNOLDS (Re)")
        self.calculos_detallados.append(f"   Fórmula: Re = (v0_cms × e_cm) / Viscosidad")
        self.calculos_detallados.append(f"   Sustitución: ({v0_cms:.3f} × {e_cm:.1f}) / {viscosidad}")
        self.calculos_detallados.append(f"   Resultado: {Re:.0f} → {estado_flujo}")
        self.calculos_detallados.append("")
        
        # Tiempo de Retención
        t_dia = L_placa / v0_md
        t_min = t_dia * 1440
        
        self.calculos_detallados.append("4.3 TIEMPO DE RETENCIÓN EN PLACAS")
        self.calculos_detallados.append(f"   Fórmula: t = L_placa / v0")
        self.calculos_detallados.append(f"   Sustitución: {L_placa} / {v0_md:.2f}")
        self.calculos_detallados.append(f"   Resultado: {t_min:.2f} minutos")
        self.calculos_detallados.append("")
        
        # ==========================================
        # 5. RESUMEN FINAL
        # ==========================================
        self.calculos_detallados.append("--- 5. CONCLUSIÓN DE DISEÑO ---")
        self.calculos_detallados.append(f"Para aumentar la capacidad {factor_ampliacion} veces:")
        self.calculos_detallados.append(f"• Se instalarán módulos en los últimos {L_cubierta:.2f} m del tanque")
        self.calculos_detallados.append(f"• Placas: {L_placa} m de largo, {theta_deg}° de inclinación")
        self.calculos_detallados.append(f"• Separación: {e_cm:.1f} cm entre placas")
        self.calculos_detallados.append(f"• Régimen: {estado_flujo} (Re = {Re:.0f})")
        
        # Almacenar resultados
        self.resultados = {
            'caudal_actual_ls': Q_tanque_ls,
            'caudal_nuevo_ls': Q_nuevo_ls,
            'carga_superficial_actual': CS_actual,
            'velocidad_flujo': v0_cms,
            'area_placas': A_lam,
            'longitud_cubierta': L_cubierta,
            'separacion_placas_cm': e_cm,
            'numero_reynolds': Re,
            'tiempo_retencion': t_min,
            'estado_flujo': estado_flujo
        }
        
        # Verificaciones
        self.verificaciones = {
            'Flujo laminar (Re < 500)': Re < 500,
            'Tiempo retención adecuado (5-15 min)': 5 <= t_min <= 15,
            f'Capacidad aumentada {factor_ampliacion} veces': True,
            'Longitud cubierta < Largo tanque': L_cubierta <= L_tanque
        }
        
        return True
    
    def generar_grafica(self):
        if not self.resultados:
            return None
            
        L_tanque = self.parametros['largo_tanque']
        B_tanque = self.parametros['ancho_tanque']
        L_cubierta = self.resultados['longitud_cubierta']
        theta_deg = self.parametros['angulo_inclinacion']
        L_placa = self.parametros['largo_placa']
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # ================= VISTA PLANTA =================
        ax1.set_title('VISTA EN PLANTA - DISTRIBUCIÓN DE MÓDULOS', 
                     fontsize=14, fontweight='bold', pad=20)
        
        # Zona sin placas
        rect_sin_placas = patches.Rectangle((0, 0), L_tanque - L_cubierta, B_tanque,
                                          facecolor='#FFE0B2', edgecolor='#FF9800', linewidth=2,
                                          label='Zona Convencional')
        ax1.add_patch(rect_sin_placas)
        
        # Zona con placas
        rect_con_placas = patches.Rectangle((L_tanque - L_cubierta, 0), L_cubierta, B_tanque,
                                          facecolor='#B3E5FC', edgecolor='#0288D1', linewidth=2,
                                          label='Zona con Placas')
        ax1.add_patch(rect_con_placas)
        
        # Cotas
        ax1.annotate('', xy=(0, -1), xytext=(L_tanque, -1),
                    arrowprops=dict(arrowstyle='<->', color='black', lw=2))
        ax1.text(L_tanque/2, -2, f'L Total = {L_tanque} m', ha='center', fontweight='bold')
        
        ax1.annotate('', xy=(L_tanque - L_cubierta, -3), xytext=(L_tanque, -3),
                    arrowprops=dict(arrowstyle='<->', color='blue', lw=2))
        ax1.text(L_tanque - L_cubierta/2, -4, f'L Placas = {L_cubierta:.1f} m', 
                ha='center', fontweight='bold', color='blue')
        
        ax1.set_xlim(-2, L_tanque + 2)
        ax1.set_ylim(-5, B_tanque + 2)
        ax1.set_aspect('equal')
        ax1.legend(loc='upper right')
        ax1.set_xlabel("Longitud (m)", fontweight='bold')
        ax1.set_ylabel("Ancho (m)", fontweight='bold')
        ax1.grid(True, linestyle='--', alpha=0.3)
        
        # ================= VISTA DETALLE PLACAS =================
        ax2.set_title('VISTA DETALLE - CONFIGURACIÓN DE PLACAS', 
                     fontsize=14, fontweight='bold', pad=20)
        
        # Representación esquemática de placas
        theta_rad = math.radians(theta_deg)
        dx = L_placa * math.cos(theta_rad)
        dy = L_placa * math.sin(theta_rad)
        
        # Dibujar varias placas
        for i in range(5):
            x_start = i * dx * 1.2
            y_start = 1 + i * 0.5
            ax2.plot([x_start, x_start + dx], [y_start, y_start + dy], 
                    'b-', linewidth=2, alpha=0.7)
        
        # Información técnica
        info_text = (
            f"ESPECIFICACIONES TÉCNICAS:\n"
            f"• Largo placa: {L_placa} m\n"
            f"• Ángulo: {theta_deg}°\n"
            f"• Separación: {self.resultados['separacion_placas_cm']:.1f} cm\n"
            f"• Velocidad: {self.resultados['velocidad_flujo']:.3f} cm/s\n"
            f"• Tiempo: {self.resultados['tiempo_retencion']:.1f} min"
        )
        
        ax2.text(0.5, 4, info_text, fontsize=10, 
                bbox=dict(facecolor='white', alpha=0.9, boxstyle='round'),
                fontweight='bold')
        
        ax2.set_xlim(0, 6)
        ax2.set_ylim(0, 5)
        ax2.set_aspect('equal')
        ax2.set_xlabel("Distancia (m)", fontweight='bold')
        ax2.set_ylabel("Altura (m)", fontweight='bold')
        ax2.grid(True, linestyle='--', alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def generar_reporte_pdf(self):
        pdf = FPDF()
        pdf.add_page()
        
        # Encabezado
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, 'REPOTENCIACION CON PLACAS INCLINADAS', 0, 1, 'C')
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, f'Fecha: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
        pdf.ln(5)
        
        # Datos de entrada
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(0, 10, 'DATOS DE ENTRADA', 1, 1, 'L', 1)
        pdf.set_font("Arial", '', 10)
        p = self.parametros
        pdf.cell(0, 6, f'Caudal total actual: {p["caudal_total_ls"]} L/s', 0, 1)
        pdf.cell(0, 6, f'Numero de tanques: {p["numero_tanques"]}', 0, 1)
        pdf.cell(0, 6, f'Dimensiones tanque: {p["largo_tanque"]}m x {p["ancho_tanque"]}m', 0, 1)
        pdf.cell(0, 6, f'Factor de ampliacion: {p["factor_ampliacion"]} veces', 0, 1)
        pdf.cell(0, 6, f'Placas: {p["largo_placa"]}m, {p["angulo_inclinacion"]} grados', 0, 1)
        pdf.cell(0, 6, f'Longitud relativa: {p["longitud_relativa"]}', 0, 1)
        pdf.ln(5)
        
        # Cálculos detallados - SOLO PRIMERAS LÍNEAS
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(0, 10, 'MEMORIA DE CALCULO (RESUMEN)', 1, 1, 'L', 1)
        pdf.set_font("Courier", '', 8)
        
        # Tomar solo las líneas más importantes (primeras 20 líneas)
        lineas_importantes = []
        for linea in self.calculos_detallados:
            # Limpiar caracteres problemáticos
            linea_limpia = (linea.replace('×', 'x')
                            .replace('θ', 'theta')
                            .replace('°', 'grados')
                            .replace('³', '3')
                            .replace('²', '2')
                            .replace('–', '-'))
            
            # Solo incluir líneas clave (no todas las líneas de separación)
            if any(keyword in linea_limpia for keyword in ['---', 'RESULTADO', 'FORMULA', 'SUSTITUCION']):
                if len(linea_limpia) > 100:
                    # Dividir líneas muy largas
                    partes = [linea_limpia[i:i+80] for i in range(0, len(linea_limpia), 80)]
                    lineas_importantes.extend(partes)
                else:
                    lineas_importantes.append(linea_limpia)
            
            # Limitar a 30 líneas máximo
            if len(lineas_importantes) >= 30:
                lineas_importantes.append("... [Calculos completos en la aplicacion]")
                break
        
        # Escribir líneas importantes con ancho específico
        for linea in lineas_importantes:
            try:
                pdf.multi_cell(190, 4, linea)  # Ancho específico de 190mm
            except:
                # Si falla, escribir línea truncada
                pdf.multi_cell(190, 4, linea[:80] + "...")
        
        # Resultados
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(0, 10, 'RESULTADOS FINALES', 1, 1, 'L', 1)
        pdf.set_font("Arial", '', 10)
        
        r = self.resultados
        pdf.cell(0, 6, f'Nuevo caudal por tanque: {r["caudal_nuevo_ls"]:.1f} L/s', 0, 1)
        pdf.cell(0, 6, f'Longitud a cubrir con placas: {r["longitud_cubierta"]:.2f} m', 0, 1)
        pdf.cell(0, 6, f'Separacion entre placas: {r["separacion_placas_cm"]:.1f} cm', 0, 1)
        pdf.cell(0, 6, f'Numero de Reynolds: {r["numero_reynolds"]:.0f}', 0, 1)
        pdf.cell(0, 6, f'Tiempo de retencion: {r["tiempo_retencion"]:.1f} min', 0, 1)
        pdf.cell(0, 6, f'Estado del flujo: {r["estado_flujo"]}', 0, 1)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf.output(tmp_file.name)
            return tmp_file.name

# ==========================================
# INTERFAZ PRINCIPAL
# ==========================================
def main():
    st.title("🔄 Repotenciación con Placas Inclinadas")
    st.markdown("### Ampliación de Capacidad en Sedimentadores Existentes")
    
    if 'repotenciacion' not in st.session_state:
        st.session_state.repotenciacion = RepotenciacionPlacas()
    
    # --- SIDEBAR ---
    st.sidebar.header("📋 Parámetros de Repotenciación")
    
    with st.sidebar.expander("💡 Información del Sistema", expanded=False):
        st.info("""
        **Objetivo:** Aumentar la capacidad de sedimentadores existentes 
        mediante la instalación de módulos de placas inclinadas.
        
        **Aplicación:** Plantas que requieren ampliar su capacidad 
        sin construir nuevos tanques.
        
        **Ejemplo típico:** Aumentar 3 veces la capacidad manteniendo 
        la misma calidad de efluente.
        """)
    
    with st.sidebar.form("form_repotenciacion"):
        st.subheader("Datos de la Planta Existente")
        
        caudal_total_ls = st.number_input(
            "Caudal total actual (L/s)",
            min_value=10.0,
            max_value=1000.0,
            value=150.0,
            step=10.0
        )
        
        numero_tanques = st.number_input(
            "Número de sedimentadores",
            min_value=1,
            max_value=10,
            value=2,
            step=1
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            largo_tanque = st.number_input(
                "Largo del tanque (m)",
                min_value=5.0,
                max_value=50.0,
                value=18.0,
                step=1.0
            )
        
        with col2:
            ancho_tanque = st.number_input(
                "Ancho del tanque (m)",
                min_value=2.0,
                max_value=20.0,
                value=7.5,
                step=0.5
            )
        
        st.subheader("Objetivo de Ampliación")
        
        factor_ampliacion = st.slider(
            "Factor de ampliación (veces)",
            min_value=1.5,
            max_value=5.0,
            value=3.0,
            step=0.5
        )
        
        st.subheader("Configuración de Placas")
        
        col3, col4 = st.columns(2)
        
        with col3:
            largo_placa = st.number_input(
                "Largo de placa (m)",
                min_value=0.5,
                max_value=3.0,
                value=1.2,
                step=0.1
            )
            
            angulo_inclinacion = st.slider(
                "Ángulo de inclinación (°)",
                min_value=45,
                max_value=75,
                value=60
            )
        
        with col4:
            longitud_relativa = st.number_input(
                "Longitud relativa (L/e)",
                min_value=10.0,
                max_value=40.0,
                value=20.0,
                step=1.0
            )
            
            viscosidad = st.number_input(
                "Viscosidad cinemática (cm²/s)",
                min_value=0.008,
                max_value=0.020,
                value=0.01146,
                step=0.0001,
                format="%.5f",
                help="Agua a 15-20°C: 0.01146 cm²/s"
            )
        
        # Botón de cálculo
        if st.form_submit_button("🚀 Calcular Repotenciación"):
            parametros = {
                'caudal_total_ls': caudal_total_ls,
                'numero_tanques': numero_tanques,
                'largo_tanque': largo_tanque,
                'ancho_tanque': ancho_tanque,
                'factor_ampliacion': factor_ampliacion,
                'largo_placa': largo_placa,
                'angulo_inclinacion': angulo_inclinacion,
                'longitud_relativa': longitud_relativa,
                'viscosidad': viscosidad
            }
            st.session_state.repotenciacion.calcular(parametros)
            st.rerun()
    
    # --- EJEMPLO ORIGINAL ---
    with st.sidebar.expander("🎯 Ejemplo del Libro"):
        if st.button("Cargar Valores del Ejercicio 2"):
            st.session_state.repotenciacion.calcular({
                'caudal_total_ls': 150.0,
                'numero_tanques': 2,
                'largo_tanque': 18.0,
                'ancho_tanque': 7.5,
                'factor_ampliacion': 3.0,
                'largo_placa': 1.2,
                'angulo_inclinacion': 60,
                'longitud_relativa': 20.0,
                'viscosidad': 0.01146
            })
            st.rerun()
    
    # --- RESULTADOS PRINCIPALES ---
    repot = st.session_state.repotenciacion
    
    if repot.resultados:
        st.success("✅ Análisis de repotenciación completado")
        
        # Mostrar configuración
        st.info(f"""
        **Configuración analizada:**
        - Planta actual: {repot.parametros['caudal_total_ls']} L/s, {repot.parametros['numero_tanques']} tanques
        - Objetivo: Aumentar {repot.parametros['factor_ampliacion']} veces la capacidad
        - Tanques: {repot.parametros['largo_tanque']}m × {repot.parametros['ancho_tanque']}m
        """)
        
        # Mostrar en pestañas
        tab1, tab2, tab3 = st.tabs(["📊 Resultados", "🧮 Cálculos", "📥 Reporte"])
        
        with tab1:
            st.subheader("Resultados de la Repotenciación")
            
            # Métricas principales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Nuevo Caudal/Tanque", 
                    f"{repot.resultados['caudal_nuevo_ls']:.1f} L/s",
                    f"+{repot.parametros['factor_ampliacion']} veces"
                )
            
            with col2:
                st.metric(
                    "Longitud con Placas", 
                    f"{repot.resultados['longitud_cubierta']:.1f} m"
                )
            
            with col3:
                st.metric(
                    "Separación Placas", 
                    f"{repot.resultados['separacion_placas_cm']:.1f} cm"
                )
            
            with col4:
                estado_color = "🟢" if repot.resultados['numero_reynolds'] < 500 else "🔴"
                st.metric(
                    "Régimen Flujo", 
                    f"{estado_color} {repot.resultados['estado_flujo']}"
                )
            
            # Gráfico
            st.pyplot(repot.generar_grafica())
            
            # Verificaciones
            st.subheader("✅ Verificaciones de Diseño")
            cols = st.columns(2)
            idx = 0
            for criterio, cumple in repot.verificaciones.items():
                if cumple:
                    cols[idx % 2].success(f"✓ {criterio}")
                else:
                    cols[idx % 2].error(f"✗ {criterio}")
                idx += 1
            
            # Especificaciones técnicas
            st.subheader("📋 Especificaciones Técnicas")
            
            datos_especificaciones = {
                'Parámetro': [
                    'Caudal actual por tanque',
                    'Caudal nuevo por tanque', 
                    'Carga superficial actual',
                    'Velocidad en placas',
                    'Área de módulos requerida',
                    'Tiempo de retención',
                    'Número de Reynolds'
                ],
                'Valor': [
                    f"{repot.resultados['caudal_actual_ls']:.1f} L/s",
                    f"{repot.resultados['caudal_nuevo_ls']:.1f} L/s",
                    f"{repot.resultados['carga_superficial_actual']:.2f} m/d",
                    f"{repot.resultados['velocidad_flujo']:.3f} cm/s",
                    f"{repot.resultados['area_placas']:.1f} m²",
                    f"{repot.resultados['tiempo_retencion']:.1f} min",
                    f"{repot.resultados['numero_reynolds']:.0f}"
                ],
                'Observación': [
                    'Caudal actual por unidad',
                    'Caudal después de ampliación',
                    'Eficiencia actual del sistema',
                    'Velocidad entre placas',
                    'Área para módulos de placas',
                    'Tiempo en zona de placas',
                    'Indicador régimen de flujo'
                ]
            }
            
            df_especificaciones = pd.DataFrame(datos_especificaciones)
            st.dataframe(df_especificaciones, use_container_width=True)
        
        with tab2:
            st.subheader("🧮 Cálculos Detallados Paso a Paso")
            st.code("\n".join(repot.calculos_detallados), language="text")
        
        with tab3:
            st.subheader("📥 Generar Reporte de Repotenciación")
            
            if st.button("🖨️ Generar Reporte Completo en PDF"):
                with st.spinner("Generando reporte PDF..."):
                    try:
                        pdf_file = repot.generar_reporte_pdf()
                        with open(pdf_file, "rb") as f:
                            st.download_button(
                                label="📥 Descargar Reporte PDF",
                                data=f,
                                file_name=f"repotenciacion_placas_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                mime="application/pdf"
                            )
                        os.unlink(pdf_file)
                    except Exception as e:
                        st.error(f"Error al generar PDF: {str(e)}")
    
    else:
        # Pantalla inicial
        st.info("""
        ## 🔄 Repotenciación con Placas Inclinadas
        
        **Objetivo:** Aumentar la capacidad de sedimentadores existentes mediante 
        la instalación de módulos de placas inclinadas sin necesidad de construir 
        nuevas estructuras.
        
        **Problema típico del libro:**
        - Planta trata 150 L/s con 2 sedimentadores
        - Dimensiones: 18m × 7.5m cada tanque
        - Se desea triplicar la capacidad (3 veces)
        - Solución: Instalar placas de 1.2m a 60°
        
        **Metodología de cálculo:**
        1. Diagnóstico de condiciones actuales
        2. Determinación del nuevo caudal objetivo
        3. Cálculo de velocidad en módulos de placas
        4. Dimensionamiento del área requerida
        5. Verificación de condiciones hidráulicas
        
        **Ventajas de la repotenciación:**
        - Menor costo que construcción nueva
        - Tiempos de implementación reducidos
        - Mantenimiento de misma calidad de efluente
        - Flexibilidad operativa
        
        **🎯 Resultado esperado:** Diseño completo para ampliar la capacidad 
        manteniendo los tanques existentes.
        """)

if __name__ == "__main__":
    main()
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
    page_title="Diseño de Sedimentador Circular",
    page_icon="⭕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CLASE PRINCIPAL DE CÁLCULO Y REPORTE
# ==========================================
class DiseñoSedimentadorCircular:
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
        caudal_total = parametros['caudal_total_m3d']
        carga_superficial = parametros['carga_superficial']
        tiempo_retencion = parametros['tiempo_retencion_horas']
        
        self.procedimientos.append("MEMORIA DE CÁLCULO - DISEÑO SEDIMENTADOR CIRCULAR")
        self.procedimientos.append("=" * 70)
        self.procedimientos.append("")
        
        # 1. Datos del problema
        self.procedimientos.append("1. DATOS DEL PROBLEMA")
        self.procedimientos.append(f"   Caudal de diseño: {caudal_total:,} m³/d")
        self.procedimientos.append(f"   Carga superficial: {carga_superficial} m/d")
        self.procedimientos.append(f"   Tiempo de retención: {tiempo_retencion} horas")
        self.procedimientos.append("")
        
        # 2. Cálculo del Área Superficial
        self.procedimientos.append("2. CÁLCULO DEL ÁREA SUPERFICIAL")
        self.procedimientos.append("   Fórmula: A_s = Q / CS")
        self.procedimientos.append(f"   A_s = {caudal_total:,} / {carga_superficial}")
        
        area_superficial = caudal_total / carga_superficial
        self.procedimientos.append(f"   A_s = {area_superficial:.2f} m²")
        self.procedimientos.append("")
        
        # 3. Cálculo del Diámetro
        self.procedimientos.append("3. CÁLCULO DEL DIÁMETRO")
        self.procedimientos.append("   Fórmula: A_s = π × D² / 4")
        self.procedimientos.append(f"   {area_superficial:.2f} = π × D² / 4")
        self.procedimientos.append(f"   D² = {area_superficial:.2f} × 4 / π")
        
        diametro = math.sqrt((area_superficial * 4) / math.pi)
        self.procedimientos.append(f"   D² = {area_superficial * 4 / math.pi:.2f}")
        self.procedimientos.append(f"   D = √{area_superficial * 4 / math.pi:.2f} = {diametro:.2f} m")
        self.procedimientos.append("")
        
        # 4. Cálculo del Volumen Requerido
        self.procedimientos.append("4. CÁLCULO DEL VOLUMEN REQUERIDO")
        self.procedimientos.append("   Fórmula: V = Q × t")
        self.procedimientos.append(f"   V = {caudal_total:,} m³/d × ({tiempo_retencion}/24) días")
        
        tiempo_dias = tiempo_retencion / 24
        volumen_requerido = caudal_total * tiempo_dias
        self.procedimientos.append(f"   V = {caudal_total:,} × {tiempo_dias:.4f}")
        self.procedimientos.append(f"   V = {volumen_requerido:.2f} m³")
        self.procedimientos.append("")
        
        # 5. Cálculo de la Profundidad Útil
        self.procedimientos.append("5. CÁLCULO DE LA PROFUNDIDAD ÚTIL")
        self.procedimientos.append("   Fórmula: h = V / A_s")
        self.procedimientos.append(f"   h = {volumen_requerido:.2f} / {area_superficial:.2f}")
        
        profundidad_util = volumen_requerido / area_superficial
        self.procedimientos.append(f"   h = {profundidad_util:.2f} m")
        self.procedimientos.append("")
        
        # 6. Verificación de Profundidad Mínima
        self.procedimientos.append("6. VERIFICACIÓN DE PROFUNDIDAD")
        self.procedimientos.append(f"   Profundidad calculada: {profundidad_util:.2f} m")
        self.procedimientos.append(f"   Profundidad mínima recomendada: 2.5 m")
        
        if profundidad_util < 2.5:
            self.procedimientos.append("   ❌ PROFUNDIDAD INSUFICIENTE - Se ajusta a mínimo")
            profundidad_final = 2.5
            self.procedimientos.append(f"   h_final = 2.5 m")
            
            # Recalcular volumen real
            volumen_real = area_superficial * profundidad_final
            tiempo_real = (volumen_real / caudal_total) * 24
            self.procedimientos.append(f"   Volumen real: {volumen_real:.2f} m³")
            self.procedimientos.append(f"   Tiempo real: {tiempo_real:.2f} horas")
        else:
            profundidad_final = profundidad_util
            volumen_real = volumen_requerido
            tiempo_real = tiempo_retencion
            self.procedimientos.append("   ✅ PROFUNDIDAD ADECUADA")
        
        self.procedimientos.append("")
        
        # 7. Cálculo de Velocidad de Flujo
        self.procedimientos.append("7. CÁLCULO DE VELOCIDAD DE FLUJO")
        caudal_m3s = caudal_total / 86400
        self.procedimientos.append(f"   Q = {caudal_total:,} m³/d = {caudal_m3s:.4f} m³/s")
        
        # Área transversal aproximada para flujo radial
        area_transversal = math.pi * diametro * profundidad_final
        self.procedimientos.append(f"   Área transversal aproximada: {area_transversal:.2f} m²")
        
        velocidad_promedio = caudal_m3s / area_transversal
        velocidad_cms = velocidad_promedio * 100
        self.procedimientos.append(f"   v = {caudal_m3s:.4f} / {area_transversal:.2f} = {velocidad_promedio:.6f} m/s")
        self.procedimientos.append(f"   v = {velocidad_cms:.3f} cm/s")
        self.procedimientos.append("")
        
        # 8. Cálculo de Carga de Rebose
        self.procedimientos.append("8. CÁLCULO DE CARGA DE REBOSE")
        perimetro = math.pi * diametro
        self.procedimientos.append(f"   Perímetro del tanque: π × {diametro:.2f} = {perimetro:.2f} m")
        
        carga_rebose = caudal_m3s / perimetro
        carga_rebose_lsm = carga_rebose * 1000
        self.procedimientos.append(f"   q = {caudal_m3s:.4f} / {perimetro:.2f} = {carga_rebose:.6f} m³/s·m")
        self.procedimientos.append(f"   q = {carga_rebose_lsm:.3f} L/s·m")
        self.procedimientos.append("")
        
        # Almacenar resultados
        self.resultados = {
            'diametro': diametro,
            'profundidad_util': profundidad_final,
            'area_superficial': area_superficial,
            'volumen_real': volumen_real,
            'tiempo_retencion_real': tiempo_real,
            'velocidad_promedio_cms': velocidad_cms,
            'carga_rebose_lsm': carga_rebose_lsm,
            'caudal_m3s': caudal_m3s,
            'perimetro': perimetro
        }
        
        # Verificaciones y recomendaciones
        self._generar_verificaciones_y_recomendaciones()
        
        return True
    
    def _generar_verificaciones_y_recomendaciones(self):
        """Genera verificaciones y recomendaciones específicas"""
        r = self.resultados
        p = self.parametros
        
        # Verificaciones básicas
        self.verificaciones = {
            'Profundidad ≥ 2.5 m': r['profundidad_util'] >= 2.5,
            'Velocidad < 1.5 cm/s': r['velocidad_promedio_cms'] < 1.5,
            'Carga de rebose < 7.25 L/s·m': r['carga_rebose_lsm'] < 7.25,
            'Tiempo retención ≥ 1.5 horas': r['tiempo_retencion_real'] >= 1.5,
            'Diámetro en rango práctico (5-50 m)': 5 <= r['diametro'] <= 50
        }
        
        # Generar recomendaciones específicas
        self.recomendaciones = []
        
        if not self.verificaciones['Profundidad ≥ 2.5 m']:
            self.recomendaciones.append({
                'tipo': 'CRÍTICA',
                'mensaje': f'Profundidad insuficiente ({r["profundidad_util"]:.2f} m < 2.5 m)',
                'accion': 'Aumentar tiempo de retención o reducir carga superficial'
            })
        
        if not self.verificaciones['Velocidad < 1.5 cm/s']:
            self.recomendaciones.append({
                'tipo': 'ALTA',
                'mensaje': f'Velocidad muy alta ({r["velocidad_promedio_cms"]:.2f} cm/s > 1.5 cm/s)',
                'accion': 'Considerar aumentar el diámetro o usar múltiples tanques'
            })
        
        if not self.verificaciones['Carga de rebose < 7.25 L/s·m']:
            self.recomendaciones.append({
                'tipo': 'MEDIA', 
                'mensaje': f'Carga de rebose alta ({r["carga_rebose_lsm"]:.2f} L/s·m > 7.25 L/s·m)',
                'accion': 'Aumentar perímetro con vertederos adicionales o usar múltiples tanques'
            })
        
        if not self.verificaciones['Tiempo retención ≥ 1.5 horas']:
            self.recomendaciones.append({
                'tipo': 'CRÍTICA',
                'mensaje': f'Tiempo de retención insuficiente ({r["tiempo_retencion_real"]:.2f} h < 1.5 h)',
                'accion': 'Aumentar volumen (mayor diámetro o profundidad) o reducir caudal'
            })
        
        if not self.verificaciones['Diámetro en rango práctico (5-50 m)']:
            if r['diametro'] < 5:
                self.recomendaciones.append({
                    'tipo': 'MEDIA',
                    'mensaje': f'Diámetro muy pequeño ({r["diametro"]:.2f} m)',
                    'accion': 'Considerar tanque rectangular o aumentar carga superficial'
                })
            else:
                self.recomendaciones.append({
                    'tipo': 'ALTA',
                    'mensaje': f'Diámetro muy grande ({r["diametro"]:.2f} m > 50 m)',
                    'accion': 'Usar múltiples tanques más pequeños para mejor operación'
                })
        
        # Recomendaciones generales de optimización
        if len(self.recomendaciones) == 0:
            self.recomendaciones.append({
                'tipo': 'ÓPTIMO',
                'mensaje': 'Todos los parámetros están dentro de rangos recomendados',
                'accion': 'El diseño actual es adecuado para construcción'
            })
        else:
            # Añadir recomendación general si hay problemas
            self.recomendaciones.append({
                'tipo': 'GENERAL',
                'mensaje': 'Ajuste los parámetros de diseño y recalcule',
                'accion': 'Modificar tiempo de retención, carga superficial o considerar múltiples tanques'
            })
    
    def generar_grafica(self):
        if not self.resultados:
            return None
            
        diametro = self.resultados['diametro']
        profundidad = self.resultados['profundidad_util']
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Gráfica 1: Vista en Planta
        ax1.set_title('VISTA EN PLANTA - SEDIMENTADOR CIRCULAR', fontweight='bold', fontsize=14)
        
        # Dibujar círculo del tanque
        circle = plt.Circle((0, 0), diametro/2, fill=True, color='lightblue', 
                          alpha=0.6, edgecolor='blue', linewidth=2)
        ax1.add_patch(circle)
        
        # Flechas de flujo radial
        for angle in [45, 135, 225, 315]:
            rad = math.radians(angle)
            x_end = (diametro/2 - 1) * math.cos(rad)
            y_end = (diametro/2 - 1) * math.sin(rad)
            ax1.arrow(0, 0, x_end, y_end, head_width=diametro*0.05, 
                     head_length=diametro*0.05, fc='red', ec='red', linewidth=1.5)
        
        # Cotas de diámetro
        ax1.plot([-diametro/2, diametro/2], [-diametro/2-2, -diametro/2-2], 'k-', lw=2)
        ax1.plot([-diametro/2, -diametro/2], [-diametro/2-3, -diametro/2-1], 'k-', lw=2)
        ax1.plot([diametro/2, diametro/2], [-diametro/2-3, -diametro/2-1], 'k-', lw=2)
        ax1.text(0, -diametro/2-4, f'D = {diametro:.1f} m', ha='center', va='top', 
                fontweight='bold', fontsize=12)
        
        ax1.set_xlim(-diametro/2-5, diametro/2+5)
        ax1.set_ylim(-diametro/2-5, diametro/2+5)
        ax1.set_aspect('equal')
        ax1.axis('off')
        
        # Gráfica 2: Vista Transversal
        ax2.set_title('VISTA TRANSVERSAL - COTAS EN METROS', fontweight='bold', fontsize=14)
        
        # Dibujar sección transversal
        rect = plt.Rectangle((-diametro/2, 0), diametro, profundidad, 
                           fill=True, color='lightgreen', alpha=0.6, edgecolor='green', linewidth=2)
        ax2.add_patch(rect)
        
        # Línea de agua
        ax2.axhline(y=profundidad, color='blue', linestyle='--', alpha=0.7, 
                   label='Nivel de agua', linewidth=2)
        
        # Cotas de profundidad
        ax2.plot([-diametro/2-2, -diametro/2-1], [0, 0], 'k-', lw=2)
        ax2.plot([-diametro/2-2, -diametro/2-1], [profundidad, profundidad], 'k-', lw=2)
        ax2.plot([-diametro/2-1.5, -diametro/2-1.5], [0, profundidad], 'k-', lw=2)
        ax2.text(-diametro/2-3, profundidad/2, f'h = {profundidad:.1f} m', 
                ha='center', va='center', rotation=90, fontweight='bold', fontsize=12)
        
        # Cota de diámetro
        ax2.plot([-diametro/2, diametro/2], [-1, -1], 'k-', lw=2)
        ax2.text(0, -2, f'D = {diametro:.1f} m', ha='center', va='top', 
                fontweight='bold', fontsize=12)
        
        ax2.set_xlim(-diametro/2-5, diametro/2+5)
        ax2.set_ylim(-3, profundidad+2)
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
        pdf.cell(0, 10, 'REPORTE: DISEÑO SEDIMENTADOR CIRCULAR', 0, 1, 'C')
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, f'Fecha: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
        pdf.ln(5)
        
        # Datos del problema
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(0, 10, 'DATOS DEL PROBLEMA', 1, 1, 'L', 1)
        pdf.set_font("Arial", '', 10)
        p = self.parametros
        pdf.cell(0, 6, f'Caudal: {p["caudal_total_m3d"]:,} m³/d', 0, 1)
        pdf.cell(0, 6, f'Carga superficial: {p["carga_superficial"]} m/d', 0, 1)
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
        pdf.cell(0, 10, 'RESULTADOS DEL DISEÑO', 1, 1, 'L', 1)
        pdf.set_font("Arial", '', 10)
        
        r = self.resultados
        pdf.cell(0, 6, f'Diámetro del tanque: {r["diametro"]:.2f} m', 0, 1)
        pdf.cell(0, 6, f'Profundidad útil: {r["profundidad_util"]:.2f} m', 0, 1)
        pdf.cell(0, 6, f'Área superficial: {r["area_superficial"]:.2f} m²', 0, 1)
        pdf.cell(0, 6, f'Volumen: {r["volumen_real"]:.2f} m³', 0, 1)
        pdf.cell(0, 6, f'Tiempo retención real: {r["tiempo_retencion_real"]:.2f} horas', 0, 1)
        pdf.cell(0, 6, f'Velocidad promedio: {r["velocidad_promedio_cms"]:.2f} cm/s', 0, 1)
        pdf.cell(0, 6, f'Carga de rebose: {r["carga_rebose_lsm"]:.3f} L/s·m', 0, 1)
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
        pdf.ln(5)
        
        # Recomendaciones
        if self.recomendaciones:
            pdf.set_font("Arial", 'B', 12)
            pdf.set_fill_color(255, 240, 200)
            pdf.cell(0, 10, 'RECOMENDACIONES Y AJUSTES', 1, 1, 'L', 1)
            pdf.set_font("Arial", '', 10)
            
            for rec in self.recomendaciones:
                if rec['tipo'] == 'CRÍTICA':
                    pdf.set_text_color(200, 0, 0)
                elif rec['tipo'] == 'ALTA':
                    pdf.set_text_color(200, 100, 0)
                elif rec['tipo'] == 'MEDIA':
                    pdf.set_text_color(150, 150, 0)
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
    st.title("⭕ Diseño de Sedimentador Circular")
    st.markdown("### Resolución del Problema 5.21.4 - Capítulo 5: Sedimentación")
    
    if 'diseñador_circular' not in st.session_state:
        st.session_state.diseñador_circular = DiseñoSedimentadorCircular()
    
    # --- SIDEBAR ---
    st.sidebar.header("📋 Parámetros de Diseño")
    
    with st.sidebar.form("form_parametros"):
        st.subheader("Datos del Proyecto")
        
        caudal_total_m3d = st.number_input(
            "Caudal de diseño (m³/d)",
            min_value=1000.0,
            max_value=100000.0,
            value=15000.0,
            step=1000.0,
            help="Caudal máximo que debe tratar el sedimentador"
        )
        
        carga_superficial = st.number_input(
            "Carga superficial (m/d)",
            min_value=10.0,
            max_value=60.0,
            value=20.0,
            step=1.0,
            help="Carga hidráulica superficial típica: 20-40 m/d"
        )
        
        tiempo_retencion_horas = st.number_input(
            "Tiempo de retención (horas)",
            min_value=1.0,
            max_value=8.0,
            value=4.0,
            step=0.5,
            help="Tiempo recomendado: 1.5-4 horas"
        )
        
        # Botón de cálculo
        if st.form_submit_button("🚀 Calcular Diseño"):
            parametros = {
                'caudal_total_m3d': caudal_total_m3d,
                'carga_superficial': carga_superficial,
                'tiempo_retencion_horas': tiempo_retencion_horas
            }
            st.session_state.diseñador_circular.calcular(parametros)
            st.rerun()
    
    # --- INFORMACIÓN DE NORMA ---
    with st.sidebar.expander("📚 Parámetros Recomendados"):
        st.markdown("""
        **Valores típicos (RAS):**
        
        - **Carga superficial:** 20-40 m/d
        - **Tiempo de retención:** 1.5-4 horas
        - **Profundidad útil:** ≥ 2.5 m
        - **Velocidad horizontal:** < 1.5 cm/s
        - **Carga de rebose:** < 7.25 L/s·m
        - **Diámetro práctico:** 5-50 m
        """)
    
    # --- EJEMPLOS RÁPIDOS ---
    with st.sidebar.expander("🎯 Ejemplos Rápidos"):
        if st.button("Problema 5.21.4 Original"):
            st.session_state.diseñador_circular.calcular({
                'caudal_total_m3d': 15000.0,
                'carga_superficial': 20.0,
                'tiempo_retencion_horas': 4.0
            })
            st.rerun()
        
        if st.button("Planta Mediana (25,000 m³/d)"):
            st.session_state.diseñador_circular.calcular({
                'caudal_total_m3d': 25000.0,
                'carga_superficial': 25.0,
                'tiempo_retencion_horas': 3.0
            })
            st.rerun()
        
        if st.button("Alta Carga (50,000 m³/d)"):
            st.session_state.diseñador_circular.calcular({
                'caudal_total_m3d': 50000.0,
                'carga_superficial': 40.0,
                'tiempo_retencion_horas': 2.0
            })
            st.rerun()
    
    # --- RESULTADOS PRINCIPALES ---
    diseñador = st.session_state.diseñador_circular
    
    if diseñador.resultados:
        st.success("✅ Diseño calculado exitosamente")
        
        # Mostrar configuración actual
        st.info(f"""
        **Configuración del diseño:** 
        - Caudal: {diseñador.parametros['caudal_total_m3d']:,} m³/d
        - Carga superficial: {diseñador.parametros['carga_superficial']} m/d
        - Tiempo retención: {diseñador.parametros['tiempo_retencion_horas']} horas
        """)
        
        # Mostrar resultados en pestañas
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📐 Resultados", "📋 Procedimiento", "💡 Recomendaciones", "📊 Esquemas", "📥 Reporte"])
        
        with tab1:
            st.subheader("Resultados del Diseño")
            
            # Métricas principales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Diámetro", f"{diseñador.resultados['diametro']:.2f} m")
            
            with col2:
                st.metric("Profundidad", f"{diseñador.resultados['profundidad_util']:.2f} m")
            
            with col3:
                st.metric("Tiempo Retención", f"{diseñador.resultados['tiempo_retencion_real']:.2f} h")
            
            with col4:
                st.metric("Volumen", f"{diseñador.resultados['volumen_real']:.0f} m³")
            
            # Tabla de resultados detallados
            st.subheader("📊 Resumen de Dimensiones")
            datos_resumen = {
                'Parámetro': ['Diámetro del tanque', 'Profundidad útil', 'Área superficial', 
                             'Volumen total', 'Tiempo de retención', 'Velocidad promedio',
                             'Carga de rebose', 'Perímetro vertedero'],
                'Valor': [f"{diseñador.resultados['diametro']:.2f} m",
                         f"{diseñador.resultados['profundidad_util']:.2f} m",
                         f"{diseñador.resultados['area_superficial']:.0f} m²",
                         f"{diseñador.resultados['volumen_real']:.0f} m³",
                         f"{diseñador.resultados['tiempo_retencion_real']:.2f} horas",
                         f"{diseñador.resultados['velocidad_promedio_cms']:.2f} cm/s",
                         f"{diseñador.resultados['carga_rebose_lsm']:.3f} L/s·m",
                         f"{diseñador.resultados['perimetro']:.2f} m"],
                'Recomendación': ['5-50 m', '≥ 2.5 m', '-', '-', '1.5-4 horas', 
                                '< 1.5 cm/s', '< 7.25 L/s·m', '-']
            }
            
            df_resumen = pd.DataFrame(datos_resumen)
            st.dataframe(df_resumen, use_container_width=True)
            
            # Verificaciones
            st.subheader("✅ Verificaciones de Cumplimiento")
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
            st.subheader("💡 Recomendaciones y Ajustes")
            
            if diseñador.recomendaciones:
                for rec in diseñador.recomendaciones:
                    if rec['tipo'] == 'CRÍTICA':
                        st.error(f"**{rec['tipo']}:** {rec['mensaje']}")
                        st.info(f"**Acción recomendada:** {rec['accion']}")
                    elif rec['tipo'] == 'ALTA':
                        st.warning(f"**{rec['tipo']}:** {rec['mensaje']}")
                        st.info(f"**Acción recomendada:** {rec['accion']}")
                    elif rec['tipo'] == 'MEDIA':
                        st.warning(f"**{rec['tipo']}:** {rec['mensaje']}")
                        st.info(f"**Acción recomendada:** {rec['accion']}")
                    else:
                        st.success(f"**{rec['tipo']}:** {rec['mensaje']}")
                        st.info(f"**Acción recomendada:** {rec['accion']}")
                    st.markdown("---")
            else:
                st.success("**✅ DISEÑO ÓPTIMO:** No se requieren ajustes adicionales")
            
            # Sugerencias de optimización
            st.subheader("🔧 Sugerencias de Optimización")
            st.markdown("""
            **Para mejorar el diseño considere:**
            - **Múltiples tanques** si el diámetro es muy grande (> 40 m)
            - **Aumentar tiempo de retención** si la profundidad es insuficiente
            - **Reducir carga superficial** para mejorar eficiencia
            - **Vertederos adicionales** si la carga de rebose es alta
            """)
        
        with tab4:
            st.subheader("📊 Esquemas del Sedimentador")
            fig = diseñador.generar_grafica()
            if fig:
                st.pyplot(fig)
        
        with tab5:
            st.subheader("📥 Generar Reporte PDF")
            
            if st.button("🖨️ Generar Reporte Completo en PDF"):
                with st.spinner("Generando reporte PDF..."):
                    pdf_file = diseñador.generar_reporte_pdf()
                    
                    with open(pdf_file, "rb") as f:
                        st.download_button(
                            label="📥 Descargar Reporte PDF",
                            data=f,
                            file_name=f"diseno_circular_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
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
           - Carga superficial (m/d)
           - Tiempo de retención (horas)
        
        2. **Haga clic en "Calcular Diseño"** para dimensionar el sedimentador
        
        3. **Revise los resultados** en las diferentes pestañas:
           - 📐 Resultados: Dimensiones y verificaciones
           - 📋 Procedimiento: Cálculos detallados paso a paso
           - 💡 Recomendaciones: Ajustes específicos si no cumple
           - 📊 Esquemas: Diagramas del sedimentador circular
           - 📥 Reporte: Descarga en PDF
        
        ### 🎯 Problema 5.21.4 Original:
        Diseñar sedimentador circular para 15,000 m³/d con:
        - Carga superficial: 20 m/d
        - Tiempo de retención: 4 horas
        """)

if __name__ == "__main__":
    main()
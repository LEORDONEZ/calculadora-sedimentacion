import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from fpdf import FPDF
import tempfile
import os
from datetime import datetime

# ==========================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="Ejemplo 5.19 - Diseño Sedimentador Convencional",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CLASE PARA EJEMPLO 5.19
# ==========================================
class AnalizadorEjemplo519:
    def __init__(self):
        self.parametros = {}
        self.resultados = {}
        self.calculos_detallados = []
    
    def calcular(self, parametros):
        self.parametros = parametros
        self.calculos_detallados = []
        
        # --- DATOS DE ENTRADA ---
        Q_m3d = parametros['caudal_diseno']
        CS = parametros['carga_superficial']
        t_retencion_h = parametros['tiempo_retencion']
        relacion_LW = parametros['relacion_longitud_ancho']
        borde_libre = parametros['borde_libre']
        altura_lodos = parametros['altura_lodos']
        vel_paso_orificios = parametros['velocidad_orificios']
        carga_vertedero = parametros['carga_vertedero']
        
        # ==========================================
        # CÁLCULOS DETALLADOS
        # ==========================================
        self.calculos_detallados.append("=" * 60)
        self.calculos_detallados.append("SOLUCIÓN PASO A PASO: EJEMPLO 5.19")
        self.calculos_detallados.append("=" * 60)
        self.calculos_detallados.append("")
        
        # --- 1. DATOS DEL PROBLEMA ---
        self.calculos_detallados.append("--- 1. DATOS DEL PROBLEMA ---")
        self.calculos_detallados.append(f"   Caudal de diseño: {Q_m3d} m³/d")
        self.calculos_detallados.append(f"   Carga superficial: {CS} m/d")
        self.calculos_detallados.append(f"   Tiempo de retención: {t_retencion_h} horas")
        self.calculos_detallados.append(f"   Relación longitud/ancho: {relacion_LW}/1")
        self.calculos_detallados.append(f"   Borde libre: {borde_libre} m")
        self.calculos_detallados.append(f"   Altura para lodos: {altura_lodos} m")
        self.calculos_detallados.append("")
        
        # --- PASO 1: VOLUMEN DEL SEDIMENTADOR ---
        V = Q_m3d * (t_retencion_h / 24.0)
        
        self.calculos_detallados.append("--- 2. VOLUMEN DEL SEDIMENTADOR ---")
        self.calculos_detallados.append(f"   Fórmula: V = Q × t")
        self.calculos_detallados.append(f"   V = {Q_m3d} × ({t_retencion_h}/24)")
        self.calculos_detallados.append(f"   V = {V:.0f} m³")
        self.calculos_detallados.append("")
        
        # --- PASO 2: ÁREA SUPERFICIAL ---
        A = Q_m3d / CS
        
        self.calculos_detallados.append("--- 3. ÁREA SUPERFICIAL ---")
        self.calculos_detallados.append(f"   Fórmula: A = Q / CS")
        self.calculos_detallados.append(f"   A = {Q_m3d} / {CS}")
        self.calculos_detallados.append(f"   A = {A:.0f} m²")
        self.calculos_detallados.append("")
        
        # --- PASO 3: DIMENSIONES DEL TANQUE ---
        Ancho_calc = np.sqrt(A / relacion_LW)
        Ancho_final = round(Ancho_calc)  # Redondeo práctico
        L_calc = A / Ancho_final
        L_final = round(L_calc, 1)  # Un decimal para longitud
        
        self.calculos_detallados.append("--- 4. DIMENSIONES DEL TANQUE ---")
        self.calculos_detallados.append(f"   Relación L/W = {relacion_LW}/1")
        self.calculos_detallados.append(f"   Ancho calculado = √(A / {relacion_LW}) = √({A:.0f} / {relacion_LW})")
        self.calculos_detallados.append(f"   Ancho calculado = {Ancho_calc:.2f} m → Se adopta: {Ancho_final} m")
        self.calculos_detallados.append(f"   Longitud calculada = A / Ancho = {A:.0f} / {Ancho_final}")
        self.calculos_detallados.append(f"   Longitud calculada = {L_calc:.2f} m → Se adopta: {L_final} m")
        self.calculos_detallados.append("")
        
        # --- PASO 4: PROFUNDIDADES ---
        H_agua = V / (Ancho_final * L_final)
        H_total = H_agua + borde_libre + altura_lodos
        
        self.calculos_detallados.append("--- 5. PROFUNDIDADES ---")
        self.calculos_detallados.append(f"   Profundidad útil del agua:")
        self.calculos_detallados.append(f"   H_agua = V / (Ancho × Longitud)")
        self.calculos_detallados.append(f"   H_agua = {V:.0f} / ({Ancho_final} × {L_final})")
        self.calculos_detallados.append(f"   H_agua = {H_agua:.2f} m")
        self.calculos_detallados.append("")
        self.calculos_detallados.append(f"   Profundidad total del tanque:")
        self.calculos_detallados.append(f"   H_total = H_agua + borde libre + altura lodos")
        self.calculos_detallados.append(f"   H_total = {H_agua:.2f} + {borde_libre} + {altura_lodos}")
        self.calculos_detallados.append(f"   H_total = {H_total:.2f} m")
        self.calculos_detallados.append("")
        
        # --- PASO 5: VELOCIDAD HORIZONTAL ---
        Q_m3s = Q_m3d / 86400
        Area_transversal = Ancho_final * H_agua
        v_ms = Q_m3s / Area_transversal
        v_cms = v_ms * 100
        
        self.calculos_detallados.append("--- 6. VELOCIDAD HORIZONTAL ---")
        self.calculos_detallados.append(f"   Caudal en m³/s: Q = {Q_m3d} / 86400 = {Q_m3s:.4f} m³/s")
        self.calculos_detallados.append(f"   Área transversal = Ancho × H_agua = {Ancho_final} × {H_agua:.2f}")
        self.calculos_detallados.append(f"   Área transversal = {Area_transversal:.2f} m²")
        self.calculos_detallados.append(f"   Velocidad = Q / Área_transversal = {Q_m3s:.4f} / {Area_transversal:.2f}")
        self.calculos_detallados.append(f"   Velocidad = {v_ms:.4f} m/s = {v_cms:.2f} cm/s")
        
        if v_cms < 1.5:
            self.calculos_detallados.append(f"   ✓ Verificación: OK (v = {v_cms:.2f} cm/s < 1.5 cm/s)")
        else:
            self.calculos_detallados.append(f"   ✗ Verificación: Velocidad muy alta (v = {v_cms:.2f} cm/s > 1.5 cm/s)")
        self.calculos_detallados.append("")
        
        # --- PASO 6: DISEÑO DE LA ENTRADA ---
        Area_orif = Q_m3s / vel_paso_orificios
        N_orif = Area_orif / (0.10 * 0.10)  # Orificios de 10x10 cm
        
        self.calculos_detallados.append("--- 7. DISEÑO DE LA ENTRADA (Pantalla Difusora) ---")
        self.calculos_detallados.append(f"   Velocidad en orificios: {vel_paso_orificios} m/s")
        self.calculos_detallados.append(f"   Área total de orificios = Q / v_orificio")
        self.calculos_detallados.append(f"   Área total = {Q_m3s:.4f} / {vel_paso_orificios} = {Area_orif:.3f} m²")
        self.calculos_detallados.append(f"   Área por orificio (10×10 cm) = 0.10 × 0.10 = 0.01 m²")
        self.calculos_detallados.append(f"   Número de orificios = {Area_orif:.3f} / 0.01 = {N_orif:.0f} orificios")
        self.calculos_detallados.append("")
        
        # --- PASO 7: DISEÑO DE LA SALIDA ---
        Q_ls = Q_m3s * 1000
        L_vert = Q_ls / carga_vertedero
        
        self.calculos_detallados.append("--- 8. DISEÑO DE LA SALIDA (Vertedero) ---")
        self.calculos_detallados.append(f"   Caudal en L/s: Q = {Q_m3s:.4f} × 1000 = {Q_ls:.1f} L/s")
        self.calculos_detallados.append(f"   Carga del vertedero: {carga_vertedero} L/s·m")
        self.calculos_detallados.append(f"   Longitud del vertedero = Q / carga")
        self.calculos_detallados.append(f"   Longitud = {Q_ls:.1f} / {carga_vertedero} = {L_vert:.1f} m")
        self.calculos_detallados.append("")
        
        # Verificación longitud vertedero vs ancho tanque
        if L_vert <= Ancho_final:
            self.calculos_detallados.append(f"   ✓ Verificación: Longitud suficiente (se puede colocar en un solo lado)")
        else:
            self.calculos_detallados.append(f"   ⚠ Advertencia: Se requieren vertederos en múltiples lados")
        
        # Almacenar resultados
        self.resultados = {
            'volumen': V,
            'area_superficial': A,
            'ancho': Ancho_final,
            'longitud': L_final,
            'profundidad_agua': H_agua,
            'profundidad_total': H_total,
            'velocidad_horizontal': v_cms,
            'area_orificios': Area_orif,
            'numero_orificios': int(round(N_orif)),
            'longitud_vertedero': L_vert,
            'velocidad_ok': v_cms < 1.5
        }
        
        return True
    
    def generar_grafica_planos(self):
        if not self.resultados:
            return None
            
        L = self.resultados['longitud']
        W = self.resultados['ancho']
        H_total = self.resultados['profundidad_total']
        H_agua = self.resultados['profundidad_agua']
        
        fig = plt.figure(figsize=(14, 10))
        gs = fig.add_gridspec(2, 1, height_ratios=[1.2, 1])
        
        ax_planta = fig.add_subplot(gs[0])
        ax_perfil = fig.add_subplot(gs[1])
        
        # --- VISTA EN PLANTA ---
        ax_planta.set_title(f"VISTA EN PLANTA - Sedimentador {L}m × {W}m", 
                          fontsize=14, fontweight='bold', pad=20)
        
        # Rectángulo principal
        rect_planta = patches.Rectangle((0, 0), L, W, lw=3, 
                                      edgecolor='#37474F', facecolor='#E1F5FE')
        ax_planta.add_patch(rect_planta)
        
        # Elementos de la planta
        # Pantalla de entrada
        ax_planta.plot([2, 2], [0.5, W-0.5], 'k-', lw=3, label='Pantalla entrada')
        
        # Canaletas de salida
        for y in [W/4, W/2, 3*W/4]:
            ax_planta.plot([L-3, L], [y, y], 'b-', lw=2, alpha=0.7)
        
        # Zona de lodos (indicación)
        ax_planta.add_patch(patches.Rectangle((0, 0), L, 0.5, 
                                            facecolor='#8D6E63', alpha=0.3))
        ax_planta.text(L/2, 0.25, "Zona de Lodos", ha='center', va='center', 
                     fontweight='bold', color='white', fontsize=10)
        
        # Cotas
        ax_planta.annotate('', xy=(0, -2), xytext=(L, -2),
                         arrowprops=dict(arrowstyle='|-|', lw=2, color='black'), 
                         annotation_clip=False)
        ax_planta.text(L/2, -3.5, f'LONGITUD = {L} m', 
                     ha='center', fontweight='bold', fontsize=12)
        
        ax_planta.annotate('', xy=(-2, 0), xytext=(-2, W),
                         arrowprops=dict(arrowstyle='|-|', lw=2, color='black'),
                         annotation_clip=False)
        ax_planta.text(-4, W/2, f'ANCHO = {W} m', 
                     va='center', rotation=90, fontweight='bold', fontsize=12)
        
        ax_planta.set_xlim(-8, L+5)
        ax_planta.set_ylim(-5, W+5)
        ax_planta.set_aspect('equal')
        ax_planta.axis('off')
        
        # Leyenda
        ax_planta.legend(loc='upper right', bbox_to_anchor=(0.98, 0.98))

        # --- VISTA EN PERFIL ---
        ax_perfil.set_title(f"CORTE LONGITUDINAL - Profundidad Total {H_total:.2f}m", 
                          fontsize=14, fontweight='bold', pad=20)
        
        # Capas del sedimentador
        h_lodos = 0.5
        h_nivel_agua = h_lodos + H_agua
        
        # Capa de lodos
        rect_lodos = patches.Rectangle((0, 0), L, h_lodos, 
                                     facecolor='#5D4037', alpha=0.8, label='Lodos')
        ax_perfil.add_patch(rect_lodos)
        ax_perfil.text(3, h_lodos/2, f"Lodos ({h_lodos}m)", 
                     color='white', va='center', fontweight='bold')
        
        # Columna de agua
        rect_agua = patches.Rectangle((0, h_lodos), L, H_agua, 
                                    facecolor='#29B6F6', alpha=0.4, label='Agua')
        ax_perfil.add_patch(rect_agua)
        
        # Borde libre (espacio vacío)
        rect_borde = patches.Rectangle((0, h_nivel_agua), L, H_total - h_nivel_agua, 
                                     facecolor='#B3E5FC', alpha=0.3, label='Borde libre')
        ax_perfil.add_patch(rect_borde)
        
        # Contorno del tanque
        rect_contorno = patches.Rectangle((0, 0), L, H_total, 
                                        fill=False, edgecolor='black', lw=3)
        ax_perfil.add_patch(rect_contorno)
        
        # Línea de nivel de agua
        ax_perfil.plot([0, L], [h_nivel_agua, h_nivel_agua], 'b--', lw=2, alpha=0.7)
        ax_perfil.text(L-2, h_nivel_agua + 0.1, 'Nivel de agua', color='blue', fontweight='bold')
        
        # Cotas de profundidad
        # Profundidad útil
        ax_perfil.annotate('', xy=(L+2, h_lodos), xytext=(L+2, h_nivel_agua),
                         arrowprops=dict(arrowstyle='<->', lw=2, color='blue'))
        ax_perfil.text(L+3, h_lodos + H_agua/2, f'H útil = {H_agua:.2f} m', 
                     color='blue', va='center', fontweight='bold')
        
        # Profundidad total
        ax_perfil.annotate('', xy=(L+6, 0), xytext=(L+6, H_total),
                         arrowprops=dict(arrowstyle='|-|', lw=2, color='black'))
        ax_perfil.text(L+7.5, H_total/2, f'H Total = {H_total:.2f} m', 
                     rotation=90, va='center', fontweight='bold')
        
        ax_perfil.set_xlim(-2, L+12)
        ax_perfil.set_ylim(-0.5, H_total+1)
        ax_perfil.set_aspect('equal')
        ax_perfil.axis('off')
        
        # Leyenda del perfil
        ax_perfil.legend(loc='upper right', bbox_to_anchor=(0.98, 0.98))

        plt.tight_layout()
        return fig
    
    def generar_reporte_pdf(self):
        pdf = FPDF()
        pdf.add_page()
        
        # Encabezado
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, 'EJEMPLO 5.19 - DISEÑO SEDIMENTADOR CONVENCIONAL', 0, 1, 'C')
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, f'Fecha: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
        pdf.ln(5)
        
        # Datos del problema
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(0, 10, 'DATOS DE DISEÑO', 1, 1, 'L', 1)
        pdf.set_font("Arial", '', 10)
        p = self.parametros
        pdf.cell(0, 6, f'Caudal de diseño: {p["caudal_diseno"]} m³/d', 0, 1)
        pdf.cell(0, 6, f'Carga superficial: {p["carga_superficial"]} m/d', 0, 1)
        pdf.cell(0, 6, f'Tiempo de retención: {p["tiempo_retencion"]} horas', 0, 1)
        pdf.cell(0, 6, f'Relación L/W: {p["relacion_longitud_ancho"]}/1', 0, 1)
        pdf.cell(0, 6, f'Borde libre: {p["borde_libre"]} m', 0, 1)
        pdf.cell(0, 6, f'Altura lodos: {p["altura_lodos"]} m', 0, 1)
        pdf.ln(5)
        
        # Cálculos detallados
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(0, 10, 'CÁLCULOS DETALLADOS', 1, 1, 'L', 1)
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
        pdf.cell(0, 6, f'Dimensiones: {r["longitud"]}m × {r["ancho"]}m × {r["profundidad_total"]:.2f}m', 0, 1)
        pdf.cell(0, 6, f'Volumen: {r["volumen"]:.0f} m³', 0, 1)
        pdf.cell(0, 6, f'Área superficial: {r["area_superficial"]:.0f} m²', 0, 1)
        pdf.cell(0, 6, f'Velocidad horizontal: {r["velocidad_horizontal"]:.2f} cm/s', 0, 1)
        pdf.cell(0, 6, f'Número de orificios entrada: {r["numero_orificios"]}', 0, 1)
        pdf.cell(0, 6, f'Longitud vertedero salida: {r["longitud_vertedero"]:.1f} m', 0, 1)
        
        # Guardar PDF temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf.output(tmp_file.name)
            return tmp_file.name

# ==========================================
# INTERFAZ PRINCIPAL
# ==========================================
def main():
    st.title("📐 Ejemplo 5.19 - Diseño de Sedimentador Convencional")
    st.markdown("### Dimensionamiento de Sedimentador Rectangular de Flujo Horizontal")
    
    if 'analizador_519' not in st.session_state:
        st.session_state.analizador_519 = AnalizadorEjemplo519()
    
    # --- SIDEBAR ---
    st.sidebar.header("📋 Parámetros de Diseño")
    
    with st.sidebar.form("form_parametros_519"):
        st.subheader("Datos Hidráulicos")
        
        caudal_diseno = st.number_input(
            "Caudal de diseño (m³/d)",
            min_value=1000.0,
            max_value=50000.0,
            value=10000.0,
            step=1000.0
        )
        
        carga_superficial = st.number_input(
            "Carga superficial (m/d)",
            min_value=10.0,
            max_value=50.0,
            value=20.0,
            step=1.0
        )
        
        tiempo_retencion = st.number_input(
            "Tiempo de retención (horas)",
            min_value=1.0,
            max_value=8.0,
            value=2.0,
            step=0.5
        )
        
        relacion_longitud_ancho = st.number_input(
            "Relación Longitud/Ancho",
            min_value=2.0,
            max_value=5.0,
            value=3.0,
            step=0.5
        )
        
        st.subheader("Parámetros Constructivos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            borde_libre = st.number_input(
                "Borde libre (m)",
                min_value=0.2,
                max_value=1.0,
                value=0.34,
                step=0.05
            )
            
            altura_lodos = st.number_input(
                "Altura para lodos (m)",
                min_value=0.3,
                max_value=1.0,
                value=0.5,
                step=0.1
            )
        
        with col2:
            velocidad_orificios = st.number_input(
                "Velocidad en orificios (m/s)",
                min_value=0.1,
                max_value=0.3,
                value=0.15,
                step=0.01
            )
            
            carga_vertedero = st.number_input(
                "Carga en vertedero (L/s·m)",
                min_value=1.0,
                max_value=5.0,
                value=2.0,
                step=0.1
            )
        
        # Botón de cálculo
        if st.form_submit_button("🚀 Calcular Ejemplo 5.19"):
            parametros = {
                'caudal_diseno': caudal_diseno,
                'carga_superficial': carga_superficial,
                'tiempo_retencion': tiempo_retencion,
                'relacion_longitud_ancho': relacion_longitud_ancho,
                'borde_libre': borde_libre,
                'altura_lodos': altura_lodos,
                'velocidad_orificios': velocidad_orificios,
                'carga_vertedero': carga_vertedero
            }
            st.session_state.analizador_519.calcular(parametros)
            st.rerun()
    
    # --- EJEMPLO ORIGINAL ---
    with st.sidebar.expander("🎯 Ejemplo Original 5.19"):
        if st.button("Cargar Valores Originales"):
            st.session_state.analizador_519.calcular({
                'caudal_diseno': 10000.0,
                'carga_superficial': 20.0,
                'tiempo_retencion': 2.0,
                'relacion_longitud_ancho': 3.0,
                'borde_libre': 0.34,
                'altura_lodos': 0.5,
                'velocidad_orificios': 0.15,
                'carga_vertedero': 2.0
            })
            st.rerun()
    
    # --- RESULTADOS PRINCIPALES ---
    analizador = st.session_state.analizador_519
    
    if analizador.resultados:
        st.success("✅ Diseño del sedimentador completado")
        
        # Mostrar configuración actual
        st.info(f"""
        **Parámetros de diseño:** 
        - Caudal: {analizador.parametros['caudal_diseno']} m³/d
        - Carga superficial: {analizador.parametros['carga_superficial']} m/d
        - Tiempo retención: {analizador.parametros['tiempo_retencion']} horas
        - Relación L/W: {analizador.parametros['relacion_longitud_ancho']}/1
        """)
        
        # Mostrar resultados en pestañas
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Resultados", "🧮 Cálculos", "📈 Planos", "📥 Reporte"])
        
        with tab1:
            st.subheader("Resultados del Diseño")
            
            # Métricas principales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Dimensiones", f"{analizador.resultados['longitud']}m × {analizador.resultados['ancho']}m")
            
            with col2:
                st.metric("Profundidad Total", f"{analizador.resultados['profundidad_total']:.2f} m")
            
            with col3:
                st.metric("Velocidad", f"{analizador.resultados['velocidad_horizontal']:.2f} cm/s")
            
            with col4:
                status_color = "🟢" if analizador.resultados['velocidad_ok'] else "🔴"
                st.metric("Verificación", f"{status_color} {'OK' if analizador.resultados['velocidad_ok'] else 'ALTA'}")
            
            # Tabla de resultados detallados
            st.subheader("📋 Especificaciones Técnicas")
            
            datos_especificaciones = {
                'Parámetro': [
                    'Volumen del sedimentador',
                    'Área superficial', 
                    'Profundidad útil de agua',
                    'Velocidad horizontal',
                    'Orificios de entrada',
                    'Longitud de vertedero',
                    'Relación L/W actual'
                ],
                'Valor': [
                    f"{analizador.resultados['volumen']:.0f} m³",
                    f"{analizador.resultados['area_superficial']:.0f} m²",
                    f"{analizador.resultados['profundidad_agua']:.2f} m",
                    f"{analizador.resultados['velocidad_horizontal']:.2f} cm/s",
                    f"{analizador.resultados['numero_orificios']} unidades",
                    f"{analizador.resultados['longitud_vertedero']:.1f} m",
                    f"{analizador.resultados['longitud']/analizador.resultados['ancho']:.2f}/1"
                ],
                'Recomendación': [
                    'Suficiente para tiempo de retención',
                    'Adecuada para carga superficial',
                    'Entre 1.5-4.0 m (OK)',
                    '< 1.5 cm/s (OK)' if analizador.resultados['velocidad_ok'] else '> 1.5 cm/s (REVISAR)',
                    'Distribuir uniformemente',
                    'Colocar en lado de salida',
                    f"Objetivo: {analizador.parametros['relacion_longitud_ancho']}/1"
                ]
            }
            
            df_especificaciones = pd.DataFrame(datos_especificaciones)
            st.dataframe(df_especificaciones, use_container_width=True)
            
            # Verificaciones de diseño
            st.subheader("✅ Verificaciones de Diseño")
            
            col_ver1, col_ver2 = st.columns(2)
            
            with col_ver1:
                # Verificación velocidad
                if analizador.resultados['velocidad_ok']:
                    st.success("**Velocidad horizontal:** ✓ ACEPTABLE")
                    st.write(f"Valor calculado: {analizador.resultados['velocidad_horizontal']:.2f} cm/s < 1.5 cm/s")
                else:
                    st.error("**Velocidad horizontal:** ✗ MUY ALTA")
                    st.write(f"Valor calculado: {analizador.resultados['velocidad_horizontal']:.2f} cm/s > 1.5 cm/s")
            
            with col_ver2:
                # Verificación relación L/W
                relacion_actual = analizador.resultados['longitud'] / analizador.resultados['ancho']
                objetivo = analizador.parametros['relacion_longitud_ancho']
                if abs(relacion_actual - objetivo) < 0.5:
                    st.success("**Relación L/W:** ✓ ACEPTABLE")
                    st.write(f"Valor actual: {relacion_actual:.2f}/1 (Objetivo: {objetivo}/1)")
                else:
                    st.warning("**Relación L/W:** ⚠ DIFERENTE")
                    st.write(f"Valor actual: {relacion_actual:.2f}/1 (Objetivo: {objetivo}/1)")
        
        with tab2:
            st.subheader("🧮 Cálculos Detallados Paso a Paso")
            st.code("\n".join(analizador.calculos_detallados), language="text")
        
        with tab3:
            st.subheader("📈 Planos del Sedimentador")
            fig = analizador.generar_grafica_planos()
            if fig:
                st.pyplot(fig)
                st.caption("Figura: Vista en planta y corte longitudinal del sedimentador diseñado")
        
        with tab4:
            st.subheader("📥 Generar Reporte de Diseño")
            
            if st.button("🖨️ Generar Reporte Completo en PDF"):
                with st.spinner("Generando reporte PDF..."):
                    pdf_file = analizador.generar_reporte_pdf()
                    
                    with open(pdf_file, "rb") as f:
                        st.download_button(
                            label="📥 Descargar Reporte PDF",
                            data=f,
                            file_name=f"ejemplo_5_19_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                            mime="application/pdf"
                        )
                    
                    # Limpiar archivo temporal
                    os.unlink(pdf_file)
    
    else:
        # Pantalla inicial
        st.info("""
        ## 🧭 Ejemplo 5.19 - Diseño de Sedimentador Convencional
        
        **Objetivo:** Dimensionar un sedimentador rectangular de flujo horizontal para tratamiento de agua.
        
        **Problema original del libro:**
        - Caudal: 10,000 m³/d (116 L/s)
        - Carga superficial: 20 m/d (para floc de alumbre)
        - Tiempo de retención: 2 horas
        - Relación longitud/ancho: 3/1
        
        **Elementos a diseñar:**
        1. **Dimensiones principales:** Largo, ancho, profundidad
        2. **Volumen y área superficial**
        3. **Velocidad horizontal** de flujo
        4. **Sistema de entrada:** Pantalla con orificios
        5. **Sistema de salida:** Vertedero de rebose
        
        **Criterios de diseño:**
        - Velocidad horizontal < 1.5 cm/s
        - Relación L/W entre 3:1 y 5:1
        - Profundidad útil entre 1.5-4.0 m
        - Borde libre mínimo 0.3 m
        
        **🎯 Resultado esperado:** Diseño completo de sedimentador con todas las especificaciones técnicas.
        """)

if __name__ == "__main__":
    main()
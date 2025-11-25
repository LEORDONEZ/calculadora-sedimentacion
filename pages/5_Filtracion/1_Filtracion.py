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
    page_title="Diseño Sedimentador Convencional",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CLASE PRINCIPAL DE LÓGICA Y REPORTE
# ==========================================
class SedimentadorConvencional:
    def __init__(self):
        self.parametros = {}
        self.resultados = {}
        self.calculos_detallados = []
    
    def calcular(self, parametros):
        self.parametros = parametros
        self.calculos_detallados = []
        
        # --- DATOS DE ENTRADA ---
        Q_total = parametros['caudal_total']
        N = parametros['numero_sedimentadores']
        CS = parametros['carga_superficial']
        H = parametros['profundidad_tanque']
        b_lat = parametros['ancho_canaleta_lateral']
        b_front = parametros['ancho_canaleta_frontal']
        
        self.calculos_detallados.append("=" * 60)
        self.calculos_detallados.append("DISEÑO AUTOMATIZADO DE SEDIMENTADOR CONVENCIONAL")
        self.calculos_detallados.append("=" * 60)
        self.calculos_detallados.append("")
        
        # ==========================================
        # PASO 1: CAUDAL UNITARIO
        # ==========================================
        Q_unit_m3d = Q_total / N
        Q_unit_ls = (Q_unit_m3d * 1000) / 86400  
        Q_unit_m3s = Q_unit_m3d / 86400
        
        self.calculos_detallados.append("--- 1. CAUDAL POR UNIDAD (Q) ---")
        self.calculos_detallados.append(f"   Fórmula: Q = Q_total / N")
        self.calculos_detallados.append(f"   Sustitución: {Q_total} / {N}")
        self.calculos_detallados.append(f"   Resultado: {Q_unit_m3d:.2f} m³/d ({Q_unit_ls:.2f} L/s)")
        self.calculos_detallados.append("")
        
        # ==========================================
        # PASO 2: ÁREA SUPERFICIAL
        # ==========================================
        As = Q_unit_m3d / CS
        
        self.calculos_detallados.append("--- 2. ÁREA SUPERFICIAL (As) ---")
        self.calculos_detallados.append(f"   Fórmula: As = Q / CS")
        self.calculos_detallados.append(f"   Sustitución: {Q_unit_m3d:.2f} / {CS}")
        self.calculos_detallados.append(f"   Resultado: {As:.2f} m²")
        self.calculos_detallados.append("")
        
        # ==========================================
        # PASO 3 y 4: DIMENSIONES (Relación 3:1)
        # ==========================================
        B = math.sqrt(As / 3)
        L = B * 3
        
        # Redondeo constructivo
        B = round(B, 2)
        L = round(L, 2)
        As_real = B * L
        
        self.calculos_detallados.append("--- 3. ANCHO (B) - Relación 1:3 ---")
        self.calculos_detallados.append(f"   Fórmula: B = √(As / 3)")
        self.calculos_detallados.append(f"   Sustitución: √({As:.2f} / 3)")
        self.calculos_detallados.append(f"   Resultado: {B} m")
        self.calculos_detallados.append("")
        
        self.calculos_detallados.append("--- 4. LARGO (L) - Relación 3:1 ---")
        self.calculos_detallados.append(f"   Fórmula: L = 3 × B")
        self.calculos_detallados.append(f"   Sustitución: 3 × {B}")
        self.calculos_detallados.append(f"   Resultado: {L} m")
        self.calculos_detallados.append("")
        
        # ==========================================
        # PASO 5: TIEMPO DE RETENCIÓN
        # ==========================================
        Volumen = As_real * H
        t_horas = (Volumen / Q_unit_m3d) * 24
        
        self.calculos_detallados.append("--- 5. TIEMPO DE RETENCIÓN (t) ---")
        self.calculos_detallados.append(f"   Fórmula: t = (Volumen / Q) × 24")
        self.calculos_detallados.append(f"   Sustitución: ({As_real:.1f} × {H}) / {Q_unit_m3d:.1f} × 24")
        self.calculos_detallados.append(f"   Resultado: {t_horas:.2f} horas")
        self.calculos_detallados.append("")
        
        # ==========================================
        # PASO 6: VELOCIDAD HORIZONTAL
        # ==========================================
        At = B * H
        Vh_ms = Q_unit_m3s / At
        Vh_cms = Vh_ms * 100
        
        self.calculos_detallados.append("--- 6. VELOCIDAD HORIZONTAL (Vh) ---")
        self.calculos_detallados.append(f"   Fórmula: Vh = Q / (B × H)")
        self.calculos_detallados.append(f"   Sustitución: {Q_unit_m3s:.4f} / ({B} × {H})")
        self.calculos_detallados.append(f"   Resultado: {Vh_cms:.2f} cm/s")
        self.calculos_detallados.append("")
        
        # ==========================================
        # PASO 7: CARGA SOBRE VERTEDERO
        # ==========================================
        self.calculos_detallados.append("--- 7. DISEÑO DE VERTEDEROS DE SALIDA ---")
        
        # Longitud requerida para carga < 5 L/s-m
        L_vert_requerida = Q_unit_ls / 5.0
        L_lat_sugerida = (L_vert_requerida - B) / 2
        
        if L_lat_sugerida < 0:
            L_lat_sugerida = 0
        
        self.calculos_detallados.append(f"   Longitud requerida para Cv < 5 L/s-m: {L_vert_requerida:.2f} m")
        self.calculos_detallados.append(f"   Longitud sugerida brazos laterales: {max(1.0, round(L_lat_sugerida, 1))} m")
        
        # Usamos la sugerida automáticamente
        L_lat = max(1.0, round(L_lat_sugerida, 1))
        L_total = B + (2 * L_lat)
        Cv = Q_unit_ls / L_total
        
        self.calculos_detallados.append(f"   Longitud adoptada brazos: {L_lat} m")
        self.calculos_detallados.append(f"   Longitud total vertedero: {L_total} m")
        self.calculos_detallados.append(f"   Carga sobre vertedero: {Cv:.2f} L/s·m")
        self.calculos_detallados.append("")
        
        # ==========================================
        # PASO 8: DISEÑO DE CANALETAS
        # ==========================================
        self.calculos_detallados.append("--- 8. DISEÑO HIDRÁULICO DE CANALETAS ---")
        
        # Caudal por tramo
        Q_lat = Q_unit_m3s * (L_lat / L_total)
        Q_front = Q_unit_m3s * (B / L_total)
        
        # Alturas de lámina de agua
        h_lat = (Q_lat / (1.375 * b_lat)) ** (2/3)
        h_front = (Q_front / (1.375 * b_front)) ** (2/3)
        
        self.calculos_detallados.append(f"   Caudal canaleta lateral: {Q_lat:.4f} m³/s")
        self.calculos_detallados.append(f"   Caudal canaleta frontal: {Q_front:.4f} m³/s")
        self.calculos_detallados.append(f"   Altura lámina lateral: {h_lat:.3f} m")
        self.calculos_detallados.append(f"   Altura lámina frontal: {h_front:.3f} m")
        self.calculos_detallados.append("")
        
        # Almacenar resultados
        self.resultados = {
            'caudal_unitario_m3d': Q_unit_m3d,
            'caudal_unitario_ls': Q_unit_ls,
            'area_superficial': As_real,
            'ancho': B,
            'largo': L,
            'volumen': Volumen,
            'tiempo_retencion': t_horas,
            'velocidad_horizontal': Vh_cms,
            'longitud_vertedero_total': L_total,
            'carga_vertedero': Cv,
            'altura_laminas': {
                'lateral': h_lat,
                'frontal': h_front
            },
            'caudales_canaletas': {
                'lateral': Q_lat,
                'frontal': Q_front
            }
        }
        
        # Verificaciones
        self.verificaciones = {
            'Velocidad horizontal < 1.5 cm/s': Vh_cms < 1.5,
            'Tiempo retención 2-4 horas': 2 <= t_horas <= 4,
            'Carga vertedero < 5 L/s·m': Cv < 5,
            'Relación L/B = 3:1': abs(L/B - 3) < 0.1
        }
        
        return True
    
    def generar_grafica(self):
        if not self.resultados:
            return None
            
        L = self.resultados['largo']
        B = self.resultados['ancho']
        H = self.parametros['profundidad_tanque']
        b_lat = self.parametros['ancho_canaleta_lateral']
        b_front = self.parametros['ancho_canaleta_frontal']
        
        # Calcular longitud de brazos para el gráfico
        L_vert_requerida = self.resultados['caudal_unitario_ls'] / 5.0
        L_lat = max(1.0, round((L_vert_requerida - B) / 2, 1))
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # ================= VISTA EN PLANTA =================
        ax.set_title('VISTA EN PLANTA - SEDIMENTADOR CONVENCIONAL', 
                   fontsize=14, fontweight='bold', pad=20)
        
        # Tanque principal
        tanque = patches.Rectangle((0, 0), L, B, linewidth=3, 
                                 edgecolor='#37474F', facecolor='#E1F5FE',
                                 label='Zona de Sedimentación')
        ax.add_patch(tanque)
        
        # Canaletas
        # Canaleta frontal
        canaleta_frontal = patches.Rectangle((L - b_front, 0), b_front, B, 
                                           facecolor='#0277BD', alpha=0.7,
                                           label='Canaleta Frontal')
        ax.add_patch(canaleta_frontal)
        
        # Canaletas laterales
        canaleta_lat1 = patches.Rectangle((L - L_lat, B - b_lat), L_lat, b_lat, 
                                        facecolor='#0288D1', alpha=0.7,
                                        label='Canaleta Lateral')
        ax.add_patch(canaleta_lat1)
        
        canaleta_lat2 = patches.Rectangle((L - L_lat, 0), L_lat, b_lat, 
                                        facecolor='#0288D1', alpha=0.7)
        ax.add_patch(canaleta_lat2)
        
        # Texto informativo
        info_texto = (
            f"RESULTADOS PRINCIPALES:\n"
            f"Dimensiones: {L} × {B} × {H} m\n"
            f"Caudal: {self.resultados['caudal_unitario_ls']:.1f} L/s\n"
            f"Tiempo retención: {self.resultados['tiempo_retencion']:.2f} h\n"
            f"Velocidad: {self.resultados['velocidad_horizontal']:.2f} cm/s\n"
            f"Carga vertedero: {self.resultados['carga_vertedero']:.2f} L/s·m"
        )
        
        plt.text(L * 0.05, B * 0.7, info_texto, fontsize=10, 
                bbox=dict(facecolor='white', alpha=0.9, boxstyle='round'),
                fontweight='bold')
        
        # Cotas
        # Cota largo
        ax.annotate('', xy=(0, -1), xytext=(L, -1),
                  arrowprops=dict(arrowstyle='<->', color='black', lw=2))
        ax.text(L/2, -2, f'L = {L} m', ha='center', fontweight='bold', fontsize=12)
        
        # Cota ancho
        ax.annotate('', xy=(-1, 0), xytext=(-1, B),
                  arrowprops=dict(arrowstyle='<->', color='black', lw=2))
        ax.text(-3, B/2, f'B = {B} m', va='center', rotation=90, 
               fontweight='bold', fontsize=12)
        
        # Cota brazos laterales
        ax.text(L - L_lat/2, B/2, f"Vertedero Lateral\n{L_lat} m", 
               ha='center', va='center', color='white', fontweight='bold',
               bbox=dict(facecolor='black', alpha=0.7))
        
        # Configuración del gráfico
        ax.set_xlim(-5, L + 2)
        ax.set_ylim(-3, B + 2)
        ax.set_aspect('equal')
        ax.set_xlabel("Longitud (m)", fontweight='bold')
        ax.set_ylabel("Ancho (m)", fontweight='bold')
        ax.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
        ax.grid(True, linestyle='--', alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def generar_reporte_pdf(self):
        pdf = FPDF()
        pdf.add_page()
        
        # Encabezado
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, 'DISEÑO SEDIMENTADOR CONVENCIONAL', 0, 1, 'C')
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, f'Fecha: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
        pdf.ln(5)
        
        # Datos de entrada
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(0, 10, 'DATOS DE ENTRADA', 1, 1, 'L', 1)
        pdf.set_font("Arial", '', 10)
        p = self.parametros
        pdf.cell(0, 6, f'Caudal total: {p["caudal_total"]} m³/d', 0, 1)
        pdf.cell(0, 6, f'Número de sedimentadores: {p["numero_sedimentadores"]}', 0, 1)
        pdf.cell(0, 6, f'Carga superficial: {p["carga_superficial"]} m/d', 0, 1)
        pdf.cell(0, 6, f'Profundidad tanque: {p["profundidad_tanque"]} m', 0, 1)
        pdf.cell(0, 6, f'Ancho canaleta lateral: {p["ancho_canaleta_lateral"]} m', 0, 1)
        pdf.cell(0, 6, f'Ancho canaleta frontal: {p["ancho_canaleta_frontal"]} m', 0, 1)
        pdf.ln(5)
        
        # Cálculos detallados
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(0, 10, 'CÁLCULOS DETALLADOS', 1, 1, 'L', 1)
        pdf.set_font("Courier", '', 8)
        
        for linea in self.calculos_detallados:
            # Limpiar texto para PDF
            txt = linea.replace('×', 'x').replace('³', '3').replace('²', '2')
            if len(txt) > 100:
                # Dividir líneas muy largas
                partes = [txt[i:i+80] for i in range(0, len(txt), 80)]
                for parte in partes:
                    pdf.multi_cell(0, 4, parte)
            else:
                pdf.multi_cell(0, 4, txt)
        
        # Resultados
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(0, 10, 'RESULTADOS FINALES', 1, 1, 'L', 1)
        pdf.set_font("Arial", '', 10)
        
        r = self.resultados
        pdf.cell(0, 6, f'Dimensiones: {r["largo"]}m × {r["ancho"]}m × {self.parametros["profundidad_tanque"]}m', 0, 1)
        pdf.cell(0, 6, f'Caudal por unidad: {r["caudal_unitario_ls"]:.1f} L/s', 0, 1)
        pdf.cell(0, 6, f'Tiempo retención: {r["tiempo_retencion"]:.2f} horas', 0, 1)
        pdf.cell(0, 6, f'Velocidad horizontal: {r["velocidad_horizontal"]:.2f} cm/s', 0, 1)
        pdf.cell(0, 6, f'Carga vertedero: {r["carga_vertedero"]:.2f} L/s·m', 0, 1)
        pdf.cell(0, 6, f'Altura lámina lateral: {r["altura_laminas"]["lateral"]:.3f} m', 0, 1)
        pdf.cell(0, 6, f'Altura lámina frontal: {r["altura_laminas"]["frontal"]:.3f} m', 0, 1)
        
        # Guardar PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf.output(tmp_file.name)
            return tmp_file.name

# ==========================================
# INTERFAZ PRINCIPAL
# ==========================================
def main():
    st.title("🏭 Diseño de Sedimentador Convencional")
    st.markdown("### Dimensionamiento Automático con Relación 3:1")
    
    if 'sedimentador_conv' not in st.session_state:
        st.session_state.sedimentador_conv = SedimentadorConvencional()
    
    # --- SIDEBAR ---
    st.sidebar.header("📋 Parámetros de Diseño")
    
    with st.sidebar.form("form_diseno_conv"):
        st.subheader("Datos Hidráulicos")
        
        caudal_total = st.number_input(
            "Caudal total de planta (m³/d)",
            min_value=1000.0,
            max_value=200000.0,
            value=60000.0,
            step=1000.0
        )
        
        numero_sedimentadores = st.number_input(
            "Número de sedimentadores",
            min_value=1,
            max_value=10,
            value=4,
            step=1
        )
        
        carga_superficial = st.number_input(
            "Carga superficial (m/d)",
            min_value=10.0,
            max_value=50.0,
            value=20.0,
            step=1.0
        )
        
        profundidad_tanque = st.number_input(
            "Profundidad del tanque (m)",
            min_value=2.0,
            max_value=6.0,
            value=3.5,
            step=0.5
        )
        
        st.subheader("Diseño de Canaletas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            ancho_canaleta_lateral = st.number_input(
                "Ancho canaleta lateral (m)",
                min_value=0.2,
                max_value=0.5,
                value=0.3,
                step=0.05
            )
        
        with col2:
            ancho_canaleta_frontal = st.number_input(
                "Ancho canaleta frontal (m)",
                min_value=0.2,
                max_value=0.5,
                value=0.35,
                step=0.05
            )
        
        # Botón de cálculo
        if st.form_submit_button("🚀 Calcular Diseño"):
            parametros = {
                'caudal_total': caudal_total,
                'numero_sedimentadores': numero_sedimentadores,
                'carga_superficial': carga_superficial,
                'profundidad_tanque': profundidad_tanque,
                'ancho_canaleta_lateral': ancho_canaleta_lateral,
                'ancho_canaleta_frontal': ancho_canaleta_frontal
            }
            st.session_state.sedimentador_conv.calcular(parametros)
            st.rerun()
    
    # --- EJEMPLO ORIGINAL ---
    with st.sidebar.expander("🎯 Ejemplo Original"):
        if st.button("Cargar Valores Originales"):
            st.session_state.sedimentador_conv.calcular({
                'caudal_total': 60000.0,
                'numero_sedimentadores': 4,
                'carga_superficial': 20.0,
                'profundidad_tanque': 3.5,
                'ancho_canaleta_lateral': 0.3,
                'ancho_canaleta_frontal': 0.35
            })
            st.rerun()
    
    # --- RESULTADOS PRINCIPALES ---
    sedimentador = st.session_state.sedimentador_conv
    
    if sedimentador.resultados:
        st.success("✅ Diseño del sedimentador completado")
        
        # Mostrar configuración
        st.info(f"""
        **Configuración analizada:**
        - Caudal total: {sedimentador.parametros['caudal_total']} m³/d
        - Número de unidades: {sedimentador.parametros['numero_sedimentadores']}
        - Carga superficial: {sedimentador.parametros['carga_superficial']} m/d
        - Profundidad: {sedimentador.parametros['profundidad_tanque']} m
        """)
        
        # Mostrar en pestañas
        tab1, tab2, tab3 = st.tabs(["📊 Resultados", "🧮 Cálculos", "📥 Reporte"])
        
        with tab1:
            st.subheader("Resultados del Diseño")
            
            # Métricas principales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Dimensiones", f"{sedimentador.resultados['largo']}×{sedimentador.resultados['ancho']}m")
            
            with col2:
                st.metric("Caudal/unidad", f"{sedimentador.resultados['caudal_unitario_ls']:.1f} L/s")
            
            with col3:
                st.metric("Tiempo retención", f"{sedimentador.resultados['tiempo_retencion']:.2f} h")
            
            with col4:
                st.metric("Velocidad", f"{sedimentador.resultados['velocidad_horizontal']:.2f} cm/s")
            
            # Gráfico
            st.pyplot(sedimentador.generar_grafica())
            
            # Verificaciones
            st.subheader("✅ Verificaciones de Diseño")
            cols = st.columns(2)
            idx = 0
            for criterio, cumple in sedimentador.verificaciones.items():
                if cumple:
                    cols[idx % 2].success(f"✓ {criterio}")
                else:
                    cols[idx % 2].error(f"✗ {criterio}")
                idx += 1
            
            # Tabla de resultados detallados
            st.subheader("📋 Especificaciones Técnicas")
            
            datos_especificaciones = {
                'Parámetro': [
                    'Volumen por unidad',
                    'Área superficial', 
                    'Longitud total vertedero',
                    'Carga sobre vertedero',
                    'Altura lámina lateral',
                    'Altura lámina frontal',
                    'Relación L/B actual'
                ],
                'Valor': [
                    f"{sedimentador.resultados['volumen']:.0f} m³",
                    f"{sedimentador.resultados['area_superficial']:.0f} m²",
                    f"{sedimentador.resultados['longitud_vertedero_total']:.1f} m",
                    f"{sedimentador.resultados['carga_vertedero']:.2f} L/s·m",
                    f"{sedimentador.resultados['altura_laminas']['lateral']:.3f} m",
                    f"{sedimentador.resultados['altura_laminas']['frontal']:.3f} m",
                    f"{sedimentador.resultados['largo']/sedimentador.resultados['ancho']:.2f}:1"
                ],
                'Observación': [
                    'Volumen útil de sedimentación',
                    'Área para carga superficial',
                    'Longitud total de vertederos',
                    'Carga hidráulica en vertedero',
                    'Altura en canaletas laterales',
                    'Altura en canaleta frontal',
                    'Relación longitud/ancho'
                ]
            }
            
            df_especificaciones = pd.DataFrame(datos_especificaciones)
            st.dataframe(df_especificaciones, use_container_width=True)
        
        with tab2:
            st.subheader("🧮 Cálculos Detallados Paso a Paso")
            st.code("\n".join(sedimentador.calculos_detallados), language="text")
        
        with tab3:
            st.subheader("📥 Generar Reporte PDF")
            
            if st.button("🖨️ Generar Reporte Completo"):
                with st.spinner("Generando reporte PDF..."):
                    try:
                        pdf_file = sedimentador.generar_reporte_pdf()
                        with open(pdf_file, "rb") as f:
                            st.download_button(
                                label="📥 Descargar Reporte PDF",
                                data=f,
                                file_name=f"sedimentador_convencional_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                mime="application/pdf"
                            )
                        os.unlink(pdf_file)
                    except Exception as e:
                        st.error(f"Error al generar PDF: {str(e)}")
    
    else:
        # Pantalla inicial
        st.info("""
        ## 🏭 Diseño de Sedimentador Convencional
        
        **Características del sistema:**
        - Diseño automático con relación longitud/ancho 3:1
        - Cálculo completo de dimensiones
        - Diseño de sistema de vertederos
        - Dimensionamiento de canaletas de salida
        - Verificaciones hidráulicas automáticas
        
        **Parámetros del ejemplo original:**
        - Caudal total: 60,000 m³/d
        - Número de sedimentadores: 4 unidades
        - Carga superficial: 20 m/d
        - Profundidad: 3.5 m
        - Relación L/B: 3:1 (automática)
        
        **Criterios de diseño verificados:**
        - Velocidad horizontal < 1.5 cm/s
        - Tiempo de retención 2-4 horas
        - Carga sobre vertedero < 5 L/s·m
        - Relación L/B = 3:1
        
        **🎯 Resultado esperado:** Diseño completo de sedimentador convencional con todas las especificaciones técnicas.
        """)

if __name__ == "__main__":
    main()
import streamlit as st
import math
import numpy as np
import pandas as pd  # <--- NUEVA IMPORTACIÓN NECESARIA
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
    page_title="Diseño Sedimentador Alta Tasa",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CLASE PRINCIPAL DE LÓGICA Y REPORTE
# ==========================================
class SedimentadorAltaTasa:
    def __init__(self):
        self.parametros = {}
        self.calculos = {}
        self.verificaciones = {}
        self.procedimientos = []
        self.grafica_path = None
    
    def calcular(self, parametros):
        """
        Realiza todos los cálculos hidráulicos y genera el texto del procedimiento
        paso a paso para el reporte.
        """
        self.parametros = parametros
        self.procedimientos = [] # Reiniciar procedimientos
        
        # --- 1. EXTRACCIÓN DE VARIABLES ---
        Q_ls = parametros['caudal_ls']
        Lx = parametros['lado_x']
        Ly = parametros['lado_y']
        e = parametros['espesor']
        d = parametros['separacion']
        theta_grados = parametros['angulo_grados']
        B = parametros['ancho_sedimentacion']
        nu = parametros['viscosidad']
        CS = parametros['carga_superficial']
        
        # Constantes
        espacio_paneles = 1.6
        g = 9.81
        theta_rad = math.radians(theta_grados)
        
        # --- INICIO DE PROCEDIMIENTOS ---
        self.procedimientos.append("MEMORIA DE CÁLCULO DETALLADA")
        self.procedimientos.append("-" * 80)

        # 1. Conversión de Caudal
        Q_m3s = Q_ls / 1000
        Q_m3d = Q_ls * 86.4
        
        self.procedimientos.append("1. CONVERSIÓN DE CAUDAL")
        self.procedimientos.append(f"   Q = {Q_ls} L/s / 1000 = {Q_m3s:.5f} m3/s")
        self.procedimientos.append(f"   Q = {Q_ls} L/s * 86.4 = {Q_m3d:.2f} m3/d")
        self.procedimientos.append("")

        # 2. Área Superficial (As)
        # As = Q / CS
        As = Q_m3d / CS
        
        self.procedimientos.append("2. CÁLCULO DEL ÁREA SUPERFICIAL (As)")
        self.procedimientos.append("   Fórmula: As = Q(m3/d) / Carga Superficial")
        self.procedimientos.append(f"   As = {Q_m3d:.2f} / {CS} = {As:.2f} m2")
        self.procedimientos.append("")
        
        # 3. Longitud del Sedimentador (Ls)
        # Ls = As / B
        Ls = As / B
        
        self.procedimientos.append("3. LONGITUD DEL SEDIMENTADOR (Ls)")
        self.procedimientos.append("   Fórmula: Ls = As / B")
        self.procedimientos.append(f"   Ls = {As:.2f} / {B} = {Ls:.2f} m")
        self.procedimientos.append("")

        # 4. Velocidad de flujo entre placas (Vo)
        # Vo = Q / (As * sin(theta))
        sen_theta = math.sin(theta_rad)
        Vo_ms = Q_m3s / (As * sen_theta)
        Vo_cms = Vo_ms * 100
        
        self.procedimientos.append("4. VELOCIDAD ENTRE PLACAS (Vo)")
        self.procedimientos.append("   Fórmula: Vo = Q / (As * sen(theta))")
        self.procedimientos.append(f"   sen({theta_grados}) = {sen_theta:.4f}")
        self.procedimientos.append(f"   Vo = {Q_m3s:.5f} / ({As:.2f} * {sen_theta:.4f})")
        self.procedimientos.append(f"   Vo = {Vo_ms:.5f} m/s = {Vo_cms:.3f} cm/s")
        self.procedimientos.append("")

        # 5. Número de Reynolds (Re)
        # Re = (Vo * d) / nu
        Re = (Vo_ms * d) / nu
        
        self.procedimientos.append("5. NÚMERO DE REYNOLDS (NRe)")
        self.procedimientos.append("   Fórmula: Re = (Vo * d) / viscosidad")
        self.procedimientos.append(f"   Re = ({Vo_ms:.5f} * {d}) / {nu:.2e}")
        self.procedimientos.append(f"   Re = {Re:.2f}")
        self.procedimientos.append("")

        # 6. Longitud Relativa y Corregida (L y L')
        L_rel = Ly / d
        L_prima = Re * 0.013
        
        self.procedimientos.append("6. LONGITUD RELATIVA (L) Y DESARROLLO (L')")
        self.procedimientos.append(f"   L = Ly / d = {Ly} / {d} = {L_rel:.2f}")
        self.procedimientos.append(f"   L' = Re * 0.013 = {Re:.2f} * 0.013 = {L_prima:.3f} m")
        
        # Longitud Crítica Lc
        if L_prima > Ly / 2:
            Lc = 2 * (Ly - L_prima)
            condicion_lc = "Como L' > Ly/2"
        else:
            Lc = Ly - L_prima
            condicion_lc = "Como L' <= Ly/2"
            
        self.procedimientos.append(f"   {condicion_lc}, Lc = {Lc:.3f} m")
        self.procedimientos.append("")

        # 7. Velocidad Crítica de Sedimentación (Vs)
        cos_theta = math.cos(theta_rad)
        denominador_vs = sen_theta + (Lc * cos_theta)
        Vs_ms = Vo_ms / denominador_vs
        Vs_mdia = Vs_ms * 86400
        
        self.procedimientos.append("7. VELOCIDAD CRÍTICA (Vs)")
        self.procedimientos.append("   Fórmula: Vs = Vo / (sen(theta) + Lc * cos(theta))")
        self.procedimientos.append(f"   Vs = {Vo_ms:.5f} / ({sen_theta:.4f} + {Lc:.3f}*{cos_theta:.4f})")
        self.procedimientos.append(f"   Vs = {Vs_ms:.6f} m/s = {Vs_mdia:.2f} m/d")
        self.procedimientos.append("")

        # 8. Número de Placas (N)
        # N = (Ls * sen(theta) + d) / (d + e)
        num_placas_exacto = (Ls * sen_theta + d) / (d + e)
        N_placas = int(num_placas_exacto)
        
        self.procedimientos.append("8. NÚMERO DE PLACAS (N)")
        self.procedimientos.append("   Fórmula: N = (Ls * sen(theta) + d) / (d + e)")
        self.procedimientos.append(f"   N = ({Ls:.2f} * {sen_theta:.4f} + {d}) / ({d} + {e})")
        self.procedimientos.append(f"   N = {num_placas_exacto:.2f} -> Se adoptan {N_placas} placas")
        self.procedimientos.append("")

        # 9. Geometría del Tanque y Tiempos
        ht = (Ly * sen_theta) + 1.96 # 1.96m zona lodos/borde libre
        Vol = As * ht
        Tret_min = (Vol / Q_m3s) / 60
        Tce_seg = 1 / Vo_ms
        
        self.procedimientos.append("9. GEOMETRÍA FINAL Y TIEMPOS")
        self.procedimientos.append(f"   Altura Total (ht) = (Ly * sen(theta)) + 1.96 = {ht:.2f} m")
        self.procedimientos.append(f"   Volumen (Vol) = As * ht = {As:.2f} * {ht:.2f} = {Vol:.2f} m3")
        self.procedimientos.append(f"   Tiempo Retención (Tret) = Vol/Q = {Tret_min:.2f} min")
        self.procedimientos.append(f"   Tiempo en Celdas (Tce) = 1/Vo = {Tce_seg:.2f} s")
        self.procedimientos.append("")

        # 10. Hidráulica del Tanque (Reynolds y Froude)
        Ax = B * ht
        Vf = Q_m3s / Ax
        Pm = B + 2*ht
        RH = Ax / Pm
        
        Re_tanque = (Vf * RH) / nu
        Fr = (Vf**2) / (g * RH)
        
        self.procedimientos.append("10. HIDRÁULICA DEL TANQUE")
        self.procedimientos.append(f"   Área Transversal (Ax) = {Ax:.2f} m2")
        self.procedimientos.append(f"   Radio Hidráulico (RH) = Ax/Pm = {RH:.4f} m")
        self.procedimientos.append(f"   Velocidad Horizontal (Vf) = {Vf:.5f} m/s")
        self.procedimientos.append(f"   Reynolds Tanque = (Vf * RH)/nu = {Re_tanque:.0f}")
        self.procedimientos.append(f"   Froude = Vf^2 / (g * RH) = {Fr:.6f}")

        # Guardar resultados en diccionario
        self.calculos = {
            'As': As, 'Ls': Ls, 'Vo_cms': Vo_cms, 'Re': Re,
            'Lc': Lc, 'Vs_mdia': Vs_mdia, 'N_placas': N_placas,
            'ht': ht, 'Vol': Vol, 'Tret_min': Tret_min, 'Tce_seg': Tce_seg,
            'Re_tanque': Re_tanque, 'Fr': Fr, 'espacio_paneles': espacio_paneles
        }
        
        # Verificaciones booleanas
        self.verificaciones = {
            'Vo < 1 cm/s': Vo_cms < 1.0,
            'Re < 500': Re < 500,
            '15 < Tret < 25': 15 <= Tret_min <= 25, # Rango ampliado usual
            'Re_tanque < 20000': Re_tanque < 20000,
            'Fr > 1e-5': Fr > 1e-5
        }
        
        return True

    def generar_grafica(self):
        """Genera gráficos detallados con énfasis en el número de placas"""
        ancho = self.parametros['ancho_sedimentacion']
        longitud = self.calculos['Ls']
        espacio = self.calculos['espacio_paneles']
        ht = self.calculos['ht']
        theta = self.parametros['angulo_grados']
        Ly = self.parametros['lado_y']
        N_placas = self.calculos['N_placas']
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        
        # --- VISTA SUPERIOR ---
        ax1.set_xlim(0, longitud + espacio + 1)
        ax1.set_ylim(0, ancho + 1)
        ax1.set_title('VISTA PLANTA', fontweight='bold')
        ax1.set_xlabel('Longitud (m)')
        ax1.set_ylabel('Ancho (m)')
        
        # Zonas
        rect_entrada = patches.Rectangle((0,0), espacio, ancho, facecolor='#ff9999', alpha=0.3, label='Entrada')
        rect_placas = patches.Rectangle((espacio,0), longitud, ancho, facecolor='#99ccff', alpha=0.3, label='Zona Placas')
        ax1.add_patch(rect_entrada)
        ax1.add_patch(rect_placas)
        
        # Texto destacado de placas
        ax1.text(espacio + longitud/2, ancho/2, 
                 f"ZONA DE SEDIMENTACIÓN\nL = {longitud:.2f} m\n\nN = {N_placas} PLACAS", 
                 ha='center', va='center', fontweight='bold', fontsize=11,
                 bbox=dict(boxstyle="round,pad=0.5", fc="white", ec="blue", alpha=0.8))
        
        ax1.text(espacio/2, ancho/2, "Zona de\nEntrada", ha='center', va='center')
        ax1.grid(True, linestyle='--', alpha=0.3)

        # --- VISTA PERFIL ---
        ax2.set_xlim(0, longitud + espacio + 1)
        ax2.set_ylim(0, ht + 1)
        ax2.set_title('VISTA PERFIL (CORTE)', fontweight='bold')
        ax2.set_xlabel('Longitud (m)')
        ax2.set_ylabel('Altura (m)')
        
        # Tanque
        tanque = patches.Rectangle((espacio, 0), longitud, ht, facecolor='#f0f0f0', edgecolor='black')
        ax2.add_patch(tanque)
        
        # Dibujar representación de placas
        theta_rad = math.radians(theta)
        dx = Ly * math.cos(theta_rad)
        dy = Ly * math.sin(theta_rad)
        base_h = 1.96
        
        # Dibujamos lineas representativas (no las 1000 placas, sino un patrón visual)
        step = longitud / 15 # Dibujar aprox 15 placas visuales
        for i in np.arange(0, longitud, step):
            x_start = espacio + i
            if x_start + dx < espacio + longitud:
                ax2.plot([x_start, x_start + dx], [base_h, base_h + dy], 'b-', alpha=0.6)
        
        # Acotaciones y etiquetas
        ax2.axhline(y=base_h, color='r', linestyle=':', label='Nivel Lodos')
        ax2.text(espacio + longitud + 0.2, ht/2, f"Ht={ht:.2f}m", color='black', fontweight='bold')
        
        # Etiqueta flotante con el número de placas también aquí
        ax2.text(espacio + longitud/2, base_h + dy + 0.5, 
                 f"Detalle: {N_placas} Placas a {theta}°", 
                 ha='center', va='bottom', color='blue', fontweight='bold', fontsize=10)

        ax2.legend(loc='upper right')
        ax2.grid(True, linestyle='--', alpha=0.3)
        
        plt.tight_layout()
        
        # Guardar imagen temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            fig.savefig(tmp_file.name, dpi=150)
            self.grafica_path = tmp_file.name
            
        return fig

    def generar_reporte_pdf(self):
        """Genera el PDF incluyendo el procedimiento paso a paso"""
        pdf = FPDF()
        pdf.add_page()
        
        # Encabezado
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, 'REPORTE DE DISEÑO: SEDIMENTADOR ALTA TASA', 0, 1, 'C')
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, f'Fecha: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
        pdf.ln(5)
        
        # 1. Datos de Entrada
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 10, '1. DATOS DE ENTRADA', 1, 1, 'L', 1)
        pdf.set_font("Arial", '', 10)
        
        p = self.parametros
        texto_datos = (f"Caudal: {p['caudal_ls']} L/s | Ancho B: {p['ancho_sedimentacion']} m | "
                       f"Carga Superficial: {p['carga_superficial']} m/d\n"
                       f"Placa Lx: {p['lado_x']} m | Placa Ly: {p['lado_y']} m | "
                       f"Angulo: {p['angulo_grados']} deg | Espesor: {p['espesor']} m")
        pdf.multi_cell(0, 6, texto_datos)
        pdf.ln(5)
        
        # 2. Procedimiento de Cálculo (El núcleo de tu solicitud)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, '2. MEMORIA DE CÁLCULO DETALLADA', 1, 1, 'L', 1)
        pdf.set_font("Courier", '', 9) # Fuente monoespaciada para alineación tipo código
        
        for linea in self.procedimientos:
            # Codificación latin-1 para manejar tildes básicas si ocurren
            try:
                txt = linea.encode('latin-1', 'replace').decode('latin-1')
            except:
                txt = linea
            pdf.multi_cell(0, 5, txt)
        
        pdf.ln(5)
        
        # 3. Resumen de Verificaciones
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, '3. VERIFICACIÓN DE CRITERIOS', 1, 1, 'L', 1)
        pdf.set_font("Arial", '', 10)
        
        for crit, cumple in self.verificaciones.items():
            estado = "CUMPLE" if cumple else "NO CUMPLE"
            col = (0, 128, 0) if cumple else (200, 0, 0)
            pdf.set_text_color(*col)
            pdf.cell(0, 6, f" criterio [{crit}]: {estado}", 0, 1)
        
        pdf.set_text_color(0, 0, 0)
        
        # 4. Gráficos
        if self.grafica_path and os.path.exists(self.grafica_path):
            pdf.add_page()
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, '4. ANEXO GRÁFICO', 0, 1, 'L')
            pdf.image(self.grafica_path, x=10, y=30, w=190)
            
        # Guardar PDF temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf.output(tmp_file.name)
            return tmp_file.name

# ==========================================
# INTERFAZ DE USUARIO (MAIN)
# ==========================================
def main():
    st.title("💧 Diseño de Sedimentador de Alta Tasa")
    st.markdown("Generación de reportes detallados con procedimiento paso a paso.")
    
    # Inicializar estado
    if 'app' not in st.session_state:
        st.session_state.app = SedimentadorAltaTasa()
    
    # --- SIDEBAR INPUTS ---
    st.sidebar.header("Parámetros de Diseño")
    
    # ---- NUEVA SECCIÓN: TABLA DE REFERENCIA NORMATIVA ----
    with st.sidebar.expander("📘 Consultar Parámetros de Diseño (Normativa RAS)", expanded=False):
        st.markdown("Rango de valores típicos recomendados:")
        datos_norma = {
            "Parámetro": [
                "Carga Superficial (CS)", 
                "Tiempo Retención (TR)", 
                "Reynolds (Re) Placas", 
                "Ángulo Inclinación",
                "Velocidad de paso (Vo)"
            ],
            "Unidad": ["m³/m²/d", "minutos", "Adim.", "Grados", "cm/s"],
            "Rango Recomendado": ["120 - 185", "15 - 25", "< 500", "≥ 60°", "< 1.0"]
        }
        df_norma = pd.DataFrame(datos_norma)
        st.table(df_norma)
    # -----------------------------------------------------

    with st.sidebar.form("form_diseno"):
        col_sb1, col_sb2 = st.columns(2)
        with col_sb1:
            q_ls = st.number_input("Caudal (L/s)", 10.0, 500.0, 45.0)
            lx = st.number_input("Lado X Placa (m)", 0.5, 3.0, 1.2)
            ly = st.number_input("Lado Y Placa (m)", 0.5, 3.0, 1.2)
        with col_sb2:
            theta = st.slider("Ángulo (°)", 45, 70, 60)
            d = st.number_input("Separación (m)", 0.04, 0.1, 0.06)
            e = st.number_input("Espesor (m)", 0.001, 0.05, 0.01)
            
        st.sidebar.markdown("---")
        b = st.number_input("Ancho Tanque (m)", 1.0, 10.0, 2.5)
        cs = st.number_input("Carga Superficial (m/d)", 80.0, 300.0, 120.0, help="Valor típico RAS: 120-185 m/d")
        nu = st.number_input("Viscosidad (m2/s)", format="%.2e", value=1.00e-6)
        
        calcular_btn = st.form_submit_button("🚀 Calcular y Diseñar")
        
    if calcular_btn:
        params = {
            'caudal_ls': q_ls, 'lado_x': lx, 'lado_y': ly,
            'angulo_grados': theta, 'separacion': d, 'espesor': e,
            'ancho_sedimentacion': b, 'carga_superficial': cs, 'viscosidad': nu
        }
        
        app = st.session_state.app
        app.calcular(params)
        
        # --- PESTAÑAS DE RESULTADOS ---
        tab1, tab2, tab3 = st.tabs(["📊 Resultados y Gráficos", "📝 Procedimiento Detallado", "📄 Descargar Reporte"])
        
        with tab1:
            # Métricas Clave
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Número de Placas", app.calculos['N_placas'])
            c2.metric("Longitud (Ls)", f"{app.calculos['Ls']:.2f} m")
            c3.metric("Reynolds", f"{app.calculos['Re']:.0f}")
            c4.metric("Froude", f"{app.calculos['Fr']:.1e}")
            
            # Gráfico
            fig = app.generar_grafica()
            st.pyplot(fig)
            
            # Tabla resumen de cumplimiento
            st.subheader("Verificación Normativa")
            col_check = st.columns(3)
            idx = 0
            for k, v in app.verificaciones.items():
                with col_check[idx % 3]:
                    if v:
                        st.success(f"✅ {k}")
                    else:
                        st.error(f"❌ {k}")
                idx += 1

        with tab2:
            st.markdown("### Memoria de Cálculo Generada")
            st.text("Este texto exacto aparecerá en el PDF:")
            texto_completo = "\n".join(app.procedimientos)
            st.code(texto_completo, language="text")
            
        with tab3:
            st.success("¡Cálculo finalizado! Descarga el reporte profesional.")
            pdf_file = app.generar_reporte_pdf()
            
            with open(pdf_file, "rb") as f:
                pdf_data = f.read()
                
            st.download_button(
                label="📥 Descargar Reporte PDF (Incluye Procedimientos)",
                data=pdf_data,
                file_name="memoria_calculo_sedimentador.pdf",
                mime="application/pdf"
            )
            
            # Limpieza
            os.unlink(pdf_file)
            if app.grafica_path: os.unlink(app.grafica_path)

if __name__ == "__main__":
    main()
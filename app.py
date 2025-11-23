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
        self.parametros = parametros
        self.procedimientos = [] 
        
        # --- VARIABLES ---
        Q_ls = parametros['caudal_ls']
        Lx = parametros['lado_x']
        Ly = parametros['lado_y']
        e = parametros['espesor']
        d = parametros['separacion']
        theta_grados = parametros['angulo_grados']
        B = parametros['ancho_sedimentacion']
        nu = parametros['viscosidad']
        CS = parametros['carga_superficial']
        
        espacio_paneles = 1.6
        g = 9.81
        theta_rad = math.radians(theta_grados)
        
        self.procedimientos.append("MEMORIA DE CÁLCULO DETALLADA")
        self.procedimientos.append("-" * 80)

        # 1. Conversión de Caudal
        Q_m3s = Q_ls / 1000
        Q_m3d = Q_ls * 86.4
        
        self.procedimientos.append("1. CONVERSIÓN DE CAUDAL")
        self.procedimientos.append(f"   Q = {Q_m3d:.2f} m3/d ({Q_m3s:.5f} m3/s)")
        self.procedimientos.append("")

        # 2. Área Superficial (As)
        As = Q_m3d / CS
        self.procedimientos.append("2. ÁREA SUPERFICIAL (As)")
        self.procedimientos.append(f"   As = {Q_m3d:.2f} / {CS} = {As:.2f} m2")
        self.procedimientos.append("")
        
        # 3. Longitud (Ls)
        Ls = As / B
        self.procedimientos.append("3. LONGITUD (Ls)")
        self.procedimientos.append(f"   Ls = {As:.2f} / {B} = {Ls:.2f} m")
        self.procedimientos.append("")

        # 4. Velocidad entre placas (Vo)
        sen_theta = math.sin(theta_rad)
        Vo_ms = Q_m3s / (As * sen_theta)
        Vo_cms = Vo_ms * 100
        
        self.procedimientos.append("4. VELOCIDAD ENTRE PLACAS (Vo)")
        self.procedimientos.append(f"   Vo = {Vo_ms:.5f} m/s ({Vo_cms:.3f} cm/s)")
        self.procedimientos.append("")

        # 5. Reynolds (Re)
        Re = (Vo_ms * d) / nu
        self.procedimientos.append("5. NÚMERO DE REYNOLDS (Re)")
        self.procedimientos.append(f"   Re = ({Vo_ms:.5f} * {d}) / {nu:.2e} = {Re:.2f}")
        self.procedimientos.append("")

        # =======================================================
        # 6. CORRECCIÓN APLICADA AQUÍ (Longitudes Relativas)
        # =======================================================
        # L_rel es la longitud relativa geométrica (adimensional)
        L_rel = Ly / d
        # L_prima es la longitud relativa de desarrollo de flujo (adimensional)
        L_prima = Re * 0.013 
        
        self.procedimientos.append("6. LONGITUDES RELATIVAS (L y L')")
        self.procedimientos.append(f"   L (geométrica) = Ly/d = {Ly}/{d} = {L_rel:.2f}")
        self.procedimientos.append(f"   L' (desarrollo) = Re * 0.013 = {L_prima:.3f}")
        
        # Lc también debe ser adimensional para la fórmula de Vs
        if L_prima > (L_rel / 2):
            Lc_rel = 2 * (L_rel - L_prima)
            condicion = "Como L' > L/2"
            formula_txt = "Lc = 2 * (L - L')"
        else:
            Lc_rel = L_rel - L_prima
            condicion = "Como L' <= L/2"
            formula_txt = "Lc = L - L'"
            
        self.procedimientos.append(f"   {condicion} -> Usamos: {formula_txt}")
        self.procedimientos.append(f"   Lc (relativa) = {Lc_rel:.3f}")
        self.procedimientos.append("")

        # 7. Velocidad Crítica (Vs)
        # OJO: Aquí Lc debe ser el valor RELATIVO (adimensional) 
        cos_theta = math.cos(theta_rad)
        denominador_vs = sen_theta + (Lc_rel * cos_theta)
        
        Vs_ms = Vo_ms / denominador_vs
        Vs_mdia = Vs_ms * 86400
        
        self.procedimientos.append("7. VELOCIDAD CRÍTICA (Vs)")
        self.procedimientos.append("   Fórmula: Vs = Vo / (sen(θ) + Lc_rel * cos(θ))")
        self.procedimientos.append(f"   Denom = {sen_theta:.3f} + ({Lc_rel:.3f} * {cos_theta:.3f}) = {denominador_vs:.3f}")
        self.procedimientos.append(f"   Vs = {Vo_ms:.5f} / {denominador_vs:.3f}")
        self.procedimientos.append(f"   Vs = {Vs_ms:.6f} m/s ({Vs_mdia:.2f} m/d)")
        self.procedimientos.append("")
        # =======================================================

        # 8. Número de Placas (N)
        num_placas_exacto = (Ls * sen_theta + d) / (d + e)
        N_placas = int(num_placas_exacto)
        
        self.procedimientos.append("8. NÚMERO DE PLACAS")
        self.procedimientos.append(f"   N calculado: {num_placas_exacto:.2f} -> Adoptado: {N_placas}")
        self.procedimientos.append("")

        # 9. Geometría Final
        ht = (Ly * sen_theta) + 1.96 
        Vol = As * ht
        Tret_min = (Vol / Q_m3s) / 60
        Tce_seg = 1 / Vo_ms
        
        self.procedimientos.append("9. GEOMETRÍA Y TIEMPOS")
        self.procedimientos.append(f"   Altura Total (ht) = {ht:.2f} m")
        self.procedimientos.append(f"   Tiempo Retención = {Tret_min:.2f} min")
        self.procedimientos.append("")

        # 10. Hidráulica Tanque
        Ax = B * ht
        Pm = B + 2*ht
        RH = Ax / Pm
        Vf = Q_m3s / Ax
        Re_tanque = (Vf * RH) / nu
        Fr = (Vf**2) / (g * RH)
        
        self.procedimientos.append("10. VERIFICACIÓN TANQUE")
        self.procedimientos.append(f"   Reynolds Tanque = {Re_tanque:.0f}")
        self.procedimientos.append(f"   Froude = {Fr:.2e}")

        # Resultados
        self.calculos = {
            'As': As, 'Ls': Ls, 'Vo_cms': Vo_cms, 'Re': Re,
            'Lc_rel': Lc_rel, 'Vs_mdia': Vs_mdia, 'N_placas': N_placas,
            'ht': ht, 'Vol': Vol, 'Tret_min': Tret_min, 
            'Re_tanque': Re_tanque, 'Fr': Fr, 'espacio_paneles': espacio_paneles
        }
        
        # Verificaciones
        self.verificaciones = {
            'Vo < 1 cm/s': Vo_cms < 1.0,
            'Re < 500': Re < 500,
            '15 < Tret < 25': 15 <= Tret_min <= 25,
            'Re_tanque < 20000': Re_tanque < 20000,
            'Fr > 1e-5': Fr > 1e-5
        }
        return True

    def generar_grafica(self):
        ancho = self.parametros['ancho_sedimentacion']
        longitud = self.calculos['Ls']
        espacio = self.calculos['espacio_paneles']
        ht = self.calculos['ht']
        theta = self.parametros['angulo_grados']
        Ly = self.parametros['lado_y']
        N_placas = self.calculos['N_placas']
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        
        # VISTA PLANTA
        ax1.set_xlim(0, longitud + espacio + 1)
        ax1.set_ylim(0, ancho + 1)
        ax1.set_title('VISTA PLANTA', fontweight='bold')
        ax1.set_xlabel('Longitud (m)')
        ax1.set_ylabel('Ancho (m)')
        
        rect_entrada = patches.Rectangle((0,0), espacio, ancho, facecolor='#ff9999', alpha=0.3)
        rect_placas = patches.Rectangle((espacio,0), longitud, ancho, facecolor='#99ccff', alpha=0.3)
        ax1.add_patch(rect_entrada)
        ax1.add_patch(rect_placas)
        
        ax1.text(espacio + longitud/2, ancho/2, 
                 f"ZONA DE SEDIMENTACIÓN\nL = {longitud:.2f} m\n\nN = {N_placas} PLACAS", 
                 ha='center', va='center', fontweight='bold', fontsize=11,
                 bbox=dict(boxstyle="round,pad=0.5", fc="white", ec="blue", alpha=0.8))
        ax1.grid(True, linestyle='--', alpha=0.3)

        # VISTA PERFIL
        ax2.set_xlim(0, longitud + espacio + 1)
        ax2.set_ylim(0, ht + 1)
        ax2.set_title('VISTA PERFIL (CORTE)', fontweight='bold')
        ax2.set_xlabel('Longitud (m)')
        ax2.set_ylabel('Altura (m)')
        
        tanque = patches.Rectangle((espacio, 0), longitud, ht, facecolor='#f0f0f0', edgecolor='black')
        ax2.add_patch(tanque)
        
        theta_rad = math.radians(theta)
        dx = Ly * math.cos(theta_rad)
        dy = Ly * math.sin(theta_rad)
        base_h = 1.96
        
        step = longitud / 15 
        for i in np.arange(0, longitud, step):
            x_start = espacio + i
            if x_start + dx < espacio + longitud:
                ax2.plot([x_start, x_start + dx], [base_h, base_h + dy], 'b-', alpha=0.6)
        
        ax2.axhline(y=base_h, color='r', linestyle=':', label='Nivel Lodos')
        ax2.text(espacio + longitud + 0.2, ht/2, f"Ht={ht:.2f}m", color='black', fontweight='bold')
        ax2.text(espacio + longitud/2, base_h + dy + 0.5, 
                 f"Detalle: {N_placas} Placas a {theta}°", 
                 ha='center', va='bottom', color='blue', fontweight='bold', fontsize=10)
        ax2.legend(loc='upper right')
        ax2.grid(True, linestyle='--', alpha=0.3)
        plt.tight_layout()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            fig.savefig(tmp_file.name, dpi=150)
            self.grafica_path = tmp_file.name
        return fig

    def generar_reporte_pdf(self):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, 'REPORTE DE DISEÑO: SEDIMENTADOR ALTA TASA', 0, 1, 'C')
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, f'Fecha: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
        pdf.ln(5)
        
        # Datos
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 10, '1. DATOS DE ENTRADA', 1, 1, 'L', 1)
        pdf.set_font("Arial", '', 10)
        p = self.parametros
        texto_datos = (f"Caudal: {p['caudal_ls']} L/s | Ancho B: {p['ancho_sedimentacion']} m | CS: {p['carga_superficial']} m/d\n"
                       f"Placa: {p['lado_x']}x{p['lado_y']} m | Angulo: {p['angulo_grados']}° | Sep: {p['separacion']} m")
        pdf.multi_cell(0, 6, texto_datos)
        pdf.ln(5)
        
        # Procedimiento
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, '2. MEMORIA DE CÁLCULO', 1, 1, 'L', 1)
        pdf.set_font("Courier", '', 9)
        for linea in self.procedimientos:
            try: txt = linea.encode('latin-1', 'replace').decode('latin-1')
            except: txt = linea
            pdf.multi_cell(0, 5, txt)
        pdf.ln(5)
        
        # Verificación
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, '3. CONCLUSIONES', 1, 1, 'L', 1)
        pdf.set_font("Arial", '', 10)
        for crit, cumple in self.verificaciones.items():
            col = (0, 128, 0) if cumple else (200, 0, 0)
            pdf.set_text_color(*col)
            pdf.cell(0, 6, f"[{'CUMPLE' if cumple else 'NO CUMPLE'}] {crit}", 0, 1)
        pdf.set_text_color(0, 0, 0)
        
        # Gráficos
        if self.grafica_path and os.path.exists(self.grafica_path):
            pdf.add_page()
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, '4. ANEXO GRÁFICO', 0, 1, 'L')
            pdf.image(self.grafica_path, x=10, y=30, w=190)
            
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf.output(tmp_file.name)
            return tmp_file.name

# ==========================================
# INTERFAZ (MAIN)
# ==========================================
def main():
    st.title("💧 Diseño de Sedimentador de Alta Tasa")
    
    if 'app' not in st.session_state:
        st.session_state.app = SedimentadorAltaTasa()
    
    # --- SIDEBAR ---
    st.sidebar.header("Parámetros de Diseño")
    
    # Tabla RAS
    with st.sidebar.expander("📘 Referencia Normativa (RAS)", expanded=False):
        datos_norma = {
            "Parámetro": ["Carga Superficial", "Tiempo Retención", "Reynolds Placas", "Ángulo", "Velocidad (Vo)"],
            "Unidad": ["m³/m²/d", "min", "Adim.", "Grados", "cm/s"],
            "Rango": ["120 - 185", "15 - 25", "< 500", "≥ 60°", "< 1.0"]
        }
        st.table(pd.DataFrame(datos_norma))

    with st.sidebar.form("form_diseno"):
        c1, c2 = st.columns(2)
        q_ls = c1.number_input("Caudal (L/s)", 1.0, 500.0, 45.0)
        lx = c1.number_input("Lado X (m)", 0.5, 3.0, 1.2)
        ly = c2.number_input("Lado Y (m)", 0.5, 3.0, 1.2)
        
        theta = st.slider("Ángulo (°)", 45, 70, 60)
        c1, c2 = st.columns(2)
        d = c1.number_input("Separación (m)", 0.01, 0.2, 0.06)
        e = c2.number_input("Espesor (m)", 0.001, 0.05, 0.01)
        
        st.sidebar.markdown("---")
        b = st.number_input("Ancho Tanque (m)", 1.0, 10.0, 2.5)
        cs = st.number_input("Carga Superficial (m/d)", 50.0, 300.0, 120.0)
        nu = st.number_input("Viscosidad (m2/s)", format="%.2e", value=1.00e-6)
        
        if st.form_submit_button("🚀 Calcular"):
            params = {
                'caudal_ls': q_ls, 'lado_x': lx, 'lado_y': ly,
                'angulo_grados': theta, 'separacion': d, 'espesor': e,
                'ancho_sedimentacion': b, 'carga_superficial': cs, 'viscosidad': nu
            }
            st.session_state.app.calcular(params)

    # --- RESULTADOS ---
    app = st.session_state.app
    if app.calculos:
        t1, t2, t3 = st.tabs(["Resultados", "Memoria", "Descargas"])
        
        with t1:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Placas", app.calculos['N_placas'])
            col2.metric("Longitud", f"{app.calculos['Ls']:.2f} m")
            col3.metric("Reynolds", f"{app.calculos['Re']:.0f}")
            col4.metric("Froude", f"{app.calculos['Fr']:.1e}")
            
            st.pyplot(app.generar_grafica())
            
            st.subheader("Verificación")
            cols = st.columns(3)
            idx=0
            for k, v in app.verificaciones.items():
                if v: cols[idx%3].success(f"✅ {k}")
                else: cols[idx%3].error(f"❌ {k}")
                idx+=1

        with t2:
            st.code("\n".join(app.procedimientos), language="text")
            
        with t3:
            pdf_file = app.generar_reporte_pdf()
            with open(pdf_file, "rb") as f:
                st.download_button("📥 Descargar PDF", f, "memoria.pdf", "application/pdf")
            os.unlink(pdf_file)

if __name__ == "__main__":
    main()
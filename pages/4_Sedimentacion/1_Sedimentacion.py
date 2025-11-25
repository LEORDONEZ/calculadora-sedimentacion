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
import re

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
        self.grafica_canaletas_path = None
    
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
        tipo_sedimentador = parametros['tipo_sedimentador']
        num_canaletas = parametros['num_canaletas']
        
        # Definir Sc según tipo de sedimentador
        if tipo_sedimentador == "Placas Paralelas":
            Sc = 1.0
        elif tipo_sedimentador == "Tubos Circulares":
            Sc = 4/3
        elif tipo_sedimentador == "Conductos Cuadrados":
            Sc = 11/8
        else:
            Sc = 1.0  # Valor por defecto
        
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
        self.procedimientos.append("3. LONGITUD DEL SEDIMENTADOR (Ls)")
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
        self.procedimientos.append("5. NÚMERO DE REYNOLDS EN PLACAS (Re)")
        self.procedimientos.append(f"   Re = ({Vo_ms:.5f} * {d}) / {nu:.2e}")
        self.procedimientos.append(f"   Re = {Re:.2f} (Adimensional)")
        self.procedimientos.append("")

        # 6. Longitudes Relativas (L y L')
        L_rel = Ly / d
        L_prima = Re * 0.013 
        self.procedimientos.append("6. LONGITUDES RELATIVAS (L y L')")
        self.procedimientos.append(f"   L = {L_rel:.2f} (Adimensional)")
        self.procedimientos.append(f"   L' = {L_prima:.3f} (Adimensional)")
        self.procedimientos.append("")

        # 7. Longitud Crítica (Lc)
        if L_prima > (L_rel / 2):
            Lc_rel = 2 * (L_rel - L_prima)
            condicion = "Como L' > L/2"
            formula_txt = "Lc = 2 * (L - L')"
        else:
            Lc_rel = L_rel - L_prima
            condicion = "Como L' <= L/2"
            formula_txt = "Lc = L - L'"
            
        self.procedimientos.append("7. LONGITUD CRÍTICA RELATIVA (Lc)")
        self.procedimientos.append(f"   {condicion} -> Usamos: {formula_txt}")
        self.procedimientos.append(f"   Lc = {Lc_rel:.3f} (Adimensional)")
        self.procedimientos.append("")

        # 8. Velocidad Crítica (Vs) - CON SC VARIABLE
        cos_theta = math.cos(theta_rad)
        denominador_vs = sen_theta + (Lc_rel * cos_theta)
        Vs_ms = (Sc * Vo_ms) / denominador_vs
        Vs_mdia = Vs_ms * 86400
        
        self.procedimientos.append("8. VELOCIDAD CRÍTICA (Vs)")
        self.procedimientos.append(f"   Tipo de sedimentador: {tipo_sedimentador}")
        self.procedimientos.append(f"   Sc = {Sc:.3f}")
        self.procedimientos.append(f"   Vs = (Sc × Vo) / (senθ + Lc × cosθ)")
        self.procedimientos.append(f"   Vs = ({Sc:.3f} × {Vo_ms:.5f}) / ({sen_theta:.3f} + {Lc_rel:.3f} × {cos_theta:.3f})")
        self.procedimientos.append(f"   Vs = {Vs_ms:.6f} m/s ({Vs_mdia:.2f} m/d)")
        self.procedimientos.append("")

        # 9. Número de Placas (N)
        num_placas_exacto = (Ls * sen_theta + d) / (d + e)
        N_placas = int(num_placas_exacto)
        self.procedimientos.append("9. NÚMERO DE PLACAS")
        self.procedimientos.append(f"   N calculado: {num_placas_exacto:.2f} -> Adoptado: {N_placas}")
        self.procedimientos.append("")

        # 10. Geometría Final y Tiempos
        ht = (Ly * sen_theta) + 1.96 
        Vol = As * ht
        self.procedimientos.append("10. GEOMETRÍA Y VOLUMEN")
        self.procedimientos.append(f"   Altura Total (ht) = {ht:.2f} m")
        self.procedimientos.append(f"   Volumen (Vol) = {Vol:.2f} m³")
        self.procedimientos.append("")

        # Tiempos de Retención
        Tret_min = (Vol / Q_m3s) / 60
        Tce_seg = Ly / Vo_ms
        self.procedimientos.append("11. TIEMPOS DE RETENCIÓN")
        self.procedimientos.append(f"   Tce = {Tce_seg:.2f} s")
        self.procedimientos.append(f"   Tret = {Tret_min:.2f} min")
        self.procedimientos.append("")

        # 12. HIDRÁULICA DEL TANQUE
        Ax = B * ht
        Pm = B + 2*ht
        RH = Ax / Pm
        Vf = Q_m3s / Ax
        Re_tanque = (Vf * RH) / nu
        Fr = (Vf**2) / (g * RH)
        
        self.procedimientos.append("12. HIDRÁULICA DEL TANQUE")
        self.procedimientos.append(f"   Área Transversal (Ax) = {Ax:.2f} m²")
        self.procedimientos.append(f"   Perímetro Mojado (Pm) = {Pm:.2f} m")
        self.procedimientos.append(f"   Radio Hidráulico (RH) = {RH:.4f} m")
        self.procedimientos.append(f"   Velocidad Horizontal (Vf) = {Vf:.5f} m/s")
        self.procedimientos.append(f"   Re Tanque = {Re_tanque:.0f}")
        self.procedimientos.append(f"   Froude = {Fr:.2e}")
        self.procedimientos.append("")

        # 13. DISEÑO DE CANALETAS
        self.procedimientos.append("13. DISEÑO DE CANALETAS DE SALIDA")
        self.procedimientos.append(f"   Número de canaletas: {num_canaletas}")
        
        # Caudal por canaleta
        Qc = Q_m3s / num_canaletas
        self.procedimientos.append(f"   Caudal por canaleta (Qc) = {Q_m3s:.4f} / {num_canaletas} = {Qc:.4f} m³/s")
        
        # Ancho de canaleta (asumido)
        b_canaleta = 0.3  # m
        self.procedimientos.append(f"   Ancho de canaleta (b) = {b_canaleta} m (asumido)")
        
        # Altura de agua en canaleta (ho)
        try:
            ho = (Qc / (1.345 * b_canaleta)) ** (2/3)
            self.procedimientos.append(f"   Altura de agua (ho) = [Qc / (1.345 × b)]^(2/3)")
            self.procedimientos.append(f"   ho = [{Qc:.4f} / (1.345 × {b_canaleta})]^(2/3) = {ho:.3f} m")
        except:
            ho = 0.1
            self.procedimientos.append("   Error en cálculo de ho, se asume ho = 0.1 m")
        
        # Borde libre
        borde_libre = 0.15  # m
        altura_total_canaleta = ho + borde_libre

        self.procedimientos.append(f"   Borde libre = {borde_libre} m")
        self.procedimientos.append(f"   Altura total canaleta = {altura_total_canaleta:.3f} m")
        self.procedimientos.append("")

        # Resultados finales
        self.calculos = {
            'As': As, 'Ls': Ls, 'Vo_cms': Vo_cms, 'Re': Re,
            'Lc_rel': Lc_rel, 'Vs_mdia': Vs_mdia, 'N_placas': N_placas,
            'ht': ht, 'Vol': Vol, 'Tret_min': Tret_min, 
            'Re_tanque': Re_tanque, 'Fr': Fr, 'espacio_paneles': espacio_paneles,
            'tipo_sedimentador': tipo_sedimentador, 'Sc': Sc,
            'num_canaletas': num_canaletas, 'Qc': Qc, 'b_canaleta': b_canaleta,
            'ho': ho, 'altura_total_canaleta': altura_total_canaleta
        }
        
        self.verificaciones = {
            'Vo < 1 cm/s': Vo_cms < 1.0,
            'Re < 500': Re < 500,
            '15 < Tret < 25': 15 <= Tret_min <= 25,
            'Re_tanque < 20000': Re_tanque < 20000,
            'Fr > 1e-5': Fr > 1e-5,
            f'Sc correcto ({tipo_sedimentador})': True
        }
        return True

    def _dibujar_cota(self, ax, x1, y1, x2, y2, texto, color='black', offset_label=0):
        """Función auxiliar para dibujar cotas tipo ingeniería"""
        # Línea principal
        ax.annotate('', xy=(x1, y1), xytext=(x2, y2),
                    arrowprops=dict(arrowstyle='<->', color=color, lw=1.0))
        # Texto centrado
        xm, ym = (x1 + x2) / 2, (y1 + y2) / 2
        
        # Ajuste para que el texto no pise la línea
        if x1 == x2: # Cota vertical
            angle = 90
            offset_x = -0.3 if offset_label == 0 else offset_label
            offset_y = 0
            va = 'center'
            ha = 'right'
        else: # Cota horizontal
            angle = 0
            offset_x = 0
            offset_y = 0.2 if offset_label == 0 else offset_label
            va = 'bottom'
            ha = 'center'

        ax.text(xm + offset_x, ym + offset_y, texto, 
                color=color, ha=ha, va=va, rotation=angle, fontsize=9, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.8))

    def generar_grafica(self):
        B = self.parametros['ancho_sedimentacion']
        Ls = self.calculos['Ls']
        E = self.calculos['espacio_paneles']
        ht = self.calculos['ht']
        theta = self.parametros['angulo_grados']
        Ly = self.parametros['lado_y']
        N_placas = self.calculos['N_placas']
        
        # Aumentar tamaño para que quepan las cotas
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
        
        # ================= VISTA PLANTA =================
        ax1.set_title('VISTA PLANTA (COTAS EN METROS)', fontweight='bold', pad=20)
        
        # Dibujos
        rect_entrada = patches.Rectangle((0,0), E, B, facecolor='#ff9999', alpha=0.3, edgecolor='red')
        rect_placas = patches.Rectangle((E,0), Ls, B, facecolor='#99ccff', alpha=0.3, edgecolor='blue')
        ax1.add_patch(rect_entrada)
        ax1.add_patch(rect_placas)
        
        # Cotas Planta
        # Ancho B (Izquierda)
        self._dibujar_cota(ax1, -0.5, 0, -0.5, B, f"B = {B:.2f} m")
        
        # Longitud Entrada (Arriba)
        self._dibujar_cota(ax1, 0, B+0.5, E, B+0.5, f"E={E}m")
        
        # Longitud Sedimentador (Arriba)
        self._dibujar_cota(ax1, E, B+0.5, E+Ls, B+0.5, f"Ls = {Ls:.2f} m")
        
        # Longitud Total (Abajo)
        self._dibujar_cota(ax1, 0, -0.8, E+Ls, -0.8, f"L Total = {E+Ls:.2f} m")

        # Texto interno
        ax1.text(E/2, B/2, "ENTRADA", ha='center', va='center', fontsize=8)
        ax1.text(E + Ls/2, B/2, f"ZONA PLACAS\nN={N_placas}", ha='center', va='center', fontsize=10, fontweight='bold')

        # Configuración ejes
        ax1.set_xlim(-1.5, E+Ls+1)
        ax1.set_ylim(-1.5, B+1.5)
        ax1.axis('off') # Ocultar ejes coordenados feos, dejar solo dibujo

        # ================= VISTA PERFIL =================
        ax2.set_title('VISTA PERFIL (COTAS EN METROS)', fontweight='bold', pad=20)
        
        # Tanque
        tanque = patches.Rectangle((E, 0), Ls, ht, facecolor='#f0f0f0', edgecolor='black', linewidth=1.5)
        ax2.add_patch(tanque)
        
        # Placas (Representación visual)
        theta_rad = math.radians(theta)
        dx = Ly * math.cos(theta_rad)
        dy = Ly * math.sin(theta_rad)
        base_h = 1.96
        
        # Dibujar placas
        step = Ls / 12
        for i in np.arange(0, Ls, step):
            x_start = E + i
            if x_start + dx < E + Ls:
                ax2.plot([x_start, x_start + dx], [base_h, base_h + dy], 'b-', alpha=0.5)
        
        # Línea de lodos
        ax2.plot([E, E+Ls], [base_h, base_h], 'r--', linewidth=1)
        
        # Cotas Perfil
        # Altura Total (Derecha)
        self._dibujar_cota(ax2, E+Ls+0.5, 0, E+Ls+0.5, ht, f"Ht = {ht:.2f} m")
        
        # Altura Lodos (Izquierda)
        self._dibujar_cota(ax2, E-0.3, 0, E-0.3, base_h, f"Lodos = {base_h} m")
        
        # Altura Placas (Izquierda, arriba de lodos)
        self._dibujar_cota(ax2, E-0.3, base_h, E-0.3, base_h+dy, f"H_placa = {dy:.2f} m")
        
        # Longitud Tanque (Abajo)
        self._dibujar_cota(ax2, E, -0.5, E+Ls, -0.5, f"Ls = {Ls:.2f} m")

        # Configuración ejes
        ax2.set_xlim(E-1, E+Ls+1.5)
        ax2.set_ylim(-1, ht+1)
        ax2.axis('off')

        plt.tight_layout()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            fig.savefig(tmp_file.name, dpi=150)
            self.grafica_path = tmp_file.name
        return fig

    def generar_grafica_canaletas(self):
        """Genera gráfico específico para las canaletas de salida"""
        b = self.calculos['b_canaleta']
        ho = self.calculos['ho']
        altura_total = self.calculos['altura_total_canaleta']
        num_canaletas = self.calculos['num_canaletas']
        Qc = self.calculos['Qc']
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # ================= VISTA EN PLANTA DE CANALETAS =================
        ax1.set_title('VISTA EN PLANTA - CANALETAS DE SALIDA', fontweight='bold', pad=15)
        
        # Dibujar canaletas
        separacion = 0.5  # m entre canaletas
        ancho_total = num_canaletas * b + (num_canaletas - 1) * separacion
        
        for i in range(num_canaletas):
            x_start = i * (b + separacion)
            canaleta = patches.Rectangle((x_start, 0), b, 2, 
                                       facecolor='#E1F5FE', edgecolor='#01579B', linewidth=2)
            ax1.add_patch(canaleta)
            ax1.text(x_start + b/2, 1, f'Canaleta {i+1}', 
                    ha='center', va='center', fontweight='bold')
        
        # Cotas
        self._dibujar_cota(ax1, 0, -0.3, b, -0.3, f'b = {b} m')
        if num_canaletas > 1:
            self._dibujar_cota(ax1, 0, -0.8, ancho_total, -0.8, f'Ancho total = {ancho_total:.2f} m')
        
        ax1.set_xlim(-0.5, ancho_total + 0.5)
        ax1.set_ylim(-1, 2.5)
        ax1.set_aspect('equal')
        ax1.axis('off')
        
        # ================= VISTA EN CORTE DE CANALETA =================
        ax2.set_title('VISTA EN CORTE - DETALLE CANALETA', fontweight='bold', pad=15)
        
        # Dibujar sección transversal de canaleta
        canaleta_corte = patches.Rectangle((0, 0), b, altura_total, 
                                         facecolor='#B3E5FC', edgecolor='#0277BD', linewidth=2)
        ax2.add_patch(canaleta_corte)
        
        # Nivel de agua
        ax2.plot([0, b], [ho, ho], 'b-', linewidth=3, label='Nivel de agua')
        
        # Cotas
        self._dibujar_cota(ax2, -0.3, 0, -0.3, ho, f'ho = {ho:.3f} m', color='blue')
        self._dibujar_cota(ax2, -0.6, 0, -0.6, altura_total, f'H total = {altura_total:.3f} m')
        self._dibujar_cota(ax2, 0, altura_total + 0.1, b, altura_total + 0.1, f'b = {b} m')
        
        # Información adicional
        ax2.text(b/2, altura_total + 0.3, f'Q = {Qc:.4f} m³/s', 
                ha='center', va='center', fontweight='bold', fontsize=10)
        
        ax2.set_xlim(-1, b + 0.5)
        ax2.set_ylim(-0.1, altura_total + 0.5)
        ax2.set_aspect('equal')
        ax2.legend(loc='upper right')
        ax2.axis('off')
        
        plt.tight_layout()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            fig.savefig(tmp_file.name, dpi=150)
            self.grafica_canaletas_path = tmp_file.name
        return fig

    def _limpiar_texto_pdf(self, texto):
        """Limpia el texto para evitar problemas con FPDF"""
        # Reemplazar caracteres problemáticos
        texto = texto.replace('×', 'x')
        texto = texto.replace('°', 'grados')
        texto = texto.replace('θ', 'theta')
        texto = texto.replace('→', '->')
        texto = texto.replace('≤', '<=')
        texto = texto.replace('≥', '>=')
        texto = texto.replace('³', '3')
        texto = texto.replace('²', '2')
        
        # Limitar longitud máxima de línea
        lineas = texto.split('\n')
        lineas_limpias = []
        for linea in lineas:
            if len(linea) > 120:  # Límite seguro para PDF
                # Dividir líneas muy largas
                palabras = linea.split(' ')
                linea_actual = ""
                for palabra in palabras:
                    if len(linea_actual + palabra) < 100:
                        linea_actual += palabra + " "
                    else:
                        lineas_limpias.append(linea_actual.strip())
                        linea_actual = palabra + " "
                lineas_limpias.append(linea_actual.strip())
            else:
                lineas_limpias.append(linea)
        
        return '\n'.join(lineas_limpias)

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
                       f"Placa: {p['lado_x']} x {p['lado_y']} m | Angulo: {p['angulo_grados']} grados | Sep: {p['separacion']} m\n"
                       f"Tipo: {p['tipo_sedimentador']} | Canaletas: {p['num_canaletas']}")
        pdf.multi_cell(0, 6, texto_datos)
        pdf.ln(5)
        
        # Procedimiento - CON ANCHO ESPECIFICADO
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, '2. MEMORIA DE CÁLCULO', 1, 1, 'L', 1)
        pdf.set_font("Courier", '', 8)  # Fuente más pequeña
        
        for linea in self.procedimientos:
            try: 
                txt = self._limpiar_texto_pdf(linea)
                # Usar ancho específico en lugar de 0
                pdf.multi_cell(190, 4, txt)  # 190 mm de ancho
            except Exception as e:
                # Si hay error, usar texto alternativo
                txt_alt = f"Linea: {linea[:50]}..." if len(linea) > 50 else linea
                pdf.multi_cell(190, 4, txt_alt)
        pdf.ln(5)
        
        # Verificación
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, '3. CONCLUSIONES', 1, 1, 'L', 1)
        pdf.set_font("Arial", '', 10)
        for crit, cumple in self.verificaciones.items():
            col = (0, 128, 0) if cumple else (200, 0, 0)
            pdf.set_text_color(*col)
            # Limpiar también las verificaciones
            crit_limpio = self._limpiar_texto_pdf(crit)
            pdf.cell(0, 6, f"[{'CUMPLE' if cumple else 'NO CUMPLE'}] {crit_limpio}", 0, 1)
        pdf.set_text_color(0, 0, 0)
        
        # Gráficos
        if self.grafica_path and os.path.exists(self.grafica_path):
            try:
                pdf.add_page()
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, '4. ANEXO GRÁFICO - SEDIMENTADOR', 0, 1, 'L')
                pdf.image(self.grafica_path, x=10, y=30, w=190)  # Margen más pequeño
            except:
                pdf.cell(0, 6, "Error al cargar gráfico del sedimentador", 0, 1)
            
        if self.grafica_canaletas_path and os.path.exists(self.grafica_canaletas_path):
            try:
                pdf.add_page()
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, '5. ANEXO GRÁFICO - CANALETAS', 0, 1, 'L')
                pdf.image(self.grafica_canaletas_path, x=10, y=30, w=190)
            except:
                pdf.cell(0, 6, "Error al cargar gráfico de canaletas", 0, 1)
            
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
        
        e = c2.number_input("Espesor (m)", 0.001, 0.05, 0.01, format="%.3f", 
                            help="Valores típicos: Fibrocemento 0.006-0.010m | Plástico/Lona 0.001-0.003m")
        
        st.sidebar.markdown("---")
        
        # Nuevos parámetros
        tipo_sedimentador = st.selectbox(
            "Tipo de Sedimentador",
            ["Placas Paralelas", "Tubos Circulares", "Conductos Cuadrados"],
            help="Seleccione el tipo de sedimentador para determinar el coeficiente Sc"
        )
        
        num_canaletas = st.number_input("Número de Canaletas", 1, 5, 2)
        
        b = st.number_input("Ancho Tanque (m)", 1.0, 10.0, 2.5)
        cs = st.number_input("Carga Superficial (m/d)", 50.0, 300.0, 120.0)
        nu = st.number_input("Viscosidad (m2/s)", format="%.2e", value=1.00e-6)
        
        if st.form_submit_button("🚀 Calcular"):
            params = {
                'caudal_ls': q_ls, 'lado_x': lx, 'lado_y': ly,
                'angulo_grados': theta, 'separacion': d, 'espesor': e,
                'ancho_sedimentacion': b, 'carga_superficial': cs, 'viscosidad': nu,
                'tipo_sedimentador': tipo_sedimentador, 'num_canaletas': num_canaletas
            }
            st.session_state.app.calcular(params)

    # --- RESULTADOS ---
    app = st.session_state.app
    if app.calculos:
        t1, t2, t3, t4 = st.tabs(["Resultados", "Memoria", "Canaletas", "Descargas"])
        
        with t1:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Placas", app.calculos['N_placas'])
            col2.metric("Longitud (Ls)", f"{app.calculos['Ls']:.2f} m")
            col3.metric("Reynolds", f"{app.calculos['Re']:.0f}")
            col4.metric("Sc", f"{app.calculos['Sc']:.3f}")
            
            # Mostrar gráfico grande
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
            st.subheader("Diseño de Canaletas de Salida")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Caudal por canaleta", f"{app.calculos['Qc']:.4f} m³/s")
                st.metric("Altura de agua (ho)", f"{app.calculos['ho']:.3f} m")
            with col2:
                st.metric("Ancho canaleta", f"{app.calculos['b_canaleta']} m")
                st.metric("Altura total", f"{app.calculos['altura_total_canaleta']:.3f} m")
            
            # Mostrar gráfico de canaletas
            st.pyplot(app.generar_grafica_canaletas())
            
        with t4:
            try:
                pdf_file = app.generar_reporte_pdf()
                with open(pdf_file, "rb") as f:
                    st.download_button("📥 Descargar PDF", f, "memoria.pdf", "application/pdf")
                os.unlink(pdf_file)
            except Exception as e:
                st.error(f"Error al generar PDF: {str(e)}")
                st.info("Intente reducir la cantidad de texto o usar valores más simples")

if __name__ == "__main__":
    main()
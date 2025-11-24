import streamlit as st
import numpy as np
import math
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from fpdf import FPDF
import tempfile
import os
from datetime import datetime

# --- FUNCIONES DE AYUDA (Fuera de la clase) ---

def guardar_fig_temporal(fig):
    """Guarda una figura de Matplotlib en un archivo temporal y devuelve la ruta."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
        fig.savefig(tmp_file.name, dpi=150, bbox_inches='tight')
        return tmp_file.name

def obtener_tabla_ras_data():
    """Devuelve los datos de la Tabla 5 del RAS 0330"""
    return {
        "Parámetro": [
            "Carga hidráulica", "Altura total", "Número de bandejas",
            "Distancia entre bandejas", "Altura de bandeja", "Diametro medio orificios",
            "Separación media entre orificios", "Espesor del lecho de contacto", "Tamaño del material de contacto"
        ],
        "Valor (Rango)": [
            "500 - 1500 m³/m²/d", "1,2 - 3,0 m", "3 - 9",
            "0,3 - 0,5 m", "0,20 - 0,25 m", "0,5 - 0,6 cm",
            "0,25 m", "0,15 - 0,20 m", "4 - 12 cm"
        ]
    }

# --- CLASE PRINCIPAL DE DISEÑO ---

class DisenoAireadorBandejas:
    """
    Clase para almacenar y calcular los parámetros de diseño de un aireador de bandejas,
    basado en el RAS 0330 de 2017 (Tabla 5) y ecuaciones estándar.
    """
    def __init__(self):
        # Constantes
        self.g = 9.81  # m/s²
        
        # --- Parámetros de Entrada ---
        self.Q_lps = 0.0
        self.CH_m3_m2_d = 0.0
        self.h_separacion_m = 0.0
        self.diametro_orificio_cm = 0.0
        self.Cd_descarga = 0.0
        self.h_agua_bandeja_m = 0.0
        self.t_contacto_s_deseado = 0.0
        self.S_perforaciones_cm = 0.0
        
        # --- Parámetros Calculados ---
        (self.n_calculado, self.n_bandejas, self.Q_m3_dia, self.Q_m3_s,
         self.Area_total_m2, self.Area_bandeja_m2, self.L_bandeja_m,
         self.d_orificio_m, self.Ao_m2, self.Qo_m3_s, self.Qo_lps,
         self.No_orificios_total_calculado, self.N_orificios_fila,
         self.No_orificios_total_real, self.S_perforaciones_m,
         self.L_calculada_orificios_m, self.H_total_m) = (0,) * 17
         
        # --- Verificaciones ---
        self.check_n = ""
        self.check_L = ""
        self.check_orificios = ""

    def realizar_calculos(self, Q, CH, h, diam_cm, Cd, h_agua, t_deseado, S_cm):
        """Ejecuta toda la secuencia de cálculo hidráulico."""
        
        # 1. Guardar Inputs
        self.Q_lps = Q
        self.CH_m3_m2_d = CH
        self.h_separacion_m = h
        self.diametro_orificio_cm = diam_cm
        self.Cd_descarga = Cd
        self.h_agua_bandeja_m = h_agua
        self.t_contacto_s_deseado = t_deseado
        self.S_perforaciones_cm = S_cm
        self.d_orificio_m = self.diametro_orificio_cm / 100.0
        self.S_perforaciones_m = self.S_perforaciones_cm / 100.0

        # 2. Calcular Número de Bandejas (n)
        denominador_t = math.sqrt((2 * self.h_separacion_m) / self.g)
        self.n_calculado = self.t_contacto_s_deseado / denominador_t
        self.n_bandejas = math.ceil(self.n_calculado)

        # 3. Conversión de Caudal (Q)
        self.Q_m3_s = self.Q_lps / 1000.0
        self.Q_m3_dia = self.Q_m3_s * 86400

        # 4. Calcular Áreas (A_total, A_bandeja)
        self.Area_total_m2 = self.Q_m3_dia / self.CH_m3_m2_d
        self.Area_bandeja_m2 = self.Area_total_m2 / self.n_bandejas

        # 5. Calcular Longitud de Bandeja (L)
        self.L_bandeja_m = math.sqrt(self.Area_bandeja_m2)

        # 6. Calcular Caudal por Orificio (Qo)
        self.Ao_m2 = math.pi * (self.d_orificio_m ** 2) / 4
        self.Qo_m3_s = self.Cd_descarga * self.Ao_m2 * math.sqrt(2 * self.g * self.h_agua_bandeja_m)
        self.Qo_lps = self.Qo_m3_s * 1000.0

        # 7. Calcular Número de Orificios (No)
        self.No_orificios_total_calculado = self.Q_m3_s / self.Qo_m3_s
        
        # 8. Orificios por Fila (N_fila)
        self.N_orificios_fila = math.ceil(math.sqrt(self.No_orificios_total_calculado))
        self.No_orificios_total_real = self.N_orificios_fila ** 2

        # 9. Calcular Longitud Requerida por Orificios (L_check)
        self.L_calculada_orificios_m = (self.N_orificios_fila - 1) * self.S_perforaciones_m + (self.N_orificios_fila * self.d_orificio_m)

        # 10. Calcular Altura Total (H)
        self.H_total_m = self.h_separacion_m * (self.n_bandejas - 1) + self.h_agua_bandeja_m * self.n_bandejas

        # 11. Realizar Verificaciones
        self.realizar_verificaciones()

        st.session_state.calculos_realizados = True
        st.success("Cálculos realizados con éxito!")
        return True

    def realizar_verificaciones(self):
        """Realiza las 3 verificaciones de diseño y guarda los mensajes."""
        # Check 1: Número de Bandejas (n)
        n_min, n_max = 3, 9
        if n_min <= self.n_bandejas <= n_max:
            self.check_n = f"CUMPLE. ({self.n_bandejas}) esta en el rango [{n_min} - {n_max}]."
        else:
            self.check_n = f"FALLA. ({self.n_bandejas}) esta fuera del rango [{n_min} - {n_max}]."
        
        # Check 2: Manejabilidad de Longitud (L)
        L_manejable = 1.5
        if self.L_bandeja_m <= L_manejable:
            self.check_L = f"CUMPLE. ({self.L_bandeja_m:.2f} m) es manejable (<= {L_manejable} m)."
        else:
            self.check_L = f"ADVERTENCIA. ({self.L_bandeja_m:.2f} m) no es manejable (> {L_manejable} m)."

        # Check 3: Verificación de Orificios vs Longitud
        if self.L_calculada_orificios_m <= self.L_bandeja_m:
            self.check_orificios = f"CUMPLE. ({self.L_calculada_orificios_m:.2f} m) <= ({self.L_bandeja_m:.2f} m)."
        else:
            self.check_orificios = f"FALLA. ({self.L_calculada_orificios_m:.2f} m) > ({self.L_bandeja_m:.2f} m)."

    def generar_grafica_planta(self):
        """Genera una vista en planta de la bandeja con sus orificios"""
        L = self.L_bandeja_m
        N = self.N_orificios_fila
        d = self.d_orificio_m
        
        fig, ax = plt.subplots(figsize=(8, 8))
        
        # 1. Dibujar la bandeja
        bandeja = patches.Rectangle((0, 0), L, L, facecolor='#E0F7FA', edgecolor='black', linewidth=2)
        ax.add_patch(bandeja)
        
        # 2. Calcular posiciones de los orificios
        L_requerida = self.L_calculada_orificios_m
        margen = (L - L_requerida) / 2.0
        
        if margen < 0: margen = 0.0
            
        pos_inicial = margen + (d / 2.0)
        
        centros = []
        if N > 1:
            for i in range(N):
                # Pos = inicio + i * (separacion_centro_a_centro)
                pos = pos_inicial + i * (self.S_perforaciones_m + self.d_orificio_m)
                centros.append(pos)
        else:
            centros = [L / 2.0]

        # 3. Dibujar los orificios
        if centros:
            for x_centro in centros:
                for y_centro in centros:
                    orificio = patches.Circle((x_centro, y_centro), radius=d/2.0, facecolor='blue', edgecolor='darkblue')
                    ax.add_patch(orificio)
        
        ax.set_aspect('equal')
        ax.set_xlim(-0.1 * L, L * 1.1)
        ax.set_ylim(-0.1 * L, L * 1.1)
        ax.set_title(f'Vista en Planta de 1 Bandeja\n({N}x{N} = {self.No_orificios_total_real} orificios)')
        ax.set_xlabel(f'Longitud (L) = {L:.2f} m')
        ax.set_ylabel(f'Ancho = {L:.2f} m')
        plt.grid(True, linestyle='--', alpha=0.6)
        return fig

    def generar_grafica_perfil(self):
        """Genera una vista transversal (perfil) del paquete de bandejas"""
        n = self.n_bandejas
        h_sep = self.h_separacion_m
        h_agua = self.h_agua_bandeja_m
        L = self.L_bandeja_m
        H_total = self.H_total_m
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        y_actual = 0
        
        for i in range(n):
            y_bandeja = H_total - (i * (h_sep + h_agua)) - h_agua
            bandeja = patches.Rectangle((0, y_bandeja), L, h_agua, facecolor='lightblue', edgecolor='black', linewidth=1)
            ax.add_patch(bandeja)
            ax.text(L / 2, y_bandeja + h_agua / 2, f'Bandeja {i+1}', ha='center', va='center', fontsize=10, fontweight='bold')
            
            if i < n - 1:
                y_caida_inicio = y_bandeja
                y_caida_fin = y_bandeja - h_sep
                ax.arrow(L * 0.75, y_caida_inicio, 0, -h_sep + 0.05, 
                         head_width=0.05*L, head_length=0.03*H_total, fc='blue', ec='blue', length_includes_head=True)
                ax.text(L * 0.80, (y_caida_inicio + y_caida_fin) / 2, f'h = {h_sep} m', va='center')
        
        ax.set_xlim(-0.1 * L, L * 1.5)
        ax.set_ylim(0, H_total * 1.1)
        ax.set_title('Vista Transversal (Perfil) del Aireador')
        ax.set_xlabel(f'Longitud (L) = {L:.2f} m')
        ax.set_ylabel(f'Altura Total (H) = {H_total:.2f} m')
        ax.set_yticklabels([])
        ax.set_xticklabels([])
        return fig

    def generar_reporte_pdf(self, fig_planta_path, fig_perfil_path):
        """Genera el reporte PDF con todos los cálculos, tablas y gráficas."""
        
        pdf = FPDF()
        pdf.add_page()
        
        pdf.set_font("helvetica", 'B', 16)
        pdf.cell(0, 10, 'REPORTE DE DISEÑO DE AIREADOR DE BANDEJAS', ln=1, align='C')
        pdf.set_font("helvetica", '', 10)
        pdf.cell(0, 6, f'Fecha de generacion: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', ln=1, align='C')
        pdf.ln(5)

        # --- 1. Parámetros de Entrada ---
        pdf.set_font("helvetica", 'B', 12)
        pdf.cell(0, 10, '1. PARÁMETROS DE ENTRADA', ln=1)
        pdf.set_font("helvetica", '', 10)
        pdf.cell(0, 6, f"Caudal de Diseno (Q): {self.Q_lps} L/s  ({self.Q_m3_s:.4f} m³/s)", ln=1)
        pdf.cell(0, 6, f"Tiempo de Contacto deseado (t): {self.t_contacto_s_deseado} s", ln=1)
        pdf.cell(0, 6, f"Carga Hidraulica (CH): {self.CH_m3_m2_d} m³/m²/d", ln=1)
        pdf.cell(0, 6, f"Separacion entre Bandejas (h): {self.h_separacion_m} m", ln=1)
        pdf.cell(0, 6, f"Diametro de Orificio: {self.diametro_orificio_cm} cm  ({self.d_orificio_m} m)", ln=1)
        pdf.cell(0, 6, f"Coeficiente de Descarga (Cd): {self.Cd_descarga}", ln=1)
        pdf.cell(0, 6, f"Altura de Agua en Bandeja (h'): {self.h_agua_bandeja_m} m", ln=1)
        pdf.cell(0, 6, f"Separacion entre Orificios (S): {self.S_perforaciones_cm} cm  ({self.S_perforaciones_m} m)", ln=1)
        pdf.ln(5)

        # --- 2. Tabla RAS 0330 ---
        pdf.set_font("helvetica", 'B', 12)
        pdf.cell(0, 10, '2. PARÁMETROS DE REFERENCIA (RAS 0330 - Tabla 5)', ln=1)
        pdf.set_font("helvetica", 'B', 10)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(100, 8, "Parametro", border=1, fill=True)
        pdf.cell(0, 8, "Valor (Rango)", border=1, fill=True, ln=1)
        pdf.set_font("helvetica", '', 9)
        tabla_data = obtener_tabla_ras_data()
        for i in range(len(tabla_data["Parámetro"])):
            pdf.cell(100, 6, tabla_data["Parámetro"][i], border=1)
            pdf.cell(0, 6, tabla_data["Valor (Rango)"][i], border=1, ln=1)
        pdf.ln(5)

        # --- 3. Memoria de Cálculo ---
        pdf.set_font("helvetica", 'B', 12)
        pdf.cell(0, 10, '3. MEMORIA DE CÁLCULO', ln=1)
        
        def escribir_calculo(titulo, formula, calculo, resultado):
            pdf.set_font("helvetica", 'B', 10)
            pdf.cell(0, 6, titulo, ln=1)
            pdf.set_font("Courier", '', 10)
            pdf.cell(0, 5, f"  Formula: {formula}", ln=1)
            pdf.set_font("helvetica", '', 10)
            pdf.cell(0, 5, f"  Calculo: {calculo}", ln=1)
            pdf.set_font("helvetica", 'B', 10)
            pdf.cell(0, 5, f"  Resultado: {resultado}", ln=1)
            pdf.ln(3)

        escribir_calculo(
            "Numero de Bandejas (n)",
            "n = t / sqrt(2*h / g)",
            f"n = {self.t_contacto_s_deseado} / sqrt(2*{self.h_separacion_m} / {self.g}) = {self.n_calculado:.2f}",
            f"{self.n_bandejas} (Redondeado)"
        )
        escribir_calculo(
            "Area Total (A)",
            "A = Q_m3_dia / CH",
            f"A = {self.Q_m3_dia:.2f} / {self.CH_m3_m2_d} = {self.Area_total_m2:.2f} m²",
            f"{self.Area_total_m2:.2f} m²"
        )
        escribir_calculo(
            "Area por Bandeja (A_bandeja)",
            "A_bandeja = A / n",
            f"A_bandeja = {self.Area_total_m2:.2f} / {self.n_bandejas} = {self.Area_bandeja_m2:.2f} m²",
            f"{self.Area_bandeja_m2:.2f} m²"
        )
        escribir_calculo(
            "Longitud de Bandeja (L)",
            "L = sqrt(A_bandeja)",
            f"L = sqrt({self.Area_bandeja_m2:.2f}) = {self.L_bandeja_m:.2f} m",
            f"{self.L_bandeja_m:.2f} m (Asumiendo bandeja cuadrada)"
        )
        escribir_calculo(
            "Caudal por Orificio (Qo)",
            "Qo = Cd * (pi*d²/4) * sqrt(2*g*h')",
            f"Qo = {self.Cd_descarga} * (pi*{self.d_orificio_m}²/4) * sqrt(2*{self.g}*{self.h_agua_bandeja_m}) = {self.Qo_m3_s:.6f} m³/s",
            f"{self.Qo_lps:.4f} L/s"
        )
        escribir_calculo(
            "Numero de Orificios (No)",
            "No = Q_m3_s / Qo_m3_s",
            f"No = {self.Q_m3_s:.4f} / {self.Qo_m3_s:.6f} = {self.No_orificios_total_calculado:.2f}",
            f"{self.No_orificios_total_real} (Cuadricula {self.N_orificios_fila}x{self.N_orificios_fila})"
        )
        escribir_calculo(
            "Altura Total del Aireador (H)",
            "H = h * (n - 1) + h' * n",
            f"H = {self.h_separacion_m} * ({self.n_bandejas} - 1) + {self.h_agua_bandeja_m} * {self.n_bandejas}",
            f"{self.H_total_m:.2f} m"
        )
        
        # --- 4. Verificaciones de Diseño ---
        pdf.set_font("helvetica", 'B', 12)
        pdf.cell(0, 10, '4. VERIFICACIONES DE DISEÑO', ln=1)
        pdf.set_font("helvetica", '', 10)
        pdf.cell(0, 6, f"Check 1 (N° Bandejas): {self.check_n}", ln=1)
        pdf.cell(0, 6, f"Check 2 (Manejabilidad L): {self.check_L}", ln=1)
        pdf.cell(0, 6, f"Check 3 (Espacio Orificios): {self.check_orificios}", ln=1)
        pdf.ln(5)
        
        # --- 5. Planos ---
        pdf.add_page()
        pdf.set_font("helvetica", 'B', 12)
        pdf.cell(0, 10, '5. PLANOS DE DISEÑO', ln=1)
        
        if fig_planta_path:
            pdf.set_font("helvetica", 'B', 10)
            pdf.cell(0, 8, "Vista en Planta (Bandeja Individual)", ln=1)
            pdf.image(fig_planta_path, x = 10, y = None, w = 190)
            pdf.ln(5)

        if fig_perfil_path:
            pdf.add_page()
            pdf.set_font("helvetica", 'B', 10)
            pdf.cell(0, 8, "Vista de Perfil (Paquete de Bandejas)", ln=1)
            pdf.image(fig_perfil_path, x = 10, y = None, w = 190)

        # Guardar PDF en un archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf.output(tmp_file.name)
            return tmp_file.name


def mostrar_tabla_5_st():
    """Muestra la Tabla 5 del RAS 0330 en un dataframe de Streamlit"""
    df_tabla_5 = pd.DataFrame(obtener_tabla_ras_data())
    with st.expander("Ver Parámetros de Referencia (RAS 0330 - Tabla 5)"):
        st.dataframe(df_tabla_5, hide_index=True)

def main():
    """Función principal de la aplicación Streamlit"""
    st.set_page_config(
        page_title="Diseño de Aireador por Bandejas",
        page_icon="🌊",
        layout="wide"
    )
    
    st.title("🌊 Diseño de Aireador por Bandejas")
    mostrar_tabla_5_st()
    st.markdown("---")
    
    # Inicializar session state
    if 'diseno_app' not in st.session_state:
        st.session_state.diseno_app = DisenoAireadorBandejas()
    if 'calculos_realizados' not in st.session_state:
        st.session_state.calculos_realizados = False

    # Sidebar para ingresar datos
    with st.sidebar:
        st.header("📋 Parámetros de Diseño")
        
        # --- REQUERIMIENTO 1: Cargar Caudal de la página anterior ---
        q_default = 100.0 # Valor por defecto si no hay nada
        if 'resultados_demanda' in st.session_state:
            q_default = st.session_state.resultados_demanda.get('q_diseno_planta', 100.0)
            st.info(f"Caudal pre-cargado: {q_default:.2f} L/s")

        with st.form("design_form"):
            st.info("Parámetros de entrada principales")
            Q_lps = st.number_input("Caudal (Q) en L/s", min_value=0.1, value=q_default, step=1.0, 
                                    help="Valor por defecto del cálculo de demanda, pero editable.")
            t_contacto_s_deseado = st.number_input("Tiempo de Contacto (t) en segundos", min_value=0.1, value=2.0, step=0.1)

            st.markdown("---")
            st.info("Parámetros de la Tabla 5 (RAS 0330)")
            CH_m3_m2_d = st.number_input("Carga Hidráulica (m³/m²/d)", min_value=500.0, max_value=1500.0, value=1000.0, step=10.0, help="Rango RAS: 500 - 1500")
            h_separacion_m = st.number_input("Separación entre Bandejas (h) en metros", min_value=0.3, max_value=0.5, value=0.4, step=0.01, help="Rango RAS: 0.3 - 0.5")
            diametro_orificio_cm = st.number_input("Diámetro Perforaciones (cm)", min_value=0.5, max_value=0.6, value=0.5, step=0.01, help="Rango RAS: 0.5 - 0.6 cm")

            st.markdown("---")
            st.info("Parámetros de Orificios (Ecuación 8.9)")
            Cd_descarga = st.number_input("Coeficiente de Descarga (Cd)", min_value=0.1, max_value=1.0, value=0.85, step=0.01, help="Adimensional (Ej: 0.6 - 0.9)")
            h_agua_bandeja_m = st.number_input("Altura de Agua sobre Bandeja (h') en metros", min_value=0.05, max_value=0.30, value=0.15, step=0.01, help="Lámina de agua sobre los orificios")
            S_perforaciones_cm = st.number_input("Separación entre Perforaciones (S) en cm", min_value=0.1, value=2.5, step=0.1, help="Distancia entre bordes de orificios. Se recomienda 2.5 cm")
            
            submitted = st.form_submit_button("Realizar Cálculos")
            
            if submitted:
                st.session_state.diseno_app.realizar_calculos(
                    Q=Q_lps,
                    CH=CH_m3_m2_d,
                    h=h_separacion_m,
                    diam_cm=diametro_orificio_cm,
                    Cd=Cd_descarga,
                    h_agua=h_agua_bandeja_m,
                    t_deseado=t_contacto_s_deseado,
                    S_cm=S_perforaciones_cm
                )

    # Contenido principal - Mostrar resultados
    if st.session_state.calculos_realizados:
        app_data = st.session_state.diseno_app
        
        # Generar figuras una sola vez
        fig_planta = app_data.generar_grafica_planta()
        fig_perfil = app_data.generar_grafica_perfil()
        
        # Crear pestañas para organizar los resultados
        tab_res, tab_check, tab_planta, tab_perfil, tab_pdf = st.tabs([
            "📊 Resultados Principales", 
            "⚠️ Verificaciones de Diseño", 
            "🗺️ Gráfico en Planta", 
            "📏 Gráfico de Perfil",
            "📄 Reporte PDF"
        ])

        with tab_res:
            st.header("Resultados de Cálculo")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Caudal (Q)", f"{app_data.Q_lps} L/s")
                st.metric("N° Bandejas (n) Calculado", f"{app_data.n_calculado:.2f}")
                st.metric("N° Bandejas (n) Adoptado", f"{app_data.n_bandejas}")
                
            with col2:
                st.metric("Área Total de Bandejas (A)", f"{app_data.Area_total_m2:.2f} m²")
                st.metric("Área por Bandeja (A_bandeja)", f"{app_data.Area_bandeja_m2:.2f} m²")
                st.metric("Longitud de Bandeja (L)", f"{app_data.L_bandeja_m:.2f} m", help="Asumiendo bandeja cuadrada (L = sqrt(A_bandeja))")
                
            with col3:
                st.metric("Caudal por Orificio (Qo)", f"{app_data.Qo_lps:.4f} L/s")
                st.metric("N° Orificios Total (Real)", f"{app_data.No_orificios_total_real}", help=f"Basado en una cuadrícula de {app_data.N_orificios_fila}x{app_data.N_orificios_fila}")
                st.metric("Altura Total del Aireador (H)", f"{app_data.H_total_m:.2f} m")

        with tab_check:
            st.header("Verificaciones de Diseño (Checks)")
            
            # Check 1: Número de Bandejas (n)
            st.subheader("Check 1: Número de Bandejas (n)")
            if "CUMPLE" in app_data.check_n: st.success(app_data.check_n)
            else: st.error(app_data.check_n)
            
            # Check 2: Manejabilidad de Longitud (L)
            st.subheader("Check 2: Manejabilidad de la Bandeja (L)")
            if "CUMPLE" in app_data.check_L: st.success(app_data.check_L)
            else: st.warning(app_data.check_L)

            # Check 3: Verificación de Orificios vs Longitud
            st.subheader("Check 3: Espacio de Orificios vs Bandeja")
            if "CUMPLE" in app_data.check_orificios: st.success(app_data.check_orificios)
            else: st.error(app_data.check_orificios)

        with tab_planta:
            st.header("Gráfico en Planta (Vista Superior)")
            st.pyplot(fig_planta)
            
        with tab_perfil:
            st.header("Gráfico de Perfil (Vista Transversal)")
            st.pyplot(fig_perfil)
        
        with tab_pdf:
            st.header("Generar Reporte PDF")
            st.info("El reporte incluirá todos los datos, cálculos, verificaciones, la tabla RAS y los planos.")
            
            if st.button("📄 Generar Reporte PDF"):
                with st.spinner("Generando reporte y guardando gráficos..."):
                    # Guardar figuras en archivos temporales
                    fig_planta_path = guardar_fig_temporal(fig_planta)
                    fig_perfil_path = guardar_fig_temporal(fig_perfil)
                    
                    # Generar PDF
                    pdf_path = app_data.generar_reporte_pdf(fig_planta_path, fig_perfil_path)
                    
                    with open(pdf_path, "rb") as pdf_file:
                        pdf_bytes = pdf_file.read()
                    
                    st.download_button(
                        label="⬇️ Descargar Reporte PDF",
                        data=pdf_bytes,
                        file_name=f"reporte_aireador_bandejas_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf"
                    )
                    
                    # Limpiar archivos temporales
                    os.unlink(fig_planta_path)
                    os.unlink(fig_perfil_path)
                    os.unlink(pdf_path)

    else:
        st.info("⬅️ Ingrese los parámetros de diseño en el panel lateral y presione 'Realizar Cálculos'.")

if __name__ == "__main__":
    main()
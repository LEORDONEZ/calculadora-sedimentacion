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
    page_title="Cálculo Velocidad de Sedimentación - Ley de Stokes",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CLASE PRINCIPAL DE CÁLCULO Y REPORTE
# ==========================================
class CalculadorStokes:
    def __init__(self):
        self.parametros = {}
        self.resultados = {}
        self.verificaciones = {}
        self.procedimientos = []
    
    def calcular(self, parametros):
        self.parametros = parametros
        self.procedimientos = []
        
        # --- DATOS DEL PROBLEMA ---
        D_um = parametros['diametro_um']
        S_s = parametros['densidad_relativa']
        temperaturas = parametros['temperaturas']
        
        # Conversión de unidades
        D_m = D_um * 1e-6
        
        self.procedimientos.append("MEMORIA DE CÁLCULO - PROBLEMA 5.21.1")
        self.procedimientos.append("=" * 60)
        self.procedimientos.append("")
        
        # 1. Datos del problema
        self.procedimientos.append("1. DATOS DEL PROBLEMA")
        self.procedimientos.append(f"   Diámetro de partícula: {D_um} μm = {D_m:.2e} m")
        self.procedimientos.append(f"   Densidad relativa (S_s): {S_s}")
        self.procedimientos.append(f"   Temperaturas a evaluar: {', '.join(map(str, temperaturas))} °C")
        self.procedimientos.append("")
        
        # 2. Viscosidades cinemáticas (según Cuadro 5.4 del documento)
        viscosidades = {
            0: 1.765e-6,
            5: 1.519e-6,
            10: 1.306e-6,
            15: 1.139e-6,
            20: 1.003e-6,
            25: 0.893e-6,
            30: 0.800e-6,
            35: 0.727e-6,
            40: 0.667e-6
        }
        
        self.procedimientos.append("2. VISCOSIDADES CINEMÁTICAS DEL AGUA")
        self.procedimientos.append("   (Según Cuadro 5.4 del documento y valores extendidos)")
        for temp in temperaturas:
            if temp in viscosidades:
                self.procedimientos.append(f"   ν({temp}°C) = {viscosidades[temp]:.3e} m²/s")
            else:
                # Interpolación lineal para temperaturas no listadas
                temp_min = max(t for t in viscosidades.keys() if t <= temp)
                temp_max = min(t for t in viscosidades.keys() if t >= temp)
                if temp_min == temp_max:
                    nu = viscosidades[temp_min]
                else:
                    # Interpolación lineal
                    nu_min = viscosidades[temp_min]
                    nu_max = viscosidades[temp_max]
                    nu = nu_min + (nu_max - nu_min) * (temp - temp_min) / (temp_max - temp_min)
                    self.procedimientos.append(f"   ν({temp}°C) = {nu:.3e} m²/s (interpolado)")
        self.procedimientos.append("")
        
        # 3. Fórmula de Stokes
        g = 9.81  # m/s²
        
        self.procedimientos.append("3. FÓRMULA DE STOKES")
        self.procedimientos.append("   U = [g × (S_s - 1) × D²] / (18 × ν)")
        self.procedimientos.append(f"   Donde:")
        self.procedimientos.append(f"   g = {g} m/s² (aceleración gravitacional)")
        self.procedimientos.append(f"   S_s = {S_s} (densidad relativa)")
        self.procedimientos.append(f"   D = {D_m:.2e} m (diámetro partícula)")
        self.procedimientos.append(f"   ν = viscosidad cinemática (m²/s)")
        self.procedimientos.append("")
        
        # 4. Cálculos para cada temperatura
        resultados_temp = []
        
        self.procedimientos.append("4. CÁLCULOS POR TEMPERATURA")
        self.procedimientos.append("-" * 40)
        
        for temp in temperaturas:
            if temp in viscosidades:
                nu = viscosidades[temp]
            else:
                # Interpolación para temperaturas no listadas
                temp_min = max(t for t in viscosidades.keys() if t <= temp)
                temp_max = min(t for t in viscosidades.keys() if t >= temp)
                if temp_min == temp_max:
                    nu = viscosidades[temp_min]
                else:
                    nu_min = viscosidades[temp_min]
                    nu_max = viscosidades[temp_max]
                    nu = nu_min + (nu_max - nu_min) * (temp - temp_min) / (temp_max - temp_min)
            
            # Cálculo de velocidad
            U_ms = (g * (S_s - 1) * (D_m ** 2)) / (18 * nu)
            U_mms = U_ms * 1000  # Convertir a mm/s
            
            # Verificación del régimen (Número de Reynolds)
            N_Re = (U_ms * D_m) / nu
            
            resultados_temp.append({
                'Temperatura (°C)': temp,
                'ν (m²/s)': nu,
                'U (m/s)': U_ms,
                'U (mm/s)': U_mms,
                'N_Re': N_Re,
                'Régimen': 'Laminar' if N_Re < 0.5 else 'Transición/Turbulento'
            })
            
            self.procedimientos.append(f"   Para T = {temp}°C:")
            self.procedimientos.append(f"     ν = {nu:.3e} m²/s")
            self.procedimientos.append(f"     U = [9.81 × ({S_s}-1) × ({D_m:.2e})²] / (18 × {nu:.3e})")
            self.procedimientos.append(f"     U = {U_ms:.6f} m/s = {U_mms:.3f} mm/s")
            self.procedimientos.append(f"     N_Re = ({U_ms:.6f} × {D_m:.2e}) / {nu:.3e} = {N_Re:.6f}")
            self.procedimientos.append(f"     Régimen: {N_Re:.6f} {'<' if N_Re < 0.5 else '>='} 0.5 → {resultados_temp[-1]['Régimen']}")
            self.procedimientos.append("")
        
        # 5. Resumen de resultados
        self.procedimientos.append("5. RESUMEN DE RESULTADOS")
        self.procedimientos.append("-" * 40)
        
        df_resultados = pd.DataFrame(resultados_temp)
        
        for _, fila in df_resultados.iterrows():
            self.procedimientos.append(f"   {fila['Temperatura (°C)']}°C: {fila['U (mm/s)']:.3f} mm/s ({fila['Régimen']})")
        
        self.procedimientos.append("")
        
        # Almacenar resultados
        self.resultados = {
            'dataframe': df_resultados,
            'diametro_um': D_um,
            'densidad_relativa': S_s
        }
        
        # Verificaciones
        self.verificaciones = {
            'Todos los N_Re < 0.5 (Laminar)': all(df_resultados['N_Re'] < 0.5),
            'Velocidades dentro de rango esperado': all(0.001 <= u <= 100 for u in df_resultados['U (mm/s)']),
            'Temperaturas en rango válido (0-40°C)': all(0 <= t <= 40 for t in temperaturas)
        }
        
        return True
    
    def generar_grafica(self):
        if not self.resultados:
            return None
            
        df = self.resultados['dataframe']
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Gráfica 1: Velocidad vs Temperatura
        ax1.plot(df['Temperatura (°C)'], df['U (mm/s)'], 'bo-', linewidth=2, markersize=8)
        ax1.set_xlabel('Temperatura (°C)')
        ax1.set_ylabel('Velocidad de Sedimentación (mm/s)')
        ax1.set_title('Velocidad de Sedimentación vs Temperatura')
        ax1.grid(True, alpha=0.3)
        
        # Añadir valores en los puntos
        for i, row in df.iterrows():
            ax1.annotate(f'{row["U (mm/s)"]:.3f}', 
                        (row['Temperatura (°C)'], row['U (mm/s)']),
                        textcoords="offset points", 
                        xytext=(0,10), 
                        ha='center',
                        fontweight='bold')
        
        # Gráfica 2: Número de Reynolds vs Temperatura
        ax2.plot(df['Temperatura (°C)'], df['N_Re'], 'ro-', linewidth=2, markersize=8)
        ax2.set_xlabel('Temperatura (°C)')
        ax2.set_ylabel('Número de Reynolds (N_Re)')
        ax2.set_title('Número de Reynolds vs Temperatura')
        ax2.grid(True, alpha=0.3)
        
        # Línea de referencia para régimen laminar
        ax2.axhline(y=0.5, color='red', linestyle='--', alpha=0.7, label='Límite régimen laminar (N_Re = 0.5)')
        ax2.legend()
        
        # Añadir valores en los puntos
        for i, row in df.iterrows():
            ax2.annotate(f'{row["N_Re"]:.4f}', 
                        (row['Temperatura (°C)'], row['N_Re']),
                        textcoords="offset points", 
                        xytext=(0,10), 
                        ha='center',
                        fontweight='bold')
        
        plt.tight_layout()
        return fig
    
    def generar_reporte_pdf(self):
        pdf = FPDF()
        pdf.add_page()
        
        # Encabezado
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, 'REPORTE: CÁLCULO VELOCIDAD DE SEDIMENTACIÓN', 0, 1, 'C')
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, f'Fecha: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
        pdf.ln(5)
        
        # Datos del problema
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(0, 10, 'DATOS DEL PROBLEMA', 1, 1, 'L', 1)
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 6, f'Diámetro de partícula: {self.parametros["diametro_um"]} μm', 0, 1)
        pdf.cell(0, 6, f'Densidad relativa: {self.parametros["densidad_relativa"]}', 0, 1)
        pdf.cell(0, 6, f'Temperaturas evaluadas: {", ".join(map(str, self.parametros["temperaturas"]))} °C', 0, 1)
        pdf.ln(5)
        
        # Procedimiento de cálculo
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(0, 10, 'PROCEDIMIENTO DE CÁLCULO', 1, 1, 'L', 1)
        pdf.set_font("Courier", '', 8)
        
        for linea in self.procedimientos:
            # Manejar caracteres especiales
            try:
                txt = linea.encode('latin-1', 'replace').decode('latin-1')
            except:
                txt = linea
            pdf.multi_cell(0, 4, txt)
        
        pdf.ln(5)
        
        # Tabla de resultados
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(0, 10, 'TABLA DE RESULTADOS', 1, 1, 'L', 1)
        
        # Crear tabla
        if self.resultados:
            df = self.resultados['dataframe']
            columnas = ['Temperatura (°C)', 'ν (m²/s)', 'U (m/s)', 'U (mm/s)', 'N_Re', 'Régimen']
            
            # Encabezados de tabla
            pdf.set_font("Arial", 'B', 9)
            for col in columnas:
                pdf.cell(32, 8, col, 1, 0, 'C')
            pdf.ln()
            
            # Datos de tabla
            pdf.set_font("Arial", '', 8)
            for _, fila in df.iterrows():
                pdf.cell(32, 6, f"{fila['Temperatura (°C)']}", 1, 0, 'C')
                pdf.cell(32, 6, f"{fila['ν (m²/s)']:.2e}", 1, 0, 'C')
                pdf.cell(32, 6, f"{fila['U (m/s)']:.6f}", 1, 0, 'C')
                pdf.cell(32, 6, f"{fila['U (mm/s)']:.3f}", 1, 0, 'C')
                pdf.cell(32, 6, f"{fila['N_Re']:.6f}", 1, 0, 'C')
                pdf.cell(32, 6, f"{fila['Régimen']}", 1, 1, 'C')
        
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
    st.title("🧮 Cálculo de Velocidad de Sedimentación - Ley de Stokes")
    st.markdown("### Resolución del Problema 5.21.1 - Capítulo 5: Sedimentación")
    
    if 'calculador' not in st.session_state:
        st.session_state.calculador = CalculadorStokes()
    
    # --- SIDEBAR ---
    st.sidebar.header("📊 Parámetros del Problema")
    
    with st.sidebar.form("form_parametros"):
        st.subheader("Datos de la Partícula")
        
        diametro_um = st.number_input(
            "Diámetro de partícula (μm)",
            min_value=1.0,
            max_value=1000.0,
            value=20.0,
            step=1.0,
            help="Diámetro en micrómetros (1 μm = 10⁻⁶ m)"
        )
        
        densidad_relativa = st.number_input(
            "Densidad relativa (S_s)",
            min_value=1.0,
            max_value=5.0,
            value=2.65,
            step=0.01,
            help="Densidad de partícula / Densidad del agua"
        )
        
        st.subheader("Selección de Temperaturas")
        
        # Selección del número de temperaturas
        num_temperaturas = st.radio(
            "Número de temperaturas a calcular:",
            [1, 2, 3],
            horizontal=True,
            help="Seleccione cuántas temperaturas desea evaluar"
        )
        
        # Contenedores para las temperaturas
        col1, col2, col3 = st.columns(3)
        temperaturas_seleccionadas = []
        
        with col1:
            if num_temperaturas >= 1:
                temp1 = st.number_input(
                    "Temperatura 1 (°C)",
                    min_value=0,
                    max_value=40,
                    value=10,
                    step=1,
                    key="temp1"
                )
                temperaturas_seleccionadas.append(temp1)
        
        with col2:
            if num_temperaturas >= 2:
                temp2 = st.number_input(
                    "Temperatura 2 (°C)",
                    min_value=0,
                    max_value=40,
                    value=20,
                    step=1,
                    key="temp2"
                )
                temperaturas_seleccionadas.append(temp2)
        
        with col3:
            if num_temperaturas >= 3:
                temp3 = st.number_input(
                    "Temperatura 3 (°C)",
                    min_value=0,
                    max_value=40,
                    value=30,
                    step=1,
                    key="temp3"
                )
                temperaturas_seleccionadas.append(temp3)
        
        # Validación de temperaturas únicas
        if len(temperaturas_seleccionadas) != len(set(temperaturas_seleccionadas)):
            st.warning("⚠️ Las temperaturas deben ser diferentes")
        
        # Botón de cálculo
        calcular_disabled = (len(temperaturas_seleccionadas) != len(set(temperaturas_seleccionadas))) or (num_temperaturas != len(temperaturas_seleccionadas))
        
        if st.form_submit_button("🚀 Calcular Velocidades", disabled=calcular_disabled):
            if not temperaturas_seleccionadas:
                st.error("Seleccione al menos una temperatura")
            else:
                parametros = {
                    'diametro_um': diametro_um,
                    'densidad_relativa': densidad_relativa,
                    'temperaturas': temperaturas_seleccionadas
                }
                st.session_state.calculador.calcular(parametros)
                st.rerun()
    
    # --- INFORMACIÓN TEÓRICA ---
    with st.sidebar.expander("📚 Información Teórica"):
        st.markdown("""
        **Ley de Stokes** (Para flujo laminar, N_Re < 0.5):
        
        $$U = \\frac{g (S_s - 1) D^2}{18 \\nu}$$
        
        Donde:
        - U = Velocidad de sedimentación (m/s)
        - g = 9.81 m/s² (gravedad)
        - S_s = Densidad relativa partícula/agua
        - D = Diámetro partícula (m)
        - ν = Viscosidad cinemática (m²/s)
        
        **Verificación del régimen:**
        - N_Re < 0.5: Flujo laminar (✓ Stokes válido)
        - N_Re ≥ 0.5: Otro régimen (✗ Stokes no aplicable)
        
        **Temperaturas disponibles:** 0°C a 40°C
        """)
    
    # --- EJEMPLOS RÁPIDOS ---
    with st.sidebar.expander("🎯 Ejemplos Rápidos"):
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Problema 5.21.1"):
                st.session_state.calculador.calcular({
                    'diametro_um': 20.0,
                    'densidad_relativa': 2.65,
                    'temperaturas': [10, 20, 30]
                })
                st.rerun()
        
        with col2:
            if st.button("Arena Fina"):
                st.session_state.calculador.calcular({
                    'diametro_um': 100.0,
                    'densidad_relativa': 2.65,
                    'temperaturas': [15, 25]
                })
                st.rerun()
    
    # --- RESULTADOS PRINCIPALES ---
    calculador = st.session_state.calculador
    
    if calculador.resultados:
        st.success("✅ Cálculos completados exitosamente")
        
        # Mostrar configuración actual
        st.info(f"""
        **Configuración actual:** 
        - Diámetro: {calculador.parametros['diametro_um']} μm
        - Densidad relativa: {calculador.parametros['densidad_relativa']}
        - Temperaturas: {', '.join(map(str, calculador.parametros['temperaturas']))}°C
        """)
        
        # Mostrar resultados en pestañas
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Resultados", "📋 Procedimiento", "📊 Gráficas", "📥 Reporte"])
        
        with tab1:
            st.subheader("Resultados del Cálculo")
            
            # Mostrar tabla de resultados
            df = calculador.resultados['dataframe']
            st.dataframe(df.style.format({
                'ν (m²/s)': '{:.3e}',
                'U (m/s)': '{:.6f}',
                'U (mm/s)': '{:.3f}',
                'N_Re': '{:.6f}'
            }), use_container_width=True)
            
            # Resumen ejecutivo
            st.subheader("📊 Resumen Ejecutivo")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Diámetro partícula", f"{calculador.parametros['diametro_um']} μm")
            
            with col2:
                st.metric("Densidad relativa", f"{calculador.parametros['densidad_relativa']}")
            
            with col3:
                num_temps = len(calculador.parametros['temperaturas'])
                st.metric("Temperaturas", f"{num_temps}")
            
            with col4:
                regimen_valido = all(df['N_Re'] < 0.5)
                st.metric("Régimen válido", "✓ Laminar" if regimen_valido else "✗ No laminar")
            
            # Análisis comparativo si hay más de una temperatura
            if len(df) > 1:
                st.subheader("📈 Análisis Comparativo")
                min_vel = df['U (mm/s)'].min()
                max_vel = df['U (mm/s)'].max()
                incremento = (max_vel / min_vel - 1) * 100
                
                st.markdown(f"""
                - **Rango de velocidades:** {min_vel:.3f} a {max_vel:.3f} mm/s
                - **Incremento máximo:** {incremento:.1f}%
                - **Temperatura más favorable:** {df.loc[df['U (mm/s)'].idxmax(), 'Temperatura (°C)']}°C
                - **Temperatura menos favorable:** {df.loc[df['U (mm/s)'].idxmin(), 'Temperatura (°C)']}°C
                """)
            
            # Verificaciones
            st.subheader("✅ Verificaciones")
            for criterio, cumple in calculador.verificaciones.items():
                if cumple:
                    st.success(f"**{criterio}**")
                else:
                    st.error(f"**{criterio}**")
        
        with tab2:
            st.subheader("📝 Procedimiento Detallado de Cálculo")
            st.code("\n".join(calculador.procedimientos), language="text")
        
        with tab3:
            st.subheader("📊 Gráficas de Resultados")
            fig = calculador.generar_grafica()
            if fig:
                st.pyplot(fig)
                
                # Análisis de resultados
                st.subheader("📈 Análisis de Resultados")
                df = calculador.resultados['dataframe']
                
                if len(df) > 1:
                    st.markdown(f"""
                    **Observaciones:**
                    - La velocidad de sedimentación **aumenta con la temperatura** debido a la disminución de la viscosidad
                    - El incremento de {df['Temperatura (°C)'].min()}°C a {df['Temperatura (°C)'].max()}°C produce un aumento de **{df['U (mm/s)'].max()/df['U (mm/s)'].min():.2f}x** en la velocidad
                    - Todos los números de Reynolds están **{'por debajo' if all(df['N_Re'] < 0.5) else 'por encima'}** del límite de 0.5
                    - La **Ley de Stokes es {'aplicable' if all(df['N_Re'] < 0.5) else 'no aplicable'}** para estas condiciones
                    """)
                else:
                    st.markdown(f"""
                    **Observaciones para {df['Temperatura (°C)'].iloc[0]}°C:**
                    - Velocidad de sedimentación: **{df['U (mm/s)'].iloc[0]:.3f} mm/s**
                    - Número de Reynolds: **{df['N_Re'].iloc[0]:.6f}**
                    - Régimen: **{df['Régimen'].iloc[0]}**
                    - Ley de Stokes: **{'Aplicable' if df['N_Re'].iloc[0] < 0.5 else 'No aplicable'}**
                    """)
        
        with tab4:
            st.subheader("📥 Generar Reporte PDF")
            
            if st.button("🖨️ Generar Reporte Completo en PDF"):
                with st.spinner("Generando reporte PDF..."):
                    pdf_file = calculador.generar_reporte_pdf()
                    
                    with open(pdf_file, "rb") as f:
                        st.download_button(
                            label="📥 Descargar Reporte PDF",
                            data=f,
                            file_name=f"reporte_stokes_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                            mime="application/pdf"
                        )
                    
                    # Limpiar archivo temporal
                    os.unlink(pdf_file)
    
    else:
        # Pantalla inicial - Instrucciones
        st.info("""
        ## 🧭 Instrucciones de Uso
        
        1. **Configure los parámetros** en la barra lateral:
           - Diámetro de la partícula (μm)
           - Densidad relativa (S_s)
           - Número de temperaturas (1, 2 o 3)
           - Valores específicos de temperatura (°C)
        
        2. **Haga clic en "Calcular Velocidades"** para ejecutar los cálculos
        
        3. **Revise los resultados** en las diferentes pestañas:
           - 📈 Resultados: Tabla resumen y análisis
           - 📋 Procedimiento: Cálculos detallados paso a paso
           - 📊 Gráficas: Visualización de resultados
           - 📥 Reporte: Descarga en PDF
        
        ### 🎯 Características:
        - **Flexibilidad total** en selección de temperaturas
        - **Validación automática** del régimen de flujo
        - **Interpolación** para temperaturas no listadas
        - **Análisis comparativo** entre temperaturas
        - **Reporte profesional** descargable
        """)

if __name__ == "__main__":
    main()
import streamlit as st
import numpy as np
import math
from datetime import datetime
from fpdf import FPDF
import tempfile
import os
import matplotlib.pyplot as plt

class ProyeccionPoblacion:
    def __init__(self):
        self.censos = []
        self.resultados = {}
        self.promedios = {}
        self.Tf = None
        self.T_ordenados = np.array([])
        self.P_ordenados = np.array([])
        self.Tci, self.Pci, self.Tuc, self.Puc = None, None, None, None
        self.log_P_datos = np.array([])

    def agregar_censo(self, año, poblacion):
        """Agrega un censo a la lista y la ordena"""
        # Evitar duplicados de año
        if not any(c['año'] == año for c in self.censos):
            self.censos.append({'año': año, 'poblacion': poblacion})
            self.censos.sort(key=lambda x: x['año'])
            st.session_state.censos = self.censos.copy() # Actualizar session state
            return True
        return False

    def _prepare_data(self):
        """Prepara los arrays de numpy para los cálculos"""
        if len(self.censos) < 2:
            return False
        
        datos_ordenados = sorted(self.censos, key=lambda x: x['año'])
        self.T_ordenados = np.array([d['año'] for d in datos_ordenados])
        self.P_ordenados = np.array([d['poblacion'] for d in datos_ordenados])
        
        self.Tci, self.Pci = self.T_ordenados[0], self.P_ordenados[0]
        self.Tuc, self.Puc = self.T_ordenados[-1], self.P_ordenados[-1]
        
        if any(self.P_ordenados <= 0):
            st.error("Error: Las poblaciones no pueden ser cero o negativas para métodos logarítmicos.")
            return False
            
        self.log_P_datos = np.log(self.P_ordenados)
        self.log_Pci = np.log(self.Pci)
        self.log_Puc = np.log(self.Puc)
        return True

    def _metodo_lineal_simple(self):
        """Método 1: Lineal Simple (2 Puntos)"""
        Ka_simple = (self.Puc - self.Pci) / (self.Tuc - self.Tci)
        Pf_simple = self.Puc + Ka_simple * (self.Tf - self.Tuc)
        return {
            'tasa': Ka_simple, 'Pf': Pf_simple, 'tipo_tasa': 'Ka (pers/año)',
            'formula': 'Pf = Puc + Ka * (Tf - Tuc)'
        }

    def _metodo_lineal_regresion(self):
        """Método 2: Lineal (Regresión)"""
        # Y = mX + b
        modelo_lin = np.polyfit(self.T_ordenados, self.P_ordenados, 1)
        Ka_lin_reg, b_lin_reg = modelo_lin[0], modelo_lin[1]
        Pf_lin_reg = (Ka_lin_reg * self.Tf) + b_lin_reg
        return {
            'tasa': Ka_lin_reg, 'Pf': Pf_lin_reg, 'tipo_tasa': 'Ka (pers/año)',
            'formula': 'Pf = (Ka_reg * Tf) + b_reg', 'b': b_lin_reg
        }

    def _metodo_geometrico_simple(self):
        """Método 3: Geométrico Simple (2 Puntos)"""
        # r = (Puc/Pci)^(1/(Tuc-Tci)) - 1
        denominador = self.Tuc - self.Tci
        if denominador == 0: return None # Evitar división por cero
        
        r_simple = (self.Puc / self.Pci)**(1 / denominador) - 1
        Pf_geo_simple = self.Puc * (1 + r_simple)**(self.Tf - self.Tuc)
        return {
            'tasa': r_simple, 'Pf': Pf_geo_simple, 'tipo_tasa': 'r (%/año)',
            'formula': 'Pf = Puc * (1 + r)^(Tf - Tuc)'
        }

    def _metodo_geometrico_regresion(self):
        """Método 4: Geométrico (Regresión Log-Lineal)"""
        # log(Y) = mX + b
        modelo_log = np.polyfit(self.T_ordenados, self.log_P_datos, 1)
        m_log_r, b_log_P0 = modelo_log[0], modelo_log[1]
        r_geo_reg = np.exp(m_log_r) - 1
        log_Pf_reg = (m_log_r * self.Tf) + b_log_P0
        Pf_geo_reg = np.exp(log_Pf_reg)
        return {
            'tasa': r_geo_reg, 'Pf': Pf_geo_reg, 'tipo_tasa': 'r (%/año)',
            'formula': 'Pf = exp( (m_log * Tf) + b_log )',
            'tasa_log': m_log_r, 'b': b_log_P0
        }

    def _metodo_logaritmico_prom_kg(self):
        """Método 5: Logarítmico (Promedio 'kg')"""
        if len(self.censos) < 3:
            return None # Este método necesita al menos 3 censos
            
        lista_de_kg = []
        for i in range(len(self.T_ordenados) - 1):
            kg_segmento = (self.log_P_datos[i+1] - self.log_P_datos[i]) / (self.T_ordenados[i+1] - self.T_ordenados[i])
            lista_de_kg.append(kg_segmento)
            
        kg_promedio = np.mean(lista_de_kg)
        r_avg_kg = np.exp(kg_promedio) - 1
        log_Pf_avg_kg = self.log_Pci + kg_promedio * (self.Tf - self.Tci)
        Pf_avg_kg = np.exp(log_Pf_avg_kg)
        return {
            'tasa': r_avg_kg, 'Pf': Pf_avg_kg, 'tipo_tasa': 'r (%/año)',
            'formula': 'Pf = exp( LnPci + kg_prom * (Tf - Tci) )',
            'tasa_log': kg_promedio
        }

    def calcular_proyecciones(self, año_proyeccion):
        """Ejecuta todos los métodos de proyección"""
        self.Tf = año_proyeccion
        
        if not self._prepare_data():
            st.error("Preparación de datos fallida. Verifica los datos del censo.")
            return False
            
        self.resultados = {
            'Lineal (Simple)': self._metodo_lineal_simple(),
            'Lineal (Regresión)': self._metodo_lineal_regresion(),
            'Geométrico (Simple)': self._metodo_geometrico_simple(),
            'Geométrico (Regresión)': self._metodo_geometrico_regresion(),
            'Logarítmico (Prom. Kg)': self._metodo_logaritmico_prom_kg()
        }
        
        # Filtrar resultados nulos (ej. Logarítmico si n < 3)
        self.resultados = {k: v for k, v in self.resultados.items() if v is not None}
        
        # Calcular promedios
        p_lineales = [v['Pf'] for k, v in self.resultados.items() if 'Lineal' in k]
        p_geometricos = [v['Pf'] for k, v in self.resultados.items() if 'Geométrico' in k]
        p_logaritmico = self.resultados.get('Logarítmico (Prom. Kg)', {}).get('Pf')
        
        self.promedios = {}
        if p_lineales:
            self.promedios['Promedio Lineal'] = np.mean(p_lineales)
        if p_geometricos:
            self.promedios['Promedio Geométrico'] = np.mean(p_geometricos)
        
        lista_promedio_general = []
        if 'Promedio Lineal' in self.promedios:
            lista_promedio_general.append(self.promedios['Promedio Lineal'])
        if 'Promedio Geométrico' in self.promedios:
            lista_promedio_general.append(self.promedios['Promedio Geométrico'])
        if p_logaritmico is not None:
            lista_promedio_general.append(p_logaritmico)
            
        if lista_promedio_general:
            self.promedios['PROMEDIO GENERAL'] = np.mean(lista_promedio_general)
        
        return True

    def generar_grafica(self):
        """Genera una gráfica de matplotlib con todas las proyecciones"""
        if not self.resultados:
            return None
            
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 1. Plotear datos históricos
        ax.scatter(self.T_ordenados, self.P_ordenados, label="Censos Históricos", color='black', zorder=10)
        
        # 2. Preparar eje X de proyección
        # (Desde el último censo hasta el año proyectado)
        años_proy = np.arange(self.Tuc, self.Tf + 1)
        
        # 3. Calcular y plotear las 5 curvas de proyección
        curvas = {}
        
        if 'Lineal (Simple)' in self.resultados:
            r = self.resultados['Lineal (Simple)']
            curvas['Lineal (Simple)'] = self.Puc + r['tasa'] * (años_proy - self.Tuc)
            ax.plot(años_proy, curvas['Lineal (Simple)'], label='Lineal (Simple)')
            
        if 'Lineal (Regresión)' in self.resultados:
            r = self.resultados['Lineal (Regresión)']
            curvas['Lineal (Regresión)'] = r['tasa'] * años_proy + r['b']
            ax.plot(años_proy, curvas['Lineal (Regresión)'], label='Lineal (Regresión)')

        if 'Geométrico (Simple)' in self.resultados:
            r = self.resultados['Geométrico (Simple)']
            curvas['Geométrico (Simple)'] = self.Puc * (1 + r['tasa'])**(años_proy - self.Tuc)
            ax.plot(años_proy, curvas['Geométrico (Simple)'], label='Geométrico (Simple)')
            
        if 'Geométrico (Regresión)' in self.resultados:
            r = self.resultados['Geométrico (Regresión)']
            curvas['Geométrico (Regresión)'] = np.exp(r['tasa_log'] * años_proy + r['b'])
            ax.plot(años_proy, curvas['Geométrico (Regresión)'], label='Geométrico (Regresión)')
            
        if 'Logarítmico (Prom. Kg)' in self.resultados:
            r = self.resultados['Logarítmico (Prom. Kg)']
            curvas['Logarítmico (Prom. Kg)'] = self.Pci * np.exp(r['tasa_log'] * (años_proy - self.Tci))
            ax.plot(años_proy, curvas['Logarítmico (Prom. Kg)'], label='Logarítmico (Prom. Kg)')

        # 4. Calcular y plotear la curva promedio
        if curvas:
            promedio_curvas = np.mean(list(curvas.values()), axis=0)
            ax.plot(años_proy, promedio_curvas, label='PROMEDIO DE CURVAS', color='red', linestyle='--', linewidth=2)
            
        ax.set_title(f'Proyección de Población ({self.Tuc} - {self.Tf})')
        ax.set_xlabel('Año')
        ax.set_ylabel('Población')
        ax.legend()
        ax.grid(True, linestyle=':', alpha=0.7)
        plt.tight_layout()
        
        # Guardar figura en un archivo temporal para el PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            fig.savefig(tmp_file.name)
            return fig, tmp_file.name

    def generar_reporte_pdf(self, grafica_path):
        """Genera reporte en PDF con los resultados y la gráfica (Sintaxis fpdf 1.7)"""
        pdf = FPDF()
        pdf.add_page()
        
        pdf.set_font("helvetica", 'B', 16)
        pdf.cell(0, 10, 'REPORTE DE PROYECCIÓN DE POBLACIÓN', ln=1, align='C')
        pdf.ln(5)
        
        # Información general
        pdf.set_font("helvetica", 'B', 12)
        pdf.cell(0, 10, 'INFORMACIÓN GENERAL', ln=1)
        pdf.set_font("helvetica", '', 10)
        pdf.cell(0, 6, f'Fecha de generación: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', ln=1)
        pdf.cell(0, 6, f'Año de Proyección (Tf): {self.Tf}', ln=1)
        pdf.ln(5)
        
        # Datos de censos
        pdf.set_font("helvetica", 'B', 12)
        pdf.cell(0, 10, 'DATOS DE CENSOS INGRESADOS', ln=1)
        pdf.set_font("helvetica", '', 10)
        for i, censo in enumerate(self.censos, 1):
            pdf.cell(0, 6, f'Censo {i}: Año {censo["año"]} - {censo["poblacion"]:,} habitantes', ln=1)
        pdf.ln(5)
        
        # Resultados por método
        pdf.set_font("helvetica", 'B', 12)
        pdf.cell(0, 10, 'RESULTADOS POR MÉTODO', ln=1)
        
        for metodo, data in self.resultados.items():
            pdf.set_font("helvetica", 'B', 10)
            pdf.cell(0, 8, f'Método: {metodo}', ln=1)
            pdf.set_font("helvetica", '', 9)
            
            tasa_str = ""
            if data['tipo_tasa'] == 'Ka (pers/año)':
                tasa_str = f"{data['tasa']:.3f} pers/año"
            else:
                tasa_str = f"{data['tasa']*100:.4f} %/año"
                
            pdf.cell(0, 5, f"Tasa (Ka o r): {tasa_str}", ln=1)
            pdf.cell(0, 5, f"Población proyectada ({self.Tf}): {int(round(data['Pf'])):,} hab.", ln=1)
            pdf.ln(3)
        
        # Promedios
        pdf.set_font("helvetica", 'B', 12)
        pdf.cell(0, 10, 'PROMEDIOS DE PROYECCIÓN', ln=1)
        pdf.set_font("helvetica", '', 10)
        
        if 'Promedio Lineal' in self.promedios:
            pdf.cell(0, 6, f"Promedio Lineales: {int(round(self.promedios['Promedio Lineal'])):,} hab.", ln=1)
        if 'Promedio Geométrico' in self.promedios:
            pdf.cell(0, 6, f"Promedio Geométricos: {int(round(self.promedios['Promedio Geométrico'])):,} hab.", ln=1)
        
        pdf.set_font("helvetica", 'B', 11)
        if 'PROMEDIO GENERAL' in self.promedios:
            pdf.cell(0, 8, f"PROMEDIO GENERAL FINAL: {int(round(self.promedios['PROMEDIO GENERAL'])):,} hab.", ln=1)
        pdf.ln(5)

        # Gráfica
        if grafica_path:
            pdf.add_page()
            pdf.set_font("helvetica", 'B', 12)
            pdf.cell(0, 10, 'GRÁFICA DE PROYECCIONES', ln=1)
            pdf.image(grafica_path, x = 10, y = None, w = 190) # Ajustar ancho a 190mm
        
        # Guardar PDF en un archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf.output(tmp_file.name)
            return tmp_file.name
def main():
    """Función principal de la aplicación Streamlit"""
    st.set_page_config(
        page_title="Proyección de Población",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Calculadora de Proyección de Población")
    st.markdown("---")
    
    # Inicializar session state
    if 'proyeccion' not in st.session_state:
        st.session_state.proyeccion = ProyeccionPoblacion()
    if 'censos' not in st.session_state:
        st.session_state.censos = []
    if 'calculo_realizado' not in st.session_state:
        st.session_state.calculo_realizado = False

    # Sidebar para ingresar datos
    with st.sidebar:
        st.header("📋 Ingreso de Datos")
        
        st.subheader("Agregar Censo")
        with st.form("censo_form"):
            año_censo = st.number_input("Año del censo", min_value=1800, max_value=2100, value=1990, step=1)
            poblacion_censo = st.number_input("Población (habitantes)", min_value=1, value=10000)
            
            if st.form_submit_button("Agregar Censo"):
                if not st.session_state.proyeccion.agregar_censo(año_censo, poblacion_censo):
                    st.error(f"El año {año_censo} ya fue ingresado.")
                else:
                    st.success(f"Censo {año_censo} agregado!")
                    st.session_state.calculo_realizado = False
        
        st.markdown("---")
        
        st.subheader("Configuración de Proyección")
        
        # Usar los datos de censos si existen
        default_tf = 2050
        min_tf = 1800
        if st.session_state.censos:
            ultimo_año = st.session_state.censos[-1]['año']
            default_tf = ultimo_año + 20
            min_tf = ultimo_año + 1

        año_proyeccion = st.number_input("Año de proyección (Tf)", min_value=min_tf, max_value=2200, value=default_tf)
        
        if st.button("Calcular Proyección", type="primary"):
            n_censos = len(st.session_state.censos)
            if n_censos < 2:
                st.error("Se necesitan al menos 2 censos para proyectar.")
            elif n_censos < 3:
                st.warning("Se calcularán 4 de 5 métodos. El 'Promedio Kg' requiere 3 censos.")
                if st.session_state.proyeccion.calcular_proyecciones(año_proyeccion):
                    st.session_state.calculo_realizado = True
            else:
                if st.session_state.proyeccion.calcular_proyecciones(año_proyeccion):
                    st.session_state.calculo_realizado = True
    
    # Contenido principal
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("Datos Ingresados")
        
        if st.session_state.censos:
            st.subheader("Censos Registrados")
            for i, censo in enumerate(st.session_state.censos, 1):
                st.write(f"**Censo {i}:** Año {censo['año']} - {censo['poblacion']:,} hab.")
            
            if st.button("Limpiar Todos los Datos"):
                st.session_state.proyeccion = ProyeccionPoblacion()
                st.session_state.censos = []
                st.session_state.calculo_realizado = False
                st.rerun()
        else:
            st.info("No hay censos registrados. Agrega al menos 2 en el panel lateral.")
    
    with col2:
        if st.session_state.calculo_realizado:
            st.header(f"Resultados de Proyección al Año {año_proyeccion}")
            
            resultados = st.session_state.proyeccion.resultados
            promedios = st.session_state.proyeccion.promedios
            
            # --- Pestañas de Resultados ---
            tab1, tab2, tab3 = st.tabs(["📊 Gráfica", "📈 Resultados Detallados", "📄 Reporte PDF"])

            with tab1:
                st.subheader("Gráfica de Proyecciones")
                fig, grafica_path = st.session_state.proyeccion.generar_grafica()
                if fig:
                    st.pyplot(fig)
                else:
                    st.error("No se pudo generar la gráfica.")

            with tab2:
                st.subheader("Proyecciones Individuales")
                cols = st.columns(3)
                i = 0
                for metodo, data in resultados.items():
                    with cols[i % 3]:
                        tasa_str = f"{data['tasa']*100:.4f} %" if 'r' in data['tipo_tasa'] else f"{data['tasa']:.2f}"
                        st.metric(
                            label=metodo,
                            value=f"{int(round(data['Pf'])):,}",
                            help=f"Tasa ({data['tipo_tasa']}): {tasa_str}"
                        )
                    i += 1
                
                st.markdown("---")
                st.subheader("Promedios de Proyección")
                
                cols = st.columns(3)
                if 'Promedio Lineal' in promedios:
                    cols[0].metric("Promedio Lineal", f"{int(round(promedios['Promedio Lineal'])):,}")
                if 'Promedio Geométrico' in promedios:
                    cols[1].metric("Promedio Geométrico", f"{int(round(promedios['Promedio Geométrico'])):,}")
                if 'PROMEDIO GENERAL' in promedios:
                    with cols[2]:
                        st.success(f"**Promedio General:**\n## {int(round(promedios['PROMEDIO GENERAL'])):,}")
                if 'PROMEDIO GENERAL' in promedios:
                    with cols[2]:
                        promedio_general_final = promedios['PROMEDIO GENERAL']
                        st.success(f"**Promedio General:**\n## {int(round(promedio_general_final)):,}")
                        
                        # --- LÍNEA CLAVE QUE DEBES AGREGAR ---
                        st.session_state.poblacion_proyectada = promedio_general_final
                        # ------------------------------------
            with tab3:
                st.subheader("Generar Reporte PDF")
                st.info("El reporte PDF incluirá todos los datos, resultados y la gráfica.")
                
                # Usar la gráfica ya generada
                if 'grafica_path' in locals():
                    with st.spinner("Generando reporte PDF..."):
                        pdf_path = st.session_state.proyeccion.generar_reporte_pdf(grafica_path)
                        
                        with open(pdf_path, "rb") as pdf_file:
                            pdf_bytes = pdf_file.read()
                        
                        st.download_button(
                            label="⬇️ Descargar Reporte PDF",
                            data=pdf_bytes,
                            file_name=f"proyeccion_poblacion_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf"
                        )
                        
                        # Limpiar archivos temporales
                        os.unlink(pdf_path)
                        os.unlink(grafica_path)
        else:
            st.info("Ingresa los datos y presiona 'Calcular Proyección' en el panel lateral.")

if __name__ == "__main__":
    main()
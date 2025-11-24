import streamlit as st
import math
from fpdf import FPDF
import tempfile
import os
from datetime import datetime

# -----------------------------------------------------------------
# FUNCIÓN PARA GENERAR EL REPORTE PDF DE DEMANDA (CORREGIDA)
# -----------------------------------------------------------------
def generar_reporte_demanda_pdf(res):
    """Genera un PDF con los resultados y fórmulas de demanda (sintaxis fpdf 1.7)"""
    pdf = FPDF()
    pdf.add_page()
    
    # Función para limpiar caracteres problemáticos
    def clean_text(text):
        if text is None:
            return ""
        if isinstance(text, (int, float)):
            return str(text)
        
        replacements = {
            '•': '-',    # Viñeta
            '´': "'",    # Acentos
            '`': "'", 
            '“': '"', 
            '”': '"',
            '–': '-',
            '—': '-',
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
            'ñ': 'n', 'Ñ': 'N',
            '°': ' '  # Grado
        }
        cleaned = str(text)
        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new)
        return cleaned
    
    pdf.set_font("helvetica", 'B', 16)
    pdf.cell(0, 10, clean_text('REPORTE DE CALCULO DE DEMANDA'), ln=1, align='C')
    pdf.ln(5)
    
    # --- 1. Parámetros de Entrada ---
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, clean_text('1. PARAMETROS DE ENTRADA'), ln=1)
    pdf.set_font("helvetica", '', 10)
    pdf.cell(0, 6, clean_text(f"Poblacion Proyectada (Pf) utilizada: {res['pop_proyectada']:,} hab."), ln=1)
    pdf.cell(0, 6, clean_text(f"Altura sobre el Nivel del Mar: {res['altura_msnm']} msnm"), ln=1)
    pdf.cell(0, 6, clean_text(f"Porcentaje de Perdidas (%p): {res['p_perdidas_pct']:.0f} %"), ln=1)
    pdf.ln(5)

    # --- 2. Cálculo de Dotaciones ---
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, clean_text('2. CALCULO DE DOTACIONES'), ln=1)
    
    # Dotación Neta
    pdf.set_font("helvetica", 'B', 10)
    pdf.cell(0, 6, clean_text("Dotacion Neta (Dneta)"), ln=1)
    pdf.set_font("helvetica", '', 10)
    pdf.cell(0, 6, clean_text(f"Segun altura {res['altura_msnm']} msnm -> Dneta = {res['dneta']} L/hab-dia"), ln=1)
    pdf.ln(3)

    # Dotación Bruta
    pdf.set_font("helvetica", 'B', 10)
    pdf.cell(0, 6, clean_text("Dotacion Bruta (Dbruta)"), ln=1)
    pdf.set_font("Courier", '', 10)
    pdf.cell(0, 6, clean_text("Dbruta = Dneta / (1 - %p)"), ln=1)
    pdf.set_font("helvetica", '', 10)
    pdf.cell(0, 6, clean_text(f"Dbruta = {res['dneta']} / (1 - {res['p_perdidas']}) = {res['dbruta']:.2f} L/hab-dia"), ln=1)
    pdf.ln(5)

    # --- 3. Cálculo de Caudales Medios ---
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, clean_text('3. CALCULO DE CAUDALES MEDIOS'), ln=1)

    # Qmr
    pdf.set_font("helvetica", 'B', 10)
    pdf.cell(0, 6, clean_text("Caudal Medio Residencial (Qmr)"), ln=1)
    pdf.set_font("Courier", '', 10)
    pdf.cell(0, 6, clean_text("Qmr = (Pf * Dbruta) / 86400"), ln=1)
    pdf.set_font("helvetica", '', 10)
    pdf.cell(0, 6, clean_text(f"Qmr = ({res['pop_proyectada']:,} * {res['dbruta']:.2f}) / 86400 = {res['qmr_ls']:.2f} L/s"), ln=1)
    pdf.ln(3)

    # QOu
    pdf.set_font("helvetica", 'B', 10)
    pdf.cell(0, 6, clean_text("Caudal Otros Usos (QOu)"), ln=1)
    pdf.set_font("Courier", '', 10)
    pdf.cell(0, 6, clean_text("QOu = Qmr * 0.10"), ln=1)
    pdf.set_font("helvetica", '', 10)
    pdf.cell(0, 6, clean_text(f"QOu = {res['qmr_ls']:.2f} * 0.10 = {res['qou_ls']:.2f} L/s"), ln=1)
    pdf.ln(3)

    # Qmd
    pdf.set_font("helvetica", 'B', 10)
    pdf.cell(0, 6, clean_text("Caudal Medio Diario (Qmd)"), ln=1)
    pdf.set_font("Courier", '', 10)
    pdf.cell(0, 6, clean_text("Qmd = Qmr + QOu"), ln=1)
    pdf.set_font("helvetica", '', 10)
    pdf.cell(0, 6, clean_text(f"Qmd = {res['qmr_ls']:.2f} + {res['qou_ls']:.2f} = {res['qmd_ls']:.2f} L/s"), ln=1)
    pdf.ln(5)

    # --- 4. Cálculo de Caudales de Diseño ---
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, clean_text('4. CALCULO DE CAUDALES DE DISEÑO'), ln=1)

    # QMD
    pdf.set_font("helvetica", 'B', 10)
    pdf.cell(0, 6, clean_text("Caudal Maximo Diario (QMD)"), ln=1)
    pdf.set_font("helvetica", '', 10)
    pdf.cell(0, 6, clean_text(f"Poblacion ({res['pop_proyectada']:,}) <= 12500 hab ? {'Si' if res['pop_proyectada'] <= 12500 else 'No'} -> Kr = {res['kr']}"), ln=1)
    pdf.set_font("Courier", '', 10)
    pdf.cell(0, 6, clean_text("QMD = Qmd * Kr"), ln=1)
    pdf.set_font("helvetica", '', 10)
    pdf.cell(0, 6, clean_text(f"QMD = {res['qmd_ls']:.2f} * {res['kr']} = {res['qmd_mayorado_ls']:.2f} L/s"), ln=1)
    pdf.ln(3)

    # Q Diseño Planta
    pdf.set_font("helvetica", 'B', 10)
    pdf.cell(0, 6, clean_text("Caudal Diseno Planta (4%)"), ln=1)
    pdf.set_font("Courier", '', 10)
    pdf.cell(0, 6, clean_text("Q_Planta = QMD * 1.04"), ln=1)
    pdf.set_font("helvetica", '', 10)
    pdf.cell(0, 6, clean_text(f"Q_Planta = {res['qmd_mayorado_ls']:.2f} * 1.04 = {res['q_diseno_planta']:.2f} L/s"), ln=1)
    pdf.ln(3)

    # QMH (SECCIÓN ACTUALIZADA CON TABLA RAS)
    pdf.set_font("helvetica", 'B', 10)
    pdf.cell(0, 6, clean_text("Caudal Maximo Horario (QMH)"), ln=1)
    
    pdf.set_font("helvetica", 'I', 9)
    pdf.cell(0, 5, clean_text("Coeficiente K2 segun nivel de complejidad (RAS):"), ln=1)
    pdf.ln(2)
    
    # TABLA DE VALORES K2 SEGÚN RAS
    pdf.set_font("helvetica", 'B', 9)
    pdf.cell(40, 6, clean_text("Nivel de Complejidad"), border=1)
    pdf.cell(25, 6, clean_text("K2"), border=1, ln=1)
    
    pdf.set_font("helvetica", '', 9)
    niveles_k2 = [
        ("Bajo", "1.6"),
        ("Medio", "1.6"), 
        ("Medio alto", "1.5"),
        ("Alto", "1.5")
    ]
    
    for nivel, valor in niveles_k2:
        pdf.cell(40, 6, clean_text(nivel), border=1)
        pdf.cell(25, 6, clean_text(valor), border=1, ln=1)
    
    pdf.ln(3)
    
    # Mostrar el K2 seleccionado
    pdf.set_font("helvetica", '', 10)
    pdf.cell(0, 6, clean_text(f"Nivel de complejidad seleccionado: {res['nivel_complejidad']} -> K2 = {res['k2']}"), ln=1)
    pdf.ln(2)
    
    # Fórmula QMH
    pdf.set_font("Courier", '', 10)
    pdf.cell(0, 6, clean_text("QMH = QMD * K2"), ln=1)
    pdf.set_font("helvetica", '', 10)
    pdf.cell(0, 6, clean_text(f"QMH = {res['qmd_mayorado_ls']:.2f} * {res['k2']} = {res['qmh_ls']:.2f} L/s"), ln=1)
    pdf.ln(5)

    # --- USOS DE CADA CAUDAL ---
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, clean_text('5. USOS PARA DISEÑO'), ln=1)
    pdf.set_font("helvetica", '', 10)
    
    pdf.cell(0, 6, clean_text(f"- PLANTA DE TRATAMIENTO: Q_Planta = {res['q_diseno_planta']:.2f} L/s"), ln=1)
    pdf.cell(0, 6, clean_text(f"- RED DE DISTRIBUCION: QMH = {res['qmh_ls']:.2f} L/s"), ln=1)
    pdf.cell(0, 6, clean_text(f"- LINEA DE CONDUCCION: QMD = {res['qmd_mayorado_ls']:.2f} L/s"), ln=1)
    pdf.cell(0, 6, clean_text(f"- TANQUES DE ALMACENAMIENTO: QMD = {res['qmd_mayorado_ls']:.2f} L/s"), ln=1)
    pdf.ln(5)

    # --- Guardar ---
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        pdf.output(tmp_file.name)
        return tmp_file.name

# -----------------------------------------------------------------
# PÁGINA PRINCIPAL DE STREAMLIT
# -----------------------------------------------------------------

st.set_page_config(
    page_title="Calculos de Demanda",
    page_icon="💧",
    layout="wide"
)

st.title("💧 Calculos de Demanda de Agua")
st.markdown("---")

# Limpiar resultados anteriores si recalculamos
def clear_results():
    if 'resultados_demanda' in st.session_state:
        del st.session_state.resultados_demanda

# -----------------------------------------------------------------
# 1. RECUPERAR O INGRESAR POBLACIÓN
# -----------------------------------------------------------------
pop_default = 10000  # Valor por defecto si no hay nada

if 'poblacion_proyectada' in st.session_state:
    pop_default = int(st.session_state.poblacion_proyectada)
    st.info(f"Poblacion pre-calculada de la pagina anterior: **{pop_default:,} hab.**")
else:
    st.warning("No se encontro poblacion calculada. Usando valor por defecto.")

# REQUERIMIENTO 1: Campo de población editable
pop_proyectada = st.number_input(
    "Poblacion Proyectada (Pf) a utilizar:",
    min_value=1,
    value=pop_default,
    step=1000,
    on_change=clear_results  # Limpia resultados si se cambia la población
)

# -----------------------------------------------------------------
# 2. FORMULARIO PARA PARÁMETROS DE DISEÑO
# -----------------------------------------------------------------
with st.form("calculo_demanda_form"):
    st.header("Parametros de Diseño")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        altura_msnm = st.number_input(
            "Altura sobre el Nivel del Mar (msnm)", 
            min_value=0, max_value=5000, value=2500, step=100,
            help="La dotacion neta se definira segun este valor (RAS)."
        )
    with col2:
        p_perdidas_pct = st.number_input(
            "Porcentaje de Perdidas (%p)", 
            value=25.0, disabled=True,
            help="Fijado al 25% (0.25) segun la solicitud."
        )
    with col3:
        # SELECTOR DE NIVEL DE COMPLEJIDAD PARA K2
        nivel_complejidad = st.selectbox(
            "Nivel de Complejidad (para K2):",
            options=["Bajo", "Medio", "Medio alto", "Alto"],
            index=1,  # Medio por defecto
            help="Seleccione segun clasificacion RAS para determinar K2"
        )

    submit_button = st.form_submit_button(label="Calcular Demandas", type="primary")

# -----------------------------------------------------------------
# 3. CÁLCULOS Y ALMACENAMIENTO DE RESULTADOS
# -----------------------------------------------------------------
if submit_button:
    
    # --- VALORES K2 SEGÚN TABLA RAS ---
    k2_valores = {
        "Bajo": 1.6,
        "Medio": 1.6,
        "Medio alto": 1.5,
        "Alto": 1.5
    }
    
    k2 = k2_valores[nivel_complejidad]
    
    # --- 1. Dotación Neta (Dneta) ---
    if altura_msnm > 2000: dneta = 120
    elif altura_msnm > 1000: dneta = 130
    else: dneta = 140
    
    # --- 2. Dotación Bruta (Dbruta) ---
    p_perdidas = p_perdidas_pct / 100.0
    dbruta = dneta / (1 - p_perdidas)
    
    # --- 3. Caudal Medio Residencial (Qmr) ---
    qmr_ls = (pop_proyectada * dbruta) / 86400
    
    # --- 4. Caudal Otros Usos (QOu) ---
    qou_ls = qmr_ls * 0.10
    
    # --- 5. Caudal Medio Diario (Qmd) ---
    qmd_ls = qmr_ls + qou_ls
    
    # --- 6. Coeficiente Kr (K1) ---
    if pop_proyectada <= 12500: kr = 1.3
    else: kr = 1.2
            
    # --- 7. Caudal Máximo Diario (QMD) ---
    qmd_mayorado_ls = qmd_ls * kr
    
    # --- 8. Caudal Diseño Planta (4% adicional) ---
    q_diseno_planta = qmd_mayorado_ls * 1.04

    # --- 9. Caudal Máximo Horario (QMH) - CON K2 SEGÚN RAS ---
    qmh_ls = qmd_mayorado_ls * k2

    # Almacenar TODOS los resultados en session_state para el PDF
    st.session_state.resultados_demanda = {
        "pop_proyectada": pop_proyectada,
        "altura_msnm": altura_msnm,
        "p_perdidas_pct": p_perdidas_pct,
        "p_perdidas": p_perdidas,
        "dneta": dneta,
        "dbruta": dbruta,
        "qmr_ls": qmr_ls,
        "qou_ls": qou_ls,
        "qmd_ls": qmd_ls,
        "kr": kr,
        "qmd_mayorado_ls": qmd_mayorado_ls,
        "q_diseno_planta": q_diseno_planta,
        "k2": k2,
        "nivel_complejidad": nivel_complejidad,
        "qmh_ls": qmh_ls
    }

# -----------------------------------------------------------------
# 4. MOSTRAR RESULTADOS Y BOTÓN DE PDF
# -----------------------------------------------------------------
if 'resultados_demanda' in st.session_state:
    res = st.session_state.resultados_demanda
    
    st.markdown("---")
    st.header("Resultados del Calculo de Demanda")
    
    # Mostrar tabla K2 en Streamlit también
    st.subheader("📊 Valores de K2 segun RAS")
    col_k2_1, col_k2_2, col_k2_3, col_k2_4 = st.columns(4)
    with col_k2_1:
        st.metric("Bajo", "1.6", delta="K2=1.6" if res['nivel_complejidad'] == "Bajo" else None)
    with col_k2_2:
        st.metric("Medio", "1.6", delta="K2=1.6" if res['nivel_complejidad'] == "Medio" else None)
    with col_k2_3:
        st.metric("Medio alto", "1.5", delta="K2=1.5" if res['nivel_complejidad'] == "Medio alto" else None)
    with col_k2_4:
        st.metric("Alto", "1.5", delta="K2=1.5" if res['nivel_complejidad'] == "Alto" else None)
    
    st.subheader("Parametros Base")
    col_res1, col_res2, col_res3 = st.columns(3)
    col_res1.metric(f"Dotacion Neta (a {res['altura_msnm']} msnm)", f"{res['dneta']} L/hab-dia")
    col_res2.metric("Porcentaje Perdidas", f"{res['p_perdidas_pct']:.0f} %")
    col_res3.metric("Dotacion Bruta", f"{res['dbruta']:.2f} L/hab-dia")

    st.subheader("Caudales Medios")
    col_res4, col_res5, col_res6 = st.columns(3)
    col_res4.metric("Caudal Medio Residencial (Qmr)", f"{res['qmr_ls']:.2f} L/s")
    col_res5.metric("Caudal Otros Usos (QOu)", f"{res['qou_ls']:.2f} L/s")
    col_res6.metric("Caudal Medio Diario (Qmd)", f"{res['qmd_ls']:.2f} L/s")

    st.subheader("Caudales de Diseño")
    col_res7, col_res8, col_res9 = st.columns(3)
    col_res7.metric("Coeficiente Maximo Diario (Kr)", f"{res['kr']}")
    col_res8.metric("Caudal Maximo Diario (QMD)", f"{res['qmd_mayorado_ls']:.2f} L/s")
    col_res9.metric("Coeficiente K2 seleccionado", f"{res['k2']}")
    
    st.metric("Caudal Maximo Horario (QMH)", f"{res['qmh_ls']:.2f} L/s")
    
    st.success(f"**Caudal de Diseño de Planta (QMD + 4%):** \n## {res['q_diseno_planta']:.2f} L/s")
    
    # REQUERIMIENTO 2: Botón para generar PDF
    st.markdown("---")
    st.subheader("Generar Reporte")
    if st.button("📄 Generar Reporte de Demanda PDF"):
        with st.spinner("Generando reporte..."):
            pdf_path = generar_reporte_demanda_pdf(res)
            
            with open(pdf_path, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
            
            st.download_button(
                label="⬇️ Descargar Reporte PDF",
                data=pdf_bytes,
                file_name=f"reporte_demanda_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )
            os.unlink(pdf_path)

elif not submit_button:
    st.info("Presiona 'Calcular Demandas' para ver los resultados.")

# Mensaje de error si la página se carga sin haber calculado la población primero
elif 'poblacion_proyectada' not in st.session_state:
    st.error("⚠️ No se ha encontrado una poblacion proyectada.")
    st.info("Por favor, ve a la pagina '1_Proyecciones' y calcula una proyeccion primero.")
    if st.button("Ir a la Calculadora Principal"):
        st.switch_page("1_Proyecciones.py")
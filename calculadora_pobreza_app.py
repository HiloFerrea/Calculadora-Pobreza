%%writefile app.py
import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from io import BytesIO

# Configuración inicial de la página
st.set_page_config(
    page_title="Estimador de Pobreza e Indigencia",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para mejorar la estética general
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 25px;
    }
    .footer {
        text-align: center;
        color: #64748B;
        font-size: 0.85rem;
        padding: 20px;
        border-top: 1px solid #E2E8F0;
        margin-top: 40px;
    }
    </style>
""", unsafe_allow_html=True)

nombres_meses = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
    7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre",
    11: "noviembre", 12: "diciembre"
}

@st.cache_data(ttl=86400)
def cargar_datos_indec():
    url = "https://www.indec.gob.ar/ftp/cuadros/sociedad/serie_cba_cbt.xls"
    resp = requests.get(url)
    if resp.status_code != 200:
        return None
    df = pd.read_excel(BytesIO(resp.content), sheet_name=0, skiprows=5)
    df.columns = [str(c).strip() for c in df.columns]
    df = df.rename(columns={
        df.columns[0]: "Fecha",
        df.columns[1]: "CBA_GBA",
        df.columns[3]: "CBT_GBA"
    })
    df = df.dropna(subset=["Fecha", "CBT_GBA"])
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    return df.dropna(subset=["Fecha"]).sort_values("Fecha")

df_indec = cargar_datos_indec()
if df_indec is None:
    st.error("Error al descargar el archivo del INDEC. Verifique su conexión.")
    st.stop()

ultimo = df_indec.iloc[-1]
periodo_dt = ultimo["Fecha"]
periodo = f"{nombres_meses[periodo_dt.month]} de {periodo_dt.year}"
cbt_gba = ultimo["CBT_GBA"]
cba_gba = ultimo["CBA_GBA"]

factores = {1: 1.00, 40: 0.803, 41: 0.836, 42: 0.942, 43: 0.983, 44: 1.167}
CBT = {r: round(cbt_gba * f, 2) for r, f in factores.items()}
CBA = {r: round(cba_gba * f, 2) for r, f in factores.items()}

etiquetas_region = {
    1: "Gran Buenos Aires (CABA y Partidos del GBA)",
    40: "Noroeste", 41: "Noreste", 42: "Cuyo", 43: "Pampeana", 44: "Patagónica"
}

def calcular_adulto_equivalente(edad, sexo):
    if edad < 0:
        raise ValueError("La edad no puede ser negativa.")
    if sexo == '2':
        if edad < 1: return 0.35
        elif edad == 1: return 0.37
        elif edad == 2: return 0.46
        elif edad == 3: return 0.51
        elif edad == 4: return 0.55
        elif edad == 5: return 0.60
        elif edad == 6: return 0.64
        elif edad == 7: return 0.66
        elif edad == 8: return 0.68
        elif edad == 9: return 0.69
        elif edad == 10: return 0.70
        elif edad == 11: return 0.72
        elif edad == 12: return 0.74
        elif edad == 13: return 0.76
        elif edad == 14: return 0.76
        elif edad in [15, 16, 17]: return 0.77
        elif 18 <= edad <= 29: return 0.76
        elif 30 <= edad <= 45: return 0.77
        elif 46 <= edad <= 60: return 0.76
        elif 61 <= edad <= 75: return 0.67
        else: return 0.63
    elif sexo == '1':
        if edad < 1: return 0.35
        elif edad == 1: return 0.37
        elif edad == 2: return 0.46
        elif edad == 3: return 0.51
        elif edad == 4: return 0.55
        elif edad == 5: return 0.60
        elif edad == 6: return 0.64
        elif edad == 7: return 0.66
        elif edad == 8: return 0.68
        elif edad == 9: return 0.69
        elif edad == 10: return 0.79
        elif edad == 11: return 0.82
        elif edad == 12: return 0.85
        elif edad == 13: return 0.90
        elif edad == 14: return 0.96
        elif edad == 15: return 1.00
        elif edad == 16: return 1.03
        elif edad == 17: return 1.04
        elif 18 <= edad <= 29: return 1.02
        elif 30 <= edad <= 45: return 1.00
        elif 46 <= edad <= 60: return 0.90
        elif 61 <= edad <= 75: return 0.83
        else: return 0.74
    else:
        raise ValueError("Sexo no reconocido.")

# SIDEBAR
with st.sidebar:
    st.header("Parámetros del Hogar")
    percepcion = st.selectbox("¿Cómo creés que está tu hogar?", [
        "3 - No estoy seguro/a",
        "1 - Creo que estamos por debajo de la línea de pobreza",
        "2 - Creo que estamos por encima"
    ], index=0)
    
    st.markdown("---")
    st.subheader("👤 Composición del Hogar")
    hogar = []
    sexo_opciones = {"Varón": "1", "Mujer": "2"}
    
    st.markdown("**Tu información:**")
    edad = st.number_input("Edad:", min_value=0, max_value=120, step=1, value=30)
    sexo_label = st.selectbox("Sexo:", options=list(sexo_opciones.keys()))
    hogar.append(calcular_adulto_equivalente(edad, sexo_opciones[sexo_label]))
    
    miembros_adicionales = st.number_input("¿Cuántas personas más viven con vos?", min_value=0, max_value=20, step=1, value=0)
    
    for i in range(int(miembros_adicionales)):
        with st.expander(f"Persona adicional {i + 1}"):
            edad_otro = st.number_input("Edad:", min_value=0, max_value=120, step=1, key=f"edad_{i}")
            sexo_otro_label = st.selectbox("Sexo:", options=list(sexo_opciones.keys()), key=f"sexo_{i}")
            hogar.append(calcular_adulto_equivalente(edad_otro, sexo_opciones[sexo_otro_label]))
            
    uae_total = sum(hogar)

    st.markdown("---")
    st.subheader("📍 Ubicación e Ingresos")
    provincias_a_region = {
        "CABA": 1, "Buenos Aires": None, "Catamarca": 40, "Jujuy": 40, "La Rioja": 40,
        "Salta": 40, "Santiago del Estero": 40, "Tucumán": 40, "Chaco": 41, "Corrientes": 41,
        "Formosa": 41, "Misiones": 41, "San Juan": 42, "Mendoza": 42, "San Luis": 42,
        "Córdoba": 43, "Entre Ríos": 43, "La Pampa": 43, "Santa Fe": 43, "Chubut": 44,
        "Neuquén": 44, "Río Negro": 44, "Santa Cruz": 44, "Tierra del Fuego": 44
    }
    
    provincia = st.selectbox("Provincia:", options=list(provincias_a_region.keys()))
    if provincia == "Buenos Aires":
        vive_in_amba = st.radio("¿Vivís en el AMBA?", ["Sí", "No"], index=1)
        region = 1 if vive_in_amba == "Sí" else 43
    else:
        region = provincias_a_region[provincia]
        
    st.caption(f"Región asignada: **{etiquetas_region[region]}**")
    ingreso_total = st.number_input("Ingreso total mensual del hogar ($):", min_value=0.0, step=1000.0, value=500000.0)
    calcular_btn = st.button("Calcular Situación", type="primary", use_container_width=True)

# PRINCIPAL
st.markdown('<p class="main-header">Estimador de Pobreza e Indigencia</p>', unsafe_allow_html=True)
st.markdown(f'<p class="sub-header">Herramienta exploratoria basada en los últimos datos oficiales del INDEC (<b>{periodo}</b>).</p>', unsafe_allow_html=True)

if calcular_btn:
    lp = CBT[region] * uae_total
    li = CBA[region] * uae_total
    fragil_monto = lp * 1.25
    medio_monto = lp * 4

    col1, col2, col3 = st.columns(3)
    col1.metric("Línea de Pobreza (CBT)", f"${lp:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    col2.metric("Línea de Indigencia (CBA)", f"${li:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    col3.metric("Ingreso Declarado", f"${ingreso_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.markdown("---")
    st.subheader("📋 Diagnóstico del Hogar")
    if ingreso_total < li:
        resultado = "indigente"
        st.error("🚨 Tu hogar se encuentra por debajo de la **línea de indigencia**.")
    elif ingreso_total < lp:
        resultado = "pobre"
        st.warning("⚠️ Tu hogar se encuentra por debajo de la **línea de pobreza**.")
    else:
        resultado = "no pobre"
        st.success("✅ Tu hogar se encuentra por **encima de la línea de pobreza**.")
        if ingreso_total <= fragil_monto:
            st.info("ℹ️ Situación **frágil**: apenas por encima de la línea de pobreza.")
        elif ingreso_total <= medio_monto:
            st.info("ℹ️ Hogar perteneciente a la **clase media**.")
        else:
            st.info("ℹ️ Estrato de **ingresos acomodados**.")

    st.subheader("📊 Análisis visual de brechas")
    fig = go.Figure()
    alcance_indigencia = min(ingreso_total, li)
    alcance_pobreza = min(max(ingreso_total - li, 0), lp - li)
    tramo_faltante = max(lp - ingreso_total, 0)

    fig.add_trace(go.Bar(y=['Hogar'], x=[alcance_indigencia], name='Ingreso Indigencia cubierto', orientation='h', marker_color='#E11D48'))
    fig.add_trace(go.Bar(y=['Hogar'], x=[alcance_pobreza], name='Ingreso Pobreza cubierto', orientation='h', marker_color='#3B82F6'))
    if tramo_faltante > 0:
        fig.add_trace(go.Bar(y=['Hogar'], x=[tramo_faltante], name='Faltante para Pobreza', orientation='h', marker_color='#CBD5E1', marker_pattern_shape="x"))

    fig.add_vline(x=li, line_dash="dot", line_color="black", annotation_text=f"Indigencia: ${li:,.0f}")
    fig.add_vline(x=lp, line_dash="dash", line_color="black", annotation_text=f"Pobreza: ${lp:,.0f}")
    fig.add_vline(x=ingreso_total, line_color="#2563EB", annotation_text=f"Ingreso: ${ingreso_total:,.0f}")

    fig.update_layout(barmode='stack', title="Comparación del ingreso frente a las líneas de corte", xaxis_title="Pesos ($)", yaxis={'showticklabels': False}, height=300, margin=dict(l=20, r=20, t=40, b=20), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("👈 Completá los datos del hogar en la barra lateral y hacé clic en **Calcular Situación** para ver los resultados.")

st.markdown("---")
st.markdown(f"""
    <div class="footer">
        Herramienta desarrollada por <b>Hilario Ferrea</b><br>
        Contacto: hiloferrea@gmail.com — hferrea@estadistica.ec.gba.gov.ar<br>
        <i>Nota: Desarrollo técnico de carácter exploratorio.</i>
    </div>
""", unsafe_allow_html=True)

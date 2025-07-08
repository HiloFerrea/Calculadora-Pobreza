import streamlit as st
import pandas as pd
import requests
from io import BytesIO


# Diccionario para traducir meses abreviados a nombres completos en español
nombres_meses = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
    7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre",
    11: "noviembre", 12: "diciembre"
}


# 1. DESCARGA SERIE CANASTA DE INDEC
url = "https://www.indec.gob.ar/ftp/cuadros/sociedad/serie_cba_cbt.xls"
st.write("Descargando archivo desde INDEC...")
resp = requests.get(url)
if resp.status_code != 200:
    st.error("Error al descargar el archivo del INDEC.")
    st.stop()

# 2. LECTURA
df = pd.read_excel(BytesIO(resp.content), sheet_name=0, skiprows=5)
df.columns = [str(c).strip() for c in df.columns]
df = df.rename(columns={
    df.columns[0]: "Fecha",
    df.columns[1]: "CBA_GBA",
    df.columns[3]: "CBT_GBA"
})
df = df.dropna(subset=["Fecha", "CBT_GBA"])
df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
df = df.dropna(subset=["Fecha"]).sort_values("Fecha")
ultimo = df.iloc[-1]
periodo_dt = ultimo["Fecha"]
periodo = f"{nombres_meses[periodo_dt.month]} de {periodo_dt.year}"
cbt_gba = ultimo["CBT_GBA"]
cba_gba = ultimo["CBA_GBA"]

# 3. CANASTAS REGIONALES
factores = {
    1: 1.00,
    40: 0.804,
    41: 0.828,
    42: 0.945,
    43: 0.984,
    44: 1.151
}
CBT = {r: round(cbt_gba * f, 2) for r, f in factores.items()}
CBA = {r: round(cba_gba * f, 2) for r, f in factores.items()}

etiquetas_region = {
    1: "Gran Buenos Aires (CABA y Partidos del GBA)",
    40: "Noroeste",
    41: "Noreste",
    42: "Cuyo",
    43: "Pampeana",
    44: "Patagónica"
}

# FUNCIONES
def calcular_adulto_equivalente(edad):
    if edad < 1:
        return 0.3
    elif edad <= 3:
        return 0.5
    elif edad <= 5:
        return 0.6
    elif edad <= 7:
        return 0.7
    elif edad <= 9:
        return 0.75
    elif edad <= 12:
        return 0.8
    elif edad <= 14:
        return 0.9
    elif edad <= 17:
        return 1.0
    elif edad <= 59:
        return 1.0
    else:
        return 0.9

# UI
st.title("Estimador de Pobreza e Indigencia")
st.write("Esta herramienta te ayuda a estimar si tu hogar está en situación de pobreza o indigencia, según quiénes lo integran y el ingreso total mensual que perciben.")

percepcion = st.radio("¿Cómo creés que está tu hogar?", [
    "1 - Creo que estamos por debajo de la línea de pobreza",
    "2 - Creo que estamos por encima",
    "3 - No estoy seguro/a"
], index=2)

hogar = []
edades = []

st.subheader("Contanos sobre vos")
edad = st.number_input("¿Qué edad tenés?", min_value=0, max_value=120, step=1)
sexo = st.selectbox("¿Cuál es tu sexo?", options=[("1", "Varón"), ("2", "Mujer")], index=0)
hogar.append(calcular_adulto_equivalente(edad))
edades.append(edad)

miembros_adicionales = st.number_input("¿Cuántas personas más viven con vos?", min_value=0, max_value=20, step=1)

for i in range(int(miembros_adicionales)):
    st.subheader(f"Datos de la persona {i + 1}")
    edad_otro = st.number_input(f"Edad:", min_value=0, max_value=120, step=1, key=f"edad_{i}")
    sexo_otro = st.selectbox("Sexo:", options=[("1", "Varón"), ("2", "Mujer")], key=f"sexo_{i}")
    hogar.append(calcular_adulto_equivalente(edad_otro))
    edades.append(edad_otro)

uae_total = sum(hogar)

st.subheader("Ubicación del hogar")

region = st.selectbox("Seleccioná la región", options=list(etiquetas_region.keys()), format_func=lambda x: etiquetas_region[x])

st.markdown(f"**Los valores de pobreza e indigencia corresponden a {periodo}**, según el último dato disponible del INDEC.")
st.markdown("Por favor, indicá el ingreso mensual total del hogar correspondiente a ese período.")

ingreso_total = st.number_input("¿Cuál es el ingreso total mensual del hogar (en pesos)?", min_value=0.0, step=100.0)


lp = CBT[region] * uae_total
li = CBA[region] * uae_total

if st.button("Calcular situación del hogar"):
    total_personas = len(hogar)
    menores_18 = sum(1 for e in edades if e < 18)
    mayores_64 = sum(1 for e in edades if e >= 65)

    st.write("## Resumen del hogar")
    st.write(f"Total de personas: {total_personas}")
    st.write(f"Adultos equivalentes (estimados): {uae_total:.2f}")
    st.write(f"Menores de 18 años: {menores_18}")
    st.write(f"Mayores de 64 años: {mayores_64}")

    st.write("## Resultado")
    st.write(f"Región: {etiquetas_region.get(region)}")
    st.write(f"Línea de pobreza: ${lp:,.2f}")
    st.write(f"Línea de indigencia: ${li:,.2f}")
    st.write(f"Ingreso del hogar: ${ingreso_total:,.2f}")

    if ingreso_total < li:
        resultado = "indigente"
        st.error("Tu hogar está por debajo de la línea de indigencia.")
    elif ingreso_total < lp:
        resultado = "pobre"
        st.warning("Tu hogar está por debajo de la línea de pobreza.")
    else:
        resultado = "no pobre"
        st.success("Tu hogar no está por debajo de la línea de pobreza.")

    st.write("### Comparación con tu percepción")
    if "1" in percepcion and resultado in ["pobre", "indigente"]:
        st.info("Sí, coincide: reconociste una situación de vulnerabilidad.")
    elif "2" in percepcion and resultado == "no pobre":
        st.info("Sí, coincide: estimamos que tu hogar no está en situación de pobreza.")
    elif "3" in percepcion:
        st.info("Ahora tenés una estimación técnica que te puede ayudar a reflexionar.")
    else:
        st.info("Hay una diferencia entre tu percepción y la estimación. Puede ser útil analizar por qué.")

    st.write("### Lecturas recomendadas")
    st.markdown("- [Pobreza 2° Semestre 2024 - DPE PBA](https://www.estadistica.ec.gba.gov.ar/dpe/images/POBREZA_2S2024.pdf)")
    st.markdown("- [Anexo metodológico](https://www.estadistica.ec.gba.gov.ar/dpe/images/POBREZA_2S2024_ANEXO_METODOLOGICO.pdf)")

    st.caption("Herramienta desarrollada por Hilario Ferrea — hiloferrea@gmail.com")

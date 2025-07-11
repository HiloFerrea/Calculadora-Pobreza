import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
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
def calcular_adulto_equivalente(edad, sexo):
    """
    Calcula el valor de adulto equivalente según edad y sexo.
    Sexo debe ser '1' para varón o '2' para mujer (como lo usa el formulario).
    """
    if edad < 0:
        raise ValueError("La edad no puede ser negativa.")

    if sexo == '2':  # Mujer
        if edad < 1:
            return 0.35
        elif edad == 1:
            return 0.37
        elif edad == 2:
            return 0.46
        elif edad == 3:
            return 0.51
        elif edad == 4:
            return 0.55
        elif edad == 5:
            return 0.60
        elif edad == 6:
            return 0.64
        elif edad == 7:
            return 0.66
        elif edad == 8:
            return 0.68
        elif edad == 9:
            return 0.69
        elif edad == 10:
            return 0.70
        elif edad == 11:
            return 0.72
        elif edad == 12:
            return 0.74
        elif edad == 13:
            return 0.76
        elif edad == 14:
            return 0.76
        elif edad in [15, 16, 17]:
            return 0.77
        elif 18 <= edad <= 29:
            return 0.76
        elif 30 <= edad <= 45:
            return 0.77
        elif 46 <= edad <= 60:
            return 0.76
        elif 61 <= edad <= 75:
            return 0.67
        else:
            return 0.63

    elif sexo == '1':  # Varón
        if edad < 1:
            return 0.35
        elif edad == 1:
            return 0.37
        elif edad == 2:
            return 0.46
        elif edad == 3:
            return 0.51
        elif edad == 4:
            return 0.55
        elif edad == 5:
            return 0.60
        elif edad == 6:
            return 0.64
        elif edad == 7:
            return 0.66
        elif edad == 8:
            return 0.68
        elif edad == 9:
            return 0.69
        elif edad == 10:
            return 0.79
        elif edad == 11:
            return 0.82
        elif edad == 12:
            return 0.85
        elif edad == 13:
            return 0.90
        elif edad == 14:
            return 0.96
        elif edad == 15:
            return 1.00
        elif edad == 16:
            return 1.03
        elif edad == 17:
            return 1.04
        elif 18 <= edad <= 29:
            return 1.02
        elif 30 <= edad <= 45:
            return 1.00
        elif 46 <= edad <= 60:
            return 0.90
        elif 61 <= edad <= 75:
            return 0.83
        else:
            return 0.74

    else:
        raise ValueError("Sexo no reconocido (usar '1' para varón o '2' para mujer').")

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

sexo_opciones = {"Varón": "1", "Mujer": "2"}


st.subheader("Contanos sobre vos")
edad = st.number_input("¿Qué edad tenés?", min_value=0, max_value=120, step=1)
sexo_label = st.selectbox("¿Cuál es tu sexo?", options=list(sexo_opciones.keys()))
sexo = sexo_opciones[sexo_label]
hogar.append(calcular_adulto_equivalente(edad, sexo))
edades.append(edad)

miembros_adicionales = st.number_input("¿Cuántas personas más viven con vos?", min_value=0, max_value=20, step=1)

for i in range(int(miembros_adicionales)):
    st.subheader(f"Datos de la persona {i + 1}")
    edad_otro = st.number_input(f"Edad:", min_value=0, max_value=120, step=1, key=f"edad_{i}")
    sexo_otro_label = st.selectbox("Sexo:", options=list(sexo_opciones.keys()), key=f"sexo_{i}")
    sexo_otro = sexo_opciones[sexo_otro_label]
    hogar.append(calcular_adulto_equivalente(edad_otro, sexo_otro))

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

    # Cálculo de tramos para el gráfico
    alcance_indigencia = min(ingreso_total, li)
    alcance_pobreza = min(max(ingreso_total - li, 0), lp - li)
    tramo_faltante = max(lp - ingreso_total, 0)
    left_val = min(ingreso_total, lp)

    color_azul = (65/255, 112/255, 153/255)
    color_rojo = (232/255, 31/255, 118/255)

    # Gráfico de barra única comparativa
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.barh([""], [alcance_indigencia], color=color_rojo, label="Hasta línea de indigencia")
    ax.barh([""], [alcance_pobreza], left=alcance_indigencia, color=color_azul, label="Entre indigencia y pobreza")
    if tramo_faltante > 0:
        ax.barh([""], [tramo_faltante], left=left_val, color="#dddddd", hatch="///", edgecolor="gray", label="Falta para alcanzar línea de pobreza")

    ax.axvline(li, color="black", linestyle=":", linewidth=1.5, label=f"Línea de indigencia (${li:,.0f})")
    ax.axvline(lp, color="black", linestyle="--", linewidth=1.5, label=f"Línea de pobreza (${lp:,.0f})")
    ax.axvline(ingreso_total, color=color_azul, linestyle="-", linewidth=2, label=f"Ingreso del hogar (${ingreso_total:,.0f})")

    ax.set_yticks([])
    ax.set_xlim(0, max(lp, ingreso_total) * 1.1)
    ax.set_xlabel("Pesos mensuales")
    fig.subplots_adjust(top=0.75)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.3), ncol=2, frameon=False, fontsize=9)
    fig.suptitle("Comparación entre ingreso del hogar y líneas de pobreza", fontsize=13, y=1.05)

    st.pyplot(fig)

    # Resultado textual
    st.write("## Resultado")
    st.write(f"Región: {etiquetas_region.get(region)}")
    st.write(f"Línea de pobreza: ${lp:,.2f}")
    st.write(f"Línea

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
    st.markdown("Para comprender en mayor profundidad cómo se define y calcula la pobreza en Argentina, así como los fundamentos metodológicos que sustentan esta herramienta, te recomendamos consultar los siguientes documentos:")
    st.caption("Los documentos que siguen explican la metodología oficial del INDEC y del sistema estadístico provincial, incluyendo los criterios de cálculo, población de referencia y valores regionales.")
    st.markdown("- [Metodología N°22 - INDEC](https://www.indec.gob.ar/ftp/cuadros/sociedad/EPH_metodologia_22_pobreza.pdf)")
    st.markdown("- [Informe de pobreza - 2° semestre 2024 (DPE PBA)](https://www.estadistica.ec.gba.gov.ar/dpe/images/POBREZA_2S2024.pdf)")
    st.markdown("- [Anexo metodológico de medición de pobreza](https://www.estadistica.ec.gba.gov.ar/dpe/images/POBREZA_2S2024_ANEXO_METODOLOGICO.pdf)")
    st.caption("Herramienta desarrollada por Hilario Ferrea — hiloferrea@gmail.com")

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

# 4. FUNCIONES
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
        raise ValueError("Sexo no reconocido (usar '1' para varón o '2' para mujer').")

# 5. Entradas

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

if st.button("Calcular situación del hogar"):
    lp = CBT[region] * uae_total
    li = CBA[region] * uae_total

    ####
    # Resultado textual
    st.write("## Resultado")
    st.write(f"**Región:** {etiquetas_region.get(region)}")
    st.write(f"**Línea de pobreza del hogar:** ${lp:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    st.write(f"**Línea de indigencia del hogar:** ${li:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    st.write(f"**Ingreso del hogar:** ${ingreso_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    # Línea de indigencia
    if ingreso_total < li:
        deficit_li = li - ingreso_total
        pct_li = deficit_li / li * 100
        st.write(f"**Déficit porcentual frente a la línea de indigencia:** {pct_li:.1f}%")
        st.write(f"**Déficit nominal frente a la línea de indigencia:** ${deficit_li:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))
    else:
        superavit_li = ingreso_total - li
        pct_li = superavit_li / li * 100
        st.write(f"**Excedente porcentual frente a la línea de indigencia:** {pct_li:.1f}%")
        st.write(f"**Excedente nominal frente a la línea de indigencia:** ${excedente_li:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))

# Línea de pobreza
    if ingreso_total < lp:
        deficit_lp = lp - ingreso_total
        pct_lp = deficit_lp / lp * 100
        st.write(f"**Déficit porcentual frente a la línea de pobreza:** {pct_lp:.1f}%")
        st.write(f"**Déficit nominal frente a la línea de pobreza:** ${deficit_lp:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))
    else:
        superavit_lp = ingreso_total - lp
        pct_lp = superavit_lp / lp * 100
        st.write(f"**Excedente porcentual frente a la línea de pobreza:** {pct_lp:.1f}%")
         st.write(f"**Excedente nominal frente a la línea de pobreza:** ${excedente_lp:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))
   
###     
    
    alcance_indigencia = min(ingreso_total, li)
    alcance_pobreza = min(max(ingreso_total - li, 0), lp - li)
    tramo_faltante = max(lp - ingreso_total, 0)
    left_val = min(ingreso_total, lp)

    color_azul = (65/255, 112/255, 153/255)
    color_rojo = (232/255, 31/255, 118/255)

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.barh([""], [alcance_indigencia], color=color_rojo)
    ax.barh([""], [alcance_pobreza], left=alcance_indigencia, color=color_azul)

    if tramo_faltante > 0:
        ax.barh([""], [tramo_faltante], left=left_val, color="#dddddd", hatch="///", edgecolor="gray")
        ax.text(left_val + tramo_faltante / 2, 0, f"Falta:\n${tramo_faltante:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                ha='center', va='center', fontsize=10, color='black',
                bbox=dict(facecolor='white', edgecolor='gray', boxstyle='round,pad=0.3'))
    elif ingreso_total > lp:
        sobra = ingreso_total - lp
        offset = max(lp * 0.1, 300000)
        ax.text(ingreso_total + offset, 0, f"Extra:\n${sobra:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                ha='left', va='center', fontsize=10, color='black',
                bbox=dict(facecolor='white', edgecolor=color_azul, boxstyle='round,pad=0.3'))

    ax.axvline(li, color="black", linestyle=":", linewidth=2)
    ax.text(li, 0, f"Línea de indigencia\n${li:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            rotation=90, va='center', ha='center', fontsize=9, color="black", backgroundcolor="white")

    ax.axvline(lp, color="black", linestyle="--", linewidth=2)
    ax.text(lp, 0, f"Línea de pobreza\n${lp:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            rotation=90, va='center', ha='center', fontsize=9, color="black", backgroundcolor="white")

    ax.axvline(ingreso_total, color=color_azul, linestyle="-", linewidth=2)
    ax.text(ingreso_total, 0, f"Ingreso del hogar\n${ingreso_total:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            rotation=90, va='center', ha='center', fontsize=9, color=color_azul, backgroundcolor="white")

    ax.set_yticks([])
    ax.set_xlim(0, max(lp, ingreso_total) * 1.25)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}".replace(",", ".")))
    ax.set_xlabel("Pesos")
    fig.subplots_adjust(top=0.75)
    fig.suptitle("Brechas entre ingreso del hogar y líneas de pobreza", fontsize=13, y=0.85)
    st.pyplot(fig)

    ###
    
    if ingreso_total < li:
        resultado = "indigente"
        st.error("Tu hogar está por debajo de la línea de indigencia.")
    elif ingreso_total < lp:
        resultado = "pobre"
        st.warning("Tu hogar está por debajo de la línea de pobreza.")
    else:
        resultado = "no pobre"
        st.success("Tu hogar no está por debajo de la línea de pobreza.")


    st.write("### Percepción vs estimación")
    if "1" in percepcion and resultado in ["pobre", "indigente"]:
        st.info("Coincide: identificaste correctamente la situación de tu hogar.")
    elif "2" in percepcion and resultado == "no pobre":
        st.info("Sí, coincide: estimamos que tu hogar no está en situación de pobreza.")
    elif "3" in percepcion:
        st.info("Este resultado puede ayudarte a poner en perspectiva tu percepción.")
    else:
        st.info("Hay una diferencia entre tu percepción y la estimación. Puede ser útil analizar por qué.")

    st.write("### Materiales de referencia")
    st.markdown("Para comprender en mayor profundidad cómo se define y calcula la pobreza en Argentina, así como los fundamentos metodológicos que sustentan esta herramienta, te recomendamos consultar los siguientes documentos:")
    st.caption("Los documentos que siguen explican la metodología oficial del INDEC y del sistema estadístico provincial, incluyendo los criterios de cálculo, población de referencia y valores regionales.")
    st.markdown("- [Metodología N°22 - INDEC](https://www.indec.gob.ar/ftp/cuadros/sociedad/EPH_metodologia_22_pobreza.pdf)")
    st.markdown("- [Informe de pobreza - 2° semestre 2024 (DPE PBA)](https://www.estadistica.ec.gba.gov.ar/dpe/images/POBREZA_2S2024.pdf)")
    st.markdown("- [Anexo metodológico de medición de pobreza](https://www.estadistica.ec.gba.gov.ar/dpe/images/POBREZA_2S2024_ANEXO_METODOLOGICO.pdf)")
    
    st.markdown(
    """
        <div style="
            border: 1px solid #ccc;
            padding: 12px 20px;
            border-radius: 10px;
            background-color: #f9f9f9;
            font-size: 0.9em;
            text-align: center;
            max-width: 600px;
            margin: auto;
        ">
            Herramienta desarrollada por <strong>Hilario Ferrea</strong><br>
            <strong>Contacto:</strong> hiloferrea@gmail.com — hferrea@estadistica.ec.gba.gov.ar
        </div>
        """,
        unsafe_allow_html=True
)



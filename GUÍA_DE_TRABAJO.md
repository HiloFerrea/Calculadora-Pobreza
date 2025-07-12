
# Guía de trabajo colaborativo – Calculadora de Pobreza

Esta guía documenta el flujo de trabajo estándar para mantener y actualizar este proyecto de Streamlit desde múltiples computadoras (por ejemplo: PC personal y PC del trabajo), asegurando sincronización y orden en GitHub y Streamlit Cloud.

---

## 1. Requisitos técnicos (solo la primera vez en una PC)

- Python 3.12 o superior
- Git
- pip
- Streamlit

Para instalar dependencias necesarias:

```bash
pip install -r requirements.txt
```

---

## 2. Antes de empezar a trabajar (siempre)

> Estos pasos aseguran que estés trabajando con la última versión del proyecto.

1. Abrí la terminal
2. Entrá a la carpeta del proyecto:

```bash
cd ~/Documents/Calculadora-Pobreza
```

3. Descargá los últimos cambios del repositorio:

```bash
git pull origin main
```

---

## 3. Durante el trabajo

- Editá los archivos que necesites (`calculadora_pobreza_app.py`, `requirements.txt`, etc.)
- Podés ejecutar la app localmente con:

```bash
streamlit run calculadora_pobreza_app.py
```

- Usá `Ctrl + C` para detener la app cuando quieras liberar la terminal

---

## 4. Guardar y subir los cambios a GitHub

> Hacé esto siempre que termines de trabajar para mantener el repositorio actualizado.

1. Agregá los archivos modificados:

```bash
git add .
```

2. Hacé un commit con un mensaje claro:

```bash
git commit -m "Actualizo cálculos y añado validación de ingresos"
```

3. Subí los cambios a GitHub:

```bash
git push origin main
```

🛑 Si es tu primera vez usando Git en esta computadora, configurá tu nombre y mail así:

```bash
git config --global user.name "Hilario Ferrea"
git config --global user.email "hiloferrea@gmail.com"
```

---

## 5. Ver los cambios en Streamlit Cloud

> Streamlit Cloud detecta automáticamente los cambios y actualiza la app.

1. Ingresá al link público (ejemplo):

```
https://hiloferrea-calculadora-pobreza.streamlit.app
```

2. Si algo no carga, probá refrescar o revisá los logs de errores.

---

## 6. Si agregás nuevas bibliotecas

> Para que funcionen en la otra PC o en Streamlit Cloud:

1. Instalá la biblioteca localmente (ejemplo):

```bash
pip install xlrd
```

2. Actualizá `requirements.txt`:

```bash
pip freeze > requirements.txt
```

3. Subí los cambios como siempre (`git add`, `commit`, `push`)

---

## 7. Errores comunes

- **ModuleNotFoundError** → Instalá la dependencia faltante con `pip install ...`
- **File does not exist** → Asegurate de estar en la carpeta correcta con `cd`
- **LF will be replaced by CRLF** → Solo un aviso de Git, no es un error

---

## 8. Buenas prácticas

- Siempre hacé `git pull` antes de empezar
- Nunca trabajes en dos computadoras a la vez sin sincronizar
- Usá commits con mensajes claros
- Si algo no anda, **probá correr `streamlit run` desde cero y revisar los errores**

---

## 9. Estructura esperada del proyecto

```
Calculadora-Pobreza/
├── calculadora_pobreza_app.py
├── requirements.txt
├── GUÍA_DE_TRABAJO.md
├── README.md
└── otros archivos auxiliares...
```

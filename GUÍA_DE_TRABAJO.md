# ✅ Guía de trabajo para proyecto Streamlit con Git y Cloud

## 🔁 ANTES DE TRABAJAR (sincronizar cambios)

```bash
cd ~/Documents/Calculadora-Pobreza
git pull origin main
```

---

## 🧑‍💻 DURANTE EL TRABAJO

- Editar `calculadora_pobreza_app.py` u otros archivos
- Probar localmente:

```bash
streamlit run calculadora_pobreza_app.py
```

---

## ⬆️ DESPUÉS DE TRABAJAR (guardar y subir cambios)

```bash
git add .
git commit -m "Cambios desde mi PC personal/trabajo"
git push origin main
```

---

## 🌍 VER APP ONLINE

- Visitar el link de Streamlit Cloud:  
  `https://tu-app.streamlit.app` *(reemplace este link si es necesario)*

---

## 📦 EXTRA: actualizar dependencias

Si instalás nuevas librerías:

```bash
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Actualizo dependencias"
git push origin main
```

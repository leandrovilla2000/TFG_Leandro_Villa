import sys
import os
import streamlit as st
import tkinter as tk
from tkinter import filedialog

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from pipeline import final_pipeline_rag
from loaders import load_documents

st.title("🔍 Asistente Forense - Generador de Contraseñas")

def seleccionar_carpeta():
    root = tk.Tk()
    root.withdraw()
    carpeta = filedialog.askdirectory()
    return carpeta

if st.button("📂 Seleccionar carpeta de documentos"):
    carpeta = seleccionar_carpeta()
    if carpeta:
        st.session_state["path"] = carpeta

path = st.session_state.get("path", "")
st.text_input("Ruta seleccionada", value=path, disabled=True)

if "question" not in st.session_state:
    st.session_state.question = ""

st.text_area(
    "🧠 Escribe tu pregunta",
    placeholder="¿Qué idiomas habla el usuario?",
    key="question"
)

if st.button("Analizar"):
    if path:
        with st.spinner("Procesando..."):
            docs = load_documents(path) 
            result = final_pipeline_rag(st.session_state.question, docs)
            st.success("✅ Análisis completado")
            st.write(result)
    else:
        st.warning("Por favor, selecciona una carpeta.")

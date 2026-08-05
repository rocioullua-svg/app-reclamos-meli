import streamlit as st
import pandas as pd
from datetime import date

# Configuramos la página
st.set_page_config(page_title="Gestión de Reclamos ML", page_icon="📦", layout="centered")

st.title("📦 Sistema de Reclamos - Mercado Libre")
st.markdown("Carga los reclamos diarios para analizar las métricas al final del día.")

# Creamos el formulario web
with st.form("formulario_reclamos"):
    st.subheader("Cargar Nuevo Reclamo")
    
    # Dividimos en dos columnas para que se vea más profesional
    col1, col2 = st.columns(2)
    
    with col1:
        id_venta = st.text_input("ID Venta:")
        sku = st.text_input("SKU:")
        categoria = st.selectbox("Categoría:", ["Solicitudes de cancelación", "Demoras en el despacho", "Problemas con los productos"])
        agente = st.text_input("Tu Nombre (Agente):")
        
    with col2:
        motivo = st.text_input("Motivo exacto:")
        responsabilidad = st.selectbox("Culpa de:", ["Error de gestion", "Mercado Libre / Correo", "Comprador", "Deposito (error despacho)", "Falla de producto" ])
        estado = st.selectbox("Estado:", ["Vence hoy", "Próximo por atender", "Pendiente del comprador", "Resuelto"])
        
    # El botón para enviar
    submit = st.form_submit_button("Guardar Reclamo", type="primary")

# Qué pasa cuando aprietan el botón
if submit:
    if id_venta == "" or sku == "":
        st.error("⚠️ Por favor completa al menos el ID de Venta y el SKU.")
    else:
        st.success(f"✅ ¡El reclamo de la venta {id_venta} parece estar bien! (Nota: En el próximo paso conectaremos esto al Google Sheets para guardarlo de verdad).")

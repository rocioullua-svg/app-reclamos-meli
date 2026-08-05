import streamlit as st
import pandas as pd
from datetime import date
import gspread
import json

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Gestión de Reclamos ML", page_icon="📦", layout="centered")

# --- CONEXIÓN A GOOGLE SHEETS ---
# Usamos caché para que la app no se ponga lenta al recargar
@st.cache_resource
def conectar_sheets():
    # Leemos la llave secreta que guardamos en Streamlit
    credenciales = json.loads(st.secrets["google_credentials"])
    gc = gspread.service_account_from_dict(credenciales)
    # Abrimos tu Excel (Asegúrate de que se llame exactamente así en tu Google Drive)
    planilla = gc.open("Base_Reclamos_ML")
    return planilla.sheet1

hoja = conectar_sheets()

# --- INTERFAZ WEB ---
st.title("📦 Sistema de Reclamos - Mercado Libre")
st.markdown("Carga los reclamos diarios. Los datos se enviarán directamente a tu Google Sheets.")

with st.form("formulario_reclamos"):
    st.subheader("Cargar Nuevo Reclamo")
    
    col1, col2 = st.columns(2)
    
    with col1:
        id_venta = st.text_input("ID Venta:")
        sku = st.text_input("SKU:")
        categoria = st.selectbox("Categoría:", ["Solicitudes de cancelación", "Demoras en el despacho", "Problemas con los productos"])
        agente = st.text_input("Tu Nombre (Agente):")
        
    with col2:
        motivo = st.text_input("Motivo exacto:")
        responsabilidad = st.selectbox("Culpa de:", ["Error de Gestion", " Correo", "Comprador", "Falla de producto", "Deposito(Error despacho)"])
        estado = st.selectbox("Estado:", ["Vence hoy", "Próximo por atender", "Pendiente del comprador", "Resuelto"])
        
    submit = st.form_submit_button("Guardar Reclamo", type="primary")

# --- QUÉ PASA AL GUARDAR ---
if submit:
    if id_venta == "" or sku == "":
        st.error("⚠️ Por favor completa al menos el ID de Venta y el SKU.")
    else:
        # Preparamos la fecha de hoy
        hoy = date.today().strftime("%Y-%m-%d")
        fecha_res = hoy if estado == "Resuelto" else ""
        
        # Armamos la fila exacta con el mismo orden que tu Excel
        nueva_fila = [
            hoy,                # Fecha_Ingreso
            id_venta,           # ID_Venta
            sku,                # SKU
            categoria,          # Categoria_Principal
            motivo,             # Motivo_Especifico
            responsabilidad,    # Responsabilidad
            estado,             # Estado
            "Sí",               # Afecta_Reputacion (Fijo por ahora)
            agente,             # Agente
            fecha_res           # Fecha_Resolucion
        ]
        
        # Enviamos la fila a Google Sheets
        hoja.append_row(nueva_fila)
        
        st.success(f"✅ ¡Éxito! El reclamo de la venta {id_venta} se guardó en Google Sheets.")

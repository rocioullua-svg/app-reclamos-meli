import streamlit as st
import pandas as pd
from datetime import date
import gspread
import json

# --- CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(page_title="Gestión de Reclamos ML", page_icon="📦", layout="wide")

# CSS para darle estilo Mercado Libre
st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #ffe600; 
        color: #2d3277; 
        border-radius: 8px;
        border: none;
        font-weight: bold;
        width: 100%;
    }
    div.stButton > button:first-child:hover {
        background-color: #2d3277;
        color: #ffe600;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONEXIÓN A GOOGLE SHEETS ---
@st.cache_resource(ttl=60) # Recarga los datos cada 60 segundos
def conectar_sheets():
    credenciales = json.loads(st.secrets["google_credentials"])
    gc = gspread.service_account_from_dict(credenciales)
    planilla = gc.open("Base_Reclamos_ML")
    return planilla.sheet1

hoja = conectar_sheets()

# --- LECTURA DE DATOS PARA EL DASHBOARD ---
# Descargamos los datos del Excel
datos = hoja.get_all_records()
df = pd.DataFrame(datos)

hoy = date.today().strftime("%Y-%m-%d")

# Inicializamos las variables por si el Excel está vacío
empezamos_dia = 0
nuevos_hoy = 0
resueltos_hoy = 0
pendientes_actuales = 0

if not df.empty:
    # Convertimos las columnas a texto para evitar errores
    df['Fecha_Ingreso'] = df['Fecha_Ingreso'].astype(str)
    df['Fecha_Resolucion'] = df['Fecha_Resolucion'].astype(str)
    df['Estado'] = df['Estado'].astype(str)

    nuevos_hoy = len(df[df['Fecha_Ingreso'] == hoy])
    resueltos_hoy = len(df[df['Fecha_Resolucion'] == hoy])
    pendientes_actuales = len(df[df['Estado'] != 'Resuelto'])
    
    # La matemática de inicio del día: 
    # Los que hay ahora + los que resolvimos hoy - los nuevos que entraron hoy
    empezamos_dia = pendientes_actuales + resueltos_hoy - nuevos_hoy

# --- INTERFAZ WEB ---
st.title("📦 Panel de Reclamos - Mercado Libre")

# 1. EL DASHBOARD (MÉTRICAS)
st.subheader("📊 Resumen de Hoy")
col_a, col_b, col_c, col_d = st.columns(4)

with col_a:
    st.metric(label="Arrancamos el día con:", value=empezamos_dia)
with col_b:
    st.metric(label="⚠️ Entraron hoy:", value=nuevos_hoy)
with col_c:
    st.metric(label="✅ Resueltos hoy:", value=resueltos_hoy)
with col_d:
    st.metric(label="🔥 PENDIENTES TOTALES:", value=pendientes_actuales)

st.divider() # Una línea separadora

# 2. EL FORMULARIO DE CARGA
with st.form("formulario_reclamos"):
    st.subheader("📝 Cargar / Actualizar Reclamo")
    
    col1, col2 = st.columns(2)
    
    with col1:
        id_venta = st.text_input("ID Venta:")
        sku = st.text_input("SKU:")
        categoria = st.selectbox("Categoría:", ["Solicitudes de cancelación", "Demoras en el despacho", "Problemas con los productos"])
        agente = st.text_input("Tu Nombre (Agente):")
        
    with col2:
        motivo = st.text_input("Motivo exacto:")
        responsabilidad = st.selectbox("Culpa de:", ["Vendedor", "Mercado Libre / Correo", "Comprador"])
        estado = st.selectbox("Estado:", ["Vence hoy", "Próximo por atender", "Pendiente del comprador", "Resuelto"])
        
    submit = st.form_submit_button("Guardar Reclamo")

# --- QUÉ PASA AL GUARDAR ---
if submit:
    if id_venta == "" or sku == "":
        st.error("⚠️ Por favor completa al menos el ID de Venta y el SKU.")
    else:
        fecha_res = hoy if estado == "Resuelto" else ""
        
        nueva_fila = [
            hoy, id_venta, sku, categoria, motivo, 
            responsabilidad, estado, "Sí", agente, fecha_res
        ]
        
        hoja.append_row(nueva_fila)
        st.success(f"✅ ¡Guardado! Actualiza la página (F5) para ver los números reflejados en el panel de arriba.")

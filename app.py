import streamlit as st
import pandas as pd
from datetime import date
import gspread
import json

# --- CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(page_title="Gestión de Reclamos ML", page_icon="📦", layout="wide")

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
datos = hoja.get_all_records()
df = pd.DataFrame(datos)

hoy = date.today().strftime("%Y-%m-%d")

# ==========================================
# --- MENÚ LATERAL (SIDEBAR) ---
# ==========================================
st.sidebar.title("⚙️ Menú Principal")

# Iconos actualizados y nueva opción agregada
opcion = st.sidebar.radio(
    "Navegación:",
    ["📄 Cargar Reclamo", "📦 Cargar Envío Erróneo", "📊 Resumen Diario", "🗂️ Historial Completo"]
)

st.sidebar.divider()
st.sidebar.caption("Aplicación conectada a Google Sheets")

# ==========================================
# --- VISTA 1: CARGAR RECLAMO ---
# ==========================================
if opcion == "📄 Cargar Reclamo":
    st.title("📄 Cargar / Actualizar Reclamo")
    
    with st.form("formulario_reclamos"):
        col1, col2 = st.columns(2)
        
        with col1:
            id_venta = st.text_input("ID Venta:")
            sku = st.text_input("SKU:")
            categoria = st.selectbox("Categoría:", ["Solicitudes de cancelación", "Demoras en el despacho", "Problemas con los productos"])
            agente = st.text_input("Tu Nombre (Agente):")
            
        with col2:
            motivo = st.text_input("Motivo exacto:")
            responsabilidad = st.selectbox("Culpa de:", ["Error de Gestion", "Correo", "Comprador", "Error de despacho (Deposito)", "Falla de producto"])
            estado = st.selectbox("Estado:", ["Vence hoy", "Próximo por atender", "Pendiente del comprador", "Resuelto"])
            
        submit = st.form_submit_button("Guardar Reclamo")

    if submit:
        if id_venta == "" or sku == "":
            st.error("⚠️ Por favor completa al menos el ID de Venta y el SKU.")
        else:
            fecha_res = hoy if estado == "Resuelto" else ""
            nueva_fila = [hoy, id_venta, sku, categoria, motivo, responsabilidad, estado, "Sí", agente, fecha_res]
            hoja.append_row(nueva_fila)
            st.success("✅ ¡Guardado con éxito! (Nota: Ve a 'Historial' para ver el reclamo cargado).")

# ==========================================
# --- VISTA 2: CARGAR ENVÍO ERRÓNEO ---
# ==========================================
elif opcion == "📦 Cargar Envío Erróneo":
    st.title("📦 Cargar Envío Erróneo")
    st.markdown("Registra aquí los problemas específicos relacionados con la logística y los envíos.")
    
    with st.form("formulario_envios_erroneos"):
        col1, col2 = st.columns(2)
        
        with col1:
            id_venta = st.text_input("ID Venta:")
            sku = st.text_input("SKU:")
            agente = st.text_input("Tu Nombre (Agente):")
            
        with col2:
            motivo = st.text_input("Detalle del error (Ej: Dirección incorrecta, Extraviado):")
            responsabilidad = st.selectbox("Responsabilidad:", ["Correo / Transportista", "Error de despacho (Deposito)", "Comprador"])
            estado = st.selectbox("Estado:", ["En gestión con correo", "Devolución en camino", "Resuelto"])
            
        submit_envio = st.form_submit_button("Guardar Envío Erróneo")

    if submit_envio:
        if id_venta == "" or sku == "":
            st.error("⚠️ Por favor completa al menos el ID de Venta y el SKU.")
        else:
            fecha_res = hoy if estado == "Resuelto" else ""
            # Se mantiene la misma estructura de columnas de tu Google Sheet
            # Categoría se fija automáticamente como "Envío Erróneo"
            nueva_fila = [hoy, id_venta, sku, "Envío Erróneo", motivo, responsabilidad, estado, "Sí", agente, fecha_res]
            hoja.append_row(nueva_fila)
            st.success("✅ ¡Envío erróneo guardado con éxito!")

# ==========================================
# --- VISTA 3: RESUMEN DIARIO ---
# ==========================================
elif opcion == "📊 Resumen Diario":
    st.title("📊 Resumen de Operaciones de Hoy")
    
    empezamos_dia, nuevos_hoy, resueltos_hoy, pendientes_actuales = 0, 0, 0, 0
    
    if not df.empty:
        df['Fecha_Ingreso'] = df['Fecha_Ingreso'].astype(str)
        df['Fecha_Resolucion'] = df['Fecha_Resolucion'].astype(str)
        df['Estado'] = df['Estado'].astype(str)

        nuevos_hoy = len(df[df['Fecha_Ingreso'] == hoy])
        resueltos_hoy = len(df[df['Fecha_Resolucion'] == hoy])
        pendientes_actuales = len(df[df['Estado'] != 'Resuelto'])
        empezamos_dia = pendientes_actuales + resueltos_hoy - nuevos_hoy
        
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        st.metric(label="Arrancamos con:", value=empezamos_dia)
    with col_b:
        st.metric(label="⚠️ Entraron hoy:", value=nuevos_hoy)
    with col_c:
        st.metric(label="✅ Resueltos hoy:", value=resueltos_hoy)
    with col_d:
        st.metric(label="🔥 PENDIENTES TOTALES:", value=pendientes_actuales)

# ==========================================
# --- VISTA 4: HISTORIAL COMPLETO ---
# ==========================================
elif opcion == "🗂️ Historial Completo":
    st.title("🗂️ Historial de Reclamos y Envíos")
    st.markdown("Aquí puedes visualizar toda tu base de datos tal cual está en Excel.")
    
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Aún no hay registros en la base de datos.")

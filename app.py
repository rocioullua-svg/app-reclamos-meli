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
    .stCheckbox label {
        font-size: 15px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONEXIÓN A GOOGLE SHEETS ---
@st.cache_resource(ttl=60)
def conectar_sheets():
    credenciales = json.loads(st.secrets["google_credentials"])
    gc = gspread.service_account_from_dict(credenciales)
    planilla = gc.open("Base_Reclamos_ML")
    
    hoja_principal = planilla.sheet1
    
    # Intentamos conectar a una pestaña específica para los envíos erróneos
    try:
        hoja_envios = planilla.worksheet("Envios_Erroneos")
    except:
        hoja_envios = hoja_principal
        
    return hoja_principal, hoja_envios

hoja, hoja_envios = conectar_sheets()
datos = hoja.get_all_records()
df = pd.DataFrame(datos)

hoy = date.today().strftime("%Y-%m-%d")

# ==========================================
# --- MENÚ LATERAL (SIDEBAR) ---
# ==========================================
st.sidebar.title("⚙️ Menú Principal")

opcion = st.sidebar.radio(
    "Navegación:",
    [
        "🗓️ Agenda de Tareas",
        "📄 Cargar Reclamo", 
        "📦 Cargar Envío Erróneo", 
        "📊 Resumen Diario", 
        "🗂️ Historial Completo"
    ]
)

st.sidebar.divider()
st.sidebar.caption("Aplicación conectada a Google Sheets")

# ==========================================
# --- VISTA 1: AGENDA DE TAREAS ---
# ==========================================
if opcion == "🗓️ Agenda de Tareas":
    st.title("🗓️ Agenda Semanal de Tareas")
    st.markdown("Organización de turnos y responsabilidades de Atención al Cliente.")
    
    # Estructura de la agenda extraída del Excel
    agenda = {
        "Lunes": {
            "Gonzalo": {
                "09:00 - 13:30": ["Preguntas", "Postventa", "Envios retiros depo", "Cambios cargados en YiQi", "Pendientes Guardia"],
                "13:30 - 18:00": ["Reclamos", "Gmail", "NC Fravega (MAIL)", "Liveconnect/agent"]
            },
            "Lucas": {
                "09:00 - 13:30": ["Reclamos", "Gmail", "NC Fravega (MAIL)", "Liveconnect/agent", "Retiros Flexit"],
                "13:30 - 18:00": ["Preguntas", "Postventa", "Envios retiros depo", "Pendientes Guardia"]
            }
        },
        "Martes": {
            "Gonzalo": {
                "09:00 - 13:30": ["Reclamos", "Gmail", "NC Fravega (MAIL)", "Liveconnect/agent", "Retiros Flexit"],
                "13:30 - 18:00": ["Preguntas", "Postventa", "Cierre caja Pos"]
            },
            "Lucas": {
                "09:00 - 13:30": ["Preguntas", "Postventa", "Envios retiros depo", "Cambios cargados en YiQi", "Pendientes Guardia"],
                "13:30 - 18:00": ["Reclamos", "Gmail", "NC Fravega (MAIL)", "Liveconnect/agent"]
            }
        },
        "Miércoles": {
            "Gonzalo": {
                "09:00 - 13:30": ["Preguntas", "Postventa", "Envios retiros depo", "Cambios cargados en YiQi", "Pendientes Guardia"],
                "13:30 - 18:00": ["Reclamos", "Gmail", "NC Fravega (MAIL)", "Liveconnect/agent"]
            },
            "Lucas": {
                "09:00 - 13:30": ["Reclamos", "Gmail", "NC Fravega (MAIL)", "Liveconnect/agent", "Retiros Flexit"],
                "13:30 - 18:00": ["Preguntas", "Postventa", "Envios retiros depo", "Pendientes Guardia"]
            }
        },
        "Jueves": {
            "Gonzalo": {
                "09:00 - 13:30": ["Reclamos", "Gmail", "NC Fravega (MAIL)", "Liveconnect/agent", "Retiros Flexit"],
                "13:30 - 18:00": ["Preguntas", "Postventa", "Envios retiros depo", "Cierre caja Pos"]
            },
            "Lucas": {
                "09:00 - 13:30": ["Preguntas", "Postventa", "Envios retiros depo", "Cambios cargados en YiQi", "Pendientes Guardia"],
                "13:30 - 18:00": ["Reclamos", "Gmail", "NC Fravega (MAIL)", "Liveconnect/agent"]
            }
        },
        "Viernes": {
            "Gonzalo": {
                "09:00 - 13:30": ["Preguntas", "Postventa", "Envios retiros depo", "Cambios cargados en YiQi", "Pendientes Guardia"],
                "13:30 - 18:00": ["Reclamos", "Gmail", "NC Fravega (MAIL)", "Liveconnect/agent"]
            },
            "Lucas": {
                "09:00 - 13:30": ["Reclamos", "Gmail", "NC Fravega (MAIL)", "Liveconnect/agent", "Retiros Flexit"],
                "13:30 - 18:00": ["Preguntas", "Postventa", "Envios retiros depo", "Pendientes Guardia"]
            }
        }
    }

    # Crear pestañas para los días de la semana
    dias = list(agenda.keys())
    tabs = st.tabs(dias)

    # Llenar cada pestaña con las tareas correspondientes
    for i, tab in enumerate(tabs):
        dia_actual = dias[i]
        with tab:
            st.subheader(f"📅 Planilla del {dia_actual}")
            
            # Dividir en dos columnas para Gonzalo y Lucas
            col_gonza, col_lucas = st.columns(2)
            
            # --- Tareas de Gonzalo ---
            with col_gonza:
                st.markdown("### 👨‍💻 Gonzalo")
                
                # Turno Mañana
                st.info("**Mañana (09:00 - 13:30)**")
                for tarea in agenda[dia_actual]["Gonzalo"]["09:00 - 13:30"]:
                    st.checkbox(tarea, key=f"G_M_{dia_actual}_{tarea}")
                
                # Turno Tarde
                st.warning("**Tarde (13:30 - 18:00)**")
                for tarea in agenda[dia_actual]["Gonzalo"]["13:30 - 18:00"]:
                    st.checkbox(tarea, key=f"G_T_{dia_actual}_{tarea}")

            # --- Tareas de Lucas ---
            with col_lucas:
                st.markdown("### 👨‍💻 Lucas")
                
                # Turno Mañana
                st.info("**Mañana (09:00 - 13:30)**")
                for tarea in agenda[dia_actual]["Lucas"]["09:00 - 13:30"]:
                    st.checkbox(tarea, key=f"L_M_{dia_actual}_{tarea}")
                
                # Turno Tarde
                st.warning("**Tarde (13:30 - 18:00)**")
                for tarea in agenda[dia_actual]["Lucas"]["13:30 - 18:00"]:
                    st.checkbox(tarea, key=f"L_T_{dia_actual}_{tarea}")

# ==========================================
# --- VISTA 2: CARGAR RECLAMO ---
# ==========================================
elif opcion == "📄 Cargar Reclamo":
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
# --- VISTA 3: CARGAR ENVÍO ERRÓNEO ---
# ==========================================
elif opcion == "📦 Cargar Envío Erróneo":
    st.title("📦 Cargar Envío Erróneo")
    st.markdown("Registro de productos cruzados o mal enviados según el formato operativo.")
    
    with st.form("formulario_envios_erroneos"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            agente = st.text_input("Agente:")
            canal = st.selectbox("Canal:", ["MELI", "FLEX", "FULL", "WEB"])
            tienda = st.text_input("Tienda:", value="G24HS")
            
        with col2:
            nro_venta = st.text_input("NRO VENTA:")
            sku = st.text_input("SKU:")
            afecto_rep = st.selectbox("Afectó Rep:", ["NO", "SI"])
            
        with col3:
            comentarios = st.text_area("Comentarios:", height=130)
            
        submit_envio = st.form_submit_button("Guardar Envío Erróneo")

    if submit_envio:
        if nro_venta == "" or sku == "":
            st.error("⚠️ Por favor completa al menos el NRO VENTA y el SKU.")
        else:
            nueva_fila_envio = [agente, canal, tienda, nro_venta, sku, afecto_rep, comentarios]
            hoja_envios.append_row(nueva_fila_envio)
            st.success("✅ ¡Envío erróneo guardado con éxito!")

# ==========================================
# --- VISTA 4: RESUMEN DIARIO ---
# ==========================================
elif opcion == "📊 Resumen Diario":
    st.title("📊 Resumen de Operaciones de Hoy")
    
    empezamos_dia, nuevos_hoy, resueltos_hoy, pendientes_actuales = 0, 0, 0, 0
    
    if not df.empty and 'Fecha_Ingreso' in df.columns:
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
# --- VISTA 5: HISTORIAL COMPLETO ---
# ==========================================
elif opcion == "🗂️ Historial Completo":
    st.title("🗂️ Historial de Reclamos")
    st.markdown("Aquí puedes visualizar toda tu base de datos tal cual está en Excel.")
    
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Aún no hay registros en la base de datos.")

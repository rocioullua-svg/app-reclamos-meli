import streamlit as st
import pandas as pd
from datetime import date
import gspread
import json

# --- CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(page_title="Gestión de Reclamos", page_icon="📦", layout="wide", initial_sidebar_state="expanded")

# Inyección de CSS: Estilo Claro (CRM) y Fuente Inter
st.markdown("""
    <style>
    /* Importar fuente Inter desde Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

    /* Aplicar fuente a toda la aplicación */
    html, body, [class*="css"], .stApp, p, span, div, h1, h2, h3, h4, h5, h6, label, input, button, textarea, select {
        font-family: 'Inter', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
    }

    /* Fondo principal y tipografía */
    .stApp {
        background-color: #f4f5f7;
        color: #202124;
    }
    
    /* Barra lateral */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e0e0e0 !important;
    }
    
    /* Contenedor del Formulario y Métricas (Tarjetas blancas) */
    [data-testid="stForm"], [data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    
    /* Estilo de los Inputs (Texto, Select, Textarea) */
    div[data-baseweb="input"] > div, 
    div[data-baseweb="select"] > div, 
    div[data-baseweb="textarea"] > div {
        background-color: #f9f9f9 !important;
        border-radius: 20px !important;
        border: 1px solid #dcdcdc !important;
        color: #202124 !important;
        padding: 2px 12px;
        transition: border-color 0.2s ease;
    }
    
    /* Efecto Focus en los Inputs */
    div[data-baseweb="input"] > div:focus-within, 
    div[data-baseweb="select"] > div:focus-within, 
    div[data-baseweb="textarea"] > div:focus-within {
        border-color: #2563eb !important;
        background-color: #ffffff !important;
        box-shadow: none !important;
    }
    
    /* Botón Principal (Azul, bordes redondeados) */
    div.stButton > button {
        background-color: #2563eb !important;
        color: white !important;
        border-radius: 24px !important;
        border: none !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        transition: all 0.2s ease !important;
        width: 100%;
        margin-top: 15px;
    }
    
    div.stButton > button:hover {
        background-color: #1d4ed8 !important;
        box-shadow: 0 4px 10px rgba(37, 99, 235, 0.2) !important;
        transform: translateY(-1px);
    }
    
    /* Estilo de los Checkboxes y textos generales */
    .stCheckbox label {
        font-size: 14px !important;
        color: #202124 !important;
    }
    h1, h2, h3, p, label {
        color: #202124 !important;
    }
    
    /* Pestañas (Tabs) */
    button[data-baseweb="tab"] {
        color: #5f6368 !important;
    }
    button[aria-selected="true"] {
        color: #2563eb !important;
        font-weight: 600 !important;
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
    
    # Intentamos conectar a la pestaña "Envios_Erroneos". 
    # Si no existe, la crea automáticamente con sus encabezados.
    try:
        hoja_envios = planilla.worksheet("Envios_Erroneos")
    except gspread.exceptions.WorksheetNotFound:
        hoja_envios = planilla.add_worksheet(title="Envios_Erroneos", rows="1000", cols="10")
        hoja_envios.append_row(["Agente", "Canal", "Tienda", "NRO VENTA", "SKU", "Afectó Rep", "Comentarios"])
    except Exception:
        # Falla de seguridad por si ocurre otro tipo de error
        hoja_envios = hoja_principal
        
    return hoja_principal, hoja_envios

hoja, hoja_envios = conectar_sheets()
datos = hoja.get_all_records()
df = pd.DataFrame(datos)

hoy = date.today().strftime("%Y-%m-%d")

# ==========================================
# --- MENÚ LATERAL (SIDEBAR) ---
# ==========================================
st.sidebar.title("💬 Gestión Operativa")

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
st.sidebar.caption("Sincronizado con Google Sheets")

# ==========================================
# --- VISTA 1: AGENDA DE TAREAS ---
# ==========================================
if opcion == "🗓️ Agenda de Tareas":
    st.title("🗓️ Agenda Semanal")
    st.markdown("Organización de turnos y responsabilidades de Atención al Cliente.")
    
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

    dias = list(agenda.keys())
    tabs = st.tabs(dias)

    for i, tab in enumerate(tabs):
        dia_actual = dias[i]
        with tab:
            st.write(f"### 📅 Planilla del {dia_actual}")
            
            col_gonza, col_lucas = st.columns(2)
            
            with col_gonza:
                st.markdown("#### 👨‍💻 Gonzalo")
                st.info("**Mañana (09:00 - 13:30)**")
                for tarea in agenda[dia_actual]["Gonzalo"]["09:00 - 13:30"]:
                    st.checkbox(tarea, key=f"G_M_{dia_actual}_{tarea}")
                
                st.warning("**Tarde (13:30 - 18:00)**")
                for tarea in agenda[dia_actual]["Gonzalo"]["13:30 - 18:00"]:
                    st.checkbox(tarea, key=f"G_T_{dia_actual}_{tarea}")

            with col_lucas:
                st.markdown("#### 👨‍💻 Lucas")
                st.info("**Mañana (09:00 - 13:30)**")
                for tarea in agenda[dia_actual]["Lucas"]["09:00 - 13:30"]:
                    st.checkbox(tarea, key=f"L_M_{dia_actual}_{tarea}")
                
                st.warning("**Tarde (13:30 - 18:00)**")
                for tarea in agenda[dia_actual]["Lucas"]["13:30 - 18:00"]:
                    st.checkbox(tarea, key=f"L_T_{dia_actual}_{tarea}")

# ==========================================
# --- VISTA 2: CARGAR RECLAMO ---
# ==========================================
elif opcion == "📄 Cargar Reclamo":
    st.title("📄 Cargar Reclamo")
    
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
            st.success("✅ ¡Guardado con éxito!")

# ==========================================
# --- VISTA 3: CARGAR ENVÍO ERRÓNEO ---
# ==========================================
elif opcion == "📦 Cargar Envío Erróneo":
    st.title("📦 Cargar Envío Erróneo")
    st.markdown("Registro de productos cruzados o mal enviados.")
    
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
            # Esta fila se manda directo a la hoja "Envios_Erroneos"
            nueva_fila_envio = [agente, canal, tienda, nro_venta, sku, afecto_rep, comentarios]
            hoja_envios.append_row(nueva_fila_envio)
            st.success("✅ ¡Envío erróneo guardado con éxito en su propia pestaña!")

# ==========================================
# --- VISTA 4: RESUMEN DIARIO ---
# ==========================================
elif opcion == "📊 Resumen Diario":
    st.title("📊 Resumen de Operaciones")
    
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
        st.metric(label="Arrancamos con", value=empezamos_dia)
    with col_b:
        st.metric(label="⚠️ Entraron hoy", value=nuevos_hoy)
    with col_c:
        st.metric(label="✅ Resueltos hoy", value=resueltos_hoy)
    with col_d:
        st.metric(label="🔥 PENDIENTES", value=pendientes_actuales)

# ==========================================
# --- VISTA 5: HISTORIAL COMPLETO ---
# ==========================================
elif opcion == "🗂️ Historial Completo":
    st.title("🗂️ Historial Completo")
    
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Aún no hay registros en la base de datos.")

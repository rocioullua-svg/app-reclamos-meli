import streamlit as st
import pandas as pd
from datetime import date, datetime
import gspread
import json
import requests
import fitz  # PyMuPDF
import io

# ==========================================
# --- CONFIGURACIÓN Y ESTILOS ---
# ==========================================
st.set_page_config(page_title="Gestión Operativa", page_icon="📦", layout="wide", initial_sidebar_state="expanded")

# Inyección de CSS: Estilo Oscuro (Dark Theme) y Fuente Inter
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"], .stApp, p, span, div, h1, h2, h3, h4, h5, h6, label, input, button, textarea, select {
        font-family: 'Inter', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
    }

    /* Fondo principal y tipografía general */
    .stApp { background-color: #131314; color: #e3e3e3; }
    
    /* Barra lateral */
    [data-testid="stSidebar"] {
        background-color: #1e1f20 !important;
        border-right: 1px solid #444746 !important;
    }
    
    /* Contenedores (Formularios y Tarjetas de Métricas) */
    [data-testid="stForm"], [data-testid="metric-container"] {
        background-color: #1e1f20;
        border: 1px solid #333638;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    }
    
    /* Estilo de los Inputs (Texto, Select, Textarea) - Corrección de visibilidad al escribir */
    div[data-baseweb="input"] > div, 
    div[data-baseweb="select"] > div, 
    div[data-baseweb="textarea"] > div {
        background-color: #131314 !important;
        border-radius: 20px !important;
        border: 1px solid #444746 !important;
        color: #e3e3e3 !important; /* Color del texto al escribir */
        padding: 2px 12px;
        transition: border-color 0.3s ease;
    }
    
    /* Asegurar que el texto dentro del input sea blanco/gris claro */
    input, textarea, div[data-baseweb="select"] {
        color: #e3e3e3 !important;
    }
    
    /* Efecto Focus en los Inputs */
    div[data-baseweb="input"] > div:focus-within, 
    div[data-baseweb="select"] > div:focus-within, 
    div[data-baseweb="textarea"] > div:focus-within {
        border-color: #a8c7fa !important;
        background-color: #1e1f20 !important;
        box-shadow: none !important;
    }
    
    /* Botón Principal */
    div.stButton > button {
        background: linear-gradient(90deg, #a8c7fa 0%, #8ab4f8 100%) !important;
        color: #041e49 !important;
        border-radius: 24px !important;
        border: none !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        transition: all 0.3s ease !important;
        width: 100%;
        margin-top: 15px;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(138, 180, 248, 0.25) !important;
        background: linear-gradient(90deg, #b9d4ff 0%, #a8c7fa 100%) !important;
    }
    
    /* Checkboxes y textos fijos */
    .stCheckbox label { font-size: 14px !important; color: #e3e3e3 !important; }
    h1, h2, h3, p, label { color: #e3e3e3 !important; }
    
    /* Estilo de las Pestañas (Tabs) */
    button[data-baseweb="tab"] { color: #9aa0a6 !important; }
    button[aria-selected="true"] { 
        color: #a8c7fa !important; 
        font-weight: 600 !important; 
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# --- ESTADO GLOBAL COMPARTIDO PARA AGENDA ---
# ==========================================
@st.cache_resource
def obtener_estado_agenda():
    # Este diccionario se comparte entre todos los usuarios conectados
    return {}

estado_global_agenda = obtener_estado_agenda()

def actualizar_tarea(key):
    # Al hacer click, guardamos el estado del checkbox en la memoria global
    estado_global_agenda[key] = st.session_state[key]

# ==========================================
# --- CREDENCIALES Y FUNCIONES DE APIS ---
# ==========================================
CUENTAS_ML = {
    "Cuenta Meli 1 GAMER": {
        "APP_ID": "2388252618401483",
        "CLIENT_SECRET": "7rhcQRZYwjno2NkKgAGD9tco1TMf4r9e",
        "REFRESH_TOKEN": "TG-6a43ccce3fc6240001dbca0d-28901009" 
    },
    "Cuenta Meli 2 Growin": {
        "APP_ID": "564472504538446",
        "CLIENT_SECRET": "pBvKdfLgJdRzoo2b2FQW4CCIFEoMLFAw",
        "REFRESH_TOKEN": "TG-6a45099c4e692b0001d2b037-546645693"
    }
}
TOKEN_YIQI = "tbHM0kAJoLtIEjcp16qdeheM0P1bRkKWJPTB_LnZN7xluTecIH6zdN0OFHSwff4p71CBoLxWh847PrgHwlvjzr-cR7Czn2YYtAqn464DnDvU6KHZEh_KPwUmJp3ykcytzfWM-rTZdY1-YUnjiU9C8zFFuaTT5x60Tq3FHAabz3ua7_97aYDlz8jYsbqahJlKTaUn7P24lWRX6V1wVPbKmwv4BsDdw_FT0daXzkSoAd9mGn08UN8hkzi37CYrjUrM1db2gVdmNrgl75cji1QIsVvs1va5jWzM9OEPUK9ROZu3dpl6fvyyuK5UAtDiT1YK7_b9te9jbVm9UrsjxNr69asGZNj-YGCtGwIlijginVCsMHY1YSMwjGDXAR8629pwPxcfJJeish3xV25PbX2x7gUaH-tJ7VkCU_2k6LpJ8TUXdZbsLzmyONF6TmA4BQhMPpv7ppVxPUjWsr6XddbyVqYJyNg0BNLLh9gEVxlA6nFCh4ZNsbtPy7zdqA2rplsW"
SCHEMA_ID = "1526"
URL_PDF_MP = "https://www.mercadopago.com/org-img/MP3/PPV/formulario_PPV_032010.pdf"

def renovar_token_ml(app_id, client_secret, refresh_token):
    url = "https://api.mercadolibre.com/oauth/token"
    payload = {"grant_type": "refresh_token", "client_id": app_id, "client_secret": client_secret, "refresh_token": refresh_token}
    headers = {"accept": "application/json", "content-type": "application/x-www-form-urlencoded"}
    res = requests.post(url, headers=headers, data=payload)
    return res.json()["access_token"] if res.status_code == 200 else None

def avisar_entrega_ml(nro_operacion, token):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    res_orden = requests.get(f"https://api.mercadolibre.com/orders/{nro_operacion}", headers=headers)
    if res_orden.status_code == 200:
        datos_orden = res_orden.json()
        id_envio = datos_orden.get("shipping", {}).get("id")
        if id_envio:
            res_envio = requests.put(f"https://api.mercadolibre.com/shipments/{id_envio}", headers=headers, json={"status": "delivered"})
            if res_envio.status_code == 200: return True, f"✅ ML actualizado a Entregado (Envío: {id_envio})"
        payload_fb = {"fulfilled": True, "rating": "positive"}
        res_fb = requests.post(f"https://api.mercadolibre.com/orders/{nro_operacion}/feedback", headers=headers, json=payload_fb)
        if res_fb.status_code in [200, 201]: return True, "✅ Aviso de entrega enviado al comprador."
    return False, "⚠️ ML requiere confirmación desde la app o la API rechazó la acción."

def obtener_datos_yiqi(nro_operacion):
    url = "https://apilegacy.yiqi.com.ar/api/public/PEDIDO/search"
    headers = {"Authorization": f"Bearer {TOKEN_YIQI}", "Accept": "application/json"}
    params = {"schemaId": SCHEMA_ID, "PEDI_NUMERO": nro_operacion}
    res = requests.get(url, headers=headers, params=params)
    if res.status_code == 200 and len(res.json()) > 0:
        datos = res.json()[0] 
        nombre_articulo = "Artículos de Compra ML"
        try:
            datos_ml = json.loads(datos.get("PEDI_JSON", "{}"))
            nombre_articulo = datos_ml["order_items"][0]["item"]["title"]
        except: pass
        return {"nombre": datos.get("PEDI_RAZON_SOCIAL", ""), "dni": datos.get("PEDI_CUIT", ""), "total": datos.get("PEDI_TOTAL", 0), "articulo": nombre_articulo, "id_interno": datos.get("id")}
    return None

def actualizar_estado_yiqi(id_interno, nuevo_estado="Entregado"):
    url = "https://apilegacy.yiqi.com.ar/api/public/PEDIDO/changestate"
    headers = {"Authorization": f"Bearer {TOKEN_YIQI}", "Accept": "application/json"}
    params = {"id": id_interno, "schemaId": SCHEMA_ID, "state": nuevo_estado}
    return requests.post(url, headers=headers, params=params)

# ==========================================
# --- CONEXIÓN A GOOGLE SHEETS ---
# ==========================================
@st.cache_resource(ttl=60)
def conectar_sheets():
    credenciales = json.loads(st.secrets["google_credentials"])
    gc = gspread.service_account_from_dict(credenciales)
    planilla = gc.open("Base_Reclamos_ML")
    hoja_principal = planilla.sheet1
    try:
        hoja_envios = planilla.worksheet("Envios_Erroneos")
    except gspread.exceptions.WorksheetNotFound:
        hoja_envios = planilla.add_worksheet(title="Envios_Erroneos", rows="1000", cols="10")
        hoja_envios.append_row(["Agente", "Canal", "Tienda", "NRO VENTA", "SKU", "Afectó Rep", "Comentarios"])
    except Exception:
        hoja_envios = hoja_principal
    return hoja_principal, hoja_envios

hoja, hoja_envios = conectar_sheets()

# Cargar DataFrames
datos_reclamos = hoja.get_all_records()
df = pd.DataFrame(datos_reclamos)

datos_envios = hoja_envios.get_all_records()
df_envios = pd.DataFrame(datos_envios)

hoy = date.today().strftime("%Y-%m-%d")

# ==========================================
# --- MENÚ LATERAL (SIDEBAR) ---
# ==========================================
st.sidebar.title("💬 Gestión Operativa")

opcion = st.sidebar.radio(
    "Navegación:",
    [
        "🗓️ Agenda de Tareas",
        "🚚 Entregas y Retiros",
        "📄 Cargar Reclamo", 
        "📦 Cargar Envío Erróneo", 
        "📊 Resumen Diario", 
        "🗂️ Historial Completo"
    ]
)

st.sidebar.divider()
st.sidebar.caption("Sincronizado con G-Sheets, ML y YiQi")

# ==========================================
# --- VISTA 1: AGENDA DE TAREAS ---
# ==========================================
if opcion == "🗓️ Agenda de Tareas":
    col_titulo, col_boton = st.columns([4, 1])
    with col_titulo:
        st.title("🗓️ Agenda Semanal")
    with col_boton:
        st.write("") # Espaciado
        # Este botón permite a un usuario recargar la pantalla para ver qué tildó su compañero
        st.button("🔄 Actualizar vista", use_container_width=True)

    st.markdown("Organización de turnos y responsabilidades de Atención al Cliente.")
    
    agenda = {
        "Lunes": {
            "Gonzalo": {"09:00 - 13:30": ["Preguntas", "Postventa", "Envios retiros depo", "Cambios cargados en YiQi", "Pendientes Guardia"], "13:30 - 18:00": ["Reclamos", "Gmail", "NC Fravega (MAIL)", "Liveconnect/agent"]},
            "Lucas": {"09:00 - 13:30": ["Reclamos", "Gmail", "NC Fravega (MAIL)", "Liveconnect/agent", "Retiros Flexit"], "13:30 - 18:00": ["Preguntas", "Postventa", "Envios retiros depo", "Pendientes Guardia"]}
        },
        "Martes": {
            "Gonzalo": {"09:00 - 13:30": ["Reclamos", "Gmail", "NC Fravega (MAIL)", "Liveconnect/agent", "Retiros Flexit"], "13:30 - 18:00": ["Preguntas", "Postventa", "Cierre caja Pos"]},
            "Lucas": {"09:00 - 13:30": ["Preguntas", "Postventa", "Envios retiros depo", "Cambios cargados en YiQi", "Pendientes Guardia"], "13:30 - 18:00": ["Reclamos", "Gmail", "NC Fravega (MAIL)", "Liveconnect/agent"]}
        },
        "Miércoles": {
            "Gonzalo": {"09:00 - 13:30": ["Preguntas", "Postventa", "Envios retiros depo", "Cambios cargados en YiQi", "Pendientes Guardia"], "13:30 - 18:00": ["Reclamos", "Gmail", "NC Fravega (MAIL)", "Liveconnect/agent"]},
            "Lucas": {"09:00 - 13:30": ["Reclamos", "Gmail", "NC Fravega (MAIL)", "Liveconnect/agent", "Retiros Flexit"], "13:30 - 18:00": ["Preguntas", "Postventa", "Envios retiros depo", "Pendientes Guardia"]}
        },
        "Jueves": {
            "Gonzalo": {"09:00 - 13:30": ["Reclamos", "Gmail", "NC Fravega (MAIL)", "Liveconnect/agent", "Retiros Flexit"], "13:30 - 18:00": ["Preguntas", "Postventa", "Envios retiros depo", "Cierre caja Pos"]},
            "Lucas": {"09:00 - 13:30": ["Preguntas", "Postventa", "Envios retiros depo", "Cambios cargados en YiQi", "Pendientes Guardia"], "13:30 - 18:00": ["Reclamos", "Gmail", "NC Fravega (MAIL)", "Liveconnect/agent"]}
        },
        "Viernes": {
            "Gonzalo": {"09:00 - 13:30": ["Preguntas", "Postventa", "Envios retiros depo", "Cambios cargados en YiQi", "Pendientes Guardia"], "13:30 - 18:00": ["Reclamos", "Gmail", "NC Fravega (MAIL)", "Liveconnect/agent"]},
            "Lucas": {"09:00 - 13:30": ["Reclamos", "Gmail", "NC Fravega (MAIL)", "Liveconnect/agent", "Retiros Flexit"], "13:30 - 18:00": ["Preguntas", "Postventa", "Envios retiros depo", "Pendientes Guardia"]}
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
                    chk_key = f"G_M_{dia_actual}_{tarea}"
                    st.checkbox(tarea, key=chk_key, value=estado_global_agenda.get(chk_key, False), on_change=actualizar_tarea, args=(chk_key,))
                st.warning("**Tarde (13:30 - 18:00)**")
                for tarea in agenda[dia_actual]["Gonzalo"]["13:30 - 18:00"]: 
                    chk_key = f"G_T_{dia_actual}_{tarea}"
                    st.checkbox(tarea, key=chk_key, value=estado_global_agenda.get(chk_key, False), on_change=actualizar_tarea, args=(chk_key,))
            with col_lucas:
                st.markdown("#### 👨‍💻 Lucas")
                st.info("**Mañana (09:00 - 13:30)**")
                for tarea in agenda[dia_actual]["Lucas"]["09:00 - 13:30"]: 
                    chk_key = f"L_M_{dia_actual}_{tarea}"
                    st.checkbox(tarea, key=chk_key, value=estado_global_agenda.get(chk_key, False), on_change=actualizar_tarea, args=(chk_key,))
                st.warning("**Tarde (13:30 - 18:00)**")
                for tarea in agenda[dia_actual]["Lucas"]["13:30 - 18:00"]: 
                    chk_key = f"L_T_{dia_actual}_{tarea}"
                    st.checkbox(tarea, key=chk_key, value=estado_global_agenda.get(chk_key, False), on_change=actualizar_tarea, args=(chk_key,))

# ==========================================
# --- VISTA 2: ENTREGAS Y RETIROS ---
# ==========================================
elif opcion == "🚚 Entregas y Retiros":
    st.title("🚚 Procesador de Entregas / Retiros")
    st.markdown("Gestión conectada a YiQi ERP y cuentas de Mercado Libre.")
    
    st.write("#### 1. Buscar Operación")
    cuenta_seleccionada = st.selectbox("Selecciona la cuenta de Mercado Libre correspondiente a la venta:", list(CUENTAS_ML.keys()))
    nro_operacion = st.text_input("Ingrese el Nro de Operación de ML (Ej: 2000017044790128)")

    if st.button("🔍 Buscar en YiQi"):
        if nro_operacion:
            numero_limpio = nro_operacion.strip()
            with st.spinner("Conectando con el ERP..."):
                datos = obtener_datos_yiqi(numero_limpio)
                if not datos and not numero_limpio.startswith("ML"):
                    numero_con_prefijo = f"ML{numero_limpio}"
                    datos = obtener_datos_yiqi(numero_con_prefijo)

                if datos:
                    st.session_state['datos_encontrados'] = datos
                    st.session_state['nro_actual'] = numero_limpio
                    if 'pdf_generado' in st.session_state:
                        del st.session_state['pdf_generado']
                else:
                    st.error("❌ No se encontró la operación en YiQi. Revisa el número o el formato.")
        else:
            st.warning("⚠️ Por favor, ingresa un número primero.")

    st.markdown("---")

    if 'datos_encontrados' in st.session_state and st.session_state.get('nro_actual') == nro_operacion.strip():
        st.write("#### 2. Confirmar Datos de Quien Retira")
        st.info(f"💡 Modificando datos para operación de **{cuenta_seleccionada}**.")
        
        col1, col2 = st.columns(2)
        with col1:
            edit_nombre = st.text_input("Nombre de quien retira", value=st.session_state['datos_encontrados']['nombre'])
            edit_dni = st.text_input("DNI de quien retira", value=st.session_state['datos_encontrados']['dni'])
        with col2:
            edit_total = st.text_input("Monto Total ($)", value=str(st.session_state['datos_encontrados']['total']))
            edit_articulo = st.text_input("Artículo", value=st.session_state['datos_encontrados']['articulo'])
            
        fecha_hoy = st.date_input("Fecha de Entrega", datetime.now())

        if st.button("🚀 Confirmar Despacho (YiQi + ML + Remito)"):
            with st.status(f"Procesando operación en {cuenta_seleccionada}...", expanded=True) as status:
                st.write("1️⃣ Cambiando estado a 'Entregado' en YiQi...")
                id_interno = st.session_state['datos_encontrados']['id_interno']
                res_yiqi = actualizar_estado_yiqi(id_interno, "Entregado")
                
                if res_yiqi.status_code == 200:
                    st.write("   * ✅ ¡Pedido entregado exitosamente en tu ERP!")
                else:
                    st.write(f"   * ⚠️ Nota: No se pudo cambiar el estado en YiQi (Error {res_yiqi.status_code}).")
                
                st.write(f"2️⃣ Conectando con la API de {cuenta_seleccionada}...")
                credenciales_de_turno = CUENTAS_ML[cuenta_seleccionada]
                token_ml = renovar_token_ml(credenciales_de_turno["APP_ID"], credenciales_de_turno["CLIENT_SECRET"], credenciales_de_turno["REFRESH_TOKEN"])
                
                if token_ml:
                    exito, mensaje = avisar_entrega_ml(nro_operacion.strip(), token_ml)
                    st.write(f"   * {mensaje}")
                else:
                    st.write("   * ❌ Falló la conexión con ML para esta cuenta. Verifica sus credenciales.")

                st.write("3️⃣ Generando Recibo Oficial en PDF...")
                try:
                    response_pdf = requests.get(URL_PDF_MP)
                    doc = fitz.open(stream=response_pdf.content, filetype="pdf")
                    page = doc[0]
                    
                    fecha_formateada = fecha_hoy.strftime("%d / %m / %Y")
                    texto_articulo = f"{edit_articulo[:45]}... - Total: ${edit_total}"
                    
                    page.insert_text((160, 250), edit_nombre.upper(), fontsize=12, color=(0, 0, 0))
                    page.insert_text((180, 290), str(edit_dni), fontsize=12, color=(0, 0, 0))
                    page.insert_text((90, 375), texto_articulo, fontsize=10, color=(0, 0, 0))
                    page.insert_text((400, 375), f"Op: {nro_operacion.strip()}", fontsize=11, color=(0, 0, 0))
                    page.insert_text((150, 525), fecha_formateada, fontsize=12, color=(0, 0, 0))
                    
                    pdf_salida = io.BytesIO()
                    doc.save(pdf_salida)
                    doc.close()
                    
                    st.session_state['pdf_generado'] = pdf_salida.getvalue()
                    st.session_state['nombre_archivo'] = f"Recibo_{edit_nombre.replace(' ', '_')}.pdf"
                    status.update(label="¡Proceso Finalizado!", state="complete", expanded=False)
                    
                except Exception as e:
                    st.error(f"Error generando el PDF: {e}")
                    status.update(label="Fallo en PDF", state="error")

    if 'pdf_generado' in st.session_state and st.session_state.get('nro_actual') == nro_operacion.strip():
        st.success("🎉 ¡Todo listo!")
        st.download_button(
            label="📥 Descargar Remito (PDF)",
            data=st.session_state['pdf_generado'],
            file_name=st.session_state['nombre_archivo'],
            mime="application/pdf"
        )

# ==========================================
# --- VISTA 3: CARGAR RECLAMO ---
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
        elif not df.empty and str(id_venta) in df.astype(str).values:
            st.error("❌ Este ID de Venta ya se encuentra registrado en la base de reclamos.")
        else:
            fecha_res = hoy if estado == "Resuelto" else ""
            nueva_fila = [hoy, id_venta, sku, categoria, motivo, responsabilidad, estado, "Sí", agente, fecha_res]
            hoja.append_row(nueva_fila)
            st.success("✅ ¡Guardado con éxito!")

# ==========================================
# --- VISTA 4: CARGAR ENVÍO ERRÓNEO ---
# ==========================================
elif opcion == "📦 Cargar Envío Erróneo":
    st.title("📦 Cargar Envío Erróneo")
    st.markdown("Registro de productos cruzados o mal enviados.")
    
    with st.form("formulario_envios_erroneos"):
        col1, col2, col3 = st.columns(3)
        with col1:
            agente = st.text_input("Agente:")
            canal = st.selectbox("Canal:", ["MELI", "FLEX", "FULL", "WEB","FVG"])
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
        elif not df_envios.empty and str(nro_venta) in df_envios.astype(str).values:
            st.error("❌ Este NRO VENTA ya se encuentra registrado en la base de Envíos Erróneos.")
        else:
            nueva_fila_envio = [agente, canal, tienda, nro_venta, sku, afecto_rep, comentarios]
            hoja_envios.append_row(nueva_fila_envio)
            st.success("✅ ¡Envío erróneo guardado con éxito en su propia pestaña!")

# ==========================================
# --- VISTA 5: RESUMEN DIARIO ---
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
    with col_a: st.metric(label="Arrancamos con", value=empezamos_dia)
    with col_b: st.metric(label="⚠️ Entraron hoy", value=nuevos_hoy)
    with col_c: st.metric(label="✅ Resueltos hoy", value=resueltos_hoy)
    with col_d: st.metric(label="🔥 PENDIENTES", value=pendientes_actuales)

# ==========================================
# --- VISTA 6: HISTORIAL COMPLETO ---
# ==========================================
elif opcion == "🗂️ Historial Completo":
    st.title("🗂️ Historial Completo")
    
    # Sistema de pestañas para dividir los historiales
    tab1, tab2 = st.tabs(["📄 Base de Reclamos", "📦 Base de Envíos Erróneos"])
    
    with tab1:
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Aún no hay registros en la base de datos de Reclamos.")
            
    with tab2:
        if not df_envios.empty:
            st.dataframe(df_envios, use_container_width=True, hide_index=True)
        else:
            st.info("Aún no hay registros en la base de datos de Envíos Erróneos.")

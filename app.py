import streamlit as st

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Bandeja de Entrada", page_icon="💬", layout="wide", initial_sidebar_state="collapsed")

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
<style>
    /* Ocultar elementos predeterminados de Streamlit para simular una app completa */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding: 0rem 0rem 0rem 0rem !important;
        max-width: 100% !important;
    }
    
    /* Contenedor principal dividido */
    .main-wrapper {
        display: flex;
        height: 100vh;
        width: 100%;
        background-color: #ffffff;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }

    /* --- PANEL IZQUIERDO: LISTA DE CHATS --- */
    .chat-list-panel {
        width: 350px;
        border-right: 1px solid #e0e0e0;
        display: flex;
        flex-direction: column;
        background-color: #ffffff;
        height: 100vh;
    }
    .search-box {
        padding: 15px;
        border-bottom: 1px solid #f0f0f0;
    }
    .search-input {
        width: 100%;
        padding: 8px 12px;
        border: 1px solid #dcdcdc;
        border-radius: 20px;
        font-size: 14px;
        outline: none;
        background-color: #f9f9f9;
    }
    .filters {
        padding: 10px 15px;
        display: flex;
        gap: 8px;
        overflow-x: auto;
        border-bottom: 1px solid #f0f0f0;
        white-space: nowrap;
    }
    .filters::-webkit-scrollbar { display: none; }
    .filter-pill {
        font-size: 12px;
        color: #5f6368;
        cursor: pointer;
        padding: 4px 0px;
    }
    .filter-pill.active {
        color: #1a73e8;
        font-weight: 600;
        border-bottom: 2px solid #1a73e8;
    }
    .filter-pill-round {
        font-size: 12px;
        padding: 4px 12px;
        border-radius: 12px;
        background-color: #f1f3f4;
        color: #3c4043;
        cursor: pointer;
    }
    .filter-pill-round.blue {
        background-color: #1a73e8;
        color: white;
    }
    .chat-item {
        display: flex;
        padding: 15px;
        border-bottom: 1px solid #f0f0f0;
        cursor: pointer;
        position: relative;
    }
    .chat-item:hover {
        background-color: #f9f9f9;
    }
    .chat-item.selected {
        border-left: 3px solid #1a73e8;
        background-color: #f4f8ff;
    }
    .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background-color: #e0e0e0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: #555;
        margin-right: 12px;
    }
    .chat-item-content {
        flex: 1;
        overflow: hidden;
    }
    .chat-item-header {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        margin-bottom: 4px;
    }
    .chat-name {
        font-size: 14px;
        font-weight: 600;
        color: #202124;
    }
    .chat-time {
        font-size: 11px;
        color: #80868b;
    }
    .chat-preview {
        font-size: 13px;
        color: #80868b;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .tag-bot {
        font-size: 10px;
        background-color: #f3e8fd;
        color: #9333ea;
        padding: 2px 6px;
        border-radius: 4px;
        margin-left: 5px;
        font-weight: 600;
    }

    /* --- PANEL DERECHO: ÁREA DE CHAT --- */
    .chat-area {
        flex: 1;
        display: flex;
        flex-direction: column;
        background-color: #f0ece3; /* Color de fondo tipo WhatsApp/Web */
        height: 100vh;
    }
    .chat-header {
        background-color: #ffffff;
        padding: 15px 20px;
        display: flex;
        flex-direction: column;
        border-bottom: 1px solid #e0e0e0;
    }
    .chat-header-top {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
    }
    .chat-header-info {
        display: flex;
        flex-direction: column;
    }
    .chat-header-title {
        font-size: 16px;
        font-weight: 600;
        display: flex;
        align-items: center;
    }
    .chat-header-subtitle {
        font-size: 12px;
        color: #5f6368;
        margin-top: 2px;
    }
    .btn-tomar {
        background-color: #2563eb;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 6px;
        width: fit-content;
    }
    .btn-tomar:hover { background-color: #1d4ed8; }

    /* --- MENSAJES --- */
    .messages-container {
        flex: 1;
        padding: 20px;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
    }
    .date-divider {
        text-align: center;
        margin: 15px 0;
    }
    .date-divider span {
        background-color: #ffffff;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        color: #5f6368;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .msg-row {
        display: flex;
        flex-direction: column;
        margin-bottom: 15px;
        max-width: 65%;
    }
    .msg-row.incoming { align-self: flex-start; }
    .msg-row.outgoing { align-self: flex-end; }
    
    .msg-bubble {
        padding: 10px 14px;
        font-size: 14px;
        position: relative;
        color: #202124;
    }
    .msg-row.incoming .msg-bubble {
        background-color: #ffffff;
        border-radius: 0px 12px 12px 12px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    .msg-row.outgoing .msg-bubble {
        background-color: #f1f3f4;
        border-radius: 12px 0px 12px 12px;
    }
    .msg-meta {
        font-size: 10px;
        color: #80868b;
        text-align: right;
        margin-top: 4px;
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 4px;
    }
    .msg-sender {
        font-size: 11px;
        color: #80868b;
        margin-bottom: 4px;
    }
    .file-attachment {
        display: flex;
        align-items: center;
        gap: 10px;
        border: 1px solid #e0e0e0;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 5px;
    }
    .file-icon { font-size: 20px; color: #ea4335; }
    .file-name { font-size: 13px; flex: 1; }

    /* --- INPUT BOTTOM --- */
    .chat-input-area {
        background-color: #f9f9f9;
        padding: 15px 20px;
        display: flex;
        align-items: center;
        border-top: 1px solid #e0e0e0;
    }
    .chat-input-box {
        flex: 1;
        background-color: #ffffff;
        border: 1px solid #dcdcdc;
        padding: 12px 15px;
        border-radius: 24px;
        color: #80868b;
        font-size: 14px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- ESTRUCTURA HTML PRINCIPAL ---
html_content = """
<div class="main-wrapper">
    <!-- PANEL IZQUIERDO -->
    <div class="chat-list-panel">
        <div class="search-box">
            <input type="text" class="search-input" placeholder="🔍 Buscar por nombre, telefono o mensaje..">
        </div>
        
        <div class="filters">
            <span class="filter-pill">Todos <span style="color:#888; font-size:10px;">99+</span></span>
            <span class="filter-pill active">Bot <span style="color:#1a73e8; font-size:10px;">99+</span></span>
            <span class="filter-pill">Nuevo</span>
            <span class="filter-pill">Espera</span>
            <span class="filter-pill">Mios</span>
            <span class="filter-pill">Resuelto</span>
        </div>
        
        <div class="filters" style="padding-top: 0;">
            <span class="filter-pill-round blue">Todas</span>
            <span class="filter-pill-round">Lua Femme</span>
            <span class="filter-pill-round">Home Co Argentina</span>
        </div>
        
        <div class="filters" style="padding-top: 0; border-bottom: none; background: #f9f9f9;">
            <span class="filter-pill-round blue">Todos los agentes</span>
            <span class="filter-pill-round">QA Migracion (automatizado)</span>
        </div>

        <!-- Lista de Contactos -->
        <div style="overflow-y: auto; flex: 1;">
            <div class="chat-item selected">
                <div class="avatar">A</div>
                <div class="chat-item-content">
                    <div class="chat-item-header">
                        <span class="chat-name">Agos Taipio</span>
                        <span class="chat-time">en menos de un minuto</span>
                    </div>
                    <div class="chat-preview">Home Co Argentina</div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 2px;">
                        <span class="chat-time">4 mensajes</span>
                        <span class="tag-bot">Bot</span>
                    </div>
                </div>
            </div>

            <div class="chat-item">
                <div class="avatar" style="font-size:10px;">.</div>
                <div class="chat-item-content">
                    <div class="chat-item-header">
                        <span class="chat-name">.</span>
                        <span class="chat-time">hace 8 minutos</span>
                    </div>
                    <div class="chat-preview">The Game House</div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 2px;">
                        <span class="chat-time">2 mensajes</span>
                        <span class="tag-bot">Bot</span>
                    </div>
                </div>
            </div>

            <div class="chat-item">
                <div class="avatar">M</div>
                <div class="chat-item-content">
                    <div class="chat-item-header">
                        <span class="chat-name">M</span>
                        <span class="chat-time">hace alrededor de 1 hora</span>
                    </div>
                    <div class="chat-preview">Home Co Argentina</div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 2px;">
                        <span class="chat-time">1 mensaje</span>
                        <span class="tag-bot">Bot</span>
                    </div>
                </div>
            </div>
            
            <div class="chat-item">
                <div class="avatar">R</div>
                <div class="chat-item-content">
                    <div class="chat-item-header">
                        <span class="chat-name">R</span>
                        <span class="chat-time">hace alrededor de 2 horas</span>
                    </div>
                    <div class="chat-preview">Home Co Argentina</div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 2px;">
                        <span class="chat-time">2 mensajes</span>
                        <span class="tag-bot">Bot</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- PANEL DERECHO (CHAT) -->
    <div class="chat-area">
        <!-- Encabezado del chat -->
        <div class="chat-header">
            <div class="chat-header-top">
                <div class="avatar" style="margin-right: 15px; width: 45px; height: 45px;">A</div>
                <div class="chat-header-info">
                    <div class="chat-header-title">
                        Agos Taipio <span class="tag-bot" style="margin-left: 8px;">Bot</span>
                    </div>
                    <div class="chat-header-subtitle">
                        5491136054415 • Home Co Argentina
                    </div>
                </div>
            </div>
            <button class="btn-tomar">✋ Tomar conversacion</button>
        </div>

        <!-- Contenedor de mensajes -->
        <div class="messages-container">
            <div class="date-divider"><span>Hoy</span></div>
            
            <!-- Mensaje Entrante 1 (Hola) -->
            <div class="msg-row incoming">
                <div class="msg-bubble">
                    Hola
                    <div class="msg-meta">12:35</div>
                </div>
            </div>

            <!-- Mensaje Entrante 2 (Archivo) -->
            <div class="msg-row incoming" style="margin-top: -5px;">
                <div class="msg-bubble" style="width: 350px;">
                    <div class="file-attachment">
                        <span class="file-icon">📄</span>
                        <span class="file-name">Comprobante.pdf</span>
                        <span style="color:#888; cursor:pointer;">📥</span>
                    </div>
                    <div style="font-size: 12px; color: #555; margin-top: 5px;">
                        [Documento del cliente: "Comprobante.pdf" (application/pdf)]
                    </div>
                    <div class="msg-meta">12:35</div>
                </div>
            </div>

            <!-- Mensaje Saliente 1 (Bot - Bienvenida) -->
            <div class="msg-row outgoing" style="margin-top: 15px;">
                <div class="msg-sender">Bot</div>
                <div class="msg-bubble">
                    ¡Hola, Agos! 👋 Bienvenida a Home Co Argentina. ¿En qué te puedo ayudar hoy? ¿Buscás algo para tu casa o tenés alguna consulta?
                    <div class="msg-meta">12:35 <span style="color: #1a73e8;">✓✓</span></div>
                </div>
            </div>

            <!-- Mensaje Saliente 2 (Bot - Confirmación) -->
            <div class="msg-row outgoing">
                <div class="msg-sender">Bot</div>
                <div class="msg-bubble">
                    ¡Gracias Agos! Recibí el comprobante 📄. Ya lo estoy revisando, en un momento te confirmo.
                    <br><br>
                    Mientras tanto, ¿querés que te ayude con algo más? ¿Buscás algún producto en particular?
                    <div class="msg-meta">12:35 <span style="color: #1a73e8;">✓✓</span></div>
                </div>
            </div>
        </div>

        <!-- Input bloqueado abajo -->
        <div class="chat-input-area">
            <div class="chat-input-box">No disponible</div>
            <div style="background-color: #2563eb; color: white; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-left: 15px; opacity: 0.5;">
                ➤
            </div>
        </div>
    </div>
</div>
"""

# Renderizar el HTML
st.markdown(html_content, unsafe_allow_html=True)

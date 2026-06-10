"""Identidade visual da Nexxa para a interface Streamlit.

Recria a paleta e o estilo do design system da Nexxa (verde esmeralda sobre
verde-escuro, cards com vidro fosco e brilho) e um cabeçalho com a marca.
"""
import streamlit as st

_CSS = """
<style>
:root {
  --nx-green: #5FE08F;
  --nx-green-dark: #22C55E;
  --nx-green-deeper: #16A34A;
  --nx-text: #F0FDF4;
  --nx-text-muted: #9DB5AB;
  --nx-border-mid: rgba(95,224,143,0.18);
}

/* Fundo geral — gradiente verde-escuro da Nexxa */
.stApp {
  background:
    radial-gradient(circle at 12% -10%, rgba(95,224,143,0.14), transparent 28%),
    radial-gradient(circle at 92% 8%, rgba(34,197,94,0.10), transparent 26%),
    linear-gradient(180deg, #061815 0%, #072019 34%, #0a2a22 100%) !important;
  color: var(--nx-text);
}

/* Cabeçalho nativo do Streamlit transparente */
[data-testid="stHeader"] { background: transparent !important; }

/* Cabeçalho da marca Nexxa */
.nx-header {
  display: flex; align-items: center; gap: 16px;
  padding: 18px 22px; margin-bottom: 8px;
  background: linear-gradient(180deg, rgba(8,32,26,0.92) 0%, rgba(10,40,32,0.85) 100%);
  border: 1px solid var(--nx-border-mid);
  border-left: 4px solid var(--nx-green);
  border-radius: 16px;
  box-shadow: 0 16px 36px rgba(0,0,0,0.42);
  backdrop-filter: blur(18px);
}
.nx-logo {
  width: 52px; height: 52px; flex: none;
  display: flex; align-items: center; justify-content: center;
  font-size: 26px;
  background: linear-gradient(145deg, #22C55E 0%, #5FE08F 100%);
  border-radius: 14px;
  box-shadow: 0 8px 22px rgba(95,224,143,0.28);
}
.nx-name {
  font-size: 26px; font-weight: 800; line-height: 1.1;
  color: var(--nx-text); letter-spacing: 0.3px;
}
.nx-name .nx-accent { color: var(--nx-green); }
.nx-portal {
  display: inline-block; margin-top: 4px;
  font-size: 12px; font-weight: 600; letter-spacing: 0.4px;
  color: var(--nx-green);
  background: rgba(95,224,143,0.12);
  border: 1px solid rgba(95,224,143,0.22);
  border-radius: 999px; padding: 2px 12px;
}

/* Botões — gradiente verde da marca */
.stButton > button, .stDownloadButton > button {
  background: linear-gradient(135deg, #22C55E 0%, #5FE08F 100%) !important;
  color: #052016 !important;
  font-weight: 700 !important;
  border: 1px solid rgba(95,224,143,0.55) !important;
  border-radius: 12px !important;
  box-shadow: 0 12px 26px rgba(95,224,143,0.24) !important;
  transition: transform .12s ease, box-shadow .12s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
  background: linear-gradient(135deg, #16A34A 0%, #4ADE80 100%) !important;
  box-shadow: 0 18px 34px rgba(95,224,143,0.30) !important;
  transform: translateY(-1px);
}

/* Campos de texto e selects */
.stTextInput input, .stTextArea textarea, div[data-baseweb="select"] > div {
  background: rgba(10,36,30,0.85) !important;
  border: 1px solid var(--nx-border-mid) !important;
  color: var(--nx-text) !important;
  border-radius: 10px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
  border-color: var(--nx-green) !important;
  box-shadow: 0 0 0 4px rgba(95,224,143,0.14) !important;
}

/* Área de upload */
[data-testid="stFileUploaderDropzone"] {
  background: rgba(10,36,30,0.65) !important;
  border: 1px dashed rgba(95,224,143,0.32) !important;
  border-radius: 14px !important;
}

/* Caixa de status e alertas com borda verde */
[data-testid="stStatusWidget"], [data-testid="stNotification"] {
  border-radius: 14px !important;
  border: 1px solid var(--nx-border-mid) !important;
}

/* Títulos e divisores */
h1, h2, h3, h4 { color: var(--nx-text) !important; }
hr { border-color: var(--nx-border-mid) !important; }
</style>
"""

_CABECALHO = """
<div class="nx-header">
  <div class="nx-logo">📋</div>
  <div>
    <div class="nx-name">Ne<span class="nx-accent">xx</span>a</div>
    <span class="nx-portal">TeamsAta · Gerador de Atas</span>
  </div>
</div>
"""


def aplicar_tema():
    """Injeta o CSS da Nexxa e renderiza o cabeçalho com a marca."""
    st.markdown(_CSS, unsafe_allow_html=True)
    st.markdown(_CABECALHO, unsafe_allow_html=True)

"""Identidade visual corporativa da Nexxa para a interface Streamlit.

Usa o logo oficial (assets/nexxa-logo.png) e o verde institucional #009E52,
com tipografia Plus Jakarta Sans e superfícies escuras.
"""
import base64
from pathlib import Path

import streamlit as st

_ASSETS = Path(__file__).parent / "assets"


def _logo_data_uri():
    """Lê o logo oficial e devolve como data URI (base64) para embutir no HTML."""
    dados = base64.b64encode((_ASSETS / "nexxa-logo.png").read_bytes()).decode("ascii")
    return f"data:image/png;base64,{dados}"


_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
  --nx-green: #009E52;          /* verde institucional Nexxa */
  --nx-green-bright: #15B86A;
  --nx-green-deep: #047A40;
  --nx-text: #F0FDF4;
  --nx-text-muted: #9DB5AB;
  --nx-border: rgba(0,158,82,0.16);
  --nx-border-mid: rgba(0,158,82,0.26);
}

/* Tipografia da marca */
html, body, [class*="css"], .stApp, button, input, textarea, select {
  font-family: 'Plus Jakarta Sans', 'Segoe UI', Arial, sans-serif !important;
}

/* Fundo institucional */
.stApp {
  background:
    radial-gradient(circle at 12% -10%, rgba(0,158,82,0.12), transparent 30%),
    radial-gradient(circle at 92% 4%, rgba(0,158,82,0.07), transparent 28%),
    linear-gradient(180deg, #05140F 0%, #061a14 40%, #071e17 100%) !important;
  color: var(--nx-text);
}
[data-testid="stHeader"] { background: transparent !important; }
.block-container { max-width: 920px; padding-top: 2.2rem; }

/* ── Cabeçalho corporativo ───────────────────────────────── */
.nx-header {
  display: flex; align-items: center; justify-content: space-between;
  gap: 18px; padding: 18px 26px; margin-bottom: 6px;
  background: linear-gradient(180deg, rgba(7,26,20,0.96) 0%, rgba(8,30,23,0.90) 100%);
  border: 1px solid var(--nx-border-mid);
  border-radius: 16px;
  box-shadow: 0 18px 40px rgba(0,0,0,0.42);
  backdrop-filter: blur(18px);
  position: relative; overflow: hidden;
}
.nx-header::before {
  content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 4px;
  background: linear-gradient(180deg, #15B86A, #047A40);
}
.nx-logo { height: 46px; width: auto; display: block; }
.nx-header-right { text-align: right; }
.nx-portal {
  display: inline-block;
  font-size: 12.5px; font-weight: 700; letter-spacing: .6px; text-transform: uppercase;
  color: #C9F5DD;
  background: rgba(0,158,82,0.16);
  border: 1px solid rgba(0,158,82,0.30);
  border-radius: 999px; padding: 5px 14px;
}
.nx-portal-sub {
  display: block; margin-top: 6px;
  font-size: 12px; color: var(--nx-text-muted); letter-spacing: .2px;
}

/* ── Títulos ──────────────────────────────────────────────── */
h1, h2, h3, h4 { color: var(--nx-text) !important; font-weight: 700 !important; letter-spacing: .2px; }

/* ── Botões ───────────────────────────────────────────────── */
.stButton > button, .stDownloadButton > button {
  background: linear-gradient(135deg, #009E52 0%, #15B86A 100%) !important;
  color: #FFFFFF !important;
  font-weight: 700 !important;
  border: 1px solid rgba(0,158,82,0.55) !important;
  border-radius: 12px !important;
  padding: 0.55rem 1rem !important;
  box-shadow: 0 12px 26px rgba(0,158,82,0.22) !important;
  transition: transform .12s ease, box-shadow .12s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
  background: linear-gradient(135deg, #047A40 0%, #12A85F 100%) !important;
  box-shadow: 0 18px 34px rgba(0,158,82,0.30) !important;
  transform: translateY(-1px);
}

/* ── Campos de formulário ─────────────────────────────────── */
.stTextInput input, .stTextArea textarea, div[data-baseweb="select"] > div {
  background: rgba(9,30,23,0.85) !important;
  border: 1px solid var(--nx-border-mid) !important;
  color: var(--nx-text) !important;
  border-radius: 10px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
  border-color: var(--nx-green) !important;
  box-shadow: 0 0 0 4px rgba(0,158,82,0.16) !important;
}
.stTextInput label, .stSelectbox label, .stFileUploader label {
  color: var(--nx-text-muted) !important; font-weight: 600 !important;
}

/* ── Upload ───────────────────────────────────────────────── */
[data-testid="stFileUploaderDropzone"] {
  background: rgba(9,30,23,0.60) !important;
  border: 1px dashed rgba(0,158,82,0.32) !important;
  border-radius: 14px !important;
}

/* ── Status / alertas ─────────────────────────────────────── */
[data-testid="stStatusWidget"], [data-testid="stNotification"], [data-testid="stExpander"] {
  border-radius: 14px !important;
  border: 1px solid var(--nx-border) !important;
}
hr { border-color: var(--nx-border-mid) !important; }

/* ── Rodapé corporativo ───────────────────────────────────── */
.nx-footer {
  margin-top: 30px; padding-top: 16px;
  border-top: 1px solid var(--nx-border);
  display: flex; align-items: center; justify-content: space-between;
  font-size: 12px; color: var(--nx-text-muted);
}
.nx-footer .nx-foot-brand { font-weight: 700; color: #C7D4CD; letter-spacing: .3px; }
.nx-footer .nx-foot-brand b { color: var(--nx-green); }
</style>
"""

_RODAPE = """
<div class="nx-footer">
  <span class="nx-foot-brand">ne<b>xx</b>a · Food Service Solution</span>
  <span>TeamsAta — transcrição e atas com IA · Groq + Whisper</span>
</div>
"""


def aplicar_tema():
    """Injeta o CSS da Nexxa e renderiza o cabeçalho corporativo com o logo oficial."""
    st.markdown(_CSS, unsafe_allow_html=True)
    cabecalho = f"""
<div class="nx-header">
  <img class="nx-logo" src="{_logo_data_uri()}" alt="Nexxa Food Service Solution">
  <div class="nx-header-right">
    <span class="nx-portal">TeamsAta</span>
    <span class="nx-portal-sub">Geração inteligente de atas de reunião</span>
  </div>
</div>
"""
    st.markdown(cabecalho, unsafe_allow_html=True)


def rodape():
    """Renderiza o rodapé institucional."""
    st.markdown(_RODAPE, unsafe_allow_html=True)

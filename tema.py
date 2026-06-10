"""Identidade visual corporativa da Nexxa para a interface Streamlit.

Recria o design system da Nexxa (verde esmeralda sobre verde-escuro, tipografia
Plus Jakarta Sans, superfícies com vidro fosco) e renderiza o cabeçalho com o
logo oficial e um rodapé corporativo.
"""
import streamlit as st

# Logo oficial da Nexxa (marca + wordmark + tagline). Fonte: assets/nexxa-logo.svg
_LOGO_SVG = """
<svg class="nx-logo" viewBox="0 0 360 132" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Nexxa Food Service Solution">
  <g transform="translate(2 0)">
    <path d="M54 11 96 83H12L54 11Z" stroke="#5FE08F" stroke-width="8" stroke-linejoin="round"/>
    <path d="M54 33 78 74H30L54 33Z" stroke="#5FE08F" stroke-width="8" stroke-linejoin="round"/>
    <path d="M22 96H86" stroke="#5FE08F" stroke-width="8" stroke-linecap="round"/>
  </g>
  <text x="130" y="72" fill="#F5FAF7" font-family="Plus Jakarta Sans, Segoe UI, Arial, sans-serif" font-size="46" font-weight="600" letter-spacing="1">Nexxa</text>
  <text x="132" y="112" fill="#D9E6DF" font-family="Plus Jakarta Sans, Segoe UI, Arial, sans-serif" font-size="21" font-weight="400" letter-spacing=".4">Food Service Solution</text>
</svg>
"""

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
  --nx-green: #5FE08F;
  --nx-green-dark: #22C55E;
  --nx-green-deeper: #16A34A;
  --nx-text: #F0FDF4;
  --nx-text-muted: #9DB5AB;
  --nx-border: rgba(95,224,143,0.12);
  --nx-border-mid: rgba(95,224,143,0.18);
}

/* Tipografia corporativa da marca */
html, body, [class*="css"], .stApp, button, input, textarea, select {
  font-family: 'Plus Jakarta Sans', 'Segoe UI', Arial, sans-serif !important;
}

/* Fundo institucional — verde-escuro em gradiente */
.stApp {
  background:
    radial-gradient(circle at 12% -10%, rgba(95,224,143,0.10), transparent 30%),
    radial-gradient(circle at 92% 4%, rgba(34,197,94,0.08), transparent 28%),
    linear-gradient(180deg, #061815 0%, #072019 38%, #08231c 100%) !important;
  color: var(--nx-text);
}
[data-testid="stHeader"] { background: transparent !important; }

/* Largura de conteúdo mais ampla, com respiro */
.block-container { max-width: 920px; padding-top: 2.2rem; }

/* ── Cabeçalho corporativo ───────────────────────────────── */
.nx-header {
  display: flex; align-items: center; justify-content: space-between;
  gap: 18px; padding: 20px 26px; margin-bottom: 6px;
  background: linear-gradient(180deg, rgba(8,32,26,0.94) 0%, rgba(9,36,30,0.86) 100%);
  border: 1px solid var(--nx-border-mid);
  border-radius: 16px;
  box-shadow: 0 18px 40px rgba(0,0,0,0.40);
  backdrop-filter: blur(18px);
  position: relative; overflow: hidden;
}
.nx-header::before {
  content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 4px;
  background: linear-gradient(180deg, #5FE08F, #16A34A);
}
.nx-logo { height: 50px; width: auto; display: block; }
.nx-header-right { text-align: right; }
.nx-portal {
  display: inline-block;
  font-size: 12.5px; font-weight: 700; letter-spacing: .5px; text-transform: uppercase;
  color: var(--nx-green);
  background: rgba(95,224,143,0.10);
  border: 1px solid rgba(95,224,143,0.22);
  border-radius: 999px; padding: 5px 14px;
}
.nx-portal-sub {
  display: block; margin-top: 6px;
  font-size: 12px; color: var(--nx-text-muted); letter-spacing: .2px;
}

/* ── Títulos ──────────────────────────────────────────────── */
h1, h2, h3, h4 { color: var(--nx-text) !important; font-weight: 700 !important; letter-spacing: .2px; }

/* ── Botões — gradiente verde da marca ────────────────────── */
.stButton > button, .stDownloadButton > button {
  background: linear-gradient(135deg, #22C55E 0%, #5FE08F 100%) !important;
  color: #052016 !important;
  font-weight: 700 !important;
  border: 1px solid rgba(95,224,143,0.50) !important;
  border-radius: 12px !important;
  padding: 0.55rem 1rem !important;
  box-shadow: 0 12px 26px rgba(95,224,143,0.20) !important;
  transition: transform .12s ease, box-shadow .12s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
  background: linear-gradient(135deg, #16A34A 0%, #4ADE80 100%) !important;
  box-shadow: 0 18px 34px rgba(95,224,143,0.28) !important;
  transform: translateY(-1px);
}

/* ── Campos de formulário ─────────────────────────────────── */
.stTextInput input, .stTextArea textarea, div[data-baseweb="select"] > div {
  background: rgba(10,36,30,0.82) !important;
  border: 1px solid var(--nx-border-mid) !important;
  color: var(--nx-text) !important;
  border-radius: 10px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
  border-color: var(--nx-green) !important;
  box-shadow: 0 0 0 4px rgba(95,224,143,0.14) !important;
}
.stTextInput label, .stSelectbox label, .stFileUploader label {
  color: var(--nx-text-muted) !important; font-weight: 600 !important;
}

/* ── Upload ───────────────────────────────────────────────── */
[data-testid="stFileUploaderDropzone"] {
  background: rgba(10,36,30,0.60) !important;
  border: 1px dashed rgba(95,224,143,0.30) !important;
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
.nx-footer .nx-foot-brand { font-weight: 600; color: var(--nx-text); }
.nx-footer .nx-foot-brand b { color: var(--nx-green); }
</style>
"""

_CABECALHO = f"""
<div class="nx-header">
  <div class="nx-header-left">{_LOGO_SVG}</div>
  <div class="nx-header-right">
    <span class="nx-portal">TeamsAta</span>
    <span class="nx-portal-sub">Geração inteligente de atas de reunião</span>
  </div>
</div>
"""

_RODAPE = """
<div class="nx-footer">
  <span class="nx-foot-brand">Ne<b>xx</b>a · Food Service Solution</span>
  <span>TeamsAta — IA de transcrição e atas · Groq + Whisper</span>
</div>
"""


def aplicar_tema():
    """Injeta o CSS da Nexxa e renderiza o cabeçalho corporativo."""
    st.markdown(_CSS, unsafe_allow_html=True)
    st.markdown(_CABECALHO, unsafe_allow_html=True)


def rodape():
    """Renderiza o rodapé institucional."""
    st.markdown(_RODAPE, unsafe_allow_html=True)

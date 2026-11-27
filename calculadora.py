import streamlit as st
import streamlit.components.v1 as components
import numpy as np
from scipy.optimize import newton

# ==============================================================================
# IDENTIDADE DO PROJETO
# ==============================================================================
NOME_DO_PROJETO = "HIDRO-VIA (Laboratório Virtual de Hidrodinâmica) UERJ-ZO"
SUBTITULO = "Simulador Interativo de Propagação de Ondas Oceânicas — Teoria Linear de Airy"
INSTITUICAO = "Universidade do Estado do Rio de Janeiro (Campus Zona Oeste)"
# ==============================================================================

st.set_page_config(
    page_title="HIDRO-VIA | Laboratório Virtual de Hidrodinâmica UERJ-ZO",
    layout="wide"
)

# Estilo global (em linha única segura para evitar erro de colagem)
css_global = (
    '<style>'
    '[data-testid="stMetricValue"] { font-size: 1.32rem !important; color: #002855; font-weight: 700; }'
    '[data-testid="stMetricLabel"] { font-size: 0.84rem !important; color: #475569; }'
    'h3 { font-size: 1.15rem !important; color: #002855; }'
    '@keyframes waveMove1 { 0% { background-position-x: 0px; } 100% { background-position-x: 1000px; } }'
    '@keyframes waveMove2 { 0% { background-position-x: 1000px; } 100% { background-position-x: 0px; } }'
    '.header-banner { background: linear-gradient(135deg, #001845 0%, #002855 45%, #00509d 100%); padding: 24px 26px 32px 26px; border-radius: 12px; margin-bottom: 20px; border-left: 6px solid #00b4d8; box-shadow: 0 6px 18px rgba(0, 40, 85, 0.18); position: relative; overflow: hidden; }'
    '.header-badge { display: inline-block; background: rgba(0, 180, 216, 0.2); border: 1px solid rgba(144, 224, 239, 0.45); color: #90e0ef; font-size: 11px; font-weight: 600; padding: 3px 10px; border-radius: 20px; margin-bottom: 8px; letter-spacing: 0.5px; text-transform: uppercase; }'
    '.header-wave-back { position: absolute; bottom: 0; left: 0; width: 100%; height: 22px; background: url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 1200 120\' preserveAspectRatio=\'none\'%3E%3Cpath d=\'M0,40 C300,110 900,0 1200,50 L1200,120 L0,120 Z\' fill=\'rgba(144, 224, 239, 0.14)\'/%3E%3C/svg%3E"); background-size: 550px 22px; animation: waveMove2 16s linear infinite; }'
    '.header-wave-front { position: absolute; bottom: 0; left: 0; width: 100%; height: 18px; background: url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 1200 120\' preserveAspectRatio=\'none\'%3E%3Cpath d=\'M0,60 C350,120 850,0 1200,60 L1200,120 L0,120 Z\' fill=\'rgba(202, 240, 248, 0.22)\'/%3E%3C/svg%3E"); background-size: 480px 18px; animation: waveMove1 10s linear infinite; }'
    '.info-card { background: #f8fafc; border: 1px solid #cbd5e1; border-left: 5px solid #00509d; border-radius: 8px; padding: 16px 20px; margin-top: 10px; margin-bottom: 16px; }'
    '.welcome-box { background: linear-gradient(180deg, #f8fafc 0%, #eff6ff 100%); border: 1px solid #bfdbfe; border-radius: 10px; padding: 22px; margin-top: 14px; }'
    '.footer-uerj { text-align: center; color: #64748b; font-size: 12px; margin-top: 30px; padding: 14px; border-top: 1px solid #e2e8f0; }'
    '</style>'
)
st.markdown(css_global, unsafe_allow_html=True)

# Cabeçalho estilizado com ondas duplas animadas
header_html = (
    f'<div class="header-banner">'
    f'<div class="header-badge">Plataforma Educacional de Hidrodinâmica Costeira</div>'
    f'<h1 style="color: white; margin: 0; font-size: 22px; letter-spacing: 0.3px;">{NOME_DO_PROJETO}</h1>'
    f'<p style="color: #caf0f8; margin: 5px 0 0 0; font-size: 13.5px;">{SUBTITULO}</p>'
    f'<p style="color: #90e0ef; margin: 8px 0 0 0; font-size: 12px;"><b>Instituição:</b> {INSTITUICAO}</p>'
    f'<div class="header-wave-back"></div>'
    f'<div class="header-wave-front"></div>'
    f'</div>'
)
st.markdown(header_html, unsafe_allow_html=True)

if "calculado" not in st.session_state:
    st.session_state["calculado"] = False

# Painel de Controle diretamente na tela principal
st.markdown("### Painel de Controle do Ensaio")
st.caption("Defina os parâmetros físicos da onda incidente e clique em **Calcular** para executar a simulação:")

with st.container(border=True):
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        T = st.number_input("Período da onda T (s):", min_value=1.0, max_value=30.0, value=10.0, step=0.5, help="Tempo entre a passagem de duas cristas consecutivas.")
    with p2:
        h = st.number_input("Profundidade local h (m):", min_value=0.5, max_value=500.0, value=15.0, step=1.0, help="Distância vertical entre o nível médio do mar e o fundo.")
    with p3:
        H = st.number_input("Altura da onda H (m):", min_value=0.1, max_value=30.0, value=2.0, step=0.1, help="Distância vertical entre a cava e a crista da onda.")
    with p4:

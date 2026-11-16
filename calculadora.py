import streamlit as st
import numpy as np
from scipy.optimize import newton
import matplotlib.pyplot as plt

# ==============================================================================
# IDENTIDADE DO PROJETO
# ==============================================================================
NOME_DO_PROJETO = "HIDRO-VIA (Laboratório Virtual de Hidrodinâmica) UERJ-ZO"
SUBTITULO = "Simulador Interativo de Propagação de Ondas Oceânicas (Teoria Linear de Airy)"
INSTITUICAO = "Universidade do Estado do Rio de Janeiro (Campus Zona Oeste)"
# ==============================================================================

# Configuração da página (aba do navegador)
st.set_page_config(
    page_title="HIDRO-VIA (Laboratório Virtual de Hidrodinâmica) UERJ-ZO",
    layout="wide"
)

# Ajuste de tamanho das fontes (mais compactas e proporcionais)
st.markdown("""
    <style>
        /* Tamanho dos valores numéricos nos cartões */
        [data-testid="stMetricValue"] {
            font-size: 1.35rem !important;
        }
        /* Tamanho dos rótulos nos cartões */
        [data-testid="stMetricLabel"] {
            font-size: 0.85rem !important;
        }
        /* Subtítulos de seção */
        h3 {
            font-size: 1.15rem !important;
        }
    </style>
""", unsafe_allow_html=True)

# Cabeçalho estilizado com identidade institucional
st.markdown(f"""
    <div style="background: linear-gradient(90deg, #002855 0%, #00509d 100%); padding: 18px; border-radius: 10px; margin-bottom: 18px; border-left: 6px solid #00a8e8;">
        <h1 style="color: white; margin: 0; font-size: 21px;">{NOME_DO_PROJETO}</h1>
        <p style="color: #e0fbfc; margin: 4px 0 0 0; font-size: 13.5px;">{SUBTITULO}</p>
        <p style="color: #90e0ef; margin: 8px 0 0 0; font-size: 12px;">
            <b>Instituição:</b> {INSTITUICAO}
        </p>
    </div>
""", unsafe_allow_html=True)

# Painel de Controle com botão Calcular (st.form)
st.markdown("### Painel de Controle do Ensaio")
st.caption("Preencha os parâmetros da onda abaixo e clique em **Calcular** para gerar os resultados:")

with st.form(key="form_ensaio"):
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        T = st.number_input("Período da onda T (s):", min_value=1.0, max_value=30.0, value=10.0, step=0.5)
    with p2:
        h = st.number_input("Profundidade local h (m):", min_value=0.5, max_value=500.0, value=15.0, step=1.0)
    with p3:
        H = st.number_input("Altura da onda H (m):", min_value=0.1, max_value=30.0, value=2.0, step=0.1)
    with p4:
        rho = st.selectbox(
            "Densidade do fluido (kg/m³):",
            [1025.0, 1000.0],
            format_func=lambda x: f"{x} kg/m³ (Água do Mar)" if x == 1025.0 else f"{x} kg/m³ (Água Doce)"
        )
    
    st.markdown("")
    calcular = st.form_submit_button("Calcular", type="primary", use_container_width=True)

# Só salva os parâmetros quando o usuário clicar explicitamente no botão Calcular
if calcular:
    st.session_state["params"] = {"T": T, "h": h, "H": H, "rho": rho}

# Função matemática de cálculo (Relação de Dispersão)
def resolver_onda(T_val, h_val, g=9.81):
    omega = 2 * np.pi / T_val
    k0 = omega**2 / g
    f = lambda k: omega**2 - g * k * np.tanh(k * h_val)
    fprime = lambda k: -g * np.tanh(k * h_val) - g * k * h_val * (1 - np.tanh(k * h_val)**2)
    k = newton(f, x0=k0, fprime=fprime)
    L = 2 * np.pi / k
    C = L / T_val
    n = 0.5 * (1 + (2 * k * h_val) / np.sinh(2 * k * h_val))
    Cg = n * C

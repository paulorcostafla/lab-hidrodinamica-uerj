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
        [data-testid="stMetricValue"] {
            font-size: 1.35rem !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.85rem !important;
        }
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

# Inicializa o controle de exibição na memória da sessão
if "calculado" not in st.session_state:
    st.session_state["calculado"] = False

# Painel de Controle diretamente na tela principal
st.markdown("### Painel de Controle do Ensaio")
st.caption("Preencha os parâmetros da onda abaixo e clique em **Calcular** para gerar os resultados:")

with st.container(border=True):
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
    if st.button("Calcular", type="primary", use_container_width=True):
        st.session_state["calculado"] = True
        st.session_state["T_val"] = T
        st.session_state["h_val"] = h
        st.session_state["H_val"] = H
        st.session_state["rho_val"] = rho

# Função matemática de cálculo (Relação de Dispersão)
def resolver_onda(T_in, h_in, g=9.81):
    omega = 2 * np.pi / T_in
    k0 = omega**2 / g
    f = lambda k: omega**2 - g * k * np.tanh(k * h_in)
    fprime = lambda k: -g * np.tanh(k * h_in) - g * k * h_in * (1 - np.tanh(k * h_in)**2)
    k = newton(f, x0=k0, fprime=fprime)
    L = 2 * np.pi / k
    C = L / T_in
    n = 0.5 * (1 + (2 * k * h_in) / np.sinh(2 * k * h_in))
    Cg = n * C
    return k, L, C, Cg, h_in / L

# Só renderiza os resultados se o botão Calcular já tiver sido pressionado
if st.session_state["calculado"]:
    T_calc = st.session_state["T_val"]
    h_calc = st.session_state["h_val"]
    H_calc = st.session_state["H_val"]
    rho_calc = st.session_state["rho_val"]

    g = 9.81
    k, L, C, Cg, ratio = resolver_onda(T_calc, h_calc)
    E = (1/8) * rho_calc * g * (H_calc**2)

    if ratio > 0.5:
        regime = "Águas Profundas (h/L > 0.5)"
        cor_badge = "#0077b6"
    elif ratio < 0.05:
        regime = "Águas Rasas (h/L < 0.05)"
        cor_badge = "#d97706"
    else:
        regime = "Águas Intermediárias (0.05 ≤ h/L ≤ 0.5)"
        cor_badge = "#059669"

    st.markdown("---")
    st.markdown(f"### Resultados da Simulação — Regime: <span style='color:{cor_badge};'>{regime}</span>", unsafe_allow_html=True)

    # Bloco 1: Parâmetros de Entrada em quadrados individuais
    with st.container(border=True):
        st.markdown("**1. Parâmetros Definidos no Ensaio**")
        in1, in2, in3, in4 = st.columns(4)
        with in1:
            with st.container(border=True):
                st.metric("Período (T)", f"{T_calc:.2f} s")
        with in2:
            with st.container(border=True):
                st.metric("Altura da Onda (H)", f"{H_calc:.2f} m")
        with in3:
            with st.container(border=True):
                st.metric("Profundidade (h)", f"{h_calc:.2f} m")
        with in4:
            with st.container(border=True):
                st.metric("Densidade (ρ)", f"{rho_calc:.0f} kg/m³")

    # Bloco 2: Parâmetros Calculados em quadrados individuais
    with st.container(border=True):
        st.markdown("**2. Parâmetros Hidrodinâmicos Calculados**")
        out1, out2, out3, out4, out5 = st.columns(5)
        with out1:
            with st.container(border=True):
                st.metric("Comprimento (L)", f"{L:.2f} m")
        with out2:
            with st.container(border=True):
                st.metric("Vel. de Fase (C)", f"{C:.2f} m/s")
        with out3:
            with st.container(border=True):
                st.metric("Vel. de Grupo (Cg)", f"{Cg:.2f} m/s")
        with out4:
            with st.container(border=True):
                st.metric("Energia (E)", f"{E/1000:.2f} kJ/m²")
        with out5:
            with st.container(border=True):
                st.metric("Relação h/L", f"{ratio:.4f}")

    st.markdown("")

    # Bloco 3: Área do Gráfico Único ampliado dentro de um quadro
    with st.container(border=True):
        st.markdown("### Perfil Espacial da Onda")
        x = np.linspace(0, 2 * L, 500)
        eta = (H_calc / 2) * np.cos(k * x)

        fig, ax = plt.subplots(figsize=(10, 5.5))
        ax.plot(x, eta, color='#00509d', linewidth=2.5, label='Superfície Livre (η)')
        ax.fill_between(x, eta, -h_calc, color='#90e0ef', alpha=0.45)
        ax.axhline(0, color='gray', linestyle='--', linewidth=1.2, label='Nível Médio do Mar (z = 0)')
        ax.axhline(-h_calc, color='#7f4f24', linewidth=3.5, label=f'Fundo Oceânico (z = -{h_calc} m)')

        ax.set_xlabel("Distância horizontal x (m)", fontsize=11)
        ax.set_ylabel("Elevação vertical z (m)", fontsize=11)
        ax.tick_params(axis='both', labelsize=10)
        ax.set_ylim(-h_calc * 1.15, max(H_calc, h_calc * 0.3))
        ax.legend(loc="lower right", fontsize=10)
        ax.grid(True, linestyle=':', alpha=0.6)
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)

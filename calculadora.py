import streamlit as st
import numpy as np
from scipy.optimize import newton
import matplotlib.pyplot as plt

# ==============================================================================
# IDENTIDADE DO PROJETO
# ==============================================================================
NOME_DO_PROJETO = "Laboratório Virtual de Hidrodinâmica — UERJ-ZO"
SUBTITULO = "Simulador Interativo de Propagação de Ondas Oceânicas (Teoria Linear de Airy)"
INSTITUICAO = "Universidade do Estado do Rio de Janeiro (Campus Zona Oeste)"
# ==============================================================================

# Configuração da página (aba do navegador)
st.set_page_config(
    page_title="Lab Virtual Hidrodinâmica | UERJ-ZO",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cabeçalho estilizado com identidade institucional
st.markdown(f"""
    <div style="background: linear-gradient(90deg, #002855 0%, #00509d 100%); padding: 22px; border-radius: 10px; margin-bottom: 20px; border-left: 6px solid #00a8e8;">
        <h1 style="color: white; margin: 0; font-size: 28px;">{NOME_DO_PROJETO}</h1>
        <p style="color: #e0fbfc; margin: 6px 0 0 0; font-size: 16px;">{SUBTITULO}</p>
        <p style="color: #90e0ef; margin: 12px 0 0 0; font-size: 13px;">
            <b>Instituição:</b> {INSTITUICAO}
        </p>
    </div>
""", unsafe_allow_html=True)

# Barra lateral para os dados de entrada
st.sidebar.markdown("### UERJ - Campus Zona Oeste")
st.sidebar.header("Painel de Controle do Ensaio")
st.sidebar.markdown("Ajuste os parâmetros da onda abaixo:")

T = st.sidebar.number_input("Período da onda T (s):", min_value=1.0, max_value=30.0, value=10.0, step=0.5)
h = st.sidebar.number_input("Profundidade local h (m):", min_value=0.5, max_value=500.0, value=15.0, step=1.0)
H = st.sidebar.number_input("Altura da onda H (m):", min_value=0.1, max_value=30.0, value=2.0, step=0.1)
rho = st.sidebar.selectbox(
    "Densidade do fluido (kg/m³):",
    [1025.0, 1000.0],
    format_func=lambda x: f"{x} kg/m³ (Água do Mar)" if x == 1025.0 else f"{x} kg/m³ (Água Doce)"
)

st.sidebar.divider()
st.sidebar.info("**Dica de Simulação:** Varie a profundidade (h) para observar a transição entre águas profundas, intermediárias e rasas.")

# Função matemática de cálculo (Relação de Dispersão)
def resolver_onda(T, h, g=9.81):
    omega = 2 * np.pi / T
    k0 = omega**2 / g
    f = lambda k: omega**2 - g * k * np.tanh(k * h)
    fprime = lambda k: -g * np.tanh(k * h) - g * k * h * (1 - np.tanh(k * h)**2)
    k = newton(f, x0=k0, fprime=fprime)
    L = 2 * np.pi / k
    C = L / T
    n = 0.5 * (1 + (2 * k * h) / np.sinh(2 * k * h))
    Cg = n * C
    return k, L, C, Cg, h / L

# Execução dos cálculos
g = 9.81
k, L, C, Cg, ratio = resolver_onda(T, h)
E = (1/8) * rho * g * (H**2)  # Densidade de energia (J/m²)

# Classificação do regime de profundidade
if ratio > 0.5:
    regime = "Águas Profundas (h/L > 0.5)"
    cor_badge = "#0077b6"
elif ratio < 0.05:
    regime = "Águas Rasas (h/L < 0.05)"
    cor_badge = "#d97706"
else:
    regime = "Águas Intermediárias (0.05 ≤ h/L ≤ 0.5)"
    cor_badge = "#059669"

st.markdown(f"### Resultados da Simulação — Regime: <span style='color:{cor_badge};'>{regime}</span>", unsafe_allow_html=True)

# Linha 1 de métricas: Parâmetros de Entrada do Ensaio
st.markdown("**Parâmetros Definidos no Ensaio:**")
in1, in2, in3, in4 = st.columns(4)
in1.metric("Período (T)", f"{T:.2f} s")
in2.metric("Altura da Onda (H)", f"{H:.2f} m")
in3.metric("Profundidade (h)", f"{h:.2f} m")
in4.metric("Densidade (ρ)", f"{rho:.0f} kg/m³")

st.markdown("")

# Linha 2 de métricas: Parâmetros Hidrodinâmicos Calculados
st.markdown("**Parâmetros Hidrodinâmicos Calculados:**")
out1, out2, out3, out4, out5 = st.columns(5)
out1.metric("Comprimento (L)", f"{L:.2f} m")
out2.metric("Vel. de Fase (C)", f"{C:.2f} m/s")
out3.metric("Vel. de Grupo (Cg)", f"{Cg:.2f} m/s")
out4.metric("Energia (E)", f"{E/1000:.2f} kJ/m²")
out5.metric("Relação h/L", f"{ratio:.4f}")

st.divider()

# Área do Gráfico Único (Perfil Espacial da Onda)
st.markdown("### Perfil Espacial da Onda")
x = np.linspace(0, 2 * L, 500)
eta = (H / 2) * np.cos(k * x)

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(x, eta, color='#00509d', linewidth=2.5, label='Superfície Livre (η)')
ax.fill_between(x, eta, -h, color='#90e0ef', alpha=0.45)
ax.axhline(0, color='gray', linestyle='--', linewidth=1, label='Nível Médio do Mar (z = 0)')
ax.axhline(-h, color='#7f4f24', linewidth=3.5, label=f'Fundo Oceânico (z = -{h} m)')

ax.set_xlabel("Distância horizontal x (m)")
ax.set_ylabel("Elevação vertical z (m)")
ax.set_ylim(-h * 1.15, max(H, h * 0.3))
ax.legend(loc="lower right", fontsize=9)
ax.grid(True, linestyle=':', alpha=0.6)
st.pyplot(fig)

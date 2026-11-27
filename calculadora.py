import json
import streamlit as st
import streamlit.components.v1 as components
import numpy as np
from scipy.optimize import newton

# ==============================================================================
# IDENTIDADE DO PROJETO
# ==============================================================================
NOME_DO_PROJETO = "HIDRO-VIA (Laboratório Virtual de Hidrodinâmica) UERJ-ZO"
SUBTITULO = "Simulador Interativo de Propagação de Ondas Oceânicas (Teoria Linear de Airy)"
INSTITUICAO = "Universidade do Estado do Rio de Janeiro (Campus Zona Oeste)"
# ==============================================================================

st.set_page_config(
    page_title="HIDRO-VIA (Laboratório Virtual de Hidrodinâmica) UERJ-ZO",
    layout="wide"
)

# Ajuste de tamanho das fontes, animação do cabeçalho e estilo interativo
st.markdown("""
    <style>
        [data-testid="stMetricValue"] {
            font-size: 1.35rem !important;
            color: #002855;
            font-weight: 700;
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.85rem !important;
        }
        h3 {
            font-size: 1.15rem !important;
            color: #002855;
        }
        /* Onda animada no cabeçalho */
        @keyframes waveMove {
            0% { background-position-x: 0px; }
            100% { background-position-x: 1000px; }
        }
        .header-banner {
            background: linear-gradient(135deg, #001d3d 0%, #003566 50%, #0077b6 100%);
            padding: 22px 24px;
            border-radius: 12px;
            margin-bottom: 20px;
            border-left: 6px solid #00b4d8;
            box-shadow: 0 4px 12px rgba(0, 40, 85, 0.15);
            position: relative;
            overflow: hidden;
        }
        .header-wave {
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 18px;
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 120' preserveAspectRatio='none'%3E%3Cpath d='M0,60 C300,120 900,0 1200,60 L1200,120 L0,120 Z' fill='rgba(144, 224, 239, 0.22)'/%3E%3C/svg%3E");
            background-size: 500px 18px;
            animation: waveMove 10s linear infinite;
        }
        /* Efeito de brilho líquido e elevação no botão Calcular */
        div.stButton > button[kind="primary"] {
            background: linear-gradient(90deg, #00509d 0%, #0077b6 50%, #00b4d8 100%);
            border: none;
            border-radius: 8px;
            font-weight: 600;
            letter-spacing: 0.4px;
            box-shadow: 0 4px 14px rgba(0, 119, 182, 0.30);
            transition: all 0.22s ease;
        }
        div.stButton > button[kind="primary"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 180, 216, 0.45);
        }
        div.stButton > button[kind="primary"]:active {
            transform: scale(0.98);
        }
        /* Fundo com degradê de mar */
        .stApp {
            background: linear-gradient(180deg, #e0f7ff 0%, #f0f9ff 40%, #ffffff 100%);
        }
        /* Cartões de métricas: sobem, brilham e mudam de cor ao passar o mouse */
        [data-testid="stMetric"] {
            cursor: pointer;
            padding: 8px 10px;
            border-radius: 10px;
            border-top: 3px solid #00b4d8;
            background: linear-gradient(180deg, #ffffff 0%, #e8f8ff 100%);
            transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
        }
        [data-testid="stMetric"]:hover {
            transform: translateY(-4px) scale(1.04);
            box-shadow: 0 8px 20px rgba(0, 180, 216, 0.35);
            background: linear-gradient(135deg, #caf0f8 0%, #90e0ef 100%);
        }
        [data-testid="stMetric"]:hover [data-testid="stMetricValue"] {
            color: #023e8a;
        }
        /* Campos acendem ao passar o mouse */
        div[data-baseweb="input"], div[data-baseweb="select"] > div {
            transition: box-shadow 0.2s ease;
        }
        div[data-baseweb="input"]:hover, div[data-baseweb="select"] > div:hover {
            box-shadow: 0 0 0 3px rgba(0, 180, 216, 0.35);
        }
        /* Cabeçalho: ao passar o mouse, a onda acelera e o banner brilha */
        .header-banner { transition: box-shadow 0.3s ease, filter 0.3s ease; }
        .header-banner:hover {
            box-shadow: 0 8px 28px rgba(0, 180, 216, 0.45);
            filter: saturate(1.3) brightness(1.08);
        }
        .header-banner:hover .header-wave { animation-duration: 3s; }
    </style>
""", unsafe_allow_html=True)

# Sons de interação (hover e clique) injetados na página principal
JS_SOM = """
(function () {
  if (window.__hidroSom) return;
  window.__hidroSom = true;
  let ac = null, liberado = false;
  function blip(freq, dur, vol) {
    if (!liberado) return;  // navegadores só permitem som depois do primeiro clique
    try {
      const AC = window.AudioContext || window.webkitAudioContext;
      if (!ac) ac = new AC();
      if (ac.state === 'suspended') ac.resume();
      const t = ac.currentTime;
      const o = ac.createOscillator(), g = ac.createGain();
      o.type = 'sine';
      o.frequency.setValueAtTime(freq, t);
      o.frequency.exponentialRampToValueAtTime(freq * 1.6, t + dur);
      g.gain.setValueAtTime(0.001, t);
      g.gain.linearRampToValueAtTime(vol, t + 0.012);
      g.gain.exponentialRampToValueAtTime(0.001, t + dur);
      o.connect(g); g.connect(ac.destination);
      o.start(t); o.stop(t + dur + 0.02);
    } catch (e) {}
  }
  const alvo = '[data-testid="stMetric"], .stButton button, [data-baseweb="input"], [data-baseweb="select"]';
  let ultimo = null;
  document.addEventListener('mouseover', function (e) {
    const el = e.target.closest ? e.target.closest(alvo) : null;
    if (!el || el === ultimo) return;
    ultimo = el;
    blip(520 + Math.random() * 180, 0.09, 0.035);
  });
  document.addEventListener('mouseout', function (e) {
    if (!ultimo || !e.relatedTarget || !ultimo.contains(e.relatedTarget)) ultimo = null;
  });
  document.addEventListener('pointerdown', function (e) {
    liberado = true;
    if (e.target.closest && e.target.closest('.stButton button')) blip(330, 0.16, 0.06);
  });
  document.addEventListener('click', function (e) {
    const card = e.target.closest ? e.target.closest('[data-testid="stMetric"]') : null;
    if (!card) return;
    const caixa = card.closest('[data-testid="stVerticalBlockBorderWrapper"]');
    const btn = caixa && caixa.querySelector('[data-testid="stPopover"] button, button[data-testid="stPopoverButton"]');
    if (btn) { blip(700, 0.1, 0.05); btn.click(); }
  });
})();
"""
components.html(
    "<script>const s = window.parent.document.createElement('script');"
    f"s.textContent = {json.dumps(JS_SOM)};"
    "window.parent.document.head.appendChild(s);</script>",
    height=0,
)

# Cabeçalho estilizado com onda animada
st.markdown(f"""
    <div class="header-banner">
        <h1 style="color: white; margin: 0; font-size: 22px; letter-spacing: 0.3px;">{NOME_DO_PROJETO}</h1>
        <p style="color: #caf0f8; margin: 5px 0 0 0; font-size: 13.5px;">{SUBTITULO}</p>
        <p style="color: #90e0ef; margin: 8px 0 0 0; font-size: 12px;">
            <b>Instituição:</b> {INSTITUICAO}
        </p>
        <div class="header-wave"></div>
    </div>
""", unsafe_allow_html=True)

if "calculado" not in st.session_state:
    st.session_state["calculado"] = False

# Painel de Controle diretamente na tela principal
st.markdown("### Painel de Controle do Ensaio")
st.caption("Preencha os parâmetros da onda abaixo e clique em **Calcular** para iniciar a simulação:")

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
    k0 = omega**2 / (g * np.sqrt(np.tanh(omega**2 * h_in / g)))  # chute inicial melhor p/ águas rasas
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
        omega_calc = 2 * np.pi / T_calc
        kh = k * h_calc
        n_calc = Cg / C
        st.caption("Clique em qualquer resultado para ver, passo a passo, como ele foi calculado.")
        out1, out2, out3, out4, out5 = st.columns(5)
        with out1:
            with st.container(border=True):
                st.metric("Comprimento (L)", f"{L:.2f} m")
                with st.popover("Como chegou?", use_container_width=True):
                    st.markdown("**Comprimento de onda (L)**")
                    st.markdown("**1.** Frequência angular a partir do período:")
                    st.latex(rf"\omega = \frac{{2\pi}}{{T}} = \frac{{2\pi}}{{{T_calc:.2f}}} = {omega_calc:.4f}\ \text{{rad/s}}")
                    st.markdown("**2.** Relação de dispersão. Ela não tem solução direta para k, então o app resolve por Newton-Raphson:")
                    st.latex(r"\omega^2 = g\,k\,\tanh(kh)")
                    st.latex(rf"{omega_calc**2:.4f} = 9.81 \cdot k \cdot \tanh(k \cdot {h_calc:.2f}) \;\Rightarrow\; k = {k:.5f}\ \text{{rad/m}}")
                    st.markdown("**3.** Comprimento de onda:")
                    st.latex(rf"L = \frac{{2\pi}}{{k}} = \frac{{2\pi}}{{{k:.5f}}} = {L:.2f}\ \text{{m}}")
        with out2:
            with st.container(border=True):
                st.metric("Vel. de Fase (C)", f"{C:.2f} m/s")
                with st.popover("Como chegou?", use_container_width=True):
                    st.markdown("**Velocidade de fase (C)**")
                    st.markdown("É a velocidade com que uma crista da onda se desloca: distância de um comprimento de onda dividida pelo tempo de um período.")
                    st.latex(r"C = \frac{L}{T}")
                    st.latex(rf"C = \frac{{{L:.2f}}}{{{T_calc:.2f}}} = {C:.2f}\ \text{{m/s}}")
        with out3:
            with st.container(border=True):
                st.metric("Vel. de Grupo (Cg)", f"{Cg:.2f} m/s")
                with st.popover("Como chegou?", use_container_width=True):
                    st.markdown("**Velocidade de grupo (Cg)**")
                    st.markdown("É a velocidade com que a energia da onda se propaga.")
                    st.markdown("**1.** Número de onda vezes a profundidade:")
                    st.latex(rf"kh = {k:.5f} \cdot {h_calc:.2f} = {kh:.3f}")
                    st.markdown("**2.** Fator n:")
                    st.latex(rf"n = \frac{{1}}{{2}}\left[1 + \frac{{2kh}}{{\sinh(2kh)}}\right] = {n_calc:.4f}")
                    st.markdown("**3.** Velocidade de grupo:")
                    st.latex(rf"C_g = n \cdot C = {n_calc:.4f} \cdot {C:.2f} = {Cg:.2f}\ \text{{m/s}}")
        with out4:
            with st.container(border=True):
                st.metric("Energia (E)", f"{E/1000:.2f} kJ/m²")
                with st.popover("Como chegou?", use_container_width=True):
                    st.markdown("**Energia da onda (E)**")
                    st.markdown("Energia total (potencial + cinética) por metro quadrado de superfície, na teoria linear:")
                    st.latex(r"E = \frac{1}{8}\,\rho\, g\, H^2")
                    st.latex(rf"E = \frac{{1}}{{8}} \cdot {rho_calc:.0f} \cdot 9.81 \cdot {H_calc:.2f}^2 = {E:.1f}\ \text{{J/m}}^2")
                    st.latex(rf"E = {E/1000:.2f}\ \text{{kJ/m}}^2")
        with out5:
            with st.container(border=True):
                st.metric("Relação h/L", f"{ratio:.4f}")
                with st.popover("Como chegou?", use_container_width=True):
                    st.markdown("**Relação h/L**")
                    st.markdown("Profundidade dividida pelo comprimento de onda. É ela que define o regime:")
                    st.latex(rf"\frac{{h}}{{L}} = \frac{{{h_calc:.2f}}}{{{L:.2f}}} = {ratio:.4f}")
                    st.markdown("- h/L > 0,5: águas profundas\n- 0,05 ≤ h/L ≤ 0,5: águas intermediárias\n- h/L < 0,05: águas rasas")
                    st.markdown(f"Resultado: **{regime}**")

    st.markdown("")

    # Bloco 3: Canal de Ondas Interativo (clique na água gera ondulações, gotículas e som de água!)
    with st.container(border=True):
        st.markdown("### Canal de Ondas Interativo — η(x, t)")
        st.caption(f"Propagação em tempo real: 4 comprimentos de onda (0 a {4*L:.1f} m) | Clique em qualquer ponto da água para perturbar a superfície.")

        html_onda = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
            body {{
                margin: 0;
                padding: 0;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background: transparent;
                user-select: none;
            }}
            .controls {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
                flex-wrap: wrap;
                gap: 8px;
            }}
            .btn-group {{
                display: flex;
                gap: 8px;
                align-items: center;
            }}
            .btn {{
                background-color: #00509d;
                color: white;
                border: none;
                padding: 6px 14px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 13px;
                font-weight: 500;
                transition: all 0.2s;
            }}
            .btn:hover {{
                background-color: #003566;
                transform: translateY(-1px);
            }}
            .btn-outline {{
                background-color: #e0f2fe;
                color: #0369a1;
                border: 1px solid #7dd3fc;
            }}
            .btn-outline:hover {{
                background-color: #bae6fd;
            }}
            .legend {{
                display: flex;
                gap: 16px;
                font-size: 12px;
                color: #334155;
                flex-wrap: wrap;
            }}
            .legend-item {{
                display: flex;
                align-items: center;
                gap: 6px;
            }}
            .box-wave {{ width: 16px; height: 4px; background: #0077b6; border-radius: 2px; }}
            .box-mean {{ width: 16px; height: 0; border-top: 2px dashed #64748b; }}
            .box-bed  {{ width: 16px; height: 5px; background: #7f4f24; border-radius: 2px; }}
            canvas {{
                width: 100%;
                height: 370px;
                border-radius: 8px;
                border: 1px solid #cbd5e1;
                background: linear-gradient(180deg, #d9f4ff 0%, #f0f9ff 100%);
                display: block;
                cursor: crosshair;
            }}
        </style>
        </head>
        <body>
            <div class="controls">
                <div class="btn-group">
                    <button class="btn" id="toggleBtn" onclick="toggleAnim()">Pausar Onda</button>
                    <button class="btn btn-outline" onclick="triggerCenterSplash()">Gerar Perturbação</button>
                </div>
                <div class="legend">
                    <div class="legend-item"><span class="box-wave"></span> Superfície Livre η(x, t)</div>
                    <div class="legend-item"><span class="box-mean"></span> Nível Médio (z = 0)</div>
                    <div class="legend-item"><span class="box-bed"></span> Fundo Oceânico (z = -{h_calc:.1f} m)</div>
                </div>
            </div>
            <canvas id="waveCanvas"></canvas>

            <script>
                const canvas = document.getElementById('waveCanvas');
                const ctx = canvas.getContext('2d');

                const H = {H_calc};
                const h = {h_calc};
                const L = {L};
                const T = {T_calc};
                const numWaves = 4;
                const maxX = numWaves * L;
                const k = (2 * Math.PI) / L;
                const omega = (2 * Math.PI) / T;

                let running = true;
                let lastTime = performance.now();
                let simTime = 0;

                // Síntese de áudio realista de gota/respingo de água via Web Audio API
                let audioCtx = null;

                function playWaterSplashSound() {{
                    try {{
                        if (!audioCtx) {{
                            const AudioContext = window.AudioContext || window.webkitAudioContext;
                            audioCtx = new AudioContext();
                        }}
                        if (audioCtx.state === 'suspended') {{
                            audioCtx.resume();
                        }}

                        const now = audioCtx.currentTime;

                        // 1. Ruído filtrado curto (impacto do respingo na superfície)
                        const bufferSize = Math.floor(audioCtx.sampleRate * 0.14);
                        const noiseBuffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
                        const output = noiseBuffer.getChannelData(0);
                        for (let i = 0; i < bufferSize; i++) {{
                            output[i] = (Math.random() * 2 - 1) * Math.exp(-i / (audioCtx.sampleRate * 0.032));
                        }}

                        const whiteNoise = audioCtx.createBufferSource();
                        whiteNoise.buffer = noiseBuffer;

                        const filter = audioCtx.createBiquadFilter();
                        filter.type = 'bandpass';
                        filter.frequency.setValueAtTime(900 + Math.random() * 350, now);
                        filter.Q.setValueAtTime(2.8, now);

                        const noiseGain = audioCtx.createGain();
                        noiseGain.gain.setValueAtTime(0.28, now);
                        noiseGain.gain.exponentialRampToValueAtTime(0.001, now + 0.14);

                        whiteNoise.connect(filter);
                        filter.connect(noiseGain);
                        noiseGain.connect(audioCtx.destination);
                        whiteNoise.start(now);

                        // 2. Bolha ressonante ("plop" característico da água subindo de frequência)
                        const osc = audioCtx.createOscillator();
                        const oscGain = audioCtx.createGain();
                        osc.type = 'sine';

                        const baseFreq = 360 + Math.random() * 140;
                        osc.frequency.setValueAtTime(baseFreq, now + 0.015);
                        osc.frequency.exponentialRampToValueAtTime(baseFreq * 2.35, now + 0.16);

                        oscGain.gain.setValueAtTime(0.001, now);
                        oscGain.gain.linearRampToValueAtTime(0.18, now + 0.025);
                        oscGain.gain.exponentialRampToValueAtTime(0.001, now + 0.17);

                        osc.connect(oscGain);
                        oscGain.connect(audioCtx.destination);
                        osc.start(now + 0.01);
                        osc.stop(now + 0.18);

                        // 3. Segunda micro-bolha secundária bem sutil
                        const osc2 = audioCtx.createOscillator();
                        const osc2Gain = audioCtx.createGain();
                        osc2.type = 'sine';
                        const freq2 = 580 + Math.random() * 180;
                        osc2.frequency.setValueAtTime(freq2, now + 0.055);
                        osc2.frequency.exponentialRampToValueAtTime(freq2 * 1.9, now + 0.18);

                        osc2Gain.gain.setValueAtTime(0.001, now + 0.05);
                        osc2Gain.gain.linearRampToValueAtTime(0.08, now + 0.065);
                        osc2Gain.gain.exponentialRampToValueAtTime(0.001, now + 0.19);

                        osc2.connect(osc2Gain);
                        osc2Gain.connect(audioCtx.destination);
                        osc2.start(now + 0.05);
                        osc2.stop(now + 0.20);
                    }} catch (err) {{
                        // Ignora silenciosamente se o navegador bloquear áudio antes de interação
                    }}
                }}

                // Sistema interativo de respingos (gotículas + ondas concêntricas ao clicar)
                let splashes = [];
                let droplets = [];

                function spawnSplash(px, py, withSound = true) {{
                    if (withSound) {{
                        playWaterSplashSound();
                    }}
                    splashes.push({{
                        x: px,
                        y: py,
                        radius: 4,
                        alpha: 0.95
                    }});
                    for (let i = 0; i < 14; i++) {{
                        const angle = -Math.PI * (0.12 + Math.random() * 0.76);
                        const speed = 70 + Math.random() * 140;
                        droplets.push({{
                            x: px,
                            y: py,
                            vx: Math.cos(angle) * speed,
                            vy: Math.sin(angle) * speed,
                            radius: 1.8 + Math.random() * 2.4,
                            alpha: 1.0
                        }});
                    }}
                }}

                canvas.addEventListener('pointerdown', (e) => {{
                    const rect = canvas.getBoundingClientRect();
                    const x = e.clientX - rect.left;
                    const y = e.clientY - rect.top;
                    spawnSplash(x, y, true);
                }});

                // Mouse sobre a água: marcador que acompanha a superfície livre
                let mouseX = null;
                canvas.addEventListener('pointermove', (e) => {{
                    mouseX = e.clientX - canvas.getBoundingClientRect().left;
                }});
                canvas.addEventListener('pointerleave', () => {{ mouseX = null; }});
                canvas.addEventListener('pointerenter', () => {{
                    // tique suave ao entrar (só soa depois que a pessoa já clicou na água)
                    if (!audioCtx) return;
                    try {{
                        const t = audioCtx.currentTime;
                        const o = audioCtx.createOscillator();
                        const g = audioCtx.createGain();
                        o.frequency.setValueAtTime(620, t);
                        o.frequency.exponentialRampToValueAtTime(980, t + 0.08);
                        g.gain.setValueAtTime(0.001, t);
                        g.gain.linearRampToValueAtTime(0.04, t + 0.01);
                        g.gain.exponentialRampToValueAtTime(0.001, t + 0.09);
                        o.connect(g); g.connect(audioCtx.destination);
                        o.start(t); o.stop(t + 0.1);
                    }} catch (err) {{}}
                }});

                function triggerCenterSplash() {{
                    const rect = canvas.getBoundingClientRect();
                    spawnSplash(rect.width * 0.5, rect.height * 0.42, true);
                }}

                function toggleAnim() {{
                    running = !running;
                    document.getElementById('toggleBtn').innerText = running ? 'Pausar Onda' : 'Continuar Onda';
                    if (running) {{
                        lastTime = performance.now();  // o laço de animação já continua rodando
                    }}
                }}

                function resizeCanvas() {{
                    const rect = canvas.getBoundingClientRect();
                    const dpr = window.devicePixelRatio || 1;
                    canvas.width = rect.width * dpr;
                    canvas.height = rect.height * dpr;
                    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
                }}

                window.addEventListener('resize', resizeCanvas);
                resizeCanvas();

                // Pequena ondulação visual inicial ao abrir o gráfico (sem som automático)
                setTimeout(() => {{
                    const rect = canvas.getBoundingClientRect();
                    spawnSplash(rect.width * 0.35, rect.height * 0.42, false);
                }}, 250);

                function draw(now) {{
                    const dt = Math.min((now - lastTime) / 1000, 0.05);
                    lastTime = now;
                    if (running) {{
                        simTime += dt;
                    }}

                    const width = canvas.getBoundingClientRect().width;
                    const height = canvas.getBoundingClientRect().height;

                    const padLeft = 58;
                    const padRight = 24;
                    const padTop = 26;
                    const padBottom = 42;
                    const plotW = width - padLeft - padRight;
                    const plotH = height - padTop - padBottom;

                    ctx.clearRect(0, 0, width, height);

                    const visualDepth = Math.min(h, Math.max(H * 3.5, 12));
                    const zMax = Math.max(H * 0.85, visualDepth * 0.25);
                    const zMin = -visualDepth * 1.08;
                    const zRange = zMax - zMin;

                    const toPxX = (x) => padLeft + (x / maxX) * plotW;
                    const toPxY = (z) => padTop + ((zMax - z) / zRange) * plotH;

                    const yZero = toPxY(0);
                    const yBed = toPxY(-visualDepth);

                    // Grade horizontal
                    ctx.strokeStyle = '#e2e8f0';
                    ctx.lineWidth = 1;
                    ctx.font = '11px sans-serif';
                    ctx.fillStyle = '#475569';
                    ctx.textAlign = 'right';

                    const ticks = [zMax * 0.7, 0, -visualDepth * 0.5, -visualDepth];
                    ticks.forEach((val, idx) => {{
                        const py = toPxY(val);
                        ctx.beginPath();
                        ctx.moveTo(padLeft, py);
                        ctx.lineTo(width - padRight, py);
                        ctx.stroke();

                        let labelVal = val;
                        if (idx === 3) labelVal = -h;
                        else if (idx === 2) labelVal = -h * 0.5;
                        ctx.fillText(labelVal.toFixed(1) + ' m', padLeft - 8, py + 4);
                    }});

                    // Grade vertical
                    ctx.textAlign = 'center';
                    for (let i = 0; i <= numWaves; i++) {{
                        const xVal = i * L;
                        const px = toPxX(xVal);
                        ctx.beginPath();
                        ctx.moveTo(px, padTop);
                        ctx.lineTo(px, height - padBottom);
                        ctx.stroke();
                        ctx.fillText(xVal.toFixed(0) + ' m', px, height - padBottom + 18);
                    }}

                    // Título dos eixos
                    ctx.fillStyle = '#1e293b';
                    ctx.font = 'bold 12px sans-serif';
                    ctx.fillText('Distância horizontal x (m)', padLeft + plotW / 2, height - 8);

                    ctx.save();
                    ctx.translate(15, padTop + plotH / 2);
                    ctx.rotate(-Math.PI / 2);
                    ctx.fillText('Elevação z (m)', 0, 0);
                    ctx.restore();

                    // Corpo da água com degradê oceânico
                    const waterGrad = ctx.createLinearGradient(0, yZero - (H/2)*(plotH/zRange), 0, yBed);
                    waterGrad.addColorStop(0, 'rgba(0, 207, 255, 0.65)');
                    waterGrad.addColorStop(0.5, 'rgba(0, 119, 255, 0.50)');
                    waterGrad.addColorStop(1, 'rgba(2, 62, 138, 0.75)');

                    ctx.beginPath();
                    const steps = 300;
                    for (let i = 0; i <= steps; i++) {{
                        const x = (i / steps) * maxX;
                        const eta = (H / 2) * Math.cos(k * x - omega * simTime);
                        const px = toPxX(x);
                        const py = toPxY(eta);
                        if (i === 0) ctx.moveTo(px, py);
                        else ctx.lineTo(px, py);
                    }}
                    ctx.lineTo(toPxX(maxX), yBed);
                    ctx.lineTo(toPxX(0), yBed);
                    ctx.closePath();
                    ctx.fillStyle = waterGrad;
                    ctx.fill();

                    // Nível Médio do Mar (z = 0)
                    ctx.save();
                    ctx.setLineDash([6, 5]);
                    ctx.strokeStyle = '#64748b';
                    ctx.lineWidth = 1.3;
                    ctx.beginPath();
                    ctx.moveTo(padLeft, yZero);
                    ctx.lineTo(width - padRight, yZero);
                    ctx.stroke();
                    ctx.restore();

                    // Superfície Livre η(x, t)
                    ctx.beginPath();
                    for (let i = 0; i <= steps; i++) {{
                        const x = (i / steps) * maxX;
                        const eta = (H / 2) * Math.cos(k * x - omega * simTime);
                        const px = toPxX(x);
                        const py = toPxY(eta);
                        if (i === 0) ctx.moveTo(px, py);
                        else ctx.lineTo(px, py);
                    }}
                    ctx.strokeStyle = '#0096c7';
                    ctx.lineWidth = 3;
                    ctx.stroke();

                    // Marcador que acompanha o mouse sobre a superfície
                    if (mouseX !== null && mouseX >= padLeft && mouseX <= width - padRight) {{
                        const xm = ((mouseX - padLeft) / plotW) * maxX;
                        const etaM = (H / 2) * Math.cos(k * xm - omega * simTime);
                        const pyM = toPxY(etaM);
                        ctx.save();
                        ctx.setLineDash([3, 4]);
                        ctx.strokeStyle = 'rgba(0, 150, 199, 0.55)';
                        ctx.lineWidth = 1;
                        ctx.beginPath();
                        ctx.moveTo(mouseX, padTop);
                        ctx.lineTo(mouseX, yBed);
                        ctx.stroke();
                        ctx.restore();
                        ctx.fillStyle = 'rgba(0, 180, 216, 0.25)';
                        ctx.beginPath();
                        ctx.arc(mouseX, pyM, 13, 0, 2 * Math.PI);
                        ctx.fill();
                        ctx.fillStyle = '#00b4d8';
                        ctx.strokeStyle = '#ffffff';
                        ctx.lineWidth = 2;
                        ctx.beginPath();
                        ctx.arc(mouseX, pyM, 6, 0, 2 * Math.PI);
                        ctx.fill();
                        ctx.stroke();
                        ctx.fillStyle = '#002855';
                        ctx.font = 'bold 12px sans-serif';
                        ctx.textAlign = 'left';
                        ctx.fillText('x = ' + xm.toFixed(1) + ' m | η = ' + etaM.toFixed(2) + ' m',
                                     Math.min(mouseX + 14, width - padRight - 150), pyM - 16);
                    }}

                    // Fundo Oceânico
                    ctx.fillStyle = '#7f4f24';
                    ctx.fillRect(padLeft, yBed, plotW, 8);
                    ctx.fillStyle = '#582f0e';
                    ctx.fillRect(padLeft, yBed + 8, plotW, 4);

                    // Desenha anéis de ondulação do clique
                    for (let i = splashes.length - 1; i >= 0; i--) {{
                        const s = splashes[i];
                        s.radius += 95 * dt;
                        s.alpha -= 1.35 * dt;
                        if (s.alpha <= 0) {{
                            splashes.splice(i, 1);
                            continue;
                        }}
                        ctx.save();
                        ctx.strokeStyle = `rgba(0, 180, 216, ${{s.alpha}})`;
                        ctx.lineWidth = 2.2;
                        ctx.beginPath();
                        ctx.ellipse(s.x, s.y, s.radius, s.radius * 0.35, 0, 0, 2 * Math.PI);
                        ctx.stroke();
                        ctx.restore();
                    }}

                    // Desenha gotículas d'água saltando no clique
                    for (let i = droplets.length - 1; i >= 0; i--) {{
                        const d = droplets[i];
                        d.x += d.vx * dt;
                        d.y += d.vy * dt;
                        d.vy += 420 * dt; // gravidade nas gotas
                        d.alpha -= 1.25 * dt;
                        if (d.alpha <= 0) {{
                            droplets.splice(i, 1);
                            continue;
                        }}
                        ctx.save();
                        ctx.fillStyle = `rgba(0, 119, 182, ${{d.alpha}})`;
                        ctx.beginPath();
                        ctx.arc(d.x, d.y, d.radius, 0, 2 * Math.PI);
                        ctx.fill();
                        ctx.restore();
                    }}

                    // Indicador de tempo decorrido
                    ctx.fillStyle = '#002855';
                    ctx.font = 'bold 12px monospace';
                    ctx.textAlign = 'right';
                    ctx.fillText('t = ' + simTime.toFixed(1) + ' s', width - padRight - 10, padTop + 16);

                    requestAnimationFrame(draw);
                }}

                requestAnimationFrame(draw);
            </script>
        </body>
        </html>
        """

        components.html(html_onda, height=425)

    # Rodapé institucional limpo
    st.markdown(f"""
        <div style="text-align: center; color: #64748b; font-size: 12px; margin-top: 24px; padding-top: 12px; border-top: 1px solid #e2e8f0;">
            <b>HIDRO-VIA — Laboratório Virtual de Hidrodinâmica</b> | {INSTITUICAO}
        </div>
    """, unsafe_allow_html=True)

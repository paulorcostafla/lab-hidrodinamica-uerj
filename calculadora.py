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

css_global = (
    '<style>'
    '[data-testid="stMetricValue"] { font-size: 1.32rem !important; color: #002855; font-weight: 700; }'
    '[data-testid="stMetricLabel"] { font-size: 0.84rem !important; color: #475569; }'
    'h3 { font-size: 1.15rem !important; color: #002855; }'
    '@keyframes waveMove1 { 0% { background-position-x: 0px; } 100% { background-position-x: 1000px; } }'
    '@keyframes waveMove2 { 0% { background-position-x: 1000px; } 100% { background-position-x: 0px; } }'
    '.header-banner { background: linear-gradient(135deg, #001845 0%, #002855 45%, #00509d 100%); '
    'padding: 24px 26px 32px 26px; border-radius: 12px; margin-bottom: 20px; '
    'border-left: 6px solid #00b4d8; box-shadow: 0 6px 18px rgba(0, 40, 85, 0.18); '
    'position: relative; overflow: hidden; }'
    '.header-badge { display: inline-block; background: rgba(0, 180, 216, 0.2); '
    'border: 1px solid rgba(144, 224, 239, 0.45); color: #90e0ef; font-size: 11px; '
    'font-weight: 600; padding: 3px 10px; border-radius: 20px; margin-bottom: 8px; '
    'letter-spacing: 0.5px; text-transform: uppercase; }'
    '.header-wave-back { position: absolute; bottom: 0; left: 0; width: 100%; height: 22px; '
    'background: url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' '
    'viewBox=\'0 0 1200 120\' preserveAspectRatio=\'none\'%3E%3Cpath d=\'M0,40 C300,110 900,0 1200,50 '
    'L1200,120 L0,120 Z\' fill=\'rgba(144, 224, 239, 0.14)\'/%3E%3C/svg%3E"); '
    'background-size: 550px 22px; animation: waveMove2 16s linear infinite; }'
    '.header-wave-front { position: absolute; bottom: 0; left: 0; width: 100%; height: 18px; '
    'background: url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' '
    'viewBox=\'0 0 1200 120\' preserveAspectRatio=\'none\'%3E%3Cpath d=\'M0,60 C350,120 850,0 1200,60 '
    'L1200,120 L0,120 Z\' fill=\'rgba(202, 240, 248, 0.22)\'/%3E%3C/svg%3E"); '
    'background-size: 480px 18px; animation: waveMove1 10s linear infinite; }'
    '.info-card { background: #f8fafc; border: 1px solid #cbd5e1; border-left: 5px solid #00509d; '
    'border-radius: 8px; padding: 16px 20px; margin-top: 10px; margin-bottom: 16px; }'
    '.welcome-box { background: linear-gradient(180deg, #f8fafc 0%, #eff6ff 100%); '
    'border: 1px solid #bfdbfe; border-radius: 10px; padding: 22px; margin-top: 14px; }'
    '.footer-uerj { text-align: center; color: #64748b; font-size: 12px; '
    'margin-top: 30px; padding: 14px; border-top: 1px solid #e2e8f0; }'
    '</style>'
)
st.markdown(css_global, unsafe_allow_html=True)

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

st.markdown("### Painel de Controle do Ensaio")
st.caption("Defina os parâmetros físicos da onda incidente e clique em **Calcular** para executar a simulação:")

box_controle = st.container(border=True)
p1, p2, p3, p4 = box_controle.columns(4)

T = p1.number_input(
    "Período da onda T (s):",
    min_value=1.0,
    max_value=30.0,
    value=10.0,
    step=0.5
)
h = p2.number_input(
    "Profundidade local h (m):",
    min_value=0.5,
    max_value=500.0,
    value=15.0,
    step=1.0
)
H = p3.number_input(
    "Altura da onda H (m):",
    min_value=0.1,
    max_value=30.0,
    value=2.0,
    step=0.1
)
rho = p4.selectbox(
    "Densidade do fluido ρ (kg/m³):",
    [1025.0, 1000.0],
    format_func=lambda x: f"{x} kg/m³ (Água do Mar)" if x == 1025.0 else f"{x} kg/m³ (Água Doce)"
)

box_controle.markdown("")
if box_controle.button("Calcular", type="primary", use_container_width=True):
    st.session_state["calculado"] = True
    st.session_state["T_val"] = T
    st.session_state["h_val"] = h
    st.session_state["H_val"] = H
    st.session_state["rho_val"] = rho


def resolver_onda(T_in, h_in, g=9.81):
    omega = 2 * np.pi / T_in
    k0 = omega**2 / g

    def f(k):
        return omega**2 - g * k * np.tanh(k * h_in)

    def fprime(k):
        th = np.tanh(k * h_in)
        return -g * th - g * k * h_in * (1 - th**2)

    k = newton(f, x0=k0, fprime=fprime)
    L = 2 * np.pi / k
    C = L / T_in
    n = 0.5 * (1 + (2 * k * h_in) / np.sinh(2 * k * h_in))
    Cg = n * C
    return k, L, C, Cg, h_in / L, omega, n


if not st.session_state["calculado"]:
    welcome_html = (
        '<div class="welcome-box">'
        '<h4 style="color: #002855; margin-top: 0;">'
        'Bem-vindo ao Módulo de Propagação de Ondas (Teoria Linear de Airy)'
        '</h4>'
        '<p style="color: #334155; font-size: 13.5px; line-height: 1.55;">'
        'Este ambiente virtual permite simular o comportamento hidrodinâmico de ondas '
        'gravitacionais de superfície em diferentes profundidades. '
        'Insira os dados no painel acima e clique em <b>Calcular</b> para obter:</p>'
        '<ul style="color: #334155; font-size: 13.5px; line-height: 1.6; margin-bottom: 0;">'
        '<li><b>Classificação do Regime de Profundidade:</b> Identificação automática entre '
        '<i>Águas Profundas</i>, <i>Intermediárias</i> ou <i>Rasas</i>.</li>'
        '<li><b>Propriedades Cinemáticas e Dinâmicas:</b> Comprimento de onda (L), '
        'celeridade (C), velocidade de grupo (Cg) e densidade de energia (E).</li>'
        '<li><b>Simulação Espacial e Orbital em Tempo Real:</b> Visualização animada da '
        'superfície livre η(x, t) e das trajetórias orbitais das partículas de água na coluna d\'água.</li>'
        '</ul></div>'
    )
    st.markdown(welcome_html, unsafe_allow_html=True)

if st.session_state["calculado"]:
    T_calc = st.session_state["T_val"]
    h_calc = st.session_state["h_val"]
    H_calc = st.session_state["H_val"]
    rho_calc = st.session_state["rho_val"]

    g = 9.81
    k, L, C, Cg, ratio, omega, n_factor = resolver_onda(T_calc, h_calc)
    E = (1 / 8) * rho_calc * g * (H_calc**2)
    P = E * Cg

    if ratio > 0.5:
        regime = "Águas Profundas (h/L > 0.5)"
        cor_badge = "#0077b6"
        descricao_regime = (
            "A onda não interage com o fundo oceânico (h > L/2). As partículas de água descrevem "
            "<b>órbitas circulares</b> que decaem exponencialmente com a profundidade. A velocidade de propagação "
            "depende exclusivamente do período T, e a velocidade de grupo equivale à metade da celeridade (Cg = 0,5·C)."
        )
    elif ratio < 0.05:
        regime = "Águas Rasas (h/L < 0.05)"
        cor_badge = "#d97706"
        descricao_regime = (
            "Forte interação com o fundo (h < L/20). As partículas descrevem <b>órbitas elípticas muito achatadas</b>, "
            "com movimento horizontal quase uniforme da superfície até o leito. A onda torna-se não-dispersiva: "
            "sua velocidade depende apenas da profundidade local (C ≈ √(g·h)) e Cg ≈ C."
        )
    else:
        regime = "Águas Intermediárias (0.05 ≤ h/L ≤ 0.5)"
        cor_badge = "#059669"
        descricao_regime = (
            "Zona de transição onde a onda começa a sentir o fundo. As partículas descrevem <b>órbitas elípticas</b> "
            "que se achatam progressivamente em direção ao leito. Tanto o comprimento de onda quanto a velocidade "
            "dependem simultaneamente do período T e da profundidade local h."
        )

    st.markdown("---")
    st.markdown(
        f"### Resultados da Simulação — Regime: <span style='color:{cor_badge};'>{regime}</span>",
        unsafe_allow_html=True
    )

    diag_html = (
        f'<div class="info-card" style="border-left-color: {cor_badge};">'
        f'<div style="font-size: 13px; color: #0f172a; font-weight: 600; margin-bottom: 4px;">'
        f'Diagnóstico Hidrodinâmico do Ensaio (k = {k:.4f} rad/m | ω = {omega:.4f} rad/s | n = {n_factor:.3f})'
        f'</div>'
        f'<div style="font-size: 13px; color: #334155; line-height: 1.5;">{descricao_regime}</div>'
        f'</div>'
    )
    st.markdown(diag_html, unsafe_allow_html=True)

    box_in = st.container(border=True)
    box_in.markdown("**1. Parâmetros Definidos no Ensaio**")
    in1, in2, in3, in4 = box_in.columns(4)
    in1.container(border=True).metric("Período (T)", f"{T_calc:.2f} s")
    in2.container(border=True).metric("Altura da Onda (H)", f"{H_calc:.2f} m")
    in3.container(border=True).metric("Profundidade (h)", f"{h_calc:.2f} m")
    in4.container(border=True).metric("Densidade (ρ)", f"{rho_calc:.0f} kg/m³")

    box_out = st.container(border=True)
    box_out.markdown("**2. Parâmetros Hidrodinâmicos Calculados**")
    out1, out2, out3, out4, out5 = box_out.columns(5)
    out1.container(border=True).metric("Comprimento (L)", f"{L:.2f} m")
    out2.container(border=True).metric("Vel. de Fase (C)", f"{C:.2f} m/s")
    out3.container(border=True).metric("Vel. de Grupo (Cg)", f"{Cg:.2f} m/s")
    out4.container(border=True).metric("Energia (E)", f"{E/1000:.2f} kJ/m²")
    out5.container(border=True).metric("Relação h/L", f"{ratio:.4f}")

    st.markdown("")

    box_graf = st.container(border=True)
    box_graf.markdown("### Simulação Espacial e Cinemática Orbital — η(x, t)")
    box_graf.caption(
        f"Propagação de 4 comprimentos de onda (0 a {4*L:.1f} m) | "
        f"Fluxo de potência da onda: {P/1000:.2f} kW/m | Declividade (H/L): {H_calc/L:.4f}"
    )

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
        }}
        .btn {{
            background-color: #00509d;
            color: white;
            border: none;
            padding: 6px 13px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12.5px;
            font-weight: 500;
        }}
        .btn:hover {{
            background-color: #003566;
        }}
        .btn-secondary {{
            background-color: #0284c7;
        }}
        .btn-secondary:hover {{
            background-color: #0369a1;
        }}
        .legend {{
            display: flex;
            gap: 14px;
            font-size: 12px;
            color: #334155;
            flex-wrap: wrap;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        .box-wave {{ width: 15px; height: 4px; background: #00509d; border-radius: 2px; }}
        .box-mean {{ width: 15px; height: 0; border-top: 2px dashed #64748b; }}
        .box-bed  {{ width: 15px; height: 5px; background: #7f4f24; border-radius: 2px; }}
        .box-orb  {{ width: 10px; height: 10px; border-radius: 50%; background: #ef4444; border: 1.5px solid white; }}
        canvas {{
            width: 100%;
            height: 390px;
            border-radius: 8px;
            border: 1px solid #cbd5e1;
            background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
            display: block;
        }}
    </style>
    </head>
    <body>
        <div class="controls">
            <div class="btn-group">
                <button class="btn" id="toggleBtn" onclick="toggleAnim()">Pausar Onda</button>
                <button class="btn btn-secondary" id="orbitBtn" onclick="toggleOrbits()">Ocultar Órbitas</button>
            </div>
            <div class="legend">
                <div class="legend-item"><span class="box-wave"></span> Superfície η(x, t)</div>
                <div class="legend-item"><span class="box-orb"></span> Órbitas das Partículas</div>
                <div class="legend-item"><span class="box-mean"></span> Nível Médio (z = 0)</div>
                <div class="legend-item"><span class="box-bed"></span> Fundo (z = -{h_calc:.1f} m)</div>
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
            let showOrbits = true;
            let lastTime = performance.now();
            let simTime = 0;

            function toggleAnim() {{
                running = !running;
                document.getElementById('toggleBtn').innerText = running ? 'Pausar Onda' : 'Continuar Onda';
                if (running) {{
                    lastTime = performance.now();
                    requestAnimationFrame(draw);
                }}
            }}

            function toggleOrbits() {{
                showOrbits = !showOrbits;
                document.getElementById('orbitBtn').innerText = showOrbits ? 'Ocultar Órbitas' : 'Mostrar Órbitas';
                if (!running) drawSingleFrame();
            }}

            function resizeCanvas() {{
                const rect = canvas.getBoundingClientRect();
                const dpr = window.devicePixelRatio || 1;
                canvas.width = rect.width * dpr;
                canvas.height = rect.height * dpr;
                ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
            }}

            window.addEventListener('resize', () => {{
                resizeCanvas();
                if (!running) drawSingleFrame();
            }});
            resizeCanvas();

            function drawSingleFrame() {{
                const width = canvas.getBoundingClientRect().width;
                const height = canvas.getBoundingClientRect().height;

                const padLeft = 58;
                const padRight = 24;
                const padTop = 28;
                const padBottom = 42;
                const plotW = width - padLeft - padRight;
                const plotH = height - padTop - padBottom;

                ctx.clearRect(0, 0, width, height);

                const visualDepth = Math.min(h, Math.max(H * 3.8, 12));
                const zMax = Math.max(H * 0.9, visualDepth * 0.25);
                const zMin = -visualDepth * 1.08;
                const zRange = zMax - zMin;

                const toPxX = (x) => padLeft + (x / maxX) * plotW;
                const toPxY = (z) => padTop + ((zMax - z) / zRange) * plotH;

                const yZero = toPxY(0);
                const yBed = toPxY(-visualDepth);

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

                ctx.fillStyle = '#1e293b';
                ctx.font = 'bold 12px sans-serif';
                ctx.fillText('Distância horizontal x (m)', padLeft + plotW / 2, height - 8);

                ctx.save();
                ctx.translate(15, padTop + plotH / 2);
                ctx.rotate(-Math.PI / 2);
                ctx.fillText('Elevação z (m)', 0, 0);
                ctx.restore();

                const waterGrad = ctx.createLinearGradient(0, yZero - (H/2)*(plotH/zRange), 0, yBed);
                waterGrad.addColorStop(0, 'rgba(0, 180, 216, 0.50)');
                waterGrad.addColorStop(0.55, 'rgba(0, 119, 182, 0.42)');
                waterGrad.addColorStop(1, 'rgba(2, 62, 138, 0.62)');

                ctx.beginPath();
                const steps = 320;
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

                ctx.save();
                ctx.setLineDash([6, 5]);
                ctx.strokeStyle = '#64748b';
                ctx.lineWidth = 1.2;
                ctx.beginPath();
                ctx.moveTo(padLeft, yZero);
                ctx.lineTo(width - padRight, yZero);
                ctx.stroke();
                ctx.restore();

                if (showOrbits) {{
                    const xPositions = [0.75 * L, 1.75 * L, 2.75 * L, 3.5 * L];
                    const depthFractions = [0.15, 0.50, 0.85];
                    const kh = Math.min(k * h, 10);
                    const sinhKh = Math.sinh(kh);

                    xPositions.forEach((x0) => {{
                        depthFractions.forEach((frac) => {{
                            const zVis = -frac * visualDepth;
                            const kzPlusKh = Math.max(0, kh * (1 - frac));

                            const A_real = (H / 2) * (Math.cosh(kzPlusKh) / sinhKh);
                            const B_real = (H / 2) * (Math.sinh(kzPlusKh) / sinhKh);

                            const scaleY = plotH / zRange;
                            const rx = Math.min(28, Math.max(4, A_real * scaleY));
                            const ry = Math.min(28, Math.max(1.5, B_real * scaleY));

                            const cx = toPxX(x0);
                            const cy = toPxY(zVis);

                            ctx.save();
                            ctx.setLineDash([2, 2]);
                            ctx.strokeStyle = 'rgba(255, 255, 255, 0.8)';
                            ctx.lineWidth = 1.1;
                            ctx.beginPath();
                            ctx.ellipse(cx, cy, rx, ry, 0, 0, 2 * Math.PI);
                            ctx.stroke();
                            ctx.restore();

                            const phase = k * x0 - omega * simTime;
                            const pxPart = cx - rx * Math.sin(phase);
                            const pyPart = cy - ry * Math.cos(phase);

                            ctx.beginPath();
                            ctx.arc(pxPart, pyPart, 3.6, 0, 2 * Math.PI);
                            ctx.fillStyle = '#ef4444';
                            ctx.fill();
                            ctx.strokeStyle = 'white';
                            ctx.lineWidth = 1.2;
                            ctx.stroke();
                        }});
                    }});
                }}

                ctx.beginPath();
                for (let i = 0; i <= steps; i++) {{
                    const x = (i / steps) * maxX;
                    const eta = (H / 2) * Math.cos(k * x - omega * simTime);
                    const px = toPxX(x);
                    const py = toPxY(eta);
                    if (i === 0) ctx.moveTo(px, py);
                    else ctx.lineTo(px, py);
                }}
                ctx.strokeStyle = '#00509d';
                ctx.lineWidth = 3;
                ctx.stroke();

                ctx.fillStyle = '#7f4f24';
                ctx.fillRect(padLeft, yBed, plotW, 8);
                ctx.fillStyle = '#582f0e';
                ctx.fillRect(padLeft, yBed + 8, plotW, 4);

                ctx.fillStyle = '#002855';
                ctx.font = 'bold 12px monospace';
                ctx.textAlign = 'right';
                ctx.fillText('t = ' + simTime.toFixed(1) + ' s', width - padRight - 10, padTop + 16);
            }}

            function draw(now) {{
                if (!running) return;
                const dt = (now - lastTime) / 1000;
                lastTime = now;
                simTime += dt;
                drawSingleFrame();
                requestAnimationFrame(draw);
            }}

            requestAnimationFrame(draw);
        </script>
    </body>
    </html>
    """

    with box_graf:
        components.html(html_onda, height=445)

    st.markdown("")

    box_teoria = st.container(border=True)
    box_teoria.markdown("### Fundamentação Teórica — Teoria Linear de Airy")
    tab1, tab2 = box_teoria.tabs(["Equações Governantes", "Classificação dos Regimes de Profundidade"])

    eq1, eq2 = tab1.columns(2)
    eq1.markdown("**1. Relação de Dispersão:**")
    eq1.latex(r"\omega^2 = g \cdot k \cdot \tanh(k \cdot h)")
    eq1.markdown("**2. Comprimento de Onda (L) e Celeridade (C):**")
    eq1.latex(r"L = \frac{2\pi}{k} \qquad ; \qquad C = \frac{L}{T} = \frac{\omega}{k}")

    eq2.markdown("**3. Velocidade de Grupo (Cg):**")
    eq2.latex(r"C_g = n \cdot C \quad \text{onde} \quad n = \frac{1}{2}\left[1 + \frac{2kh}{\sinh(2kh)}\right]")
    eq2.markdown("**4. Densidade de Energia Total (E):**")
    eq2.latex(r"E = E_p + E_c = \frac{1}{8} \rho g H^2")

    tabela_md = (
        "| Regime de Profundidade | Critério Adimensional ($h/L$) | Aproximação de $\\tanh(kh)$ | Velocidade de Fase ($C$) | Trajetória das Partículas |\n"
        "| :--- | :---: | :---: | :---: | :--- |\n"
        "| **Águas Profundas** | $h/L > 0,5$ | $\\tanh(kh) \\approx 1$ | $C_0 = \\frac{gT}{2\\pi}$ | Órbitas circulares |\n"
        "| **Águas Intermediárias** | $0,05 \\le h/L \\le 0,5$ | Solução completa | $C = \\frac{gT}{2\\pi}\\tanh(kh)$ | Órbitas elípticas |\n"
        "| **Águas Rasas** | $h/L < 0,05$ | $\\tanh(kh) \\approx kh$ | $C \\approx \\sqrt{gh}$ | Elipses muito achatadas |"
    )
    tab2.markdown(tabela_md)

footer_html = f'<div class="footer-uerj"><b>HIDRO-VIA — Laboratório Virtual de Hidrodinâmica</b> | {INSTITUICAO}</div>'
st.markdown(footer_html, unsafe_allow_html=True)

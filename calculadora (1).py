import streamlit as st
import streamlit.components.v1 as components
import numpy as np
from scipy.optimize import newton

# ==============================================================================
# IDENTIDADE DO PROJETO
# ==============================================================================
NOME_DO_PROJETO = "HIDRO-VIA (Laboratório Virtual de Hidrodinâmica) UERJ-ZO"
SUBTITULO = "Teoria Linear de Airy — Propagação de Ondas"
INSTITUICAO = "Universidade do Estado do Rio de Janeiro (Campus Zona Oeste)"
# ==============================================================================

st.set_page_config(
    page_title="HIDRO-VIA | UERJ-ZO",
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
    '.footer-uerj { text-align: center; color: #64748b; font-size: 12px; '
    'margin-top: 30px; padding: 14px; border-top: 1px solid #e2e8f0; }'
    '</style>'
)
st.markdown(css_global, unsafe_allow_html=True)

header_html = (
    f'<div class="header-banner">'
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

st.markdown("### Parâmetros de Entrada")

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
    "Densidade ρ (kg/m³):",
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
    return k, L, C, Cg, h_in / L


if st.session_state["calculado"]:
    T_calc = st.session_state["T_val"]
    h_calc = st.session_state["h_val"]
    H_calc = st.session_state["H_val"]
    rho_calc = st.session_state["rho_val"]

    g = 9.81
    k, L, C, Cg, ratio = resolver_onda(T_calc, h_calc)
    E = (1 / 8) * rho_calc * g * (H_calc**2)

    if ratio > 0.5:
        regime = "Águas Profundas"
        cor_badge = "#0077b6"
    elif ratio < 0.05:
        regime = "Águas Rasas"
        cor_badge = "#d97706"
    else:
        regime = "Águas Intermediárias"
        cor_badge = "#059669"

    st.markdown("---")
    st.markdown(
        f"### Resultados — Regime: <span style='color:{cor_badge};'>{regime}</span>",
        unsafe_allow_html=True
    )

    box_out = st.container(border=True)
    out1, out2, out3, out4, out5 = box_out.columns(5)
    out1.container(border=True).metric("Comprimento (L)", f"{L:.2f} m")
    out2.container(border=True).metric("Vel. de Fase (C)", f"{C:.2f} m/s")
    out3.container(border=True).metric("Vel. de Grupo (Cg)", f"{Cg:.2f} m/s")
    out4.container(border=True).metric("Energia (E)", f"{E/1000:.2f} kJ/m²")
    out5.container(border=True).metric("Relação h/L", f"{ratio:.4f}")

    st.markdown("")

    box_graf = st.container(border=True)
    box_graf.markdown("### Perfil da Onda — η(x, t)")

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
            <button class="btn" id="toggleBtn" onclick="toggleAnim()">Pausar Onda</button>
            <div class="legend">
                <div class="legend-item"><span class="box-wave"></span> Superfície η(x, t)</div>
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

footer_html = f'<div class="footer-uerj"><b>HIDRO-VIA — Laboratório Virtual de Hidrodinâmica</b> | {INSTITUICAO}</div>'
st.markdown(footer_html, unsafe_allow_html=True)

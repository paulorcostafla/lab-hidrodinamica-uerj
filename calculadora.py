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

# Configuração da página (aba do navegador)
st.set_page_config(
    page_title="HIDRO-VIA | Laboratório Virtual de Hidrodinâmica UERJ-ZO",
    layout="wide"
)

# Estilo global (fontes, cartões, banners e ondas animadas)
st.markdown("""
    <style>
        [data-testid="stMetricValue"] {
            font-size: 1.32rem !important;
            color: #002855;
            font-weight: 700;
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.84rem !important;
            color: #475569;
        }
        h3 {
            font-size: 1.15rem !important;
            color: #002855;
        }
        @keyframes waveMove1 {
            0% { background-position-x: 0px; }
            100% { background-position-x: 1000px; }
        }
        @keyframes waveMove2 {
            0% { background-position-x: 1000px; }
            100% { background-position-x: 0px; }
        }
        .header-banner {
            background: linear-gradient(135deg, #001845 0%, #002855 45%, #00509d 100%);
            padding: 24px 26px 32px 26px;
            border-radius: 12px;
            margin-bottom: 20px;
            border-left: 6px solid #00b4d8;
            box-shadow: 0 6px 18px rgba(0, 40, 85, 0.18);
            position: relative;
            overflow: hidden;
        }
        .header-badge {
            display: inline-block;
            background: rgba(0, 180, 216, 0.2);
            border: 1px solid rgba(144, 224, 239, 0.45);
            color: #90e0ef;
            font-size: 11px;
            font-weight: 600;
            padding: 3px 10px;
            border-radius: 20px;
            margin-bottom: 8px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }
        .header-wave-back {
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 22px;
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 120' preserveAspectRatio='none'%3E%3Cpath d='M0,40 C300,110 900,0 1200,50 L1200,120 L0,120 Z' fill='rgba(144, 224, 239, 0.14)'/%3E%3C/svg%3E");
            background-size: 550px 22px;
            animation: waveMove2 16s linear infinite;
        }
        .header-wave-front {
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 18px;
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 120' preserveAspectRatio='none'%3E%3Cpath d='M0,60 C350,120 850,0 1200,60 L1200,120 L0,120 Z' fill='rgba(202, 240, 248, 0.22)'/%3E%3C/svg%3E");
            background-size: 480px 18px;
            animation: waveMove1 10s linear infinite;
        }
        .info-card {
            background: #f8fafc;
            border: 1px solid #cbd5e1;
            border-left: 5px solid #00509d;
            border-radius: 8px;
            padding: 16px 20px;

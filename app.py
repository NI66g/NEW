"""
電腦周邊 (鍵盤·滑鼠·耳機) 智慧退換貨與爭議風控小幫手
Smart Computer Peripheral Return & Dispute Risk Copilot
專為資管系畢業專題設計之原型系統 (MVP)
技術棧：Python + Streamlit + SQLite + Plotly
"""

import streamlit as st
import sqlite3
import pandas as pd
import json
import base64
import os
from datetime import datetime
from PIL import Image
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    import plotly.express as px
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# ==========================================
# 0. 網頁基本配置與電競科技風視覺樣式 (CSS)
# ==========================================
st.set_page_config(
    page_title="電腦周邊售後風控平台 · 買家門戶與後台系統",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化主題設定 (預設為深色，使用者可隨時由側邊欄切換為淺色)
if "app_theme_choice" not in st.session_state:
    st.session_state["app_theme_choice"] = "🌙 深色"

is_dark = ("深色" in st.session_state.get("app_theme_choice", "🌙 深色"))

# ==========================================
# 科技感電競深色主題 CSS (Dark Mode)
# ==========================================
DARK_CSS = """
<style>
    /* 徹底隱藏 Streamlit 預設頁首、頁尾與浮水印橫條 */
    #MainMenu {visibility: hidden !important; display: none !important;}
    #stDecoration, [data-testid="stDecoration"] {display: none !important; visibility: hidden !important; height: 0 !important; width: 0 !important; margin: 0 !important; padding: 0 !important;}
    [data-testid="stHeader"] {display: none !important; visibility: hidden !important; height: 0 !important;}

    footer {visibility: hidden !important; display: none !important;}
    header {visibility: hidden !important; display: none !important;}
    [data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    .viewerBadge_container__r5tak, .viewerBadge_link__1SuqQ {display: none !important;}

    /* 全域科技感微光漸層背景與微網格 */
    .stApp {
        background: 
            radial-gradient(circle at 12% 15%, rgba(56, 189, 248, 0.12) 0%, transparent 45%),
            radial-gradient(circle at 88% 18%, rgba(168, 85, 247, 0.14) 0%, transparent 45%),
            radial-gradient(circle at 50% 88%, rgba(34, 197, 94, 0.08) 0%, transparent 50%),
            linear-gradient(135deg, #090d16 0%, #0f172a 45%, #0a0f1d 100%) !important;
        background-attachment: fixed !important;
        color: #f1f5f9 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans TC", sans-serif !important;
    }

    /* 背景精緻科技微網格 */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background-image: 
            linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
        background-size: 38px 38px;
        pointer-events: none;
        z-index: 0;
    }

    /* 標題與一般文字色彩通盤加亮，杜絕暗字融入背景 */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    p, span, label, li {
        color: #f1f5f9;
    }

    /* 輸入框與文字區 placeholder 改為清晰明亮的淺銀白 */
    ::placeholder, ::-webkit-input-placeholder, ::-moz-placeholder, :-ms-input-placeholder,
    input::placeholder, textarea::placeholder {
        color: rgba(226, 232, 240, 0.72) !important;
        opacity: 1 !important;
    }

    /* 表單標籤純白字體 */
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label,
    label[data-testid="stWidgetLabel"],
    .stTextInput label,
    .stTextArea label,
    .stSelectbox label,
    .stFileUploader label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 14.5px !important;
        letter-spacing: 0.2px;
    }

    /* 提示小字 (st.caption) 冰藍亮白 */
    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p,
    .stCaption,
    .stCaption p {
        color: #93c5fd !important;
        font-size: 13.5px !important;
        line-height: 1.5 !important;
    }

    /* ========================================================
       重點修復一：輸入框/文字區外框與密碼眼睛按鈕徹底深色高對比化
       (徹底消除右側白塊，眼睛圖示亮白高清晰)
       ======================================================== */
    /* 輸入框與文字區整體外框容器：深黑科技背景、微邊框、圓角防溢出 */
    div[data-testid="stTextInputRootElement"],
    div[data-testid="stTextAreaRootElement"],
    div[data-testid="stTextInput"] > div > div,
    div[data-testid="stTextArea"] > div > div,
    [data-baseweb="input"],
    [data-baseweb="textarea"],
    [data-baseweb="base-input"] {
        background-color: #1e293b !important;
        background: #1e293b !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        border-radius: 8px !important;
        overflow: hidden !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stTextInputRootElement"]:focus-within,
    div[data-testid="stTextAreaRootElement"]:focus-within {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 14px rgba(56, 189, 248, 0.4) !important;
    }

    /* 內層輸入文字區域：透明背景、純白文字，杜絕與外框分離造成右側露白 */
    .stTextInput input,
    .stTextArea textarea,
    [data-testid="stTextInput"] input,
    [data-testid="stTextInputField"],
    div[data-testid="stTextInputRootElement"] input,
    .stTextArea textarea,
    [data-testid="stTextArea"] textarea,
    div[data-testid="stTextAreaRootElement"] textarea,
    [data-baseweb="input"] input,
    [data-baseweb="base-input"] input,
    [data-baseweb="textarea"] textarea {
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        outline: none !important;
        box-shadow: none !important;
        color: #ffffff !important;
        font-size: 14.5px !important;
    }

    /* 密碼框右側「顯示/隱藏密碼」按鈕：背景全透明，無任何白底方塊 */
    div[data-testid="stTextInputRootElement"] > div,
    div[data-testid="stTextInputRootElement"] button,
    div[data-testid="stTextInput"] button,
    div[data-testid="stTextInput"] [data-baseweb="input"] button,
    [data-baseweb="input"] button,
    button[aria-label*="password" i],
    button[aria-label*="Password" i] {
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
        cursor: pointer !important;
        color: #ffffff !important;
    }
    div[data-testid="stTextInputRootElement"] button:hover,
    div[data-testid="stTextInput"] button:hover,
    button[aria-label*="password" i]:hover,
    button[aria-label*="Password" i]:hover {
        background-color: rgba(255, 255, 255, 0.12) !important;
    }

    /* 密碼框眼睛圖示本體（支援 SVG、Span、Material Symbols 等）：強制純白高清晰 */
    div[data-testid="stTextInputRootElement"] button *,
    div[data-testid="stTextInput"] button *,
    button[aria-label*="password" i] *,
    button[aria-label*="Password" i] * {
        color: #ffffff !important;
        fill: #ffffff !important;
        stroke: #ffffff !important;
        opacity: 0.95 !important;
    }
    div[data-testid="stTextInputRootElement"] button:hover *,
    div[data-testid="stTextInput"] button:hover *,
    button[aria-label*="password" i]:hover *,
    button[aria-label*="Password" i]:hover * {
        color: #38bdf8 !important;
        fill: #38bdf8 !important;
        stroke: #38bdf8 !important;
        opacity: 1 !important;
    }

    /* ========================================================
       重點修復二：下拉選單選項目文字強制純白 (解決使用者截圖問題)
       ======================================================== */
    div[data-baseweb="select"],
    div[data-baseweb="select"] > div,
    [data-testid="stSelectbox"] > div > div {
        background-color: #1e293b !important;
        background: #1e293b !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        border-radius: 8px !important;
        color: #ffffff !important;
    }
    div[data-baseweb="select"] *,
    [data-testid="stSelectbox"] * {
        color: #ffffff !important;
    }
    div[data-baseweb="select"] svg {
        fill: #38bdf8 !important;
    }

    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    div[data-baseweb="popover"] ul,
    div[data-baseweb="menu"],
    div[data-baseweb="menu"] > div,
    ul[role="listbox"],
    div[role="listbox"],
    [data-testid="stSelectboxVirtualDropdown"] {
        background-color: #0f172a !important;
        background: #0f172a !important;
        border: 1px solid rgba(56, 189, 248, 0.5) !important;
        border-radius: 10px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.9) !important;
    }
    div[data-baseweb="popover"] *,
    div[data-baseweb="menu"] *,
    ul[role="listbox"] *,
    div[role="listbox"] *,
    [role="listbox"] [role="option"],
    [role="listbox"] [role="option"] *,
    [role="option"],
    [role="option"] *,
    li[role="option"],
    li[role="option"] *,
    div[role="option"],
    div[role="option"] *,
    [data-testid="stSelectboxVirtualDropdown"] * {
        color: #ffffff !important;
        background-color: transparent !important;
        background: transparent !important;
    }
    [role="option"]:hover,
    [role="option"]:hover *,
    li[role="option"]:hover,
    li[role="option"]:hover *,
    div[role="option"]:hover,
    div[role="option"]:hover * {
        background-color: #1e293b !important;
        background: #1e293b !important;
        color: #38bdf8 !important;
    }
    [role="option"][aria-selected="true"],
    [role="option"][aria-selected="true"] *,
    li[role="option"][aria-selected="true"],
    li[role="option"][aria-selected="true"] *,
    div[role="option"][aria-selected="true"],
    div[role="option"][aria-selected="true"] * {
        background-color: #2563eb !important;
        background: #2563eb !important;
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* 提示框純白文字與科技深色底色 */
    [data-testid="stAlert"],
    [data-testid="stAlert"] *,
    [data-testid="stNotification"],
    [data-testid="stNotification"] *,
    .stAlert,
    .stAlert * {
        color: #ffffff !important;
    }
    [data-testid="stAlert"] strong {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    [data-testid="stAlert"] {
        border-radius: 12px !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3) !important;
    }
    [data-testid="stAlert"]:has([data-testid="stAlertContentInfo"]),
    div[data-baseweb="notification"][kind="info"] {
        background: rgba(30, 58, 138, 0.5) !important;
        border: 1px solid rgba(96, 165, 250, 0.6) !important;
    }
    [data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]),
    div[data-baseweb="notification"][kind="success"] {
        background: rgba(20, 83, 45, 0.5) !important;
        border: 1px solid rgba(74, 222, 128, 0.6) !important;
    }
    [data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]),
    div[data-baseweb="notification"][kind="warning"] {
        background: rgba(120, 53, 15, 0.5) !important;
        border: 1px solid rgba(251, 191, 36, 0.6) !important;
    }
    [data-testid="stAlert"]:has([data-testid="stAlertContentError"]),
    div[data-baseweb="notification"][kind="error"] {
        background: rgba(127, 29, 29, 0.5) !important;
        border: 1px solid rgba(248, 113, 113, 0.6) !important;
    }

    /* 側邊欄樣式 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #080c14 0%, #0f172a 100%) !important;
        border-right: 1px solid rgba(99, 102, 241, 0.25) !important;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.5) !important;
    }
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [role="radiogroup"] * {
        color: #f1f5f9 !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }
    .sidebar-header-box {
        padding: 6px 0 14px 0; 
        border-bottom: 1px solid rgba(255,255,255,0.08); 
        margin-bottom: 14px;
    }
    .sidebar-title {
        font-size: 20px; 
        font-weight: 800; 
        color: #f8fafc; 
        letter-spacing: -0.5px;
    }
    .sidebar-subtitle {
        font-size: 12px; 
        color: #38bdf8; 
        margin-top: 4px;
    }
    .sidebar-subtitle-admin {
        font-size: 12px; 
        color: #22c55e; 
        margin-top: 4px; 
        font-weight: 600;
    }

    /* 頂部主視覺科技橫幅卡片 */
    .tech-hero {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.75) 0%, rgba(15, 23, 42, 0.85) 100%);
        border: 1px solid rgba(99, 102, 241, 0.35);
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 10px 32px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(12px);
        position: relative;
        overflow: hidden;
    }
    .tech-hero::after {
        content: '';
        position: absolute;
        top: -50%; right: -20%; width: 300px; height: 300px;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.22) 0%, transparent 70%);
        pointer-events: none;
    }
    .hero-title {
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 26px;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 6px;
    }
    .hero-subtitle {
        color: #cbd5e1;
        font-size: 14px;
        line-height: 1.6;
    }
    .badge-item {
        display: inline-flex;
        align-items: center;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
        background: rgba(99, 102, 241, 0.16);
        border: 1px solid rgba(129, 140, 248, 0.35);
        color: #c7d2fe !important;
    }

    /* 指標數據卡 (stMetric) 玻璃擬態 */
    [data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 14px !important;
        padding: 16px 20px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25) !important;
        backdrop-filter: blur(10px) !important;
        transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease !important;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-3px) !important;
        border-color: rgba(99, 102, 241, 0.5) !important;
        box-shadow: 0 10px 28px rgba(99, 102, 241, 0.25) !important;
    }
    [data-testid="stMetricLabel"] p {
        color: #cbd5e1 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    [data-testid="stMetricValue"] div {
        color: #38bdf8 !important;
        font-weight: 800 !important;
    }

    /* 摺疊審核清單 (stExpander) 徹底杜絕反白變白條 */
    [data-testid="stExpander"],
    [data-testid="stExpander"] details {
        background-color: rgba(15, 23, 42, 0.85) !important;
        background: rgba(15, 23, 42, 0.85) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25) !important;
        margin-bottom: 14px !important;
        overflow: hidden !important;
    }
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] details summary,
    .streamlit-expanderHeader {
        background-color: #1e293b !important;
        background: #1e293b !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    [data-testid="stExpander"] summary:hover,
    [data-testid="stExpander"] details summary:hover,
    .streamlit-expanderHeader:hover {
        background-color: #334155 !important;
        background: #334155 !important;
        color: #38bdf8 !important;
    }
    [data-testid="stExpander"] summary *,
    [data-testid="stExpander"] details summary *,
    .streamlit-expanderHeader *,
    [data-testid="stExpander"] p,
    [data-testid="stExpander"] span,
    [data-testid="stExpander"] div {
        color: #f1f5f9 !important;
    }
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        background-color: rgba(15, 23, 42, 0.95) !important;
        background: rgba(15, 23, 42, 0.95) !important;
        color: #f1f5f9 !important;
    }

    /* 檔案上傳器拖曳區文字與按鈕亮色，全面杜絕白底 */
    [data-testid="stFileUploader"],
    [data-testid="stFileUploader"] section,
    [data-testid="stFileUploaderDropzone"],
    div[data-testid="stFileUploaderDropzone"],
    [data-baseweb="file-uploader"],
    [data-testid="stFileUploader"] section > div {
        background-color: #1e293b !important;
        background: #1e293b !important;
        border: 1px dashed rgba(56, 189, 248, 0.4) !important;
        border-radius: 12px !important;
    }
    [data-testid="stFileUploader"] section *,
    [data-testid="stFileUploaderDropzone"] * {
        color: #cbd5e1 !important;
    }
    [data-testid="stFileUploader"] button,
    [data-testid="stFileUploaderDropzone"] button {
        background-color: #334155 !important;
        background: #334155 !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
    }

    /* 按鈕樣式 */
    .stButton > button,
    div[data-testid="stButton"] > button,
    button[data-testid="baseButton-secondary"],
    button[kind="secondary"] {
        background-color: #1e293b !important;
        background: #1e293b !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        border: 1px solid rgba(255, 255, 255, 0.22) !important;
        color: #ffffff !important;
    }
    .stButton > button:hover,
    div[data-testid="stButton"] > button:hover,
    button[data-testid="baseButton-secondary"]:hover,
    button[kind="secondary"]:hover {
        background-color: #334155 !important;
        background: #334155 !important;
        border-color: #38bdf8 !important;
        color: #38bdf8 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 14px rgba(56, 189, 248, 0.25) !important;
    }
    .stButton > button[kind="primary"],
    button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #2563eb 0%, #6366f1 100%) !important;
        background-color: #2563eb !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4) !important;
        color: #ffffff !important;
    }
    .stButton > button[kind="primary"]:hover,
    button[data-testid="baseButton-primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6) !important;
    }

    /* 浮動工具列、資料表格與圖表外框深色化 */
    [data-testid="stElementToolbar"],
    div[data-testid="stElementToolbar"],
    .stElementToolbar {
        background-color: #0f172a !important;
        background: #0f172a !important;
        border: 1px solid rgba(56, 189, 248, 0.45) !important;
        border-radius: 9999px !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.75) !important;
        color: #f1f5f9 !important;
    }
    [data-testid="stElementToolbar"] button,
    div[data-testid="stElementToolbar"] button,
    [data-testid="stElementToolbarButton"],
    button[data-testid="stElementToolbarButton"] {
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        color: #f1f5f9 !important;
        border-radius: 9999px !important;
    }
    [data-testid="stElementToolbar"] button:hover,
    div[data-testid="stElementToolbar"] button:hover {
        background-color: #1e293b !important;
        color: #38bdf8 !important;
    }
    [data-testid="stElementToolbar"] svg,
    div[data-testid="stElementToolbar"] svg {
        fill: #f1f5f9 !important;
        stroke: #f1f5f9 !important;
        color: #f1f5f9 !important;
    }

    /* 資料表格 (stDataFrame) 全面深色高對比 */
    [data-testid="stDataFrame"],
    div[data-testid="stDataFrame"],
    .stDataFrame {
        background-color: rgba(15, 23, 42, 0.85) !important;
        background: rgba(15, 23, 42, 0.85) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35) !important;
        overflow: hidden !important;
    }

    /* 圖表容器深色卡片包裝 */
    [data-testid="stVegaLiteChart"],
    div[data-testid="stVegaLiteChart"],
    [data-testid="stPlotlyChart"],
    div[data-testid="stPlotlyChart"] {
        background-color: rgba(15, 23, 42, 0.8) !important;
        background: rgba(15, 23, 42, 0.8) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        padding: 8px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35) !important;
    }

    /* 風險燈號專用標籤樣式 */
    .pill-red {
        background: rgba(239, 68, 68, 0.22);
        color: #fca5a5 !important;
        border: 1px solid rgba(239, 68, 68, 0.5);
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 13px;
        display: inline-block;
    }
    .pill-yellow {
        background: rgba(234, 179, 8, 0.22);
        color: #fde047 !important;
        border: 1px solid rgba(234, 179, 8, 0.5);
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 13px;
        display: inline-block;
    }
    .pill-green {
        background: rgba(34, 197, 94, 0.22);
        color: #86efac !important;
        border: 1px solid rgba(34, 197, 94, 0.5);
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 13px;
        display: inline-block;
    }

    /* 內嵌代碼標籤 (Inline Code) 科技亮青色高對比 */
    code {
        color: #38bdf8 !important;
        background: rgba(15, 23, 42, 0.75) !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    /* 對話彈出視窗 (Modal Dialog) 深色高質感 */
    div[role="dialog"],
    div[role="dialog"] > div,
    div[data-baseweb="modal"],
    div[data-baseweb="modal"] > div,
    div[data-baseweb="modal"] [role="dialog"],
    div[data-baseweb="modal"] [role="dialog"] > div,
    [data-testid="stDialog"],
    [data-testid="stDialog"] > div,
    [data-testid="stModal"],
    [data-testid="stModal"] > div {
        background-color: #0b1120 !important;
        background: #0b1120 !important;
        color: #f8fafc !important;
    }
    div[role="dialog"] {
        border: 1px solid rgba(56, 189, 248, 0.5) !important;
        border-radius: 16px !important;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.9) !important;
    }
    div[role="dialog"] *,
    [data-testid="stDialog"] * {
        color: #f8fafc !important;
    }
    div[role="dialog"] .stCheckbox label span {
        color: #f1f5f9 !important;
        font-weight: 500 !important;
    }
    div[role="dialog"] textarea,
    div[role="dialog"] input {
        background-color: #1e293b !important;
        background: #1e293b !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
    }

    /* 買家查詢卡片樣式 */
    .status-card {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
    }
    .card-item-title {
        font-size: 17px;
        font-weight: 700;
        color: #ffffff !important;
    }
    .card-item-body {
        font-size: 14px;
        color: #cbd5e1 !important;
        line-height: 1.7;
    }
    .status-badge-green {
        background: rgba(34, 197, 94, 0.2);
        color: #86efac !important;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 13px;
        font-weight: 700;
        border: 1px solid rgba(34, 197, 94, 0.4);
        display: inline-block;
    }
    .status-badge-yellow {
        background: rgba(234, 179, 8, 0.2);
        color: #fde047 !important;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 13px;
        font-weight: 700;
        border: 1px solid rgba(234, 179, 8, 0.4);
        display: inline-block;
    }
    .status-badge-red {
        background: rgba(239, 68, 68, 0.2);
        color: #fca5a5 !important;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 13px;
        font-weight: 700;
        border: 1px solid rgba(239, 68, 68, 0.4);
        display: inline-block;
    }
    .status-badge-pending {
        background: rgba(56, 189, 248, 0.2);
        color: #38bdf8 !important;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 13px;
        font-weight: 700;
        border: 1px solid rgba(56, 189, 248, 0.4);
        display: inline-block;
    }

    /* 維修進度追蹤卡片 */
    .repair-card {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.9) 100%);
        border: 1.5px solid rgba(56, 189, 248, 0.45);
        border-radius: 14px;
        padding: 20px 22px;
        margin-top: 14px;
        box-shadow: 0 6px 24px rgba(0,0,0,0.4);
    }
    .repair-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        padding-bottom: 12px;
        margin-bottom: 14px;
    }
    .repair-card-title {
        font-size: 16px;
        font-weight: 800;
        color: #38bdf8 !important;
    }
    .repair-stat-box {
        background: rgba(15, 23, 42, 0.7);
        padding: 12px 14px;
        border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.08);
    }
    .repair-stat-label {
        font-size: 12px;
        color: #94a3b8 !important;
        font-weight: 600;
    }
    .repair-stat-value {
        font-size: 17px;
        font-weight: 800;
        color: #ffffff !important;
        margin-top: 4px;
    }
    .repair-stat-tech {
        font-size: 17px;
        font-weight: 800;
        color: #38bdf8 !important;
        margin-top: 4px;
    }
    .repair-desc-box {
        font-size: 14px;
        color: #cbd5e1 !important;
        line-height: 1.6;
        background: rgba(0,0,0,0.25);
        padding: 10px 14px;
        border-radius: 8px;
    }

    /* 後台摘要資訊盒 */
    .manager-review-summary-box {
        background: rgba(30,41,59,0.5);
        padding: 12px 16px;
        border-radius: 10px;
        margin-top: 10px;
        border: 1px solid rgba(255,255,255,0.08);
    }
    .manager-repair-summary-box {
        background: rgba(15, 23, 42, 0.7);
        border-radius: 8px;
        padding: 10px 14px;
        margin-top: 8px;
        border: 1px solid rgba(56, 189, 248, 0.35);
    }
    .manager-repair-summary-box span {
        color: #38bdf8 !important;
    }

    /* 必填照片提醒框 */
    .photo-required-box {
        border: 2px dashed rgba(239, 68, 68, 0.45);
        border-radius: 12px;
        padding: 26px 20px;
        text-align: center;
        color: #e2e8f0;
        background: rgba(239, 68, 68, 0.08);
    }
    .photo-required-title {
        font-size: 15px;
        font-weight: 700;
        color: #fca5a5 !important;
    }
    .photo-required-desc {
        font-size: 13px;
        color: #cbd5e1 !important;
        margin-top: 6px;
        display: inline-block;
    }
</style>
"""

# ==========================================
# 簡約俐落清爽淺色主題 CSS (Light Mode)
# ==========================================
LIGHT_CSS = """
<style>
    /* 徹底隱藏 Streamlit 預設頁首、頁尾與浮水印橫條 */
    #MainMenu {visibility: hidden !important; display: none !important;}
    #stDecoration, [data-testid="stDecoration"] {display: none !important; visibility: hidden !important; height: 0 !important; width: 0 !important; margin: 0 !important; padding: 0 !important;}
    [data-testid="stHeader"] {display: none !important; visibility: hidden !important; height: 0 !important;}

    footer {visibility: hidden !important; display: none !important;}
    header {visibility: hidden !important; display: none !important;}
    [data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    .viewerBadge_container__r5tak, .viewerBadge_link__1SuqQ {display: none !important;}

    /* 全域清爽亮麗漸層背景與微網格 */
    .stApp {
        background: 
            radial-gradient(circle at 10% 12%, rgba(2, 132, 199, 0.06) 0%, transparent 40%),
            radial-gradient(circle at 90% 15%, rgba(99, 102, 241, 0.06) 0%, transparent 40%),
            linear-gradient(135deg, #f8fafc 0%, #f1f5f9 45%, #e2e8f0 100%) !important;
        background-attachment: fixed !important;
        color: #0f172a !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans TC", sans-serif !important;
    }

    /* 背景柔和微網格 */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background-image: 
            linear-gradient(rgba(15, 23, 42, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(15, 23, 42, 0.03) 1px, transparent 1px);
        background-size: 32px 32px;
        pointer-events: none;
        z-index: 0;
    }

    /* 頂部主標題與一般文字色彩高對比黑深藍 */
    h1, h2, h3, h4, h5, h6 {
        color: #0f172a !important;
        font-weight: 700 !important;
    }
    p, span, label, li {
        color: #334155;
    }

    /* 輸入框與文字區 placeholder 深灰 */
    ::placeholder, ::-webkit-input-placeholder, ::-moz-placeholder, :-ms-input-placeholder,
    input::placeholder, textarea::placeholder {
        color: #64748b !important;
        opacity: 1 !important;
    }

    /* 表單標籤深黑高對比 */
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label,
    label[data-testid="stWidgetLabel"],
    .stTextInput label,
    .stTextArea label,
    .stSelectbox label,
    .stFileUploader label {
        color: #0f172a !important;
        font-weight: 700 !important;
        font-size: 14.5px !important;
        letter-spacing: 0.2px;
    }

    /* 提示小字 (st.caption) 深藍灰 */
    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p,
    .stCaption,
    .stCaption p {
        color: #475569 !important;
        font-size: 13.5px !important;
        line-height: 1.5 !important;
    }

    /* 輸入表單整體外框容器（純白底、深黑文字、清晰微邊框） */
    div[data-testid="stTextInputRootElement"],
    div[data-testid="stTextAreaRootElement"],
    div[data-testid="stTextInput"] > div > div,
    div[data-testid="stTextArea"] > div > div,
    [data-baseweb="input"],
    [data-baseweb="textarea"],
    [data-baseweb="base-input"] {
        background-color: #ffffff !important;
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        overflow: hidden !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stTextInputRootElement"]:focus-within,
    div[data-testid="stTextAreaRootElement"]:focus-within {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15) !important;
    }

    /* 內層輸入欄位（打字文字深黑、背景透明） */
    .stTextInput input,
    .stTextArea textarea,
    [data-testid="stTextInput"] input,
    [data-testid="stTextInputField"],
    div[data-testid="stTextInputRootElement"] input,
    .stTextArea textarea,
    [data-testid="stTextArea"] textarea,
    div[data-testid="stTextAreaRootElement"] textarea,
    [data-baseweb="input"] input,
    [data-baseweb="base-input"] input,
    [data-baseweb="textarea"] textarea {
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        outline: none !important;
        box-shadow: none !important;
        color: #0f172a !important;
        font-size: 14.5px !important;
    }

    /* 密碼框眼睛按鈕（淺色模式） */
    div[data-testid="stTextInputRootElement"] > div,
    div[data-testid="stTextInputRootElement"] button,
    div[data-testid="stTextInput"] button,
    div[data-testid="stTextInput"] [data-baseweb="input"] button,
    [data-baseweb="input"] button,
    button[aria-label*="password" i],
    button[aria-label*="Password" i] {
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
        cursor: pointer !important;
        color: #64748b !important;
    }
    div[data-testid="stTextInputRootElement"] button:hover,
    div[data-testid="stTextInput"] button:hover,
    button[aria-label*="password" i]:hover,
    button[aria-label*="Password" i]:hover {
        background-color: #f1f5f9 !important;
    }
    div[data-testid="stTextInputRootElement"] button *,
    div[data-testid="stTextInput"] button *,
    button[aria-label*="password" i] *,
    button[aria-label*="Password" i] * {
        color: #64748b !important;
        fill: #64748b !important;
        stroke: #64748b !important;
    }
    div[data-testid="stTextInputRootElement"] button:hover *,
    div[data-testid="stTextInput"] button:hover *,
    button[aria-label*="password" i]:hover *,
    button[aria-label*="Password" i]:hover * {
        color: #2563eb !important;
        fill: #2563eb !important;
        stroke: #2563eb !important;
    }

    /* 下拉選單本體與彈出選單（淺色高對比） */
    div[data-baseweb="select"],
    div[data-baseweb="select"] > div,
    [data-testid="stSelectbox"] > div > div {
        background-color: #ffffff !important;
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        color: #0f172a !important;
    }
    div[data-baseweb="select"] *,
    [data-testid="stSelectbox"] * {
        color: #0f172a !important;
    }
    div[data-baseweb="select"] svg {
        fill: #2563eb !important;
    }

    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    div[data-baseweb="popover"] ul,
    div[data-baseweb="menu"],
    div[data-baseweb="menu"] > div,
    ul[role="listbox"],
    div[role="listbox"],
    [data-testid="stSelectboxVirtualDropdown"] {
        background-color: #ffffff !important;
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 10px !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1) !important;
    }
    div[data-baseweb="popover"] *,
    div[data-baseweb="menu"] *,
    ul[role="listbox"] *,
    div[role="listbox"] *,
    [role="listbox"] [role="option"],
    [role="listbox"] [role="option"] *,
    [role="option"],
    [role="option"] *,
    li[role="option"],
    li[role="option"] *,
    div[role="option"],
    div[role="option"] *,
    [data-testid="stSelectboxVirtualDropdown"] * {
        color: #0f172a !important;
        background-color: transparent !important;
        background: transparent !important;
    }
    [role="option"]:hover,
    [role="option"]:hover *,
    li[role="option"]:hover,
    li[role="option"]:hover *,
    div[role="option"]:hover,
    div[role="option"]:hover * {
        background-color: #eff6ff !important;
        background: #eff6ff !important;
        color: #1d4ed8 !important;
    }
    [role="option"][aria-selected="true"],
    [role="option"][aria-selected="true"] *,
    li[role="option"][aria-selected="true"],
    li[role="option"][aria-selected="true"] *,
    div[role="option"][aria-selected="true"],
    div[role="option"][aria-selected="true"] * {
        background-color: #2563eb !important;
        background: #2563eb !important;
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* 提示框在淺色下的配色 */
    [data-testid="stAlert"],
    [data-testid="stNotification"] {
        border-radius: 12px !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05) !important;
    }
    [data-testid="stAlert"]:has([data-testid="stAlertContentInfo"]),
    div[data-baseweb="notification"][kind="info"] {
        background: #eff6ff !important;
        border: 1px solid #93c5fd !important;
    }
    [data-testid="stAlert"]:has([data-testid="stAlertContentInfo"]) *,
    div[data-baseweb="notification"][kind="info"] * {
        color: #1e40af !important;
    }
    [data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]),
    div[data-baseweb="notification"][kind="success"] {
        background: #f0fdf4 !important;
        border: 1px solid #86efac !important;
    }
    [data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]) *,
    div[data-baseweb="notification"][kind="success"] * {
        color: #166534 !important;
    }
    [data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]),
    div[data-baseweb="notification"][kind="warning"] {
        background: #fffbeb !important;
        border: 1px solid #fde68a !important;
    }
    [data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) *,
    div[data-baseweb="notification"][kind="warning"] * {
        color: #92400e !important;
    }
    [data-testid="stAlert"]:has([data-testid="stAlertContentError"]),
    div[data-baseweb="notification"][kind="error"] {
        background: #fef2f2 !important;
        border: 1px solid #fca5a5 !important;
    }
    [data-testid="stAlert"]:has([data-testid="stAlertContentError"]) *,
    div[data-baseweb="notification"][kind="error"] * {
        color: #991b1b !important;
    }

    /* 淺色側邊欄樣式 */
    [data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 1px solid #e2e8f0 !important;
        box-shadow: 2px 0 12px rgba(0, 0, 0, 0.04) !important;
    }
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [role="radiogroup"] * {
        color: #1e293b !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #0f172a !important;
    }
    .sidebar-header-box {
        padding: 6px 0 14px 0; 
        border-bottom: 1px solid #e2e8f0; 
        margin-bottom: 14px;
    }
    .sidebar-title {
        font-size: 20px; 
        font-weight: 800; 
        color: #0f172a; 
        letter-spacing: -0.5px;
    }
    .sidebar-subtitle {
        font-size: 12px; 
        color: #0284c7; 
        margin-top: 4px;
        font-weight: 600;
    }
    .sidebar-subtitle-admin {
        font-size: 12px; 
        color: #16a34a; 
        margin-top: 4px; 
        font-weight: 600;
    }

    /* 淺色橫幅卡片 */
    .tech-hero {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #cbd5e1;
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
        position: relative;
        overflow: hidden;
    }
    .hero-title {
        background: linear-gradient(135deg, #0284c7 0%, #4f46e5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 26px;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 6px;
    }
    .hero-subtitle {
        color: #475569;
        font-size: 14px;
        line-height: 1.6;
    }
    .badge-item {
        display: inline-flex;
        align-items: center;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
        background: #e0e7ff;
        border: 1px solid #c7d2fe;
        color: #3730a3 !important;
    }

    /* 指標數據卡 (stMetric) 淺色 */
    [data-testid="stMetric"] {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 14px !important;
        padding: 16px 20px !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04) !important;
        transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease !important;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-3px) !important;
        border-color: #6366f1 !important;
        box-shadow: 0 6px 18px rgba(99, 102, 241, 0.15) !important;
    }
    [data-testid="stMetricLabel"] p {
        color: #64748b !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    [data-testid="stMetricValue"] div {
        color: #0284c7 !important;
        font-weight: 800 !important;
    }

    /* 摺疊清單 (stExpander) 淺色 */
    [data-testid="stExpander"],
    [data-testid="stExpander"] details {
        background-color: #ffffff !important;
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
        margin-bottom: 14px !important;
        overflow: hidden !important;
    }
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] details summary,
    .streamlit-expanderHeader {
        background-color: #f8fafc !important;
        background: #f8fafc !important;
        border-radius: 10px !important;
        color: #0f172a !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        border: 1px solid #e2e8f0 !important;
    }
    [data-testid="stExpander"] summary:hover,
    [data-testid="stExpander"] details summary:hover,
    .streamlit-expanderHeader:hover {
        background-color: #f1f5f9 !important;
        background: #f1f5f9 !important;
        color: #0284c7 !important;
    }
    [data-testid="stExpander"] summary *,
    [data-testid="stExpander"] details summary *,
    .streamlit-expanderHeader *,
    [data-testid="stExpander"] p,
    [data-testid="stExpander"] span,
    [data-testid="stExpander"] div {
        color: #1e293b !important;
    }
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        background-color: #ffffff !important;
        background: #ffffff !important;
        color: #1e293b !important;
    }

    /* 檔案上傳器淺色 */
    [data-testid="stFileUploader"],
    [data-testid="stFileUploader"] section,
    [data-testid="stFileUploaderDropzone"],
    div[data-testid="stFileUploaderDropzone"],
    [data-baseweb="file-uploader"],
    [data-testid="stFileUploader"] section > div {
        background-color: #f8fafc !important;
        background: #f8fafc !important;
        border: 1px dashed #94a3b8 !important;
        border-radius: 12px !important;
    }
    [data-testid="stFileUploader"] section *,
    [data-testid="stFileUploaderDropzone"] * {
        color: #475569 !important;
    }
    [data-testid="stFileUploader"] button,
    [data-testid="stFileUploaderDropzone"] button {
        background-color: #ffffff !important;
        background: #ffffff !important;
        color: #1e293b !important;
        border: 1px solid #cbd5e1 !important;
    }

    /* 按鈕樣式淺色 */
    .stButton > button,
    div[data-testid="stButton"] > button,
    button[data-testid="baseButton-secondary"],
    button[kind="secondary"] {
        background-color: #ffffff !important;
        background: #ffffff !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        border: 1px solid #cbd5e1 !important;
        color: #1e293b !important;
    }
    .stButton > button:hover,
    div[data-testid="stButton"] > button:hover,
    button[data-testid="baseButton-secondary"]:hover,
    button[kind="secondary"]:hover {
        background-color: #f1f5f9 !important;
        background: #f1f5f9 !important;
        border-color: #0284c7 !important;
        color: #0284c7 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.15) !important;
    }
    .stButton > button[kind="primary"],
    button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%) !important;
        background-color: #2563eb !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
        color: #ffffff !important;
    }
    .stButton > button[kind="primary"]:hover,
    button[data-testid="baseButton-primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(79, 70, 229, 0.4) !important;
        color: #ffffff !important;
    }

    /* 浮動工具列淺色 */
    [data-testid="stElementToolbar"],
    div[data-testid="stElementToolbar"],
    .stElementToolbar {
        background-color: #ffffff !important;
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 9999px !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08) !important;
        color: #1e293b !important;
    }
    [data-testid="stElementToolbar"] button,
    div[data-testid="stElementToolbar"] button {
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        color: #1e293b !important;
    }
    [data-testid="stElementToolbar"] svg,
    div[data-testid="stElementToolbar"] svg {
        fill: #1e293b !important;
        stroke: #1e293b !important;
        color: #1e293b !important;
    }

    /* 資料表格與圖表外框淺色 */
    [data-testid="stDataFrame"],
    div[data-testid="stDataFrame"],
    .stDataFrame {
        background-color: #ffffff !important;
        background: #ffffff !important;
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04) !important;
        overflow: hidden !important;
    }
    [data-testid="stVegaLiteChart"],
    div[data-testid="stVegaLiteChart"],
    [data-testid="stPlotlyChart"],
    div[data-testid="stPlotlyChart"] {
        background-color: #ffffff !important;
        background: #ffffff !important;
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
        padding: 8px !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04) !important;
    }

    /* 風險燈號淺色標籤 */
    .pill-red {
        background: #fee2e2;
        color: #b91c1c !important;
        border: 1px solid #fca5a5;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 13px;
        display: inline-block;
    }
    .pill-yellow {
        background: #fef9c3;
        color: #a16207 !important;
        border: 1px solid #fde047;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 13px;
        display: inline-block;
    }
    .pill-green {
        background: #dcfce7;
        color: #15803d !important;
        border: 1px solid #86efac;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 13px;
        display: inline-block;
    }

    /* 內嵌代碼標籤 (Inline Code) 淺色 */
    code {
        color: #0369a1 !important;
        background: #f1f5f9 !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
        border: 1px solid #cbd5e1 !important;
    }

    /* 對話彈出視窗 (Modal Dialog) 淺色高雅 */
    div[role="dialog"],
    div[role="dialog"] > div,
    div[data-baseweb="modal"],
    div[data-baseweb="modal"] > div,
    div[data-baseweb="modal"] [role="dialog"],
    div[data-baseweb="modal"] [role="dialog"] > div,
    [data-testid="stDialog"],
    [data-testid="stDialog"] > div,
    [data-testid="stModal"],
    [data-testid="stModal"] > div {
        background-color: #ffffff !important;
        background: #ffffff !important;
        color: #0f172a !important;
    }
    div[role="dialog"] {
        border: 1px solid #cbd5e1 !important;
        border-radius: 16px !important;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15) !important;
    }
    div[role="dialog"] *,
    [data-testid="stDialog"] * {
        color: #0f172a !important;
    }
    div[role="dialog"] .stCheckbox label span {
        color: #0f172a !important;
        font-weight: 500 !important;
    }
    div[role="dialog"] textarea,
    div[role="dialog"] input {
        background-color: #f8fafc !important;
        background: #f8fafc !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
    }

    /* 買家查詢卡片樣式淺色 */
    .status-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }
    .card-item-title {
        font-size: 17px;
        font-weight: 700;
        color: #0f172a !important;
    }
    .card-item-body {
        font-size: 14px;
        color: #334155 !important;
        line-height: 1.7;
    }
    .status-badge-green {
        background: #dcfce7;
        color: #166534 !important;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 13px;
        font-weight: 700;
        border: 1px solid #86efac;
        display: inline-block;
    }
    .status-badge-yellow {
        background: #fef9c3;
        color: #854d0e !important;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 13px;
        font-weight: 700;
        border: 1px solid #fde047;
        display: inline-block;
    }
    .status-badge-red {
        background: #fee2e2;
        color: #991b1b !important;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 13px;
        font-weight: 700;
        border: 1px solid #fca5a5;
        display: inline-block;
    }
    .status-badge-pending {
        background: #e0f2fe;
        color: #0369a1 !important;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 13px;
        font-weight: 700;
        border: 1px solid #7dd3fc;
        display: inline-block;
    }

    /* 維修進度追蹤卡片淺色 */
    .repair-card {
        background: #ffffff;
        border: 1.5px solid #93c5fd;
        border-radius: 14px;
        padding: 20px 22px;
        margin-top: 14px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.06);
    }
    .repair-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 12px;
        margin-bottom: 14px;
    }
    .repair-card-title {
        font-size: 16px;
        font-weight: 800;
        color: #0284c7 !important;
    }
    .repair-stat-box {
        background: #f8fafc;
        padding: 12px 14px;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
    .repair-stat-label {
        font-size: 12px;
        color: #64748b !important;
        font-weight: 600;
    }
    .repair-stat-value {
        font-size: 17px;
        font-weight: 800;
        color: #0f172a !important;
        margin-top: 4px;
    }
    .repair-stat-tech {
        font-size: 17px;
        font-weight: 800;
        color: #0284c7 !important;
        margin-top: 4px;
    }
    .repair-desc-box {
        font-size: 14px;
        color: #334155 !important;
        line-height: 1.6;
        background: #f1f5f9;
        padding: 10px 14px;
        border-radius: 8px;
    }

    /* 後台摘要資訊盒淺色 */
    .manager-review-summary-box {
        background: #f8fafc;
        padding: 12px 16px;
        border-radius: 10px;
        margin-top: 10px;
        border: 1px solid #e2e8f0;
    }
    .manager-repair-summary-box {
        background: #eff6ff;
        border-radius: 8px;
        padding: 10px 14px;
        margin-top: 8px;
        border: 1px solid #bfdbfe;
    }
    .manager-repair-summary-box span {
        color: #0284c7 !important;
    }

    /* 必填照片提醒框淺色 */
    .photo-required-box {
        border: 2px dashed #fca5a5;
        border-radius: 12px;
        padding: 26px 20px;
        text-align: center;
        color: #334155;
        background: #fef2f2;
    }
    .photo-required-title {
        font-size: 15px;
        font-weight: 700;
        color: #dc2626 !important;
    }
    .photo-required-desc {
        font-size: 13px;
        color: #475569 !important;
        margin-top: 6px;
        display: inline-block;
    }
</style>
"""

# 動態注入深色或淺色樣式
st.markdown(DARK_CSS if is_dark else LIGHT_CSS, unsafe_allow_html=True)

# 電腦周邊受檢類別清單（嚴格限定：鍵盤、滑鼠、耳機）
PERIPHERAL_CATEGORIES = [
    "⌨️ 機械/薄膜鍵盤",
    "🖱️ 滑鼠",
    "🎧 耳機"
]

# ==========================================
# 0.1 郵件設定持久化核心 (email_config.json)
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "email_config.json")

def load_email_config():
    """讀取本地持久化之郵件設定，防止網頁刷新後密碼遺失"""
    default_cfg = {
        "sender_email": "zhuant610@gmail.com",
        "app_password": ""
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {**default_cfg, **data}
        except Exception:
            return default_cfg
    return default_cfg

def save_email_config(sender_email, app_password):
    """將郵件設定儲存至本地 email_config.json"""
    cfg = {
        "sender_email": (sender_email or "zhuant610@gmail.com").strip(),
        "app_password": (app_password or "").strip()
    }
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"儲存郵件設定失敗: {str(e)}")
    return cfg

# 系統預設發送審核結果通知之電子郵件帳號
email_cfg = load_email_config()
SENDER_EMAIL = email_cfg.get("sender_email", "zhuant610@gmail.com")

# ==========================================
# 0.2 管理員身分與密碼設定持久化 (admin_config.json)
# ==========================================
ADMIN_CONFIG_FILE = os.path.join(BASE_DIR, "admin_config.json")

def load_admin_config():
    """讀取本地持久化之管理員後台設定"""
    default_cfg = {
        "admin_password": "admin888",
        "gemini_api_key": "",
        "gemini_model_name": "gemini-3.8-flash"
    }
    if os.path.exists(ADMIN_CONFIG_FILE):
        try:
            with open(ADMIN_CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {**default_cfg, **data}
        except Exception:
            return default_cfg
    return default_cfg

def save_admin_config(admin_password=None, gemini_api_key=None, gemini_model_name=None):
    """將管理員密碼、API Key 或模型名稱設定儲存至本地 admin_config.json"""
    cfg = load_admin_config()
    if admin_password is not None:
        cfg["admin_password"] = (admin_password or "admin888").strip()
    if gemini_api_key is not None:
        cfg["gemini_api_key"] = gemini_api_key.strip()
    if gemini_model_name is not None:
        cfg["gemini_model_name"] = gemini_model_name.strip()
    try:
        with open(ADMIN_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"儲存管理員設定失敗: {str(e)}")
    return cfg


# ==========================================
# 0.3 會員與角色權限認證系統 (SQLite users)
# ==========================================
import hashlib

def hash_password(password: str) -> str:
    """密碼 SHA-256 安全雜湊運算"""
    return hashlib.sha256(password.strip().encode("utf-8")).hexdigest()

def init_users_table(cursor):
    """初始化 users 帳號資料表並預設植入管理方與買家示範帳號"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TEXT NOT NULL
        )
    """)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 預設平台管理員: admin / admin888
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (username, password_hash, email, role, created_at) VALUES (?, ?, ?, ?, ?)",
            ("admin", hash_password("admin888"), "admin@copilot.com", "admin", now_str)
        )
    # 管理方指定帳號: stillni / 1919clow114514
    cursor.execute("SELECT id FROM users WHERE username = 'stillni'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (username, password_hash, email, role, created_at) VALUES (?, ?, ?, ?, ?)",
            ("stillni", hash_password("1919clow114514"), "burnie.chen@gmail.com", "admin", now_str)
        )
    else:
        cursor.execute(
            "UPDATE users SET password_hash = ?, email = ?, role = 'admin' WHERE username = 'stillni'",
            (hash_password("1919clow114514"), "burnie.chen@gmail.com")
        )
    # 預設一般買家帳號: buyer01 / buyer123
    cursor.execute("SELECT id FROM users WHERE username = 'buyer01'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (username, password_hash, email, role, created_at) VALUES (?, ?, ?, ?, ?)",
            ("buyer01", hash_password("buyer123"), "buyer01@gmail.com", "user", now_str)
        )

def register_user(username, password, email, role="user", admin_code=""):
    """新使用者註冊"""
    username = username.strip()
    email = email.strip()
    if not username:
        return False, "❌ 請輸入使用者帳號！"
    if len(username) < 3:
        return False, "❌ 帳號長度至少需 3 個字元！"
    if not password or len(password) < 4:
        return False, "❌ 密碼長度至少需 4 個字元！"
    if not email or "@" not in email:
        return False, "❌ 請輸入有效的電子郵件信箱！"

    # 若申請管理方權限，需驗證管理員授權碼
    if role == "admin":
        correct_admin_code = load_admin_config().get("admin_password", "admin888")
        if admin_code.strip() != correct_admin_code:
            return False, "❌ 管理員註冊授權碼錯誤！無法註冊為管理方身份。"

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ?", (username,))
    if c.fetchone():
        conn.close()
        return False, f"❌ 帳號「{username}」已被註冊，請更換其他帳號名稱！"

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute(
        "INSERT INTO users (username, password_hash, email, role, created_at) VALUES (?, ?, ?, ?, ?)",
        (username, hash_password(password), email, role, now_str)
    )
    conn.commit()
    conn.close()
    role_label = "🛡️ 平台管理員 (店長)" if role == "admin" else "👤 一般使用者 (買家)"
    return True, f"🎉 註冊成功！您已獲得【{role_label}】身份，請使用新帳號登入系統。"

def authenticate_user(username, password):
    """會員登入驗證"""
    username = username.strip()
    if not username or not password:
        return False, None, "❌ 請輸入帳號與密碼！"

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, username, password_hash, email, role, created_at FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if not row:
        return False, None, "❌ 帳號不存在，請先切換至「📝 註冊新帳號」進行註冊！"
    if row[2] != hash_password(password):
        return False, None, "❌ 密碼錯誤，請重新確認！"

    user_info = {
        "id": row[0],
        "username": row[1],
        "email": row[3],
        "role": row[4],
        "created_at": row[5]
    }
    return True, user_info, "✅ 登入成功！"

def get_all_users():
    """查詢所有註冊會員清單"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, username, email, role, created_at FROM users ORDER BY id ASC")
    rows = c.fetchall()
    conn.close()
    return rows

def delete_user(user_id):
    """刪除指定帳號 (不允許刪除原始 admin)"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return False, "❌ 找不到指定帳號！"
    if row[0] == "admin":
        conn.close()
        return False, "❌ 系統預設根管理員 (admin) 不可刪除！"
    c.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True, f"✅ 已成功刪除帳號「{row[0]}」！"

def update_user_role(user_id, new_role):
    """變更使用者身份權限"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return False, "❌ 找不到指定帳號！"
    if row[0] == "admin" and new_role != "admin":
        conn.close()
        return False, "❌ 系統預設根管理員 (admin) 權限不可降級！"
    c.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
    conn.commit()
    conn.close()
    return True, f"✅ 已成功將「{row[0]}」身份變更為【{new_role}】！"

# ==========================================
# 1. 資料庫初始化與資料遷移 (SQLite)
# ==========================================
DB_FILE = os.path.join(BASE_DIR, "disputes.db")

def encode_images_to_db(images_bytes_list):
    """將多張圖片 bytes 清單轉換為 (primary_blob, images_json) 供資料庫存儲"""
    if not images_bytes_list:
        return None, ""
    primary_blob = images_bytes_list[0]
    b64_list = [base64.b64encode(b).decode('utf-8') for b in images_bytes_list]
    return primary_blob, json.dumps(b64_list)

def decode_images_from_db(image_data, images_json=None):
    """從資料庫欄位解析並回傳所有圖片 bytes 清單 (相容歷史單張與全新多張)"""
    if images_json:
        try:
            b64_list = json.loads(images_json)
            if isinstance(b64_list, list) and len(b64_list) > 0:
                return [base64.b64decode(item) for item in b64_list]
        except Exception:
            pass
    if image_data:
        try:
            if isinstance(image_data, bytes) and image_data.startswith(b'["') and image_data.endswith(b'"]'):
                b64_list = json.loads(image_data.decode('utf-8'))
                return [base64.b64decode(item) for item in b64_list]
        except Exception:
            pass
        return [image_data]
    return []

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS return_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT,
            customer_email TEXT,
            product_category TEXT,
            product_name TEXT,
            customer_reason TEXT,
            image_data BLOB,
            images_json TEXT DEFAULT '',
            status TEXT DEFAULT '待審核',
            risk_level TEXT,
            risk_score INTEGER,
            ai_verdict TEXT,
            ai_evidence TEXT,
            ai_recommendation TEXT,
            review_comment TEXT DEFAULT '',
            repair_date TEXT DEFAULT '',
            technician_id TEXT DEFAULT '',
            repair_status TEXT DEFAULT '',
            created_at TEXT,
            reviewed_at TEXT
        )
    """)
    conn.commit()

    # 自動檢查並為現有資料庫新增欄位
    for col_def in [
        "customer_email TEXT DEFAULT ''",
        "repair_date TEXT DEFAULT ''",
        "technician_id TEXT DEFAULT ''",
        "repair_status TEXT DEFAULT ''",
        "images_json TEXT DEFAULT ''",
        "username TEXT DEFAULT ''"
    ]:
        try:
            c.execute(f"ALTER TABLE return_requests ADD COLUMN {col_def}")
            conn.commit()
        except sqlite3.OperationalError:
            pass

    # 初始化 users 帳號資料表
    init_users_table(c)
    conn.commit()

    # 為歷史舊資料補上預設展示用電子郵件
    c.execute("UPDATE return_requests SET customer_email = 'buyer_sample@example.com' WHERE customer_email IS NULL OR customer_email = ''")

    # 自動遷移舊版資料庫中的非周邊資料，並全數統一為三大周邊標準品類
    c.execute("""
        UPDATE return_requests 
        SET product_category = '⌨️ 機械/薄膜鍵盤',
            product_name = '客製化鋁合金熱插拔機械鍵盤',
            customer_reason = '收到鍵盤外殼角落摔裂凹陷，多個鍵軸被暴力拔起且插座針腳折斷，PCB銅箔破裂。',
            ai_verdict = '疑似嚴重人為摔落撞擊與私自暴力拆改',
            ai_evidence = '鋁合金外殼具有尖銳著地凹痕，且軸座受力屬於垂直外力拔扯斷裂，研判為使用摔落或改裝失誤導致。',
            ai_recommendation = '高風險人為損毀，建議【駁回申請】並提供自費維修報價'
        WHERE product_category LIKE '%平板%' OR product_category LIKE '%手機%'
    """)
    c.execute("UPDATE return_requests SET product_category = '🎧 耳機' WHERE product_category LIKE '%耳機%'")
    c.execute("UPDATE return_requests SET product_category = '⌨️ 機械/薄膜鍵盤' WHERE product_category LIKE '%鍵盤%'")
    c.execute("UPDATE return_requests SET product_category = '🖱️ 滑鼠' WHERE product_category LIKE '%滑鼠%'")
    conn.commit()
    
    # 檢查是否需要預設展示資料
    c.execute("SELECT COUNT(*) FROM return_requests")
    count = c.fetchone()[0]
    if count == 0:
        seed_sample_data(c)
        conn.commit()
    conn.close()

def seed_sample_data(cursor):
    """
    預設示範案例：全面聚焦於電腦周邊 (鍵盤、滑鼠、耳機) 之典型客訴與詐欺情境（包含買家信箱）
    """
    sample_cases = [
        (
            "ORD-PERI-8821", "buyer.service88@gmail.com", "🎧 耳機", "7.1聲道雙模無線降噪耳機",
            "剛開箱充電整晚完全無法開機，電源指示燈完全不亮，插線亦無任何聲音輸出。",
            None, "已通過", "綠燈", 15,
            "電源迴路故障 / 出廠新品不良 (DOA)",
            "外觀無任何外力擠壓裂痕或人為泡水生鏽痕跡，符合保固新品不良免費換新條件。",
            "建議通過全額退款或換新，並安排逆物流取件",
            "已核准新品換貨", "2026-10-05 10:15:00", "2026-10-05 10:30:00"
        ),
        (
            "ORD-PERI-9043", "user.keyboard90@gmail.com", "⌨️ 機械/薄膜鍵盤", "客製化鋁合金熱插拔機械鍵盤",
            "收到鍵盤外殼角落摔裂凹陷，多個鍵軸被暴力拔起且插座針腳折斷，PCB銅箔破裂。",
            None, "已駁回", "紅燈", 92,
            "疑似嚴重人為摔落撞擊與私自暴力拆改",
            "照片顯示鋁合金定位板與外殼有明顯尖銳著地凹痕，且軸座受力屬於垂直外力拔扯斷裂，外包裝盒無相對應壓損，高機率為使用摔落或改裝不當所致。",
            "高風險人為損壞，建議【駁回申請】並告知不屬出廠保固範疇，提供自費維修報價",
            "外力撞擊凹痕與拆解損壞明顯，已電話聯繫買家駁回", "2026-10-06 14:20:00", "2026-10-06 14:45:00"
        ),
        (
            "ORD-PERI-9188", "tech.user91@gmail.com", "⌨️ 機械/薄膜鍵盤", "RGB三模無線矮軸機械鍵盤",
            "打字起來手感怪怪的，鍵程好像太短不順手，有時候打太快感覺有按鍵沒反應。",
            None, "待審核", "黃燈", 55,
            "手感主觀感受爭議 / 缺特定鍵位測試事證",
            "買家描述偏向主觀手感不適應，且未指出具體失靈鍵位（未提供線上 Key-Test 按鍵測試截圖或動態操作短片）。",
            "建議要求買家補件：提供線上鍵盤測試網頁操作截圖或特定卡鍵按鍵短片",
            "", "2026-10-07 09:10:00", None
        ),
        (
            "ORD-PERI-9302", "office.worker93@gmail.com", "🖱️ 滑鼠", "PAW3395 輕量化無線滑鼠",
            "使用第三天左鍵微動開關嚴重雙擊連點（按一下變兩下），且滾輪下滾時偶爾向上跳動。",
            None, "待審核", "綠燈", 22,
            "微動開關彈片耗損與滾輪編碼器信號跳動",
            "買家回報為典型滑鼠微動開關觸點異常與光學/機械編碼器跳幀現象，外觀無摔裂泡水跡象，符合新品保固條款。",
            "建議核准換貨新品（小額電腦周邊可評估免寄回不良品以節省逆物流運費）",
            "", "2026-10-07 13:40:00", None
        )
    ]
    cursor.executemany("""
        INSERT INTO return_requests 
        (order_id, customer_email, product_category, product_name, customer_reason, image_data, status, risk_level, risk_score, ai_verdict, ai_evidence, ai_recommendation, review_comment, created_at, reviewed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_cases)

init_db()

# ==========================================
# 2. 審核判決郵件發送核心 (寄件信箱: zhuant610@gmail.com)
# ==========================================
def send_decision_email(customer_email, order_id, product_name, status, review_comment, verdict="", recommendation="", repair_date="", technician_id="", repair_status=""):
    """
    於店長審核判決拍板時，寄送電子郵件通知至買家信箱
    寄送時使用的電子信箱: zhuant610@gmail.com
    嚴格診斷連線與認證狀態，提供清晰的反饋資訊
    """
    if not customer_email or "@" not in customer_email:
        return False, "⚠️ 買家未填寫有效之電子信箱，跳過郵件發送。"

    cfg = load_email_config()
    sender = cfg.get("sender_email", "zhuant610@gmail.com").strip()
    app_pwd = cfg.get("app_password", "").strip() or st.session_state.get("gmail_app_password", "").strip() or os.environ.get("GMAIL_APP_PASSWORD", "").strip()

    if not app_pwd:
        return False, f"⚠️ 尚未設定 Gmail 應用程式密碼！目前無法由 {sender} 發送真實 Email。\n\nGoogle 自 2022 年起已全面禁用一般帳號密碼發信，請前往「⚙️ 系統設定 & API」輸入 16 碼應用程式密碼。"

    subject = f"【售後退換貨審核通知】訂單 {order_id} - 審核結果：{status}"

    # 針對維修件動態生成維修時程表格區塊
    repair_section_html = ""
    if status == "已通過" and (repair_date or technician_id or repair_status):
        repair_section_html = f"""
        <tr style="border-bottom: 1px solid #e2e8f0; background-color: #f0fdf4;">
            <td style="padding: 10px 0; color: #166534; font-weight: 600;">🛠️ 維修處置狀態</td>
            <td style="padding: 10px 0; color: #15803d; font-weight: 700;">{repair_status or '已安排寄回維修'}</td>
        </tr>
        <tr style="border-bottom: 1px solid #e2e8f0; background-color: #f0fdf4;">
            <td style="padding: 10px 0; color: #166534; font-weight: 600;">📅 預計完修送回日期</td>
            <td style="padding: 10px 0; color: #0f172a; font-weight: 700;">{repair_date or '排程檢測中'}</td>
        </tr>
        <tr style="border-bottom: 1px solid #e2e8f0; background-color: #f0fdf4;">
            <td style="padding: 10px 0; color: #166534; font-weight: 600;">👷 維修人員工作編號</td>
            <td style="padding: 10px 0; color: #0f172a; font-weight: 700;">{technician_id or '專責工程師'}</td>
        </tr>
        """

    comment_title = "店家核准說明與寄回指引" if status == "已通過" else ("店家駁回理由說明" if status == "已駁回" else "店長補件指示說明")

    html_body = f"""
    <html>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans TC', sans-serif; background-color: #f8fafc; padding: 24px; margin: 0;">
        <div style="max-width: 600px; margin: auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 14px rgba(0,0,0,0.08); border: 1px solid #e2e8f0;">
            <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 24px 28px; border-bottom: 3px solid #38bdf8;">
                <h2 style="color: #ffffff; margin: 0; font-size: 20px; font-weight: 700;">🛡️ 電腦周邊售後客服中心 · 審核結果通知</h2>
                <p style="color: #94a3b8; font-size: 13px; margin: 6px 0 0 0;">人機協同爭議風控平台 (HITL System)</p>
            </div>
            
            <div style="padding: 28px;">
                <p style="font-size: 15px; color: #1e293b; margin-top: 0;">親愛的買家您好：</p>
                <p style="font-size: 14px; color: #475569; line-height: 1.6;">
                    您於本平台提交之電腦周邊售後申請，經由 <strong>AI 初審與店家專業複審</strong>，最終裁決結果如下：
                </p>
                
                <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 18px 22px; margin: 20px 0;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                        <tr style="border-bottom: 1px solid #e2e8f0;">
                            <td style="padding: 10px 0; color: #64748b; width: 32%;">訂單編號</td>
                            <td style="padding: 10px 0; color: #0f172a; font-weight: 600;">{order_id}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e2e8f0;">
                            <td style="padding: 10px 0; color: #64748b;">商品名稱</td>
                            <td style="padding: 10px 0; color: #0f172a; font-weight: 600;">{product_name}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e2e8f0;">
                            <td style="padding: 10px 0; color: #64748b;">審核判決</td>
                            <td style="padding: 10px 0; font-weight: bold; font-size: 15px; color: {'#16a34a' if status == '已通過' else ('#d97706' if status == '需補件' else '#dc2626')};">
                                {status}
                            </td>
                        </tr>
                        {repair_section_html}
                        <tr style="border-bottom: 1px solid #e2e8f0;">
                            <td style="padding: 10px 0; color: #64748b; vertical-align: top;">{comment_title}</td>
                            <td style="padding: 10px 0; color: #0f172a; white-space: pre-wrap; line-height: 1.6;">{review_comment or '無特別備註'}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e2e8f0;">
                            <td style="padding: 10px 0; color: #64748b;">AI 判定依據</td>
                            <td style="padding: 10px 0; color: #334155; font-size: 13px;">{verdict}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px 0; color: #64748b;">處置建議</td>
                            <td style="padding: 10px 0; color: #334155; font-size: 13px;">{recommendation}</td>
                        </tr>
                    </table>
                </div>
                
                <p style="font-size: 13px; color: #64748b; line-height: 1.6; margin-bottom: 0;">
                    ※ 本郵件由系統自動發送，寄件信箱：<strong>{sender}</strong>。<br>
                    ※ 若有補傳瑕疵照片/操作短片之需求，或對審核結果有任何疑問，歡迎直接回覆此郵件聯繫我們。
                </p>
            </div>
            
            <div style="background-color: #f1f5f9; padding: 14px 28px; text-align: center; border-top: 1px solid #e2e8f0; font-size: 12px; color: #94a3b8;">
                電腦周邊智慧退換貨與爭議風控系統 · 感謝您的配合
            </div>
        </div>
    </body>
    </html>
    """

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"電腦周邊售後客服中心 <{sender}>"
        msg["To"] = customer_email
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        clean_pwd = app_pwd.replace(" ", "")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(sender, clean_pwd)
            server.sendmail(sender, customer_email, msg.as_string())
        return True, f"已成功由 {sender} 發送真實通知信至買家信箱：{customer_email}！"
    except smtplib.SMTPAuthenticationError:
        return False, f"❌ Gmail 認證失敗 (535)：帳號 {sender} 或應用程式密碼錯誤。請確認 Google 帳戶已開啟「兩步驟驗證」，並至安全性設定中產生專用 16 碼「應用程式密碼」（注意：非一般登入密碼）。"
    except smtplib.SMTPConnectError as e:
        return False, f"❌ 無法連線至 Gmail 伺服器 (smtp.gmail.com:465)：{str(e)}"
    except Exception as e:
        return False, f"❌ 郵件發送失敗：{str(e)}"

# ==========================================
# 2.1 人機協同審核決策小視窗 (Approval / Rejection / Supplement Modals)
# ==========================================
dialog_decorator = getattr(st, "dialog", getattr(st, "experimental_dialog", None))

def render_approve_dialog_content(case_id, order_id, product_name, customer_email, ai_verdict, ai_recommendation):
    """
    核准小視窗內容：填寫處置理由與維修資訊 (預計送回日期、維修人員工作編號)，確認後更新並發送 Email
    """
    st.markdown(f"**訂單編號**：`{order_id}` ｜ **商品名稱**：`{product_name}`")
    st.markdown(f"**買家通知信箱**：`{customer_email}`")
    st.markdown("---")

    st.markdown("##### 📦 請選擇售後處置方案：")
    action_type = st.radio(
        "處置模式",
        ["📦 寄回原廠維修 / 更換零件 (啟用買家端維修進度追蹤)", "💰 全額退款 / 免寄回換發新品"],
        index=0,
        key=f"dlg_act_{case_id}"
    )

    is_repair = "維修" in action_type
    rep_date = ""
    tech_id = ""
    rep_status = ""

    if is_repair:
        st.markdown("##### 🛠️ 維修排程與工程師指派 (皆可自訂，買家前台可即時查詢)：")
        rc1, rc2 = st.columns(2)
        with rc1:
            default_date = (datetime.now() + pd.Timedelta(days=7)).strftime("%Y-%m-%d")
            rep_date = st.text_input("預計完修送回日期", value=default_date, key=f"dlg_date_{case_id}", help="例如：2026-10-27，讓買家掌握送回時程")
        with rc2:
            default_tech = f"TECH-{(case_id * 137 % 900) + 100}"
            tech_id = st.text_input("維修人員工作編號", value=default_tech, key=f"dlg_tech_{case_id}", help="店家自訂之工程師/維修人員代碼")
        
        rep_status = st.selectbox(
            "初始維修進度狀態",
            [
                "［待收件］已核准維修，請買家將瑕疵品包裝寄回",
                "［檢測中］收到商品，工程師進行微動/軸體/電氣檢測",
                "［更換零件中］已拆機更換原廠零組件",
                "［校正完畢］清潔校正與全功能測試正常",
                "［已寄出］已交付物流黑貓宅急便，配送送回中"
            ],
            index=0,
            key=f"dlg_status_{case_id}"
        )
    else:
        rep_status = "直接退款 / 免寄回換新"

    st.markdown("##### ✍️ 店家核准說明與指示 (此內容將完整呈現於寄送買家的 Email 通知中)：")
    default_approve_text = (
        "經 AI 初審與店長複審，確認符合出廠保固免費維修標準！請依後續物流指引將故障品寄回。我們已指派專責維修工程師為您處理，您可隨時至「查詢進度」即時追蹤維修狀態與送回日期。"
        if is_repair else
        "經 AI 初審與店長複審，確認符合新品瑕疵標準，已為您核准申請！我們將主動安排款項退回或新機寄出，感謝您的配合。"
    )
    custom_desc = st.text_area(
        "核准詳細理由與注意事項：",
        value=default_approve_text,
        height=100,
        key=f"dlg_app_desc_{case_id}"
    )

    st.caption("※ 點擊下方確認按鈕後，案件將正式更新為「已通過」，並立即透過 **zhuant610@gmail.com** 發送包含上述理由與維修資訊的 Email 給買家。")

    col_send, col_cancel = st.columns([1, 1])
    with col_send:
        if st.button("🚀 確認核准並發送通知信", type="primary", use_container_width=True, key=f"dlg_app_submit_{case_id}"):
            update_conn = sqlite3.connect(DB_FILE)
            cur = update_conn.cursor()
            now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("""
                UPDATE return_requests 
                SET status='已通過', review_comment=?, reviewed_at=?, repair_date=?, technician_id=?, repair_status=? 
                WHERE id=?
            """, (custom_desc, now_time, rep_date, tech_id, rep_status, case_id))
            update_conn.commit()
            update_conn.close()

            ok, res_msg = send_decision_email(
                customer_email=customer_email,
                order_id=order_id,
                product_name=product_name,
                status='已通過',
                review_comment=custom_desc,
                verdict=ai_verdict,
                recommendation=ai_recommendation,
                repair_date=rep_date,
                technician_id=tech_id,
                repair_status=rep_status
            )

            st.session_state["last_email_notification"] = {
                "ok": ok,
                "order_id": order_id,
                "status": "已通過",
                "to": customer_email,
                "msg": res_msg
            }
            if "active_approve_id" in st.session_state:
                del st.session_state["active_approve_id"]
            st.rerun()

    with col_cancel:
        if st.button("❌ 取消返回", use_container_width=True, key=f"dlg_app_cancel_{case_id}"):
            if "active_approve_id" in st.session_state:
                del st.session_state["active_approve_id"]
            st.rerun()

def render_reject_dialog_content(case_id, order_id, product_name, customer_email, ai_verdict, ai_recommendation):
    """
    駁回小視窗內容：填寫具體駁回理由，確認後才更新案件並發送 Email
    """
    st.markdown(f"**訂單編號**：`{order_id}` ｜ **商品名稱**：`{product_name}`")
    st.markdown(f"**買家通知信箱**：`{customer_email}`")
    st.markdown("---")

    st.markdown("##### 📌 請勾選或自訂駁回主要原因：")
    c1, c2 = st.columns(2)
    with c1:
        rej_drop = st.checkbox("💥 外力重擊 / 摔落凹陷破裂 (非出廠保固)", value=True, key=f"rej_chk1_{case_id}")
        rej_mod = st.checkbox("🛠️ 私自拆解 / 暴力撬軸 / 焊點飛線", value=False, key=f"rej_chk2_{case_id}")
    with c2:
        rej_water = st.checkbox("💧 飲料進水 / 泡水受潮 PCB 氧化發霉", value=False, key=f"rej_chk3_{case_id}")
        rej_pref = st.checkbox("👂 主觀手感/音質不適應 (已拆封無硬體故障)", value=False, key=f"rej_chk4_{case_id}")

    reasons = []
    if rej_drop: reasons.append("外力重擊摔裂凹陷")
    if rej_mod: reasons.append("私自拆解或改裝改焊")
    if rej_water: reasons.append("進水受潮氧化")
    if rej_pref: reasons.append("主觀手感/音質感受爭議且無硬體故障")

    st.markdown("##### ✍️ 店家駁回詳細說明 (此內容將完整呈現於寄送給買家的 Email 通知中)：")
    default_reject_text = (
        f"經店長與 AI 複審，送檢商品特徵符合【{'、'.join(reasons) if reasons else '人為使用不當'}】，非屬原廠出廠新品不良或保固範疇，故無法受理免費退換貨申請。若有需要自費維修更換零件，請直接回覆此郵件聯繫我們取得報價。"
    )
    custom_desc = st.text_area(
        "駁回詳細指示說明：",
        value=default_reject_text,
        height=110,
        key=f"dlg_rej_desc_{case_id}"
    )

    st.caption("※ 點擊下方確認按鈕後，案件將正式更新為「已駁回」，並立即透過 **zhuant610@gmail.com** 發送包含駁回說明的 Email 給買家。")

    col_send, col_cancel = st.columns([1, 1])
    with col_send:
        if st.button("🚫 確認駁回並發送通知信", type="primary", use_container_width=True, key=f"dlg_rej_submit_{case_id}"):
            update_conn = sqlite3.connect(DB_FILE)
            cur = update_conn.cursor()
            now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("""
                UPDATE return_requests 
                SET status='已駁回', review_comment=?, reviewed_at=? 
                WHERE id=?
            """, (custom_desc, now_time, case_id))
            update_conn.commit()
            update_conn.close()

            ok, res_msg = send_decision_email(
                customer_email=customer_email,
                order_id=order_id,
                product_name=product_name,
                status='已駁回',
                review_comment=custom_desc,
                verdict=ai_verdict,
                recommendation=ai_recommendation
            )

            st.session_state["last_email_notification"] = {
                "ok": ok,
                "order_id": order_id,
                "status": "已駁回",
                "to": customer_email,
                "msg": res_msg
            }
            if "active_reject_id" in st.session_state:
                del st.session_state["active_reject_id"]
            st.rerun()

    with col_cancel:
        if st.button("❌ 取消返回", use_container_width=True, key=f"dlg_rej_cancel_{case_id}"):
            if "active_reject_id" in st.session_state:
                del st.session_state["active_reject_id"]
            st.rerun()

def render_supplement_dialog_content(case_id, order_id, product_name, customer_email, ai_verdict, ai_recommendation):
    """
    補件小視窗內容：填寫具體需補件的內容 (包含缺照片)，確認後才更新案件並發送 Email
    """
    st.markdown(f"**訂單編號**：`{order_id}` ｜ **商品型號**：`{product_name}`")
    st.markdown(f"**買家通知信箱**：`{customer_email}`")
    st.markdown("---")

    st.markdown("##### 📌 請勾選需要買家補件的項目：")
    c1, c2 = st.columns(2)
    with c1:
        req_photo = st.checkbox("📷 缺少清晰瑕疵照片 (外觀/受損處特寫)", value=True, key=f"dlg_photo_{case_id}")
        req_sn = st.checkbox("🏷️ 缺少商品序號/防偽貼紙照片", value=False, key=f"dlg_sn_{case_id}")
    with c2:
        req_video = st.checkbox("🎥 缺少故障操作短片 (連點/卡鍵/跳幀/無聲)", value=False, key=f"dlg_video_{case_id}")
        req_test = st.checkbox("📊 缺少按鍵/微動檢測截圖 (Key-Test)", value=False, key=f"dlg_test_{case_id}")

    st.markdown("##### ✍️ 填寫需補件的具體說明與要求內容：")
    default_text = "經店長與 AI 初步審核，目前退貨申訴缺乏關鍵瑕疵照片佐證。請於 3 日內補充清晰特寫照片或操作短片，以利完成出廠保固核銷與後續退換換新流程。"
    custom_desc = st.text_area(
        "補件詳細指示 (此內容將完整呈現於寄送給買家的 Email 通知中)：",
        value=default_text,
        height=110,
        key=f"dlg_desc_{case_id}"
    )

    st.caption("※ 點擊下方確認按鈕後，案件將正式更新為「需補件」，並立即透過 **zhuant610@gmail.com** 發送補件 Email 給買家。")

    col_send, col_cancel = st.columns([1, 1])
    with col_send:
        if st.button("🚀 確認送出補件要求並發送 Email", type="primary", use_container_width=True, key=f"dlg_submit_{case_id}"):
            missing_items = []
            if req_photo:
                missing_items.append("缺少清晰瑕疵照片 (外觀/受損處特寫)")
            if req_sn:
                missing_items.append("缺少商品序號/防偽貼紙照片")
            if req_video:
                missing_items.append("缺少故障操作短片 (連點/卡鍵/跳幀/無聲)")
            if req_test:
                missing_items.append("缺少按鍵/微動檢測截圖 (Key-Test)")

            missing_str = "、".join(missing_items) if missing_items else "請依說明補充相關佐證"
            final_note = f"【需補件項目】：{missing_str}\n【店長指示說明】：{custom_desc}"

            # 更新資料庫
            update_conn = sqlite3.connect(DB_FILE)
            cur = update_conn.cursor()
            now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("UPDATE return_requests SET status='需補件', review_comment=?, reviewed_at=? WHERE id=?", 
                        (final_note, now_time, case_id))
            update_conn.commit()
            update_conn.close()

            # 發送補件 Email 通知
            ok, res_msg = send_decision_email(
                customer_email=customer_email,
                order_id=order_id,
                product_name=product_name,
                status='需補件',
                review_comment=final_note,
                verdict=ai_verdict,
                recommendation=ai_recommendation
            )

            st.session_state["last_email_notification"] = {
                "ok": ok,
                "order_id": order_id,
                "status": "需補件",
                "to": customer_email,
                "msg": res_msg
            }
            if "active_supplement_id" in st.session_state:
                del st.session_state["active_supplement_id"]
            st.rerun()

    with col_cancel:
        if st.button("❌ 取消返回", use_container_width=True, key=f"dlg_cancel_{case_id}"):
            if "active_supplement_id" in st.session_state:
                del st.session_state["active_supplement_id"]
            st.rerun()

if dialog_decorator:
    @dialog_decorator("✅ 核准退換：填寫處置理由與維修資訊")
    def open_approve_modal(case_id, order_id, product_name, customer_email, ai_verdict, ai_recommendation):
        render_approve_dialog_content(case_id, order_id, product_name, customer_email, ai_verdict, ai_recommendation)

    @dialog_decorator("🚫 駁回申請：填寫駁回理由與說明")
    def open_reject_modal(case_id, order_id, product_name, customer_email, ai_verdict, ai_recommendation):
        render_reject_dialog_content(case_id, order_id, product_name, customer_email, ai_verdict, ai_recommendation)

    @dialog_decorator("⚠️ 要求補件：填寫補件內容與通知")
    def open_supplement_modal(case_id, order_id, product_name, customer_email, ai_verdict, ai_recommendation):
        render_supplement_dialog_content(case_id, order_id, product_name, customer_email, ai_verdict, ai_recommendation)


# ==========================================
# 3. 電腦周邊專用 AI 智能初審核心 (LLM / 專用模擬雙軌)
# ==========================================
def analyze_return_request(category, product_name, reason, image_file, api_key=""):
    """
    電腦周邊專用瑕疵與風控分析核心：
    - 若有提供 API Key：呼叫 Gemini 多模態視覺模型深度檢測
    - 若無 API Key：啟用電腦周邊專用風控規則引擎（覆蓋軸體、微動、編碼器、單元、進水摔裂等關鍵特徵）
    """
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            prompt = f"""
            你是一位專精於「電腦周邊（機械/薄膜鍵盤、滑鼠、耳機）」售後退換貨與爭議防詐風控的資深專家。
            檢測範圍嚴格限定於電腦周邊三大品類：鍵盤、滑鼠、耳機。
            
            請根據買家提供的退貨資訊進行嚴謹審查：
            - 周邊品類: {category}
            - 周邊名稱: {product_name}
            - 買家申訴原因: {reason}

            【電腦周邊風控研判原則】：
            1. 紅燈 (高風險人為損害/拆裝/進水，75-100分)：外力摔破、外殼凹裂、暴力撬拔軸體/微動、飲料進水受潮、私自拆解改裝、線材扯斷。
            2. 黃燈 (事證不足/主觀感受爭議，40-74分)：手感不習慣、按鍵壓力不適應、主觀音質偏好、延遲感覺模糊，未附連點測試數據或操作影片。
            3. 綠燈 (正常新品瑕疵 DOA，0-39分)：微動雙擊連點、滾輪跳幀、特定軸體不觸發、完全無法通電、無線接收器失靈、單耳無聲。

            請以 JSON 格式輸出：
            {{
                "risk_level": "綠燈" / "黃燈" / "紅燈",
                "risk_score": 0到100整數,
                "verdict": "一句話簡短判定結論 (精準指出周邊故障類型)",
                "evidence": "具體判斷依據與分析說明 (結合鍵盤/滑鼠/耳機結構特性分析)",
                "recommendation": "給賣家店長的具體處置建議 (如：免寄回換新/補傳測試短片/駁回並提供自費維修)"
            }}
            """
            contents = [prompt]
            if isinstance(image_file, list):
                for img_b in image_file[:3]:
                    try:
                        contents.append(Image.open(io.BytesIO(img_b)))
                    except Exception:
                        pass
            elif image_file:
                try:
                    contents.append(Image.open(io.BytesIO(image_file)))
                except Exception:
                    pass

            # 全面一致通用 Google 官方指定旗艦模型 gemini-3.8-flash
            try:
                response = client.models.generate_content(
                    model='gemini-3.8-flash',
                    contents=contents
                )
                res_text = response.text.replace("```json", "").replace("```", "").strip()
                data = json.loads(res_text)
                return data["risk_level"], data["risk_score"], data["verdict"], data["evidence"], data["recommendation"]
            except Exception as model_err:
                st.warning(f"真實 Gemini 3.8 Flash API 呼叫異常 ({str(model_err)})，系統已自動無縫降級為電腦周邊展示模擬引擎。")
        except Exception as e:
            st.warning(f"真實 API 呼叫異常 ({str(e)})，系統已自動無縫降級為電腦周邊展示模擬引擎。")

    # 電腦周邊專用模擬引擎 (Domain-Specific Mock Engine)
    reason_lower = reason.lower()
    
    # 1. 人為暴力外力摔裂、拆解改裝、泡水受潮 (高風險紅燈)
    if any(k in reason_lower for k in ["摔", "破", "碎", "斷", "裂", "撞", "泡水", "進水", "飲料", "撬", "拆", "改裝", "狗咬", "拉扯", "焦", "燒"]):
        return (
            "紅燈", 88,
            "周邊外觀重大受損 / 疑似人為暴力損害或私自拆裝",
            "申訴特徵符合高能量外力衝擊、飲料進水受潮或人為改裝破壞（非屬正常鍵軸/微動出廠耗損），高機率為使用不當導致之硬體損毀。",
            "建議【駁回申請】，依保固規範主動提供原廠保固外自費維修或零件更換服務報價"
        )
    # 2. 主觀手感、聽感偏好或事證模糊 (黃燈需補件)
    elif any(k in reason_lower for k in ["怪怪", "手感", "不習慣", "不順", "不好用", "不喜歡", "沒想像", "音質不如", "鍵程", "延遲", "稍微", "偏重", "偏輕", "延遲"]):
        return (
            "黃燈", 52,
            "手感或聽感主觀感受爭議 / 瑕疵事證未明",
            "買家描述偏向個人使用習慣適應性或音質主觀偏好，未附具體按鍵測試器截圖、連點測試數據或破音錄音影片，事證尚不齊全。",
            "建議【要求買家補件】：請買家提供特定按鍵/微動/聲道之動態操作測試影片或檢測截圖"
        )
    # 3. 典型出廠硬體不良 (微動雙擊、滾輪跳動、單耳無聲、軸體失靈、無法開機) (綠燈快審)
    else:
        return (
            "綠燈", 20,
            "周邊電子元件硬體瑕疵 / 出廠新品不良 (DOA)",
            "描述符合鍵盤軸體觸發不良、滑鼠微動雙擊、滾輪編碼器信號跳動或耳機單元斷路等典型出廠品質問題，無人為外力損壞跡象。",
            "建議【核准全額退款】或安排換發新品（電腦周邊小件可評估免寄回以節省逆物流運費）"
        )

# ==========================================
# 3. 會員帳號驗證與系統側邊欄導航 (帳號登入制)
# ==========================================
if "current_user" not in st.session_state:
    st.session_state["current_user"] = None

current_user = st.session_state.get("current_user")

# 側邊欄最頂部：深色/淺色主題風格即時切換
st.sidebar.radio(
    "深色/淺色",
    ["🌙 深色", "☀️ 淺色"],
    key="app_theme_choice",
    horizontal=True
)
st.sidebar.markdown("---")

if current_user is None:
    # 未登入狀態：側邊欄提示
    st.sidebar.markdown("""
    <div class="sidebar-header-box">
        <div class="sidebar-title">🛡️ Peripheral Copilot</div>
        <div class="sidebar-subtitle">● 會員權限驗證中心 (Auth Gateway)</div>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.info("""
    **👋 歡迎蒞臨電腦周邊售後與風控平台！**
    
    本系統已全面升級為**「會員帳號登入制」**：
    - 👤 **一般使用者 (買家)**：提交保固維修與退貨申請、上傳照片 AI 檢測、隨時追蹤個人案件進度。
    - 🛡️ **管理方 (店長/審核)**：具備人機協同審查 (HITL)、Google Gemini 3.8 Flash 風控研判、BI 營運儀表板與帳號權限管理。

    👉 請由主畫面【登入】或【註冊】新帳號以進入系統。
    """)
    st.sidebar.caption("📧 系統客服信箱：zhuant610@gmail.com")

    # 主畫面呈現：精緻的登入與註冊整合門戶
    st.markdown("""
    <div class="tech-hero">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div>
                <div class="hero-title">🛡️ 電腦周邊智慧售後退換貨與爭議風控平台</div>
                <div class="hero-subtitle">
                    基於 Google Gemini 3.8 Flash 多模態 AI · 鍵盤／滑鼠／耳機人機協同審核決策系統
                </div>
            </div>
            <div style="display:flex; gap:8px; flex-wrap:wrap;">
                <span class="badge-item">🔐 帳號登入制</span>
                <span class="badge-item">⚡ 角色分流權限</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    auth_tab_login, auth_tab_register = st.tabs(["🔑 會員登入 (Sign In)", "📝 註冊新帳號 (Sign Up)"])

    with auth_tab_login:
        st.markdown("#### 🔑 請輸入帳號密碼登入系統：")
        col_l1, col_l2 = st.columns([1, 1])
        with col_l1:
            login_user = st.text_input("帳號 (Username)", key="input_login_username", placeholder="例如: admin 或 buyer01")
        with col_l2:
            login_pwd = st.text_input("密碼 (Password)", type="password", key="input_login_password", placeholder="請輸入密碼")

        if st.button("🚀 登入系統", type="primary", use_container_width=True, key="btn_do_login"):
            ok, uinfo, msg = authenticate_user(login_user, login_pwd)
            if ok:
                st.session_state["current_user"] = uinfo
                st.session_state["admin_authenticated"] = (uinfo["role"] == "admin")
                st.success(f"{msg} 歡迎回來，【{uinfo['username']}】！")
                st.rerun()
            else:
                st.error(msg)

        st.markdown("---")
        st.caption("💡 **專題評審與口試展示專用快速體驗通道（點擊即可自動登入）：**")
        qc1, qc2 = st.columns(2)
        with qc1:
            if st.button("🛡️ 快速以【管理方 (stillni)】身分登入", use_container_width=True):
                ok, uinfo, msg = authenticate_user("stillni", "1919clow114514")
                ok, uinfo, msg = authenticate_user("admin", "admin888")
                if ok:
                    st.session_state["current_user"] = uinfo
                    st.session_state["admin_authenticated"] = True
                    st.rerun()
        with qc2:
            if st.button("👤 快速以【一般使用者 (買家)】身分登入 (buyer01 / buyer123)", use_container_width=True):
                ok, uinfo, msg = authenticate_user("buyer01", "buyer123")
                if ok:
                    st.session_state["current_user"] = uinfo
                    st.session_state["admin_authenticated"] = False
                    st.rerun()

    with auth_tab_register:
        st.markdown("#### 📝 填寫資料建立新會員帳號：")
        rc1, rc2 = st.columns(2)
        with rc1:
            reg_username = st.text_input("設定帳號 (至少3個字元)", key="input_reg_username", placeholder="例如: my_username")
            reg_email = st.text_input("通知電子信箱 (接收審核結果通知)", key="input_reg_email", placeholder="例如: yourname@gmail.com")
        with rc2:
            reg_pwd = st.text_input("設定密碼 (至少4個字元)", type="password", key="input_reg_pwd")
            reg_pwd_confirm = st.text_input("確認密碼", type="password", key="input_reg_pwd_confirm")

        st.caption("※ 註冊完成即獲得買家帳號資格，可立即提交周邊退換貨申請、上傳照片進行 AI 檢驗與查詢進度。")

        if st.button("✨ 立即建立會員帳號並登入", type="primary", use_container_width=True, key="btn_do_register"):
            if reg_pwd != reg_pwd_confirm:
                st.error("❌ 兩次輸入的密碼不一致，請再次確認！")
            else:
                ok, msg = register_user(reg_username, reg_pwd, reg_email, role="user")
                if ok:
                    _, uinfo, _ = authenticate_user(reg_username, reg_pwd)
                    st.session_state["current_user"] = uinfo
                    st.session_state["admin_authenticated"] = False
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    st.stop()

# ==========================================
# 已登入狀態：依照身分角色分流選單與功能
# ==========================================
is_admin = (current_user["role"] == "admin")
st.session_state["admin_authenticated"] = is_admin

if not is_admin:
    # 一般使用者 (買家) 視圖：僅提供買家前台服務
    st.sidebar.markdown(f"""
    <div class="sidebar-header-box">
        <div class="sidebar-title">🛍️ 周邊售後客服中心</div>
        <div class="sidebar-subtitle">👤 一般使用者：{current_user['username']}</div>
    </div>
    """, unsafe_allow_html=True)

    menu = st.sidebar.radio(
        "📌 買家服務選單",
        [
            "📝 買家：提交退換貨申請",
            "🔍 買家：查詢進度 / 補充照片"
        ]
    )

    st.sidebar.markdown("---")
    st.sidebar.info("""
    **🎯 受理電腦周邊範圍：**
    - ⌨️ **機械/薄膜鍵盤** (軸體/鍵位/PCB)
    - 🖱️ **滑鼠** (微動/編碼器/感應器)
    - 🎧 **耳機** (單元/頭樑/收音)

    **📋 買家售後須知：**
    1. 購買 7 日內商品享新品不良免費換新/退款服務。
    2. 申請時【必須上傳瑕疵佐證照片】，未附照片恕無法受理申請。
    3. 審核判決將自動寄發通知信至您的註冊信箱。
    """)

else:
    # 管理方 (店長/老闆) 視圖：完整解鎖管理功能
    st.sidebar.markdown(f"""
    <div class="sidebar-header-box">
        <div class="sidebar-title">🛡️ Peripheral Copilot</div>
        <div class="sidebar-subtitle-admin">🟢 管理員已登入：{current_user['username']}</div>
    </div>
    """, unsafe_allow_html=True)

    menu = st.sidebar.radio(
        "📌 系統功能導航",
        [
            "🧑‍💼 店長：人機對照審核台",
            "📊 老闆：BI 營運成效儀表板",
            "👥 帳號清單與權限管理",
            "⚙️ 系統設定 & API",
            "📝 買家：提交退換貨申請",
            "🔍 買家：查詢進度 / 補充照片"
        ]
    )

    st.sidebar.markdown("---")
    st.sidebar.info("""
    **🎯 檢測對象聚焦：**
    - ⌨️ **機械/薄膜鍵盤** (軸體/鍵位/PCB)
    - 🖱️ **滑鼠** (微動/編碼器/感應器)
    - 🎧 **耳機** (單元/頭樑/收音)
    """)

# 側邊欄底部：帳號資訊與登出按鈕
st.sidebar.markdown("---")
if st.sidebar.button(f"🚪 登出系統 ({current_user['username']})", use_container_width=True):
    st.session_state["current_user"] = None
    st.session_state["admin_authenticated"] = False
    st.rerun()

st.sidebar.caption(f"👤 當前帳號：{current_user['username']} ({'管理方' if is_admin else '買家'})")

# 安全防護：非管理員嘗試存取管理後台頁面時自動導向
if menu in ["🧑‍💼 店長：人機對照審核台", "📊 老闆：BI 營運成效儀表板", "👥 帳號清單與權限管理", "⚙️ 系統設定 & API"] and not is_admin:
    st.warning("⚠️ 該頁面僅限管理方存取，已自動導向買家服務門戶。")
    menu = "📝 買家：提交退換貨申請"

# 主畫面頂端常駐登入者狀態標籤列
user_pill_color = "#38bdf8" if is_admin else "#10b981"
user_role_tag = "👑 平台管理員 (店長/審核方)" if is_admin else "👤 一般使用者 (買家)"
st.markdown(f"""
<div style="background: rgba(30, 41, 59, 0.45); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 8px; padding: 6px 14px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
    <div style="font-size: 13px; color: #cbd5e1;">
        當前登入者：<b style="color: #fff;">{current_user['username']}</b> ｜ 權限：<span style="color: {user_pill_color}; font-weight: 600;">{user_role_tag}</span> ｜ 信箱：<code>{current_user['email']}</code>
    </div>
    <div style="font-size: 12px; color: #94a3b8;">
        ✅ 身分驗證已通過
    </div>
</div>
""", unsafe_allow_html=True)

if menu == "📝 買家：提交退換貨申請":
    st.markdown("""
    <div class="tech-hero">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div>
                <div class="hero-title">📱 買家端：電腦周邊售後與退換貨申請門戶</div>
                <div class="hero-subtitle">
                    專為 <strong>鍵盤、滑鼠、耳機</strong> 設計之 7 天鑑賞期瑕疵檢驗與智慧退換貨申訴通道
                </div>
            </div>
            <div style="display:flex; gap:8px; flex-wrap:wrap;">
                <span class="badge-item">⌨️ 鍵盤檢測</span>
                <span class="badge-item">🖱️ 滑鼠檢測</span>
                <span class="badge-item">🎧 耳機檢測</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 初始化 session_state 中的買家照片清單
    if "app_buyer_photos" not in st.session_state:
        st.session_state["app_buyer_photos"] = []

    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        st.markdown("#### 📝 填寫申訴資訊")
        order_id = st.text_input("訂單編號", value=f"ORD-PERI-{datetime.now().strftime('%m%d%H%M')}")
        default_email = current_user.get("email", "") if current_user else ""
        customer_email = st.text_input("買家電子信箱 (Email) *必填，接收審核判決通知", value=default_email, placeholder="例如：buyer@example.com")
        category = st.selectbox("周邊商品類別 (僅限電腦周邊)", PERIPHERAL_CATEGORIES)
        
        # 依據所選周邊顯示專屬檢驗指引
        if "鍵盤" in category:
            st.caption("💡 **鍵盤檢驗提示**：建議拍照包含鍵帽外觀、軸體插座或背光狀態；若為卡鍵請註明特定鍵位 (如 Space, Enter, WASD)。")
        elif "滑鼠" in category:
            st.caption("💡 **滑鼠檢驗提示**：建議拍照包含滾輪、底面腳墊磨損與接收器外觀；若為連點請註明左鍵或右鍵。")
        elif "耳機" in category:
            st.caption("💡 **耳機檢驗提示**：建議拍照包含頭樑伸縮關節、耳罩皮革與線材接頭；請註明是左耳、右耳或麥克風異常。")

        product_name = st.text_input("周邊商品型號 / 全名", placeholder="例如：Logitech G PRO X 機械鍵盤 / Razer Viper V2 Pro 無線滑鼠 / HyperX Cloud III 耳麥")
        reason = st.text_area(
            "瑕疵/異常原因詳細說明", 
            placeholder="請清楚描述周邊異常狀態（例如：滑鼠左鍵點一下會連點成雙擊、鍵盤空白鍵卡住回彈不良、耳機左耳完全無聲音等）", 
            height=130
        )

    with col2:
        st.markdown("#### 📸 提供瑕疵佐證照片 *(必填，可選取多張)")
        st.caption("支援手機鏡頭拍照 (可拍多張) 或從相簿/電腦選取多張檔案，送出前可預覽並隨時刪除修改")
        
        photo_tabs = st.tabs(["📷 手機鏡頭直接拍照", "📁 從相簿/電腦選取 (支援多張)"])
        with photo_tabs[0]:
            cam_photo = st.camera_input("點擊按鈕開啟相機拍照", key="app_buyer_cam_photo")
            if cam_photo is not None:
                cam_bytes = cam_photo.getvalue()
                existing_bytes = [p["bytes"] for p in st.session_state["app_buyer_photos"]]
                if cam_bytes not in existing_bytes:
                    p_name = f"相機拍攝 #{len(st.session_state['app_buyer_photos']) + 1}"
                    st.session_state["app_buyer_photos"].append({"name": p_name, "bytes": cam_bytes})
                    st.success(f"✅ 已成功將【{p_name}】加入佐證相簿！若需拍攝其他角度可繼續拍照。")

        with photo_tabs[1]:
            file_photos = st.file_uploader(
                "選取相片或損壞照片檔案 (可複選多張檔案)",
                type=["jpg", "jpeg", "png", "webp", "bmp", "heic", "JPG", "JPEG", "PNG", "WEBP", "HEIC"],
                accept_multiple_files=True,
                key="app_buyer_multi_files",
                help="可一次選取多張照片，支援 JPG, PNG, WEBP, HEIC 等常見格式"
            )
            if file_photos:
                existing_bytes = [p["bytes"] for p in st.session_state["app_buyer_photos"]]
                added_num = 0
                for f in file_photos:
                    b = f.getvalue()
                    if b not in existing_bytes:
                        st.session_state["app_buyer_photos"].append({"name": f.name, "bytes": b})
                        existing_bytes.append(b)
                        added_num += 1
                if added_num > 0:
                    st.success(f"✅ 已成功將 {added_num} 張照片載入佐證相簿！")

        # ==========================================
        # 🖼️ 照片管理與送出前修改區 (在送出申請前能修改照片)
        # ==========================================
        cur_photos = st.session_state["app_buyer_photos"]
        if not cur_photos:
            st.markdown("""
            <div class="photo-required-box">
                <div class="photo-required-title">⚠️ 尚未提供瑕疵照片 (此項為必填)</div>
                <div class="photo-required-desc">為保障出廠保固核銷，系統規定必須拍照或上傳實體瑕疵照片（可上傳多張不同角度），送出前可在此檢視或刪除修改。</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"**📸 目前已選取照片清單 (共 `{len(cur_photos)}` 張，送出前可預覽或刪除修改)：**")
            del_target_idx = None
            
            for p_idx, p_item in enumerate(cur_photos):
                card_col1, card_col2 = st.columns([1, 2])
                with card_col1:
                    try:
                        st.image(p_item["bytes"], use_container_width=True)
                    except Exception:
                        st.caption("(照片格式正常)")
                with card_col2:
                    st.markdown(f"**照片 #{p_idx + 1}**：`{p_item['name']}`")
                    st.caption(f"大小約 {max(1, len(p_item['bytes']) // 1024)} KB")
                    if st.button(f"🗑️ 移除此照片 (#{p_idx + 1})", key=f"del_app_photo_{p_idx}", type="secondary"):
                        del_target_idx = p_idx
                st.markdown("<hr style='margin:4px 0 8px 0; border:none; border-top:1px dashed #64748b;'>", unsafe_allow_html=True)

            if del_target_idx is not None:
                st.session_state["app_buyer_photos"].pop(del_target_idx)
                st.rerun()

            if len(cur_photos) > 1:
                if st.button("🗑️ 全部清空重新選取", key="clear_all_app_buyer_photos"):
                    st.session_state["app_buyer_photos"] = []
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    submit_btn = st.button("🚀 送出退貨申請 (立即完成初審登記)", type="primary", use_container_width=True)

    if submit_btn:
        if not order_id or not customer_email or not product_name or not reason:
            st.error("請完整填寫訂單編號、買家電子信箱、周邊名稱與瑕疵說明！")
        elif "@" not in customer_email or "." not in customer_email:
            st.error("請填寫正確有效的買家電子信箱格式（例如：user@example.com）！")
        elif not st.session_state.get("app_buyer_photos", []):
            st.error("❌ 申請失敗：為加速出廠保固核銷，系統規定【必須上傳至少一張瑕疵佐證照片】否則不給予受理申請！請使用相機或上方按鈕選取照片後再送出。")
        else:
            with st.spinner("🤖 正在為您提交退貨申訴資料並進行初步建檔..."):
                all_img_bytes = [p["bytes"] for p in st.session_state["app_buyer_photos"]]
                primary_blob, images_json_str = encode_images_to_db(all_img_bytes)
                
                # 執行電腦周邊 AI 風控初審 (優先調用已設定之 Gemini API，無則使用專用風控引擎)
                api_key_to_use = st.session_state.get("gemini_api_key", "") or load_admin_config().get("gemini_api_key", "")
                risk_lvl, risk_score, verdict, evidence, rec = analyze_return_request(
                    category, product_name, reason, all_img_bytes, api_key=api_key_to_use
                )

                # 寫入 SQLite (disputes.db)
                try:
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    c_uname = current_user.get("username", "") if current_user else ""
                    c.execute("""
                        INSERT INTO return_requests 
                        (order_id, customer_email, product_category, product_name, customer_reason, image_data, images_json, status, risk_level, risk_score, ai_verdict, ai_evidence, ai_recommendation, created_at, username)
                        VALUES (?, ?, ?, ?, ?, ?, ?, '待審核', ?, ?, ?, ?, ?, ?, ?)
                    """, (order_id, customer_email.strip(), category, product_name, reason, primary_blob, images_json_str, risk_lvl, risk_score, verdict, evidence, rec, now_str, c_uname))
                    conn.commit()
                    conn.close()

                    # 送出成功後清空暫存照片
                    st.session_state["app_buyer_photos"] = []

                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📦 買家成功提交案件：{order_id} ({product_name}) -> 資料庫: {DB_FILE}")
                    st.success(f"🎉 退換貨申請已成功提交！您的案件編號為 **`{order_id}`**。")
                    st.info(f"📧 審核結果將寄發至您的電子信箱：**`{customer_email.strip()}`**。您亦可隨時在左側「🔍 查詢申請進度」輸入訂單編號追蹤審核狀態。")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ 申訴資料寫入資料庫失敗：{str(e)}。請聯繫系統管理員確認後台連線。")

# ==========================================
# 買家門戶 模組二：查詢申請進度 / 補充照片 (Buyer Query & Supplement)
# ==========================================
elif menu == "🔍 買家：查詢進度 / 補充照片":
    st.markdown("""
    <div class="tech-hero">
        <div>
            <div class="hero-title">🔍 買家端：退貨審核進度查詢與照片補傳</div>
            <div class="hero-subtitle">
                輸入您的 <strong>訂單編號</strong> 或 <strong>電子信箱</strong>，隨時追蹤退換貨最新處理狀態。
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    query_input = st.text_input("輸入訂單編號 (例如: ORD-PERI-xxxx) 或 買家電子信箱", placeholder="請輸入完整訂單編號或送出申請時填寫的 Email")

    if query_input:
        conn = sqlite3.connect(DB_FILE)
        query_sql = """
            SELECT * FROM return_requests 
            WHERE order_id = ? OR customer_email = ? 
            ORDER BY id DESC
        """
        df_query = pd.read_sql_query(query_sql, conn, params=(query_input.strip(), query_input.strip()))
        conn.close()

        if df_query.empty:
            st.warning("⚠️ 查無相符的退換貨申請案件，請確認您輸入的訂單編號或電子信箱是否正確。")
        else:
            st.markdown(f"##### 📋 查詢結果：共找到 {len(df_query)} 筆相關案件")
            for _, item in df_query.iterrows():
                cur_status = item['status']
                if cur_status == '已通過':
                    status_badge = '<span class="status-badge-green">✅ 已通過核准</span>'
                elif cur_status == '需補件':
                    status_badge = '<span class="status-badge-yellow">⚠️ 需補充資料</span>'
                elif cur_status == '已駁回':
                    status_badge = '<span class="status-badge-red">🚫 申請已駁回</span>'
                else:
                    status_badge = '<span class="status-badge-pending">⏳ 待店長審核中</span>'

                with st.container():
                    st.markdown(f"""
                    <div class="status-card">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                            <span class="card-item-title">訂單：{item['order_id']} ({item['product_name']})</span>
                            {status_badge}
                        </div>
                        <div class="card-item-body">
                            • <strong>周邊品類</strong>：{item['product_category']}<br>
                            • <strong>申請時間</strong>：{item['created_at']}<br>
                            • <strong>申訴原因</strong>：{item['customer_reason']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # 顯示買家已提交之佐證照片
                    b_img_list = decode_images_from_db(item.get('image_data'), item.get('images_json') if 'images_json' in item else None)
                    if b_img_list:
                        if len(b_img_list) == 1:
                            st.image(b_img_list[0], caption="您已上傳之佐證照片 (共 1 張)", use_container_width=True)
                        else:
                            st.markdown(f"**📸 您已上傳之佐證照片 (共 {len(b_img_list)} 張，點選標籤開啟檢視)：**")
                            b_tabs = st.tabs([f"🖼️ 照片 #{i+1}" for i in range(len(b_img_list))])
                            for i, t in enumerate(b_tabs):
                                with t:
                                    st.image(b_img_list[i], caption=f"已上傳照片 #{i+1}", use_container_width=True)

                    # 若狀態為「需補件」，提供補件說明與上傳/拍照功能
                    if cur_status == "需補件":
                        st.info(f"**📢 客服店長補件指示說明**：\n\n{item['review_comment'] or '請補充清晰之瑕疵外觀照片或操作測試短片。'}")
                        
                        st.markdown("##### 📷 補傳瑕疵照片佐證資料：")
                        st.caption("支援手機直接鏡頭拍照或從相簿/檔案上傳")
                        supp_key = f"supp_photos_{item['id']}"
                        if supp_key not in st.session_state:
                            st.session_state[supp_key] = []

                        supp_tabs = st.tabs(["📷 手機相機直接拍照", "📁 從相簿/檔案選取 (支援多張)"])
                        with supp_tabs[0]:
                            supp_cam = st.camera_input("開啟相機拍照補件", key=f"supp_cam_{item['id']}")
                            if supp_cam is not None:
                                cam_b = supp_cam.getvalue()
                                ex_b = [p["bytes"] for p in st.session_state[supp_key]]
                                if cam_b not in ex_b:
                                    p_name = f"相機補拍 #{len(st.session_state[supp_key]) + 1}"
                                    st.session_state[supp_key].append({"name": p_name, "bytes": cam_b})
                                    st.success(f"✅ 已成功將【{p_name}】加入補件相簿！")

                        with supp_tabs[1]:
                            supp_files = st.file_uploader(
                                "選取照片檔案 (可複選多張檔案)", 
                                type=["jpg", "jpeg", "png", "webp", "bmp", "heic", "JPG", "JPEG", "PNG", "WEBP", "HEIC"],
                                accept_multiple_files=True,
                                key=f"supp_file_{item['id']}"
                            )
                            if supp_files:
                                ex_b = [p["bytes"] for p in st.session_state[supp_key]]
                                add_n = 0
                                for f in supp_files:
                                    b = f.getvalue()
                                    if b not in ex_b:
                                        st.session_state[supp_key].append({"name": f.name, "bytes": b})
                                        ex_b.append(b)
                                        add_n += 1
                                if add_n > 0:
                                    st.success(f"✅ 已成功載入 {add_n} 張補件照片！")

                        cur_supp_photos = st.session_state[supp_key]
                        if cur_supp_photos:
                            st.markdown(f"**📸 目前待送出之補件照片清單 (共 `{len(cur_supp_photos)}` 張，送出前可預覽或刪除修改)：**")
                            del_s_idx = None
                            for s_i, s_p in enumerate(cur_supp_photos):
                                s_c1, s_c2 = st.columns([1, 2])
                                with s_c1:
                                    st.image(s_p["bytes"], use_container_width=True)
                                with s_c2:
                                    st.write(f"**補件照片 #{s_i+1}**：`{s_p['name']}`")
                                    if st.button(f"🗑️ 移除此補件照片 (#{s_i+1})", key=f"del_supp_{item['id']}_{s_i}"):
                                        del_s_idx = s_i
                            if del_s_idx is not None:
                                st.session_state[supp_key].pop(del_s_idx)
                                st.rerun()

                        if st.button("🚀 確認送出補件照片", type="primary", key=f"btn_supp_{item['id']}"):
                            if cur_supp_photos:
                                supp_all_bytes = [p["bytes"] for p in cur_supp_photos]
                                p_blob, j_str = encode_images_to_db(supp_all_bytes)
                                update_conn = sqlite3.connect(DB_FILE)
                                cur = update_conn.cursor()
                                cur.execute("""
                                    UPDATE return_requests 
                                    SET image_data = ?, images_json = ?, status = '待審核', customer_reason = customer_reason || ' [買家已於 ' || ? || ' 補上 ' || ? || ' 張佐證照片]'
                                    WHERE id = ?
                                """, (p_blob, j_str, datetime.now().strftime("%Y-%m-%d %H:%M"), len(supp_all_bytes), item['id']))
                                update_conn.commit()
                                update_conn.close()
                                st.session_state[supp_key] = []
                                st.success(f"✅ 共 {len(supp_all_bytes)} 張補件照片已成功上傳！案件已重新提交給客服店長進行二次審核。")
                                st.rerun()
                            else:
                                st.warning("請先拍照或選取要上傳的照片檔案！")
                    
                    elif cur_status == "已通過":
                        # 檢查是否有店家自訂之維修排程資訊
                        b_rep_date = item.get('repair_date', '') or ''
                        b_tech_id = item.get('technician_id', '') or ''
                        b_rep_stat = item.get('repair_status', '') or ''
                        if pd.isna(b_rep_date): b_rep_date = ''
                        if pd.isna(b_tech_id): b_tech_id = ''
                        if pd.isna(b_rep_stat): b_rep_stat = ''

                        if b_rep_date or b_tech_id or b_rep_stat:
                            st.markdown(f"""
                            <div class="repair-card">
                                <div class="repair-card-header">
                                    <span class="repair-card-title">🛠️ 周邊瑕疵寄回維修 / 換新即時進度追蹤</span>
                                    <span style="background:rgba(34, 197, 94, 0.2); color:#86efac; border:1px solid rgba(34, 197, 94, 0.45); padding:4px 12px; border-radius:9999px; font-weight:700; font-size:13px;">{b_rep_stat or '維修處理中'}</span>
                                </div>
                                <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:12px; margin-bottom:14px;">
                                    <div class="repair-stat-box">
                                        <div class="repair-stat-label">📅 預計完修送回日期</div>
                                        <div class="repair-stat-value">{b_rep_date or '排程檢測中'}</div>
                                    </div>
                                    <div class="repair-stat-box">
                                        <div class="repair-stat-label">👷 維修工程師代號</div>
                                        <div class="repair-stat-tech">{b_tech_id or '專責檢修人員'}</div>
                                    </div>
                                </div>
                                <div class="repair-desc-box">
                                    <strong>📢 店家與工程師處理說明</strong>：<br>{item['review_comment'] or '您的退換貨維修申請已正式受審，請留意後續物流配送。'}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.success(f"🎉 **退換貨已核准**！\n\n客服備註：{item['review_comment'] or '已通過出廠保固瑕疵核銷，請留意款項或新品換貨通知。'}")
                    
                    elif cur_status == "已駁回":
                        st.error(f"🚫 **退貨申請未通過**\n\n駁回原因說明：{item['review_comment'] or '經檢驗非屬出廠保固範圍。'}")
                    
                    st.markdown("<hr style='border-color:rgba(255,255,255,0.08);'>", unsafe_allow_html=True)

# ==========================================
# 模組一：店長人機對照審核台 (HITL)
# ==========================================
elif menu == "🧑‍💼 店長：人機對照審核台":
    st.markdown("""
    <div class="tech-hero">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div>
                <div class="hero-title">🧑‍💼 店長端：周邊人機協同審核台 (Human-in-the-Loop)</div>
                <div class="hero-subtitle">
                    透過 <strong>紅黃綠燈風險分流</strong>，店長精準對照買家申訴與 AI 佐證，秒級裁決核准、補件或駁回。
                </div>
            </div>
            <div>
                <span class="badge-item">🛡️ 人機協同防詐</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 顯示上一筆案件之郵件通知寄送狀態
    if "last_email_notification" in st.session_state:
        n_info = st.session_state.pop("last_email_notification")
        if n_info.get("ok"):
            st.success(f"📧 **審核裁決完成，通知郵件已成功寄出！**\n\n- 訂單編號：**{n_info['order_id']}** (狀態更新為：`{n_info['status']}`)\n- 收件買家：`{n_info['to']}`\n- 寄件帳號：`{SENDER_EMAIL}`\n- 發送狀態：{n_info['msg']}")
        else:
            st.error(f"⚠️ **審核裁決已更新至資料庫，但 Email 發送未成功**！\n\n- 訂單編號：**{n_info['order_id']}** (狀態更新為：`{n_info['status']}`)\n- 收件買家：`{n_info['to']}`\n- 寄件帳號：`{SENDER_EMAIL}`\n- 失敗原因：\n{n_info['msg']}\n\n👉 *提示：請前往「⚙️ 系統設定 & API」填寫 Google 帳戶 16 碼應用程式密碼，即可正常發送信件。*")

    # 讀取案件
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM return_requests ORDER BY id DESC", conn)
    conn.close()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🧑‍💼 店長後台讀取資料庫：目前共 {len(df)} 筆案件 (待審核: {len(df[df['status'] == '待審核'])} 件) -> 來源: {DB_FILE}")

    # 頂部狀態指標卡片
    c1, c2, c3, c4 = st.columns(4)
    pending_count = len(df[df['status'] == '待審核'])
    approved_count = len(df[df['status'] == '已通過'])
    rejected_count = len(df[df['status'] == '已駁回'])
    red_count = len(df[df['risk_level'] == '紅燈'])

    c1.metric("⏳ 待審核案件", f"{pending_count} 件")
    c2.metric("✅ 已通過退換", f"{approved_count} 件")
    c3.metric("🚫 已駁回案件", f"{rejected_count} 件")
    c4.metric("🚨 高風險紅燈警告", f"{red_count} 件", delta="風控攔截")

    st.markdown("---")

    # 雙維度篩選器 (處理狀態 + 周邊類別) + 即時刷新按鈕
    filter_col1, filter_col2, filter_col3 = st.columns([2, 2, 1])
    with filter_col1:
        filter_status = st.selectbox("📌 篩選處理狀態", ["全部", "待審核", "已通過", "已駁回", "需補件"], index=1)
    with filter_col2:
        filter_cat = st.selectbox("🎯 篩選周邊品類", ["全部周邊"] + PERIPHERAL_CATEGORIES, index=0)
    with filter_col3:
        st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 刷新最新案件", use_container_width=True, help="點擊即時重新讀取資料庫，載入買家最新提交的申請"):
            st.rerun()

    filtered_df = df.copy()
    if filter_status != "全部":
        filtered_df = filtered_df[filtered_df['status'] == filter_status]
    if filter_cat != "全部周邊":
        filtered_df = filtered_df[filtered_df['product_category'] == filter_cat]

    if filtered_df.empty:
        st.info("目前無符合篩選條件的周邊退貨案件。")
    else:
        st.subheader("📋 案件審核清單")
        for idx, row in filtered_df.iterrows():
            # 燈號標籤
            if row['risk_level'] == "紅燈":
                pill_html = '<span class="pill-red">🔴 紅燈 ‧ 高風險</span>'
            elif row['risk_level'] == "黃燈":
                pill_html = '<span class="pill-yellow">🟡 黃燈 ‧ 需補件</span>'
            else:
                pill_html = '<span class="pill-green">🟢 綠燈 ‧ 低風險</span>'

            with st.expander(f"【{row['risk_level']}｜風險分 {row['risk_score']}】{row['product_category']} - 訂單：{row['order_id']} ({row['product_name']}) ｜ 狀態：{row['status']}"):
                left_col, right_col = st.columns([1, 1], gap="large")

                with left_col:
                    st.markdown("#### 👤 買家申訴原始資料")
                    target_email = row['customer_email'] if ('customer_email' in row and row['customer_email']) else '未提供'
                    st.write(f"**買家信箱**：`{target_email}`")
                    st.write(f"**商品品類**：{row['product_category']}")
                    st.write(f"**周邊型號**：`{row['product_name']}`")
                    st.write(f"**申訴原因**：{row['customer_reason']}")
                    st.write(f"**申請時間**：`{row['created_at']}`")
                    # 讀取買家佐證圖片 (支援單張與多張選取開啟)
                    img_list = decode_images_from_db(row['image_data'], row.get('images_json', '') if 'images_json' in row else None)
                    if not img_list:
                        st.caption("*(此案例未附佐證圖片)*")
                    elif len(img_list) == 1:
                        try:
                            img = Image.open(io.BytesIO(img_list[0]))
                            st.image(img, caption="買家佐證圖片 (共 1 張)", use_container_width=True)
                        except Exception:
                            st.image(img_list[0], caption="買家佐證圖片 (共 1 張)", use_container_width=True)
                    else:
                        # 照片為一張以上：提供選取開啟照片功能
                        st.markdown(f"**📸 買家佐證照片 (共 {len(img_list)} 張，點選標籤開啟檢視)：**")
                        photo_tabs = st.tabs([f"🖼️ 照片 #{i+1}" for i in range(len(img_list))])
                        for i, tab in enumerate(photo_tabs):
                            with tab:
                                try:
                                    img = Image.open(io.BytesIO(img_list[i]))
                                    st.image(img, caption=f"買家佐證圖片 #{i+1} / 共 {len(img_list)} 張 (點擊可放大)", use_container_width=True)
                                except Exception:
                                    st.image(img_list[i], caption=f"買家佐證圖片 #{i+1} / 共 {len(img_list)} 張", use_container_width=True)
                        
                        with st.expander(f"🔍 一覽全部 {len(img_list)} 張照片縮圖對照"):
                            grid_cols = st.columns(min(len(img_list), 4))
                            for i, b_item in enumerate(img_list):
                                with grid_cols[i % len(grid_cols)]:
                                    try:
                                        st.image(b_item, caption=f"#{i+1}", use_container_width=True)
                                    except Exception:
                                        pass

                with right_col:
                    st.markdown("#### 🤖 AI 周邊瑕疵與風控佐證")
                    st.markdown(f"**風控判定**：{pill_html} (人為損害/爭議指數: **{row['risk_score']} / 100**)", unsafe_allow_html=True)
                    st.markdown(f"**判定結論**：**{row['ai_verdict']}**")
                    st.info(f"**AI 判斷證據與理由**：\n{row['ai_evidence']}")
                    st.success(f"**處置建議**：\n{row['ai_recommendation']}")

                    # 審核操作區 (僅待審核案件可操作)
                    if row['status'] == "待審核":
                        st.markdown("#### ✍️ 店長最終裁決 (點選開啟決策視窗，自訂附言與維修排程)")
                        
                        btn_c1, btn_c2, btn_c3 = st.columns(3)
                        with btn_c1:
                            if st.button("✅ 核准退換 (填寫處置/維修)", key=f"app_{row['id']}", type="primary", use_container_width=True):
                                if dialog_decorator:
                                    open_approve_modal(
                                        case_id=row['id'],
                                        order_id=row['order_id'],
                                        product_name=row['product_name'],
                                        customer_email=target_email,
                                        ai_verdict=row['ai_verdict'],
                                        ai_recommendation=row['ai_recommendation']
                                    )
                                else:
                                    st.session_state["active_approve_id"] = row['id']
                                    st.rerun()
                        with btn_c2:
                            if st.button("⚠️ 要求補件 (指定缺件)", key=f"req_{row['id']}", use_container_width=True):
                                if dialog_decorator:
                                    open_supplement_modal(
                                        case_id=row['id'],
                                        order_id=row['order_id'],
                                        product_name=row['product_name'],
                                        customer_email=target_email,
                                        ai_verdict=row['ai_verdict'],
                                        ai_recommendation=row['ai_recommendation']
                                    )
                                else:
                                    st.session_state["active_supplement_id"] = row['id']
                                    st.rerun()
                        with btn_c3:
                            if st.button("🚫 駁回申請 (填寫理由)", key=f"rej_{row['id']}", use_container_width=True):
                                if dialog_decorator:
                                    open_reject_modal(
                                        case_id=row['id'],
                                        order_id=row['order_id'],
                                        product_name=row['product_name'],
                                        customer_email=target_email,
                                        ai_verdict=row['ai_verdict'],
                                        ai_recommendation=row['ai_recommendation']
                                    )
                                else:
                                    st.session_state["active_reject_id"] = row['id']
                                    st.rerun()

                        # 若環境不支援裝飾器對話框時之頁面內補件表單備援
                        if not dialog_decorator:
                            if st.session_state.get("active_approve_id") == row['id']:
                                st.markdown("---")
                                render_approve_dialog_content(row['id'], row['order_id'], row['product_name'], target_email, row['ai_verdict'], row['ai_recommendation'])
                            elif st.session_state.get("active_supplement_id") == row['id']:
                                st.markdown("---")
                                render_supplement_dialog_content(row['id'], row['order_id'], row['product_name'], target_email, row['ai_verdict'], row['ai_recommendation'])
                            elif st.session_state.get("active_reject_id") == row['id']:
                                st.markdown("---")
                                render_reject_dialog_content(row['id'], row['order_id'], row['product_name'], target_email, row['ai_verdict'], row['ai_recommendation'])

                    else:
                        st.markdown("<div class='manager-review-summary-box'>", unsafe_allow_html=True)
                        st.write(f"**審核結果**：`{row['status']}`")
                        st.write(f"**店家說明**：{row['review_comment'] or '無'}")
                        st.write(f"**完成時間**：`{row['reviewed_at']}`")

                        # 若為已核准案件且有維修排程資訊，顯示資訊摘要
                        r_date = row.get('repair_date', '') or ''
                        r_tech = row.get('technician_id', '') or ''
                        r_stat = row.get('repair_status', '') or ''
                        if row['status'] == "已通過" and (r_date or r_tech or r_stat):
                            st.markdown(f"""
                            <div class="manager-repair-summary-box">
                                <span style="font-weight:700;">🛠️ 原廠維修追蹤資訊</span><br>
                                • 當前維修進度：<strong>{r_stat or '維修中'}</strong><br>
                                • 預計送回日期：<code>{r_date or '未設定'}</code><br>
                                • 維修人員編號：<code>{r_tech or '未指定'}</code>
                            </div>
                            """, unsafe_allow_html=True)

                        st.write(f"**通知紀錄**：已發送判決郵件至 `{target_email}` (寄件者: `{SENDER_EMAIL}`)")
                        st.markdown("</div>", unsafe_allow_html=True)

                        # 若為已核准案件，允許店長隨時自訂更新維修進度與日期
                        if row['status'] == "已通過":
                            with st.expander("🛠️ 店長自訂更新維修進度與送回時程", expanded=False):
                                st.caption("在此修改之維修進度、預計送回日期與工程師編號，將即時同步至買家端查詢頁面。")
                                up_c1, up_c2 = st.columns(2)
                                with up_c1:
                                    cur_rep_date = r_date or (datetime.now() + pd.Timedelta(days=5)).strftime("%Y-%m-%d")
                                    m_rep_date = st.text_input("預計完修送回日期", value=cur_rep_date, key=f"m_date_{row['id']}")
                                with up_c2:
                                    cur_tech_id = r_tech or "TECH-802"
                                    m_tech_id = st.text_input("維修人員工作編號", value=cur_tech_id, key=f"m_tech_{row['id']}")
                                
                                cur_status_opts = [
                                    "［待收件］已核准維修，請買家將瑕疵品包裝寄回",
                                    "［檢測中］收到商品，工程師進行微動/軸體/電氣檢測",
                                    "［更換零件中］已拆機更換原廠零組件",
                                    "［校正完畢］清潔校正與全功能測試正常",
                                    "［已寄出］已交付物流黑貓宅急便，配送送回中",
                                    "［完工結案］買家已簽收完修良品"
                                ]
                                def_idx = 0
                                for i, opt in enumerate(cur_status_opts):
                                    if r_stat and r_stat[:5] in opt:
                                        def_idx = i
                                        break
                                
                                m_rep_status = st.selectbox("維修進度狀態", cur_status_opts, index=def_idx, key=f"m_status_{row['id']}")
                                m_notes = st.text_area("維修詳細進度說明 (買家查詢可見)", value=row.get('review_comment', '') or "", height=80, key=f"m_notes_{row['id']}")

                                if st.button("💾 儲存並同步更新至買家端查詢", type="primary", key=f"m_save_{row['id']}"):
                                    up_conn = sqlite3.connect(DB_FILE)
                                    up_cur = up_conn.cursor()
                                    up_cur.execute("""
                                        UPDATE return_requests 
                                        SET repair_date=?, technician_id=?, repair_status=?, review_comment=? 
                                        WHERE id=?
                                    """, (m_rep_date.strip(), m_tech_id.strip(), m_rep_status, m_notes.strip(), row['id']))
                                    up_conn.commit()
                                    up_conn.close()
                                    st.success("✅ 維修進度已成功更新！買家於前台輸入訂單編號即可即時查得最新狀態。")
                                    st.rerun()

# ==========================================
# 模組三：BI 營運成效儀表板 (限定電腦周邊)
# ==========================================
elif menu == "📊 老闆：BI 營運成效儀表板":
    st.markdown("""
    <div class="tech-hero">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div>
                <div class="hero-title">📊 老闆端：電腦周邊逆物流與客訴 BI 營運儀表板</div>
                <div class="hero-subtitle">
                    呈現導入 <strong>鍵盤/滑鼠/耳機 AI 協同審核</strong> 後之核心商業 KPI、退貨品類佔比與防詐欺成效。
                </div>
            </div>
            <div>
                <span class="badge-item">📈 商業效益量化</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM return_requests", conn)
    conn.close()

    total_cases = len(df)
    approved_rate = round(len(df[df['status'] == '已通過']) / total_cases * 100, 1) if total_cases > 0 else 0
    # 假設傳統人工作業審核平均 15 分鐘，AI 輔助後只需 2.5 分鐘 (節省約 83% 工時)
    hours_saved = round(total_cases * (12.5 / 60), 1)
    # 電腦周邊平均單價以 NT$ 2,800 計算 (鍵盤/高階滑鼠/電競耳機平均行情)
    fraud_blocked_count = len(df[(df['risk_level'] == '紅燈') & (df['status'] == '已駁回')])
    fraud_money_saved = fraud_blocked_count * 2800

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 周邊申請案件數", f"{total_cases} 件")
    col2.metric("🎯 退換貨核准率", f"{approved_rate} %")
    col3.metric("⚡ 累計節省審核工時", f"{hours_saved} 小時", delta="+83% 審核提速")
    col4.metric("💰 攔截潛在損失金額", f"NT$ {fraud_money_saved:,}", delta="高單價防損防線")

    st.markdown("---")

    chart_c1, chart_c2 = st.columns(2)

    with chart_c1:
        st.subheader("📌 案件風險燈號分佈")
        risk_counts = df['risk_level'].value_counts().reset_index()
        risk_counts.columns = ['風險等級', '案件數量']
        if HAS_PLOTLY:
            color_map = {
                "綠燈": "#22c55e",
                "黃燈": "#eab308",
                "紅燈": "#ef4444"
            }
            fig_risk = px.bar(
                risk_counts,
                x='風險等級',
                y='案件數量',
                color='風險等級',
                color_discrete_map=color_map,
                text='案件數量'
            )
            fig_risk.update_layout(
                template='plotly_dark' if is_dark else 'plotly_white',
                plot_bgcolor='rgba(15, 23, 42, 0.75)' if is_dark else '#ffffff',
                paper_bgcolor='rgba(15, 23, 42, 0.75)' if is_dark else '#ffffff',
                margin=dict(l=20, r=20, t=25, b=20),
                showlegend=False,
                font=dict(color="#f1f5f9" if is_dark else "#0f172a", size=13),
                xaxis=dict(gridcolor='rgba(255,255,255,0.06)' if is_dark else 'rgba(0,0,0,0.06)', title=''),
                yaxis=dict(gridcolor='rgba(255,255,255,0.06)' if is_dark else 'rgba(0,0,0,0.06)', title='案件數量')
            )
            fig_risk.update_traces(
                textposition='outside',
                textfont=dict(color='#ffffff' if is_dark else '#0f172a', size=13),
                marker=dict(line=dict(width=1, color='rgba(255,255,255,0.2)' if is_dark else 'rgba(0,0,0,0.1)'))
            )
            st.plotly_chart(fig_risk, use_container_width=True, config={'displayModeBar': False})
        else:
            st.bar_chart(risk_counts.set_index('風險等級'), color="#38bdf8")

    with chart_c2:
        st.subheader("🔍 電腦周邊品類退貨佔比")
        cat_counts = df['product_category'].value_counts().reset_index()
        cat_counts.columns = ['周邊品類', '退貨件數']
        st.dataframe(cat_counts, use_container_width=True, hide_index=True)


# ==========================================
# 模組四：系統設定與 API 串接
# ==========================================
# ==========================================
# 模組：系統註冊帳號與角色權限管理 (管理方專用)
# ==========================================
elif menu == "👥 帳號清單與權限管理":
    st.markdown("""
    <div class="tech-hero">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div>
                <div class="hero-title">👥 系統註冊會員與角色權限管理</div>
                <div class="hero-subtitle">
                    即時檢視 SQLite <code>users</code> 資料表，管理買家與店長之角色權限
                </div>
            </div>
            <div>
                <span class="badge-item">👑 管理方專屬模組</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    all_users = get_all_users()
    total_u = len(all_users)
    admin_u = len([u for u in all_users if u[3] == "admin"])
    buyer_u = total_u - admin_u

    m1, m2, m3 = st.columns(3)
    m1.metric("總註冊帳號數", f"{total_u} 位")
    m2.metric("平台管理員 (店長)", f"{admin_u} 位")
    m3.metric("一般使用者 (買家)", f"{buyer_u} 位")

    st.markdown("---")
    st.subheader("📋 會員名冊總覽")

    user_df = pd.DataFrame(all_users, columns=["ID", "帳號 (Username)", "電子信箱", "角色身分", "註冊時間"])
    user_df["角色身分"] = user_df["角色身分"].apply(lambda r: "👑 管理方 (admin)" if r == "admin" else "👤 使用者 (user)")
    st.dataframe(user_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("⚙️ 帳號權限管理與維護")
    u_col1, u_col2 = st.columns(2)
    with u_col1:
        st.markdown("##### 🔄 變更使用者權限身分")
        user_options = [f"ID:{u[0]} - {u[1]} ({'管理方' if u[3] == 'admin' else '使用者'})" for u in all_users]
        if user_options:
            target_user_str = st.selectbox("選擇目標帳號", user_options, key="role_change_select")
            target_uid = int(target_user_str.split(" - ")[0].replace("ID:", ""))
            new_role_choice = st.selectbox("設定新身份", ["一般使用者 (user)", "平台管理員 (admin)"], key="role_new_sel")
            new_role_val = "admin" if "admin" in new_role_choice else "user"
            if st.button("💾 儲存身分變更", type="primary", key="btn_save_user_role"):
                ok, msg = update_user_role(target_uid, new_role_val)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    with u_col2:
        st.markdown("##### 🗑️ 刪除測試會員帳號")
        deletable_users = [u for u in all_users if u[1] != "admin"]
        if deletable_users:
            del_options = [f"ID:{u[0]} - {u[1]} ({u[2]})" for u in deletable_users]
            del_target_str = st.selectbox("選擇欲刪除之帳號", del_options, key="del_user_select")
            del_uid = int(del_target_str.split(" - ")[0].replace("ID:", ""))
            if st.button("🚨 確認刪除帳號", type="secondary", key="btn_del_user"):
                ok, msg = delete_user(del_uid)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
        else:
            st.caption("※ 目前除了根管理員 (admin) 外尚無其他帳號可刪除。")

elif menu == "⚙️ 系統設定 & API":
    st.markdown("""
    <div class="tech-hero">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div>
                <div class="hero-title">⚙️ 系統設定與真實 AI 模型串接</div>
                <div class="hero-subtitle">
                    支援內建模擬規則引擎與 Google Gemini 多模態視覺模型雙軌切換
                </div>
            </div>
            <div>
                <span class="badge-item">🔌 API 管理</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("系統預設已搭載**電腦周邊智慧展示模擬引擎**（零門檻保證可跑）。若想接入真實 Google Gemini 視覺多模態模型，請在此輸入 API 金鑰。")

    admin_cfg = load_admin_config()
    current_key = st.session_state.get("gemini_api_key", "") or admin_cfg.get("gemini_api_key", "")
    new_key = st.text_input("Google Gemini API Key (選填)", value=current_key, type="password", help="支援 Google AI Studio 免費層金鑰 (例如圖中 ewtw 結尾之 API Key)")
    st.caption("⚡ **模型規格**：系統已全面鎖定並一致通用 Google 官方指定旗艦模型 **`gemini-3.8-flash`**（具備頂級多模態視覺與超低延遲分析能力）。")

    if st.button("💾 儲存 API Key", type="primary"):
        st.session_state["gemini_api_key"] = new_key
        st.session_state["gemini_model_name"] = "gemini-3.8-flash"
        save_admin_config(gemini_api_key=new_key, gemini_model_name="gemini-3.8-flash")
        st.success("API Key 已成功儲存至設定檔！後續風控分析將全面一致調用官方指定旗艦模型【gemini-3.8-flash】。")

    st.markdown("---")
    st.subheader("📧 審核結果郵件發送設定 (Gmail SMTP)")
    st.markdown(f"系統指定之發信寄件者信箱：`{SENDER_EMAIL}`")

    cfg = load_email_config()
    current_pwd = cfg.get("app_password", "")

    with st.expander("ℹ️ 為什麼需要「16 碼應用程式密碼」？（點此查看 Google 帳戶設定教學）", expanded=not bool(current_pwd)):
        st.markdown("""
        **重要說明**：
        Google 為維護帳戶安全性，自 2022 年起已全面停用「低安全性應用程式存取權限」，因此**無法直接使用您的 Google 登入密碼發送郵件**，必須在 Google 帳戶內產生專用的 **16 碼「應用程式密碼」**。

        **⚙️ 取得步驟（僅需設定一次）：**
        1. 登入寄件電子信箱 **`zhuant610@gmail.com`** 的 Google 帳戶。
        2. 前往 [Google 帳戶安全性設定 (myaccount.google.com/security)](https://myaccount.google.com/security)。
        3. 確認「**兩步驟驗證**」狀態為【**已開啟**】（未開啟兩步驟驗證將無法建立應用程式密碼）。
        4. 在頂部搜尋欄輸入「**應用程式密碼**」(App Passwords) 或至安全性頁面點擊進入。
        5. 應用程式名稱輸入「`電腦周邊退換貨小幫手`」，點擊「**建立**」。
        6. 複製彈出視窗中的 **16 碼英文字母**（例如：`abcd efgh ijkl mnop`），貼入下方輸入框並點擊「**儲存郵件設定**」即可！
        """)

    new_pwd = st.text_input(
        "Gmail 應用程式密碼 (App Password)", 
        value=current_pwd, 
        type="password",
        placeholder="例如：abcd efgh ijkl mnop (共16碼英文字母)",
        help="輸入 Google 帳戶安全性中產生的 16 碼專用密碼。儲存後會持久化記錄於本地 email_config.json，重新整理不遺失。"
    )
    if st.button("💾 儲存郵件設定", type="primary"):
        save_email_config(SENDER_EMAIL, new_pwd.strip())
        st.session_state["gmail_app_password"] = new_pwd.strip()
        st.success(f"✅ 郵件設定已成功永久儲存至 `email_config.json`！裁決時將透過 `{SENDER_EMAIL}` 正式發送通知信。")

    st.markdown("##### 📨 測試郵件寄送功能")
    test_c1, test_c2 = st.columns([3, 1])
    with test_c1:
        test_email_target = st.text_input("收件測試電子信箱", value="", placeholder="輸入您想要接收測試信件的信箱 (例如: user@gmail.com)")
    with test_c2:
        st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
        if st.button("🚀 發送測試信件", use_container_width=True):
            if test_email_target and "@" in test_email_target:
                with st.spinner(f"正在連線至 smtp.gmail.com:465 透過 {SENDER_EMAIL} 寄送測試信至 {test_email_target}..."):
                    ok, res_msg = send_decision_email(
                        customer_email=test_email_target.strip(),
                        order_id="ORD-TEST-8888",
                        product_name="客製化機械鍵盤 (系統連線測試件)",
                        status="已通過",
                        review_comment="系統連線與郵件推播功能測試正常，收發無虞！",
                        verdict="測試連線核發",
                        recommendation="此為系統發送測試信，請確認收件夾或垃圾郵件匣"
                    )
                    if ok:
                        st.success(f"{res_msg}")
                    else:
                        st.error(f"{res_msg}")
            else:
                st.warning("⚠️ 請先輸入正確格式的收件測試電子信箱！")

    st.markdown("---")
    st.subheader("🔐 管理員後台密碼管理")
    admin_cfg = load_admin_config()
    current_admin_pwd = admin_cfg.get("admin_password", "admin888")

    st.markdown("設定登入「店長審核台」與「老闆 BI 儀表板」之後台管理密碼（系統預設密碼為 `admin888`）：")
    col_ap1, col_ap2 = st.columns([3, 1])
    with col_ap1:
        new_admin_pwd = st.text_input(
            "修改管理員密碼",
            value=current_admin_pwd,
            type="password",
            help="設定新的管理員密碼。儲存後會持久化記錄於本地 admin_config.json，刷新網頁依然生效。"
        )
    with col_ap2:
        st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
        if st.button("💾 儲存管理員密碼", use_container_width=True, type="primary"):
            if new_admin_pwd.strip():
                save_admin_config(new_admin_pwd.strip())
                st.success("✅ 管理員密碼已成功更新並永久儲存至 `admin_config.json`！")
            else:
                st.warning("⚠️ 管理員密碼不可為空！")

    st.markdown("---")
    st.subheader("🛠️ 資料庫重設與展示資料還原")
    st.caption("點擊下方按鈕將清除目前資料庫，並重新載入精選的「鍵盤、滑鼠、耳機」展示案例。")
    if st.button("重設回電腦周邊示範資料 (Reset DB)"):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        init_db()
        st.success("資料庫已成功重設，並載入精選電腦周邊示範案例！")
        st.rerun()

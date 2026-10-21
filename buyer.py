"""
電腦周邊 (鍵盤·滑鼠·耳機) 買家端售後與退換貨申請門戶
Buyer Portal for Computer Peripheral Returns & Warranty
獨立買家前台：與店長/老闆管理後台完全分離，確保商務機密安全
技術棧：Python + Streamlit + SQLite
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

# ==========================================
# 0. 網頁基本配置與電競科技風視覺樣式 (CSS)
# ==========================================
st.set_page_config(
    page_title="電腦周邊售後客服中心 · 買家申請門戶",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化買家端主題設定 (預設為科技深色，買家可隨時由側邊欄切換為清爽淺色)
# 初始化買家端主題設定 (預設為深色，買家可隨時由側邊欄切換為淺色)
if "buyer_theme_choice" not in st.session_state:
    st.session_state["buyer_theme_choice"] = "🌙 深色"

is_dark = ("深色" in st.session_state.get("buyer_theme_choice", "🌙 深色"))

# ==========================================
# 科技感電競深色主題 CSS (Dark Mode)
# ==========================================
DARK_CSS = """
<style>
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

# 電腦周邊受檢類別清單
PERIPHERAL_CATEGORIES = [
    "⌨️ 機械/薄膜鍵盤",
    "🖱️ 滑鼠",
    "🎧 耳機"
]

# ==========================================
# 1. 資料庫連線與初始化 (SQLite: disputes.db)
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
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
        "images_json TEXT DEFAULT ''"
    ]:
        try:
            c.execute(f"ALTER TABLE return_requests ADD COLUMN {col_def}")
            conn.commit()
        except sqlite3.OperationalError:
            pass

    # 自動同步遷移周邊類別名稱為標準格式
    c.execute("UPDATE return_requests SET product_category = '🎧 耳機' WHERE product_category LIKE '%耳機%'")
    c.execute("UPDATE return_requests SET product_category = '⌨️ 機械/薄膜鍵盤' WHERE product_category LIKE '%鍵盤%' OR product_category LIKE '%平板%'")
    c.execute("UPDATE return_requests SET product_category = '🖱️ 滑鼠' WHERE product_category LIKE '%滑鼠%'")
    conn.commit()
    conn.close()

init_db()

# ==========================================
# 2. 電腦周邊專用 AI 初審分析引擎
# ==========================================
def analyze_return_request(category, product_name, reason, image_file, api_key=""):
    """
    電腦周邊專用瑕疵與風控分析核心：
    - 若有提供 API Key：呼叫 Gemini 多模態視覺模型深度檢測
    - 若無 API Key：啟用電腦周邊專用風控規則引擎
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
            except Exception:
                pass
        except Exception:
            pass

    # 電腦周邊專用模擬引擎
    reason_lower = reason.lower()
    if any(k in reason_lower for k in ["摔", "破", "碎", "斷", "裂", "撞", "泡水", "進水", "飲料", "撬", "拆", "改裝", "狗咬", "拉扯", "焦", "燒"]):
        return (
            "紅燈", 88,
            "周邊外觀重大受損 / 疑似人為暴力損害或私自拆裝",
            "申訴特徵符合高能量外力衝擊、飲料進水受潮或人為改裝破壞（非屬正常鍵軸/微動出廠耗損），高機率為使用不當導致之硬體損毀。",
            "建議【駁回申請】，依保固規範主動提供原廠保固外自費維修或零件更換服務報價"
        )
    elif any(k in reason_lower for k in ["怪怪", "手感", "不習慣", "不順", "不好用", "不喜歡", "沒想像", "音質不如", "鍵程", "延遲", "稍微", "偏重", "偏輕"]):
        return (
            "黃燈", 52,
            "手感或聽感主觀感受爭議 / 瑕疵事證未明",
            "買家描述偏向個人使用習慣適應性或音質主觀偏好，未附具體按鍵測試器截圖、連點測試數據或破音錄音影片，事證尚不齊全。",
            "建議【要求買家補件】：請買家提供特定按鍵/微動/聲道之動態操作測試影片或檢測截圖"
        )
    else:
        return (
            "綠燈", 20,
            "周邊電子元件硬體瑕疵 / 出廠新品不良 (DOA)",
            "描述符合鍵盤軸體觸發不良、滑鼠微動雙擊、滾輪編碼器信號跳動或耳機單元斷路等典型出廠品質問題，無人為外力損壞跡象。",
            "建議【核准全額退款】或安排換發新品（電腦周邊小件可評估免寄回以節省逆物流運費）"
        )

# ==========================================
# 3. 買家端專屬側邊欄導航 (無任何後台管理連結)
# ==========================================
# 側邊欄最頂部：深色/淺色主題風格即時切換
st.sidebar.radio(
    "深色/淺色",
    ["🌙 深色", "☀️ 淺色"],
    key="buyer_theme_choice",
    horizontal=True
)
st.sidebar.markdown("---")

st.sidebar.markdown("""
<div class="sidebar-header-box">
    <div class="sidebar-title">🛍️ 周邊售後客服中心</div>
    <div class="sidebar-subtitle">● 買家退換貨服務門戶 (Buyer Portal)</div>
</div>
""", unsafe_allow_html=True)

buyer_menu = st.sidebar.radio(
    "📌 買家服務選單",
    [
        "📝 提交退換貨申請",
        "🔍 查詢申請進度 / 補充照片"
    ]
)

st.sidebar.info("""
**🎯 受理電腦周邊範圍：**
- ⌨️ **機械/薄膜鍵盤** (軸體/鍵位/PCB)
- 🖱️ **滑鼠** (微動/編碼器/感應器)
- 🎧 **耳機** (單元/頭樑/收音)

**📋 買家售後須知：**
1. 購買 7 日內商品享新品不良免費換新/退款服務。
2. 申請時【必須上傳瑕疵佐證照片】，未附照片恕無法受理申請。
3. 請務必填寫正確的電子信箱，審核判決將自動寄發通知信。
4. 若收到「要求補件」通知，可隨時至「查詢進度」補傳照片。
""")

st.sidebar.caption("📧 售後服務信箱：zhuant610@gmail.com")

# ==========================================
# 頁面一：提交退換貨申請
# ==========================================
if buyer_menu == "📝 提交退換貨申請":
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
    if "standalone_buyer_photos" not in st.session_state:
        st.session_state["standalone_buyer_photos"] = []

    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        st.markdown("#### 📝 填寫申訴資訊")
        order_id = st.text_input("訂單編號", value=f"ORD-PERI-{datetime.now().strftime('%m%d%H%M')}")
        customer_email = st.text_input("買家電子信箱 (Email) *必填，接收審核判決通知", placeholder="例如：buyer@example.com")
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
            cam_photo = st.camera_input("點擊按鈕開啟相機拍照", key="standalone_cam_input")
            if cam_photo is not None:
                cam_bytes = cam_photo.getvalue()
                existing_bytes = [p["bytes"] for p in st.session_state["standalone_buyer_photos"]]
                if cam_bytes not in existing_bytes:
                    p_name = f"相機拍攝 #{len(st.session_state['standalone_buyer_photos']) + 1}"
                    st.session_state["standalone_buyer_photos"].append({"name": p_name, "bytes": cam_bytes})
                    st.success(f"✅ 已成功將【{p_name}】加入佐證相簿！若需拍攝其他角度可繼續拍照。")

        with photo_tabs[1]:
            file_photos = st.file_uploader(
                "選取相片或損壞照片檔案 (可複選多張檔案)",
                type=["jpg", "jpeg", "png", "webp", "bmp", "heic", "JPG", "JPEG", "PNG", "WEBP", "HEIC"],
                accept_multiple_files=True,
                key="standalone_file_photos",
                help="可一次選取多張照片，支援 JPG, PNG, WEBP, HEIC 等常見格式"
            )
            if file_photos:
                existing_bytes = [p["bytes"] for p in st.session_state["standalone_buyer_photos"]]
                added_num = 0
                for f in file_photos:
                    b = f.getvalue()
                    if b not in existing_bytes:
                        st.session_state["standalone_buyer_photos"].append({"name": f.name, "bytes": b})
                        existing_bytes.append(b)
                        added_num += 1
                if added_num > 0:
                    st.success(f"✅ 已成功將 {added_num} 張照片載入佐證相簿！")

        # ==========================================
        # 🖼️ 照片管理與送出前修改區 (在送出申請前能修改照片)
        # ==========================================
        cur_photos = st.session_state["standalone_buyer_photos"]
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
                    if st.button(f"🗑️ 移除此照片 (#{p_idx + 1})", key=f"del_standalone_photo_{p_idx}", type="secondary"):
                        del_target_idx = p_idx
                st.markdown("<hr style='margin:4px 0 8px 0; border:none; border-top:1px dashed #64748b;'>", unsafe_allow_html=True)

            if del_target_idx is not None:
                st.session_state["standalone_buyer_photos"].pop(del_target_idx)
                st.rerun()

            if len(cur_photos) > 1:
                if st.button("🗑️ 全部清空重新選取", key="clear_all_standalone_photos"):
                    st.session_state["standalone_buyer_photos"] = []
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    submit_btn = st.button("🚀 送出退貨申請 (立即完成初審登記)", type="primary", use_container_width=True)

    if submit_btn:
        if not order_id or not customer_email or not product_name or not reason:
            st.error("請完整填寫訂單編號、買家電子信箱、周邊名稱與瑕疵說明！")
        elif "@" not in customer_email or "." not in customer_email:
            st.error("請填寫正確有效的買家電子信箱格式（例如：user@example.com）！")
        elif not st.session_state.get("standalone_buyer_photos", []):
            st.error("❌ 申請失敗：為加速出廠保固核銷，系統規定【必須上傳至少一張瑕疵佐證照片】否則不給予受理申請！請使用相機或上方按鈕選取照片後再送出。")
        else:
            with st.spinner("🤖 正在為您提交退貨申訴資料並進行初步建檔..."):
                all_img_bytes = [p["bytes"] for p in st.session_state["standalone_buyer_photos"]]
                primary_blob, images_json_str = encode_images_to_db(all_img_bytes)
                
                # 讀取本地設定之 Gemini API Key (若店家已在後台設定)
                buyer_api_key = ""
                cfg_path = os.path.join(BASE_DIR, "admin_config.json")
                if os.path.exists(cfg_path):
                    try:
                        with open(cfg_path, "r", encoding="utf-8") as f:
                            buyer_api_key = json.load(f).get("gemini_api_key", "")
                    except Exception:
                        pass

                # 執行電腦周邊 AI 風控初審 (傳入所有照片)
                risk_lvl, risk_score, verdict, evidence, rec = analyze_return_request(
                    category, product_name, reason, all_img_bytes, api_key=buyer_api_key
                )

                # 寫入 SQLite (disputes.db)
                try:
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    c.execute("""
                        INSERT INTO return_requests 
                        (order_id, customer_email, product_category, product_name, customer_reason, image_data, images_json, status, risk_level, risk_score, ai_verdict, ai_evidence, ai_recommendation, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, '待審核', ?, ?, ?, ?, ?, ?)
                    """, (order_id, customer_email.strip(), category, product_name, reason, primary_blob, images_json_str, risk_lvl, risk_score, verdict, evidence, rec, now_str))
                    conn.commit()
                    conn.close()

                    # 清空暫存相簿
                    st.session_state["standalone_buyer_photos"] = []

                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📦 買家獨立門戶成功提交案件：{order_id} ({product_name}) -> 資料庫: {DB_FILE}")
                    st.success(f"🎉 退換貨申請已成功提交！您的案件編號為 **`{order_id}`**。")
                    st.info(f"📧 審核結果將寄發至您的電子信箱：**`{customer_email.strip()}`**。您亦可隨時在左側「🔍 查詢進度 / 補充照片」輸入訂單編號追蹤審核狀態。")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ 申訴資料寫入資料庫失敗：{str(e)}。請聯繫系統管理員確認後台連線。")

# ==========================================
# 頁面二：查詢申請進度 / 補充照片
# ==========================================
elif buyer_menu == "🔍 查詢申請進度 / 補充照片":
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
                # 狀態標籤樣式
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

                    # 顯示買家已提交之佐證照片 (支援多張切換檢視)
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
                        supp_key = f"standalone_supp_photos_{item['id']}"
                        if supp_key not in st.session_state:
                            st.session_state[supp_key] = []

                        supp_tabs = st.tabs(["📷 手機相機直接拍照", "📁 從相簿/檔案選取 (支援多張)"])
                        with supp_tabs[0]:
                            supp_cam = st.camera_input("開啟相機拍照補件", key=f"standalone_supp_cam_{item['id']}")
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
                                key=f"standalone_supp_file_{item['id']}"
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
                                    if st.button(f"🗑️ 移除此補件照片 (#{s_i+1})", key=f"del_standalone_supp_{item['id']}_{s_i}"):
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
                            st.success(f"🎉 **退換貨已核准**！\n\n客服備註：{item['review_comment'] or '已通過出廠保固瑕疵核銷，請留意物流或退款通知。'}")
                    
                    elif cur_status == "已駁回":
                        st.error(f"🚫 **退貨申請未通過**\n\n駁回原因說明：{item['review_comment'] or '經檢驗非屬出廠保固範圍。'}")
                    
                    st.markdown("<hr style='border-color:rgba(255,255,255,0.08);'>", unsafe_allow_html=True)

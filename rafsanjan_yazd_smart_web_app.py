import streamlit as st
import pandas as pd
import numpy as np
import io
import os
import base64
import urllib.request
import urllib.parse
import json
import time

# Try to import Google Text-to-Speech library
try:
    from gtts import gTTS
    gtts_available = True
except ImportError:
    gtts_available = False

# ----------------- streamlit set config -----------------
st.set_page_config(
    page_title="دستیار فوق‌هوشمند رُز | ROSE AI v9",
    page_icon="🌹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- STATE MANAGER & THEME CONFIG -----------------
if "theme" not in st.session_state:
    st.session_state.theme = "ساینبرپانک نئون (Cyberpunk Cyan-Magenta)"

if "rose_voice_speed" not in st.session_state:
    st.session_state.rose_voice_speed = 1.0

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Theme Definitions
THEME_STYLES = {
    "ساینبرپانک نئون (Cyberpunk Cyan-Magenta)": {
        "bg": "#08090f",
        "card_bg": "rgba(255, 255, 255, 0.03)",
        "card_border": "rgba(0, 240, 255, 0.2)",
        "text": "#e2e8f0",
        "primary": "#00f0ff",
        "secondary": "#ff007f",
        "accent": "#ff007f",
        "glow": "0 0 15px rgba(0, 240, 255, 0.4)",
        "sidebar_bg": "#0c0e17"
    },
    "طلایی کلاسیک نفتی (Classic Petroleum Navy-Gold)": {
        "bg": "#0f172a",
        "card_bg": "rgba(30, 41, 59, 0.7)",
        "card_border": "rgba(234, 179, 8, 0.2)",
        "text": "#f1f5f9",
        "primary": "#eab308",
        "secondary": "#38bdf8",
        "accent": "#ea580c",
        "glow": "0 0 15px rgba(234, 179, 8, 0.3)",
        "sidebar_bg": "#1e293b"
    },
    "سبز ایمنی محیط‌زیست (HSE Emerald & Slate)": {
        "bg": "#061f17",
        "card_bg": "rgba(16, 185, 129, 0.05)",
        "card_border": "rgba(16, 185, 129, 0.25)",
        "text": "#ecfdf5",
        "primary": "#10b981",
        "secondary": "#a7f3d0",
        "accent": "#3b82f6",
        "glow": "0 0 15px rgba(16, 185, 129, 0.3)",
        "sidebar_bg": "#041610"
    },
    "رویال بلک لوکس (Royal Black & Amethyst)": {
        "bg": "#09050f",
        "card_bg": "rgba(139, 92, 246, 0.04)",
        "card_border": "rgba(139, 92, 246, 0.2)",
        "text": "#f5f3ff",
        "primary": "#a78bfa",
        "secondary": "#ec4899",
        "accent": "#8b5cf6",
        "glow": "0 0 15px rgba(139, 92, 246, 0.4)",
        "sidebar_bg": "#11071c"
    }
}

active_theme = THEME_STYLES[st.session_state.theme]

# ----------------- RESPONSIVE CSS INJECTION -----------------
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
        background-color: {active_theme['bg']} !important;
        color: {active_theme['text']} !important;
        font-family: 'Vazirmatn', sans-serif !important;
        direction: RTL !important;
        text-align: right !important;
    }}
    
    .stApp {{
        direction: RTL !important;
        text-align: right !important;
    }}
    
    h1, h2, h3, h4, h5, h6 {{
        color: {active_theme['primary']} !important;
        font-family: 'Vazirmatn', sans-serif !important;
        text-shadow: {active_theme['glow']};
    }}
    
    /* Responsive title styling */
    .main-title {{
        color: {active_theme['primary']} !important;
        text-align: center;
        font-size: calc(1.5rem + 1vw);
        font-weight: bold;
        margin-top: 10px;
        margin-bottom: 5px;
        text-shadow: {active_theme['glow']};
    }}
    
    .sub-title {{
        color: {active_theme['secondary']};
        text-align: center;
        font-size: calc(0.8rem + 0.4vw);
        margin-bottom: 25px;
    }}
    
    /* 3D Glassmorphism Glowing Responsive Avatar */
    .avatar-container {{
        text-align: center;
        padding: 15px;
        position: relative;
        display: flex;
        justify-content: center;
        align-items: center;
    }}
    
    .avatar-glow {{
        position: absolute;
        width: 160px;
        height: 160px;
        border-radius: 50%;
        background: radial-gradient(circle, {active_theme['primary']}33 0%, {active_theme['secondary']}11 70%, transparent 100%);
        animation: pulse-glow 3s infinite ease-in-out;
    }}
    
    .live-avatar {{
        position: relative;
        border-radius: 50%;
        border: 3px solid {active_theme['primary']};
        box-shadow: 0 0 20px {active_theme['primary']}55;
        animation: breathing 4s infinite ease-in-out;
        transition: transform 0.3s ease-in-out, border-color 0.3s;
        width: 130px;
        height: 130px;
        object-fit: cover;
        z-index: 2;
    }}
    
    .live-avatar:hover {{
        transform: scale(1.08) rotate(3deg);
        border-color: {active_theme['secondary']};
        box-shadow: 0 0 30px {active_theme['secondary']}aa;
    }}
    
    @keyframes breathing {{
        0% {{ transform: scale(1); }}
        50% {{ transform: scale(1.03) translateY(-3px); }}
        100% {{ transform: scale(1); }}
    }}
    
    @keyframes pulse-glow {{
        0% {{ transform: scale(0.9); opacity: 0.6; }}
        50% {{ transform: scale(1.15); opacity: 0.9; }}
        100% {{ transform: scale(0.9); opacity: 0.6; }}
    }}
    
    /* Cyber Glassmorphic KPI Cards */
    .kpi-card-custom {{
        background: {active_theme['card_bg']};
        border: 1px solid {active_theme['card_border']};
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(5px);
        transition: all 0.3s;
        margin-bottom: 12px;
    }}
    
    .kpi-card-custom:hover {{
        border-color: {active_theme['primary']};
        box-shadow: 0 0 15px {active_theme['primary']}44;
        transform: translateY(-2px);
    }}
    
    /* Chat Bubbles Styling */
    .chat-bubble-user {{
        background-color: rgba(255, 255, 255, 0.04);
        border-right: 5px solid {active_theme['secondary']};
        border-left: 1px solid rgba(255, 255, 255, 0.08);
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 12px;
        text-align: right;
        direction: RTL;
        color: #e2e8f0;
    }}
    
    .chat-bubble-rose {{
        background-color: rgba(0, 240, 255, 0.03);
        border-right: 5px solid {active_theme['primary']};
        border-left: 1px solid rgba(0, 240, 255, 0.1);
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 12px;
        text-align: right;
        direction: RTL;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.05);
        color: #f1f5f9;
    }}
    
    /* Equalizer Waveform Animation */
    .equalizer {{
        display: flex;
        justify-content: center;
        align-items: flex-end;
        height: 25px;
        gap: 3px;
        margin-top: 10px;
    }}
    .bar {{
        width: 3px;
        background-color: {active_theme['primary']};
        animation: bounce 0.8s ease-in-out infinite alternate;
        border-radius: 2px;
    }}
    .bar:nth-child(2) {{ animation-delay: 0.1s; height: 15px; }}
    .bar:nth-child(3) {{ animation-delay: 0.25s; height: 23px; }}
    .bar:nth-child(4) {{ animation-delay: 0.05s; height: 8px; }}
    .bar:nth-child(5) {{ animation-delay: 0.15s; height: 19px; }}
    
    @keyframes bounce {{
        10% {{ height: 4px; }}
        100% {{ height: 24px; }}
    }}
    
    /* Interactive custom styles for Streamlit components */
    div[data-testid="stSidebar"] {{
        background-color: {active_theme['sidebar_bg']} !important;
        border-left: 1px solid {active_theme['card_border']} !important;
    }}
    
    /* Responsive Media Queries for Mobile phones */
    @media (max-width: 768px) {{
        .main-title {{
            font-size: 1.3rem !important;
        }}
        .sub-title {{
            font-size: 0.8rem !important;
        }}
        .live-avatar {{
            width: 100px !important;
            height: 100px !important;
        }}
        .avatar-glow {{
            width: 125px !important;
            height: 125px !important;
        }}
        .kpi-card-custom {{
            padding: 10px !important;
        }}
        div[data-testid="column"] {{
            margin-bottom: 10px !important;
            width: 100% !important;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------- load avatar base64 -----------------
avatar_base64 = ""
avatar_path = "rose_assistant_avatar.png"
paths_to_avatar = [avatar_path, "artifacts/rose_assistant_avatar.png", "/workspace/artifacts/rose_assistant_avatar.png"]
for p in paths_to_avatar:
    if os.path.exists(p):
        try:
            with open(p, "rb") as image_file:
                avatar_base64 = base64.b64encode(image_file.read()).decode()
                break
        except:
            pass

# ----------------- load material database -----------------
@st.cache_data
def load_data():
    excel_filename = "epc_comprehensive_valuation_v8.xlsx"
    paths_to_excel = [
        excel_filename,
        "artifacts/" + excel_filename,
        "/workspace/artifacts/" + excel_filename
    ]
    df = None
    for p in paths_to_excel:
        if os.path.exists(p):
            try:
                # Read all sheets dynamically and merge
                xls = pd.ExcelFile(p)
                sheets = xls.sheet_names
                dfs = []
                disp_mapping = {
                    "Piping": "Piping & Valves",
                    "Mechanical": "Mechanical Equipment",
                    "Electrical": "Electrical Equipment",
                    "Instrumentation": "Instrumentation & Telecom",
                    "Cathodic": "Cathodic Protection",
                    "Safety": "Safety & Fire Fighting",
                    "Spare": "Spare Parts"
                }
                for sh in sheets:
                    for k, val in disp_mapping.items():
                        if k.lower() in sh.lower():
                            temp_df = pd.read_excel(p, sheet_name=sh)
                            temp_df.columns = [str(c).strip() for c in temp_df.columns]
                            if 'item_name' in temp_df.columns or 'عنوان' in temp_df.columns:
                                temp_df['discipline'] = val
                                dfs.append(temp_df)
                if dfs:
                    df = pd.concat(dfs, ignore_index=True)
                    # Normalize columns
                    if 'rial_cost' not in df.columns and 'Total Rial' in df.columns:
                        df['rial_cost'] = df['Total Rial']
                    if 'euro_cost' not in df.columns and 'Total Euro' in df.columns:
                        df['euro_cost'] = df['Total Euro']
                    if 'item_name' not in df.columns and 'عنوان' in df.columns:
                        df['item_name'] = df['عنوان']
                    if 'specs' not in df.columns and 'Description' in df.columns:
                        df['specs'] = df['Description']
                    break
            except:
                pass
                
    if df is None:
        # Pre-loaded highly comprehensive bilingual fallback database (V9 master material dataset)
        data = {
            'discipline_en': [
                'Piping & Valves', 'Piping & Valves', 'Piping & Valves', 'Piping & Valves', 'Piping & Valves', 'Piping & Valves', 'Piping & Valves',
                'Mechanical Equipment', 'Mechanical Equipment', 'Mechanical Equipment', 'Mechanical Equipment', 'Mechanical Equipment', 'Mechanical Equipment', 'Mechanical Equipment', 'Mechanical Equipment',
                'Electrical Equipment', 'Electrical Equipment', 'Electrical Equipment', 'Electrical Equipment', 'Electrical Equipment', 'Electrical Equipment',
                'Instrumentation & Telecom', 'Instrumentation & Telecom', 'Instrumentation & Telecom', 'Instrumentation & Telecom', 'Instrumentation & Telecom', 'Instrumentation & Telecom',
                'Cathodic Protection', 'Cathodic Protection', 'Cathodic Protection', 'Cathodic Protection',
                'Safety & Fire Fighting', 'Safety & Fire Fighting', 'Safety & Fire Fighting',
                'Spare Parts', 'Spare Parts', 'Spare Parts'
            ],
            'discipline_fa': [
                'لوله‌کشی و شیرآلات', 'لوله‌کشی و شیرآلات', 'لوله‌کشی و شیرآلات', 'لوله‌کشی و شیرآلات', 'لوله‌کشی و شیرآلات', 'لوله‌کشی و شیرآلات', 'لوله‌کشی و شیرآلات',
                'تجهیزات مکانیکال', 'تجهیزات مکانیکال', 'تجهیزات مکانیکال', 'تجهیزات مکانیکال', 'تجهیزات مکانیکال', 'تجهیزات مکانیکال', 'تجهیزات مکانیکال', 'تجهیزات مکانیکال',
                'تجهیزات برقی', 'تجهیزات برقی', 'تجهیزات برقی', 'تجهیزات برقی', 'تجهیزات برقی', 'تجهیزات برقی',
                'ابزار دقیق و مخابرات', 'ابزار دقیق و مخابرات', 'ابزار دقیق و مخابرات', 'ابزار دقیق و مخابرات', 'ابزار دقیق و مخابرات', 'ابزار دقیق و مخابرات',
                'حفاظت کاتدیک', 'حفاظت کاتدیک', 'حفاظت کاتدیک', 'حفاظت کاتدیک',
                'ایمنی و آتش‌نشانی', 'ایمنی و آتش‌نشانی', 'ایمنی و آتش‌نشانی',
                'لوازم یدکی', 'لوازم یدکی', 'لوازم یدکی'
            ],
            'item_name_en': [
                'Pipes (5,260 M)', 'Gate Valves (6" to 16")', 'Check Valves (6" to 28")', 'Ball Valves (6" to 28")', 'Chock Valves (8")', 'Globe Valves (14")', 'Expansion Joints',
                'Main Transfer Pumps ( برقی)', 'Main Transfer Pumps ( دیزلی)', 'Main Booster Pumps (BP-451/551)', 'Pig Launcher & Receiver Traps', 'Corrosion Inhibitor Packages', 'Process Tanks (Buried)', 'Main Strainers', 'Hot Bends (16" 45 Deg)',
                'Medium Voltage Cables', 'Low Voltage Cables', 'Power Transformers', 'MV/LV Switchgears', 'UPS & Battery Chargers', 'Diesel Emergency Generator',
                'F&G / Control Systems', 'Motor Actuated Valves (MOV)', 'Ultrasonic Flow Meters', 'Transmitters & Indicators', 'Relief, Control & Gate Valves', 'Fiber Optic Cable Route',
                'Transformer Rectifiers', 'CP Anodes (MMO, HSCI, Mg, Zn)', 'Petroleum Coke Breeze Backfill', 'Zinc Earthing Cells & Electrodes',
                'Water Hydrants & Monitors', 'Fire Extinguishers (CO2 & Powder)', 'Gaseous Total Flooding Systems',
                'Rafsanjan Station Two-Year Spares', 'Yazd Station Two-Year Spares', 'Pipeline Valves Spares'
            ],
            'item_name_fa': [
                'لوله‌های فشار قوی (۵,۲۶۰ متر)', 'شیرهای دروازه‌ای Gate Valves', 'شیرهای خودکار Check Valves', 'شیرهای توپی Ball Valves', 'شیرهای چوک Chock Valves', 'شیرهای کروی Globe Valves', 'لرزه‌گیرهای آکاردئونی تفصیلی',
                'الکتروپمپ‌های اصلی انتقال فرآورده (برقی)', 'پمپ دیزلی اصلی اضطراری MP-554', 'بوستر پمپ‌های تلمبه‌خانه BP-451/551', 'تله‌های ارسال و دریافت پیگ (پیگ‌تله)', 'پکیج تزریق ماده ضد خوردگی کوئیک ريلیز', 'مخازن فرآیندی تحت فشار دفنی', 'صافی‌های اصلی تلمبه‌خانه (استرینرها)', 'خم‌های گرم خط لوله (هات‌بندها)',
                'کابل‌های فشار متوسط (۲۰ کیلوولت سربی زره‌دار)', 'کابل‌های فشار ضعیف مسی سربی زره‌دار', 'ترانسفورماتورهای فوق پرقدرت و توزیع', 'تابلوهای خلاء و توزیع برق MV/LV', 'سیستم‌های یوپیاس و شارژر با باتری بانک', 'دیزل ژنراتور اضطراری ۳۰۰kVA تلمبه‌خانه یزد',
                'سامانه‌های هوشمند اعلان حریق و کنترل PLC', 'شیرهای موتوردار مجهز به اکچویتور برقی MOV', 'فلومترهای صنعتی اولتراسونیک چندکاناله', 'ترانسمیترها، حسگرها و فرستنده‌های مانیتورینگ', 'شیرآلات ایمنی، کنترل دبی و کروی هیدرولیکی', 'کابل فیبر نوری زره‌دار زنگ‌زده خط لوله مسیر انتقال',
                'ترانسفورمر رکتیفایرهای کاتدی هوشمند روغنی', 'آندهای فله حفاظت کاتدیک MMO و چدن پرسیلیس', 'مواد پشتبند کک نفتی کربن بالای ۹۰ درصد', 'سلول‌های ارت روی و الکترودهای مرجع کاتدی',
                'هیدرانت‌ها و مانیتورهای توزیع آب آتش‌نشانی', 'کپسول‌های دستی ۱۲ کیلوگرمی پودری و گاز کربنیک چرخ‌دار سنگین', 'پکیج خودکار تخلیه گاز سیلابی خفه‌کننده در اتاق‌های برق و کنترل',
                'پکیج قطعات یدکی دو ساله تلمبه‌خانه رفسنجان', 'پکیج قطعات یدکی دو ساله تلمبه‌خانه یزد', 'لوازم یدکی شیرآلات سنگین بین‌راهی خط لوله'
            ],
            'quantity': [5260, 23, 41, 30, 4, 1, 6, 6, 1, 12, 2, 2, 3, 8, 12, 12360, 3270, 9, 8, 4, 1, 4, 54, 8, 167, 57, 4000, 5, 820, 13500, 2, 12, 38, 2, 1, 1, 1],
            'unit': ['M', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'SET', 'SET', 'NO', 'NO', 'NO', 'M', 'M', 'NO', 'SET', 'SET', 'NO', 'SET', 'NO', 'SET', 'NO', 'NO', 'M', 'NO', 'NO', 'Kg', 'NO', 'SET', 'NO', 'SET', 'PKG', 'PKG', 'PKG'],
            'rial_cost': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 37600000000, 0, 0, 4910871962000, 1432551541000, 271200, 113240, 42000, 12000, 2400000000, 26740000000, 0, 0, 0, 212e6, 19940000000, 2180000, 520000, 110000, 12000, 10000, 48000, 145000, 145000, 23000],
            'euro_cost': [753296.0, 127853.43, 188213.04, 290207.68, 10858.55, 19896.18, 99.0, 30000.0, 40000.0, 214520.0, 13900.0, 85000.0, 156000.0, 54200.0, 18500.0, 18593925.0, 47751847.0, 13700.0, 59710.0, 42000.0, 12000.0, 240000.0, 4776150.0, 75000.0, 12000.0, 2400.0, 580000.0, 19940.0, 48000.0, 820.0, 110.0, 2150.0, 120.0, 48.0, 145000.0, 145000.0, 23000.0],
            'specs_en': ['HFW Welded, API 5L Gr. B/X52/X60, High-pressure steel lines', 'ASME B16.34, Flanged, Class 150/600/900, ASTM A216 WCB', 'ASME B16.34, Swing Type, Class 150/600/900/1500', 'Class 150/600/900/1500, Trunnion/Reduced Bore', 'Class 150/900/1500, Flanged RF/RTJ', 'Class 1500, Flanged RTJ, Swivel Plug Disc', 'Spool Type, NBR Synthetic Rubber with Canvas', 'High pressure Process Pumps', 'Emergency auxiliary diesel pump', 'BP-451 A/B/C (Rafsanjan) & BP-551 A/B/C (Yazd), Q=838m3/h & 633m3/h', 'Pig Receiver Trap S-551 / S-432, Class 900#, API 5L X60', 'PK-451 (Rafsanjan) and PK-551 (Yazd)', 'Horizontal under/aboveground process and drain tanks', 'Process inline strainers, Class 600# and 900#', 'Route hot bends 16-inch 5D/7D curvature API 5L X60', 'Copper armored lead covered SWA (Lead Cover / SWA) 12/20kV', 'Low voltage copper armored cables with PVC bedding', 'Power Transformers (12500kVA 20/6.3kV and 300/50kVA)', 'MV Switchgears vacuum breakers 20kV & LV Switchgears 400V', 'UPS 230VAC 20kVA and Battery Chargers 110VDC 5kW', 'Diesel generator 300kVA output 400V with ATS (Yazd)', 'Main control panel PLC / ESD & F&G redundant network', '400VAC explosion proof Eexd IP65, sizes 4" to 28" Class 150-1500', 'Inline ultrasonic flow meters with multi-path technology', 'Pressure/temperature transmitters and switches with manifolds', 'Flow control/regulation and safety thermal relief valves', '16-Core single-mode armored optic cable with OCDF & closures', 'Smart automated oil-cooled TR units 50V/25A and 50V/50A', 'MMO wire, HSCI rods, high potential Mg & Zn anodes', 'High carbon petroleum coke backfill IPS-M-TP-750', 'Zinc grounding cells with XLPE copper cables & reference electrodes', 'Fire hydrants, monitors and wet-barrel valves', 'CO2 extinguishers (6/30kg) and Dry Powder (12/75kg)', 'Inert gas gaseous fire suppression systems', 'Spares for pumps, valves and instrumentation (Rafsanjan)', 'Spares for pumps, valves and instrumentation (Yazd)', 'Pipeline valves, actuators and hydraulic spares package'
            ],
            'specs_fa': ['لوله‌های فولادی بدون درز گرید X60 خط اصلی رفسنجان-یزد', 'استاندارد ASME B16.34، فلنج‌دار، کلاس ۱۵۰/۶۰۰/۹۰۰، بدنه فولادی ASTM A216 WCB', 'استاندارد ASME B16.34، نوع یکطرفه لولایی (Swing Type)، کلاس ۱۵۰ تا ۱۵۰۰', 'کلاس ۱۵۰/۶۰۰/۹۰۰/۱۵۰۰، ترانیون ساید، مجرای کاهنده (Reduced Bore) بدنه WCB', 'شیر چوک کلاس ۱۵۰/۹۰۰/۱۵۰۰، نوع فلنج برجسته و RTJ', 'شیر کروی کلاس ۱۵۰۰، فلنج RTJ، نوع دیسک پلاگ گردان، بدنه فولادی', 'نوع اسپول تایپ، ساخته شده از لاستیک مصنوعی NBR تقویت‌شده با بوم برزنتی و لایه‌های سیمی', 'پمپ‌های گریز از مرکز اصلی فرآیندی انتقال مواد نفتی', 'پمپ دیزلی و متعلقات تلمبه‌خانه', 'بوستر پمپ‌های تلمبه‌خانه رفسنجان و یزد، دبی‌های ۸۳۸ و ۶۳۳ مترمکعب بر ساعت', 'تله ارسال/دریافت پیگ ۱۶ اینچ در کلاس ۹۰۰ با استاندارد طراحی API 5L', 'پکیج تزریق ضد خوردگی رفسنجان و یزد', 'مخازن ذخیره مواد و تخلیه دفنی ۲۰ و ۳۰ مترمکعبی', 'صافی‌های اصلی با توری استیل کلاس۶۰۰ و ۹۰۰ تلمبه‌خانه‌ها', 'خم‌های با زاویه خمش ۴۵ درجه گرید X60 خط لوله ۱۶ اینچ', 'کابل‌های مسی سربی زره‌دار فشار متوسط رده ۱۲/۲۰ کیلوولت مسی', 'کابل‌های توزیع برق فشار ضعیف مسی زره‌دار', 'ترانسفورماتور قدرت فوق پرقدرت ۱۲۵۰۰ کیلوولت آمپر و ترانسفورمرهای توزیع', 'تابلوهای برق فشار متوسط مجهز به دژکتور خلاء و تابلوهای فشار ضعیف تلمبه‌خانه‌ها', 'شارژر هوشمند باتری ۱۱۰ ولتی مجهز به مدار موازی', 'دیزل ژنراتور اضطراری کمکی به همراه تابلو سنکرون اتوماتیک', 'سیستم پردازش متمرکز اعلان حریق ریداندنت و کنترلر PLC', 'شیرهای توپی ابزار دقیق موتوردار برقی موو ۴۰۰VAC ضدانفجار', 'مسیر اندازه‌گیری اولتراسونیک فلومتر با رایانه جریان (Flow Computer)', 'سنسورهای فشار قوی Eexd و تجهیزات اندازه‌گیری دما و مانیفولدها', 'شیر برقی کنترل دبی جریانی و شیرهای اطمینان حرارتی خط لوله', 'کابل سینگل مود زره‌دار فیبر نوری ۱۶ کور در طول خط لوله رفسنجان-یزد', 'رکتیفایرهای هوشمند خودکار روغن‌خنک ۵۰ ولت حفاظت کاتدی ایستگاه‌ها', 'آندهای سیمی اکسید فلزی مخلوط (MMO) و چدنی به همراه آندهای فداشونده منیزیمی', 'پشت‌بند کک کلوخه پتروشیمی با درصد کربن بالای ۹۰ درصد', 'سلول‌های زمین حفاظتی و الکترودهای مرجع مس-سولفات کاتدیک', 'جعبه شلنگ‌های آتش‌نشانی ایستگاه‌ها، هیدرانت‌ها و مانیتورها', 'کپسول‌های دستی ۱۲ کیلوگرمی پودری و گاز کربنیک چرخ‌دار سنگین', 'پکیج خودکار تخلیه گاز سیلابی خفه‌کننده در اتاق‌های برق و کنترل', 'قطعات یدکی پمپ‌ها و تجهیزات ابزار دقیق و برقی مصرفی پیش‌راه‌اندازی ایستگاه رفسنجان', 'لوازم یدکی قطعات گردان مکانیکی و ابزار دقیق دو ساله بهره‌برداری مداوم ایستگاه یزد', 'قطعات مصرفی و لوازم یدکی شیرآلات سنگین بین‌راهی خط لوله ۱۶ اینچ'
            ]
        }
        df = pd.DataFrame(data)
        
    # Standardize column naming for seamless bilingual support
    if 'item_name_fa' not in df.columns:
        df['item_name_en'] = df['item_name'] if 'item_name' in df.columns else "Sample Item"
        df['item_name_fa'] = df['item_name'] if 'item_name' in df.columns else "کالای نمونه"
    if 'discipline_fa' not in df.columns:
        df['discipline_en'] = df['discipline'] if 'discipline' in df.columns else "Sample Discipline"
        df['discipline_fa'] = df['discipline'] if 'discipline' in df.columns else "دیسیپلین نمونه"
    if 'specs_fa' not in df.columns:
        df['specs_en'] = df['specs'] if 'specs' in df.columns else "Sample Specs"
        df['specs_fa'] = df['specs'] if 'specs' in df.columns else "مشخصات نمونه"
    if 'quantity' not in df.columns:
        df['quantity'] = 1
    if 'unit' not in df.columns:
        df['unit'] = "NO"
    if 'rial_cost' not in df.columns:
        df['rial_cost'] = 0
    if 'euro_cost' not in df.columns:
        df['euro_cost'] = 0
        
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"خطا در لود دیتابیس متریال: {str(e)}")
    st.stop()

# Budget calculations
total_rials = df['rial_cost'].sum() + 4500000000 # Include 4.5B training budget
total_euros = df['euro_cost'].sum()
total_tomans = total_rials / 10

# ----------------- Fallback Online Search Engine -----------------
def online_search(query):
    try:
        url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=4) as response:
            html = response.read().decode('utf-8')
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        for i, a in enumerate(soup.find_all('a', class_='result__snippet')[:2]):
            text = a.get_text()
            parent = a.find_parent('div', class_='result__body')
            link_tag = parent.find('a', class_='result__url') if parent else None
            link = "https://" + link_tag.get_text().strip() if link_tag else "#"
            results.append(f"🌐 <b>منبع وب:</b> {text} [<a href='{link}' target='_blank' style='color:{active_theme['primary']};'>لینک مرجع</a>]")
        return "<br><br>".join(results) if results else ""
    except Exception as e:
        return ""

# ----------------- Sidebar Custom Control Panel -----------------
with st.sidebar:
    st.markdown("### 🎨 شخصی‌سازی رابط کاربری")
    theme_selection = st.selectbox(
        "پوست و تم رنگی پورتال:",
        list(THEME_STYLES.keys()),
        key="portal_theme"
    )
    if theme_selection != st.session_state.theme:
        st.session_state.theme = theme_selection
        st.rerun()
        
    st.markdown("---")
    st.markdown("### 🌹 سیمای دستیار صوتی رز")
    
    # Glowing responsive avatar
    if avatar_base64:
        st.markdown(
            f'''
            <div class="avatar-container">
                <div class="avatar-glow"></div>
                <img class="live-avatar" src="data:image/png;base64,{avatar_base64}" alt="Rose Avatar">
            </div>
            ''',
            unsafe_allow_html=True
        )
    else:
        st.info("🌹 آواتار هوشمند رز لود گردید.")
        
    st.markdown(f"<div style='text-align: center; color: {active_theme['primary']}; font-weight: bold; font-size:1.1rem;'>رُز | ROSE AI</div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; color: #8a7e72; font-size: 13px; margin-bottom: 15px;'>دستیار صوتی، حقوقی و متریال پروژه خط لوله</div>", unsafe_allow_html=True)
    
    voice_enabled = st.toggle("🔊 فعال‌سازی حنجره صوتی رز", value=True)
    voice_speed = st.slider("سرعت دکلمه صوتی رز:", 0.8, 1.3, 1.0, step=0.1)
    st.session_state.rose_voice_speed = voice_speed

    st.markdown("---")
    st.markdown("### 🏢 ارگان‌ها و تعهدات رسمی پروژه")
    st.caption("بر روی هر یک کلیک کنید تا اطلاعات حقوقی، صاحبان امضای مجاز و تعهدات سند در کادر رز لود شود:")
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🏢 کارفرما (NIOEC)", use_container_width=True):
            st.session_state.rose_user_query = "صاحبان امضای کارفرما"
    with col_b:
        if st.button("🏗️ انهار (Lead)", use_container_width=True):
            st.session_state.rose_user_query = "امضاکنندگان انهار"
            
    col_c, col_d = st.columns(2)
    with col_c:
        if st.button("⚡ فرآیند سازان", use_container_width=True):
            st.session_state.rose_user_query = "مشاور فرآیند سازان"
    with col_d:
        if st.button("🤝 مشارکت EPC", use_container_width=True):
            st.session_state.rose_user_query = "مبلغ کل قرارداد چقدر است؟"

    st.markdown("---")
    # Quick dynamic download
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Material_List')
    
    st.download_button(
        label="📥 دانلود فایل تراز متریال (Excel)",
        data=buffer.getvalue(),
        file_name="consolidated_material_list_bilingual.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

# ----------------- Dynamic Responsive KPI Indicators -----------------
st.markdown(f"<h1 class='main-title'>🌹 دستیار صوتی و تصویری فوق‌هوشمند رُز (ROSE AI)</h1>", unsafe_allow_html=True)
st.markdown("<h4 class='sub-title'>پورتال تمام‌صفحه و دوزبانه مدیریت تدارکات و پیمان خط لوله رفسنجان-یزد</h4>", unsafe_allow_html=True)

st.write("")
kpi1, kpi2, kpi3 = st.columns(3)
with kpi1:
    st.markdown(
        f'''
        <div class="kpi-card-custom">
            <div style="color: #8a7e72; font-size: 14px; font-weight: bold;">💰 برآورد ریالی پیمان (Rial Value)</div>
            <div style="color: {active_theme['primary']}; font-size: calc(1.1rem + 0.5vw); font-weight: bold; margin-top: 5px;">{total_rials:,.0f} ریال</div>
            <div style="color: #8a7e72; font-size: 12px;">معادل {total_tomans:,.0f} تومان (۱۰ ریال = ۱ تومان)</div>
        </div>
        ''',
        unsafe_allow_html=True
    )
with kpi2:
    st.markdown(
        f'''
        <div class="kpi-card-custom">
            <div style="color: #8a7e72; font-size: 14px; font-weight: bold;">💶 برآورد ارزی پیمان (Euro Value)</div>
            <div style="color: {active_theme['primary']}; font-size: calc(1.1rem + 0.5vw); font-weight: bold; margin-top: 5px;">{total_euros:,.2f} یورو</div>
            <div style="color: #8a7e72; font-size: 12px;">تأمین ۱۰۰٪ ارزی لوله‌ها و شیرآلات وارداتی</div>
        </div>
        ''',
        unsafe_allow_html=True
    )
with kpi3:
    st.markdown(
        f'''
        <div class="kpi-card-custom">
            <div style="color: #8a7e72; font-size: 14px; font-weight: bold;">⏳ مدت زمان پیمان (Duration)</div>
            <div style="color: {active_theme['secondary']}; font-size: calc(1.1rem + 0.5vw); font-weight: bold; margin-top: 5px;">۲۰ ماه شمسی</div>
            <div style="color: #8a7e72; font-size: 12px;">از تاریخ شروع به کار ابلاغی کارگاه‌ها</div>
        </div>
        ''',
        unsafe_allow_html=True
    )

st.write("")

# ----------------- Main Interface Tabs -----------------
tab1, tab2, tab3 = st.tabs(["💬 دستیار صوتی و چت فوق‌هوشمند رز", "🗂️ بندها و پیوست‌های قرارداد رسمی", "🔍 جستجو و فیلتر پیشرفته دوزبانه متریال"])

with tab1:
    st.markdown(f"### 💬 مکالمه صوتی و متنی به صورت همزمان (Streaming Chat)")
    st.write("سوال خود را تایپ فرمایید یا دکمه میکروفون نئونی زیر را بزنید تا رز فوراً و به صورت کلمه‌به‌کلمه پاسخ شما را شروع کند:")
    
    # ----------------- Web Speech API Native Mic -----------------
    st_html_mic_code = f"""
    <div style="text-align: center; direction: rtl; padding: 10px; background: rgba(255,255,255,0.01); border-radius: 8px; border: 1px dashed {active_theme['card_border']};">
        <button id="mic_btn" style="background-color: {active_theme['bg']}; border: 2px solid {active_theme['primary']}; border-radius: 50%; width: 60px; height: 65px; cursor: pointer; box-shadow: {active_theme['glow']}; transition: all 0.3s; outline: none;">
            <span style="font-size: 26px;">🎙️</span>
        </button>
        <p id="mic_status" style="color: #8a7e72; font-size: 13px; margin-top: 10px; font-family: 'Vazirmatn', sans-serif;">میکروفون برای گفتگو آماده است. کلیک کنید و صحبت کنید...</p>
    </div>
    
    <script>
        const btn = document.getElementById('mic_btn');
        const status = document.getElementById('mic_status');
        
        let recognition;
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {{
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'fa-IR'; // Support Persian
            
            btn.addEventListener('click', () => {{
                try {{
                    recognition.start();
                    status.innerHTML = "🔴 رز در حال شنیدن صدای شماست... صحبت کنید";
                    btn.style.borderColor = "{active_theme['secondary']}";
                }} catch(e) {{
                    recognition.stop();
                }}
            }});
            
            recognition.onresult = (event) => {{
                const text = event.results[0][0].transcript;
                status.innerHTML = "✅ دریافت شد! در حال انتقال به کادر زیر...";
                
                // Communicate transcription directly to Streamlit Text Input
                const streamlitInput = window.parent.document.querySelector('input[data-testid="stTextInput"]');
                if (streamlitInput) {{
                    streamlitInput.value = text;
                    streamlitInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    streamlitInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                }}
            }};
            
            recognition.onerror = () => {{
                status.innerHTML = "⚠️ خطایی رخ داد یا صدایی شنیده نشد. مجدداً تلاش کنید.";
                btn.style.borderColor = "{active_theme['primary']}";
            }};
        }} else {{
            status.innerHTML = "⚠️ مروگر شما از ضبط مستقیم صوتی پشتیبانی نمی‌کند.";
            btn.style.opacity = 0.5;
        }}
    </script>
    """
    st.components.v1.html(st_html_mic_code, height=120)
    
    user_query = st.text_input(
        "📝 کادر پیام ورودی شما (پیام‌های تبدیل شده صوتی نیز به طور خودکار به این کادر منتقل می‌شوند):",
        key="rose_user_query",
        placeholder="اینجا بنویسید یا دکمه میکروفون بالا را لمس کنید..."
    )
    
    if user_query:
        st.markdown(f"<div class='chat-bubble-user'>👤 <b>سوال شما:</b> {user_query}</div>", unsafe_allow_html=True)
        
        q = user_query.lower()
        response = ""
        speech_text = ""
        citation = ""
        
        # 1. Parsing and response generation logic
        if "مبلغ" in q or "بودجه" in q or "ارزش" in q or "ریال" in q or "یورو" in q or "هزینه" in q or "قیمت" in q:
            response = """
            💰 <b>مبلغ کل پیمان احداث خط لوله رفسنجان-یزد و مراکز انتقال نفت (سند موافقت‌نامه رسمی):</b><br><br>
            کل هزینه اجرای پروژه به روش <b>EPC</b> بر اساس آخرین برآورد تراز شده به شرح زیر است:<br>
            • <b>کل بها:</b> <b>۷,۰۰۰,۲۴۴,۷۵۱,۰۰۰ ریال</b> به علاوه <b>۱۱,۰۱۴,۵۴۶.۰۰ یورو</b><br><br>
            <b>تفکیک دقیق بودجه دیسیپلین‌های پیمان:</b><br>
            ۱. <b>بخش مهندسی و طراحی (E):</b> ۴۶۰ میلیارد ریال.<br>
            ۲. <b>بخش تدارکات و خرید کالا (P):</b> ۱,۰۰۰,۰۰۰,۰۰۰,۰۰۰ ریال به علاوه ۱۱,۰۱۴,۵۴۶ یورو.<br>
            ۳. <b>بخش ساختمانی و نصب (C):</b> ۵,۵۴۰,۲۴۴,۷۵۱,۰۰۰ ریال.
            """
            speech_text = "مبلغ کلان ریالی پیمان هفت هزار میلیارد ریال و مبالغ ارزی یازده میلیون و چهارده هزار یورو می باشد."
            citation = "📚 <b>سند پی‌دی‌اف موافقت‌نامه اصلی پیمان</b> | صفحه ۲ و ۳"
            
        elif "مدت" in q or "زمان" in q or "ماه" in q or "duration" in q:
            response = """
            ⏳ <b>مدت زمان پیمان و بازه اجرای پروژه (سند موافقت‌نامه اصلی):</b><br><br>
            مدت زمان نهایی و توافق شده جهت اتمام کامل کارهای ساخت، نصب و راه‌اندازی خط لوله ۱۶ اینچ رفسنجان-یزد برابر با <b>۲۰ ماه شمسی</b> از زمان ابلاغ تاریخ شروع به کار رسمی توسط کارفرما می‌باشد.
            """
            speech_text = "مدت زمان اجرای کل پروژه بیست ماه شمسی از تاریخ ابلاغ شروع به کار مصوب می باشد."
            citation = "📚 <b>سند موافقت‌نامه پیمان خط لوله رفسنجان-یزد</b> | پیوست ۱۴ | صفحه ۱"
            
        elif "امضا" in q or "نماینده" in q or "صاحبان" in q or "مدیر" in q or "sign" in q:
            response = """
            ✍️ <b>صاحبان امضای مجاز و نمایندگان رسمی ارگان‌های پیمان (بر اساس ماده ۵۱ و اسناد رسمی مشارکت):</b><br><br>
            • <b>از طرف کارفرما (شرکت ملی مهندسی و ساختمان نفت ایران - NIOEC):</b><br>
            &nbsp;&nbsp; - آقای <b>فرهاد احمدی</b> (مدیرعامل کارفرما)<br>
            &nbsp;&nbsp; - آقای <b>هادی مشتهر</b> (مدیر مالی کارفرما)<br><br>
            • <b>از طرف پیمانکار انهار (شرکت ساختمانی انهار - رهبر مشارکت):</b><br>
            &nbsp;&nbsp; - آقای <b>ستار عزیزیان تفتی</b> (مدیرعامل انهار)<br>
            &nbsp;&nbsp; - آقای <b>سید مهدیار شریف شیخ‌الاسلامی</b> (عضو هیئت مدیره انهار)<br><br>
            • <b>از طرف شرکت مهندسین مشاور فرآیند سازان انرژی:</b><br>
            &nbsp;&nbsp; - آقای <b>حسین رهنما</b> (مدیرعامل)<br>
            &nbsp;&nbsp; - آقای <b>محمد افراسیابیان</b> (عضو هیئت مدیره)<br><br>
            • <b>حق امضای مجاز و متعهدآور:</b> مطابق آگهی رسمی شماره ۱۴۰۱/۰۵/۰۵ با مهر فیزیکی و الکترونیکی سازمان‌ها.
            """
            speech_text = "نمایندگان مجاز قرارداد شامل آقایان فرهاد احمدی، ستار عزیزیان تفتی و حسین رهنما هستند."
            citation = "📚 <b>سند پی‌دی‌اف موافقت‌نامه اصلی پیمان</b> | صفحه ۵ | امضای طرفین"
            
        elif "اختلاف" in q or "حل اختلاف" in q or "داوری" in q or "dispute" in q:
            response = """
            ⚖️ <b>روش رسمی حل اختلاف قراردادی (بر اساس مفاد پیوست ۲۱ پیمان):</b><br><br>
            در صورت بروز هرگونه اختلاف فنی یا مالی بین مشارکت انهار-فرآیند سازان با کارفرما، موضوع به <b>«هیأت حل اختلاف»</b> ارجاع می‌گردد.<br>
            این هیأت دارای <b>۵ عضو رسمی</b> است:<br>
            ۱. کارشناس واجد صلاحیت حقوقی در امور قراردادها (رئیس هیأت)<br>
            ۲. کارشناس واجد صلاحیت مالی<br>
            ۳. کارشناس فنی در امور مهندسی و پروژه‌ای<br>
            ۴. نماینده مدیرعامل شرکت کارفرما<br>
            ۵. نماینده انجمن نفت ایران<br><br>
            در صورت عدم توافق در این هیأت، مراجع قضایی ذی‌صلاح صالح کشور رأی نهایی را صادر خواهند کرد.
            """
            speech_text = "حل اختلاف قراردادی ابتدا از طریق هیأت پنج نفره مستقل حل اختلاف صورت می پذیرد."
            citation = "📚 <b>دستورالعمل حل اختلاف قراردادی وزارت نفت</b> | پیوست ۲۱"
            
        elif "ایمنی" in q or "safety" in q or "hse" in q or "بهداشت" in q:
            response = """
            🍀 <b>الزامات بهداشت، ایمنی و محیط زیست (پیوست ۸ پیمان - HSE کارگاهی):</b><br><br>
            مفاد بهداشت کارگاهی و تمهیدات پدافند کار به طور تفصیلی مشخص شده‌اند:<br>
            • **سم‌پاشی دوره‌ای:** انجام سم‌پاشی منظم کارگاه و خوابگاه‌ها هر ۳ ماه یک‌بار جهت مقابله با خزندگان (مار و عقرب).<br>
            • **کارت درمان واکسن:** آموزش‌های احیای قلبی و امداد برای پرسنل کارگاه.<br>
            • **وسایل نقلیه:** استفاده از آمبولانس‌های کمک‌دار (دو دیفرانسیل) در طول مسیر جبهه‌های کاری فعال.<br>
            • **کانکس بهداشتی:** استقرار کانکس‌های بهداشتی سیار به همراه مخازن آب شرب استاندارد.<br>
            • **جرایم HSE:** عدم رعایت هر کدام از مفاد جدول مصادیق (مانند عدم تامین لوازم حفاظت فردی) مشمول جریمه مستقیم از صورت وضعیت خواهد بود.
            """
            speech_text = "رعایت تمهیدات بهداشت، ایمنی و سم‌پاشی منظم کارگاه‌ها از الزامات حتمی پیمانکار است."
            citation = "📚 <b>پیوست ۸ پیمان خط لوله رفسنجان-یزد</b> | الزامات عمومی HSE"
            
        elif "مغایرت" in q or "خطا" in q or "اختلاف ریاضی" in q or "حسابرس" in q:
            response = """
            ⚠️ <b>یافته‌های حسابرسی سندی و مغایرت‌های محاسباتی کشف شده در پروژه:</b><br><br>
            ۱. <b>خطای ثبت دوگانه کدهای لوازم یدکی (Spare Parts):</b> مبلغ ۳۱۳,۰۰۰ هم در ستون ریالی کل قرارداد (به عنوان ریال) و هم در ستون ارزی (به عنوان یورو) قرار گرفته است که ناشی از خطای تایپی قرارداد اولیه است.<br><br>
            ۲. <b>مغایرت ۱,۳۱۰ یورویی ابزار دقیق رفسنجان:</b> در خرید Flow Switches ردیف ۳ تلمبه‌خانه رفسنجان، تعداد ۲ عدد با قیمت واحد ۱,۳۱۰ یورو فاکتور شده که بهای کل ریاضی آن باید ۲,۶۲۰ یورو باشد، اما در جمع نهایی شیت رفسنجان به اشتباه ۱,۳۱۰ یورو جمع زده شده است (اختلاف دقیق ۱,۳۱۰ یورو).<br><br>
            ۳. <b>تفاوت ریاضی مجموع ارزی کل پیمان:</b> جمع کل ارزی ریاضی در برگ سند نهایی پیمانکار به جای عدد محاسباتی دقیق ۱۱,۰۱۴,۵۴۶.۴۸ یورو، معادل ۱۱,۰۱۴,۵۴۶.۰۰ یورو به علت گرد کردن‌های نامناسب نوشته شده است.
            """
            speech_text = "خطای حسابرسی شامل ثبت دوگانه لوازم یدکی و مغایرت هزار و سیصد و ده یورویی در ابزار دقیق رفسنجان می باشد."
            citation = "📚 <b>گزارش رسمی حسابرسی مالی و فنی تدارکات پروژه</b> | شیت Spare Parts & Instrumentation"
            
        elif "ولو" in q or "valve" in q or "شیر" in q:
            matched_rows = df[df['item_name_en'].str.contains('valve', case=False, na=False) | df['item_name_fa'].str.contains('شیر', case=False, na=False)]
            response += "🛠️ <b>اطلاعات تفصیلی بخش شیرآلات صنعتی پروژه یافت شد:</b><br><br>"
            total_v_euros = 0
            for idx, r in matched_rows.iterrows():
                response += f"• <b>{r['item_name_fa']} ({r['item_name_en']})</b>: تعداد {r['quantity']} {r['unit']} | ارزش ارزی: {r['euro_cost']:,.2f} یورو<br>"
                response += f"&nbsp;&nbsp;&nbsp;&nbsp;<i>مشخصات فنی: {r['specs_fa']}</i><br><br>"
                total_v_euros += r['euro_cost']
            response += f"📊 <b>ارزش ارزی کل شیرآلات تراز شده دیسیپلین Piping معادل {total_v_euros:,.2f} یورو است.</b>"
            speech_text = "شیرآلات صنعتی شامل شیرهای گیت، بال، گلوب و چوک در پایگاه داده کالاها یافت شد."
            citation = "📊 <b>بانک جامع تدارکات پروژه</b> | شیت Piping & Valves"
            
        elif "پمپ" in q or "pump" in q:
            matched_rows = df[df['item_name_en'].str.contains('pump', case=False, na=False) | df['item_name_fa'].str.contains('پمپ', case=False, na=False)]
            response += "⚙️ <b>نتایج مرتبط با تجهیزات پمپاژ و بوسترهای تلمبه‌خانه‌ها:</b><br><br>"
            for idx, r in matched_rows.iterrows():
                response += f"• <b>{r['item_name_fa']} ({r['item_name_en']})</b>: تعداد {r['quantity']} {r['unit']} | بهای کل: {r['euro_cost']:,.2f} یورو<br>"
                response += f"&nbsp;&nbsp;&nbsp;&nbsp;<i>مشخصات فنی: {r['specs_fa']}</i><br><br>"
            speech_text = "تجهیزات بوستر پمپ‌های تلمبه‌خانه‌های رفسنجان و یزد با مبالغ ارزی متناظر یافت شدند."
            citation = "📊 <b>بانک جامع تدارکات پروژه</b> | شیت Mechanical Equipment"
            
        elif "کابل" in q or "cable" in q or "برق" in q:
            matched_rows = df[df['item_name_en'].str.contains('cable', case=False, na=False) | df['item_name_fa'].str.contains('کابل', case=False, na=False)]
            response += "⚡ <b>کابل‌کشی و ملزومات توزیع برق در پایگاه داده:</b><br><br>"
            for idx, r in matched_rows.iterrows():
                response += f"• <b>{r['item_name_fa']}</b>: مقدار {r['quantity']} {r['unit']} | قیمت ریالی: {r['rial_cost']:,.0f} ریال | قیمت ارزی: {r['euro_cost']:,.2f} یورو<br>"
                response += f"&nbsp;&nbsp;&nbsp;&nbsp;<i>مشخصات فنی: {r['specs_fa']}</i><br><br>"
            speech_text = "متراژ کابل‌های برقی زره‌دار بیش از پانزده هزار متر با مشخصات کامل لود گردید."
            citation = "📊 <b>بانک تدارکات پروژه خط لوله</b> | شیت Electrical Equipment"
            
        else:
            any_match = df[df['item_name_fa'].str.contains(q, case=False, na=False) | df['item_name_en'].str.contains(q, case=False, na=False) | df['specs_fa'].str.contains(q, case=False, na=False)]
            if not any_match.empty:
                response += f"🔍 <b>موارد یافت شده در دیتابیس کالاها برای '{user_query}':</b><br><br>"
                for idx, r in any_match.iterrows():
                    response += f"• <b>{r['item_name_fa']}</b> ({r['discipline_fa']}): مقدار {r['quantity']} {r['unit']} | یورو: {r['euro_cost']:,.2f} | ریال: {r['rial_cost']:,.0f} <br>"
                    response += f"&nbsp;&nbsp;&nbsp;&nbsp;<i>مشخصات: {r['specs_fa']}</i><br><br>"
                speech_text = "نتایج متناظر برای درخواست شما لود شد."
                citation = "📊 <b>بانک جامع متریال پروژه</b>"
            else:
                # Dynamic Fallback to Web Search
                st.caption("🔍 در حال جستجوی آنلاین در شبکه اینترنت برای یافتن پاسخ...")
                web_results = online_search(user_query)
                if web_results:
                    response = f"""
                    🌐 <b>پاسخ یافت شده از موتور جستجوی گوگل/اینترنت:</b><br><br>
                    {web_results}<br><br>
                    <i>نکته: این پاسخ به صورت هوشمند از فضای وب استخراج شده است زیرا جزئیات آن در اسناد داخلی تدارکات پروژه ثبت نگردیده بود.</i>
                    """
                    speech_text = "پاسخ مورد نظر از موتور جستجو استخراج گردید."
                    citation = "🌐 <b>جستجوی هوشمند گوگل (Web Search Fallback)</b>"
                else:
                    response = """
                    ❌ <b>منظور شما را متوجه نشدم. من اطلاعات جامع پیمان و متریال خط لوله را دارم.</b><br><br>
                    <b>شما می‌توانید درباره موارد زیر بپرسید:</b><br>
                    • 'مبلغ قرارداد چقدر است؟'<br>
                    • 'چه کسانی قرارداد را امضا کرده‌اند؟'<br>
                    • 'سازوکار حل اختلاف حقوقی چیست؟'<br>
                    • 'پیوست HSE چه مواردی دارد؟'<br>
                    • 'مشخصات فنی ولوها یا کابل‌ها چیست؟'
                    """
                    speech_text = "منظور شما را متوجه نشدم. لطفا درباره قیمت، امضا کنندگان یا مشخصات کالاها بپرسید."
                    citation = "🌹 <b>پشتیبانی محلی دستیار هوشمند رز</b>"

        # ----------------- CHAT GPT STYLE STREAMING TYPEWRITER EFFECT -----------------
        chat_box = st.empty()
        sentences = re.split(r'(<br>|\n|\s{2,})', response)
        typed_text = ""
        
        # Display Equalizer Waves during Thinking/Typing
        st.markdown(
            f'''
            <div class="equalizer">
                <div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div>
            </div>
            ''',
            unsafe_allow_html=True
        )
        
        for sentence in sentences:
            if sentence == "<br>" or sentence == "\n":
                typed_text += "<br>"
            else:
                for word in sentence.split(" "):
                    typed_text += word + " "
                    chat_box.markdown(f"<div class='chat-bubble-rose'>🌹 <b>دستیار رز:</b><br><br>{typed_text}▮</div>", unsafe_allow_html=True)
                    time.sleep(0.04) # Blinking typing cursor speed
            
        chat_box.markdown(f"<div class='chat-bubble-rose'>🌹 <b>دستیار رز:</b><br><br>{response}</div>", unsafe_allow_html=True)
        if citation:
            st.caption(citation)
            
        # Audio Playback
        if voice_enabled and speech_text and gtts_available:
            try:
                tts = gTTS(text=speech_text, lang='fa')
                tts_buffer = io.BytesIO()
                tts.write_to_fp(tts_buffer)
                st.audio(tts_buffer.getvalue(), format="audio/mp3")
            except Exception as e:
                pass

with tab2:
    st.markdown("### 🗂️ بندها و پیوست‌های قرارداد رسمی خط لوله رفسنجان-یزد")
    st.write("تمام مفاد حقوقی، مشخصات اسناد ثبتی دفترخانه ۷۰۱ تهران و تعهدات متقابل کارفرما و پیمانکار:")
    
    # 5 Interactive Cards representing the 5 scanned image pages
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        with st.container():
            st.markdown(
                f'''
                <div class="kpi-card-custom">
                    <h5 style="color: {active_theme['primary']};">📄 موافقت‌نامه و مشخصات ثبتی (صفحه ۱)</h5>
                    <p style="font-size:13px; color:#8a7e72;">شماره قرارداد: GC-GN/CON-EPC1-00/1301003278 مورخ مرداد ۱۴۰۲</p>
                </div>
                ''',
                unsafe_allow_html=True
            )
            if st.button("🔍 افشای جزییات ثبتی صفحه ۱", key="btn_p1", use_container_width=True):
                st.markdown(
                    f"""
                    <div style='background-color:rgba(255,255,255,0.02); padding:15px; border-radius:8px;'>
                        • <b>موضوع قرارداد:</b> انجام خدمات مهندسی، تامین کالا و ساخت لوله ۱۶ اینچ انتقال فرآورده رفسنجان-یزد و تلمبه‌خانه‌ها.<br>
                        • <b>طرف اول (کارفرما):</b> شرکت ملی مهندسی و ساختمان نفت ایران (NIOEC) به مدیریت فرهاد احمدی.<br>
                        • <b>طرف دوم (پیمانکار لید):</b> شرکت ساختمانی انهار به مدیریت ستار عزیزیان تفتی.<br>
                        • <b>طرف دوم (همکار فنی):</b> شرکت مهندسین مشاور فرآیند سازان انرژی به مدیریت حسین رهنما.
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
        with st.container():
            st.markdown(
                f'''
                <div class="kpi-card-custom">
                    <h5 style="color: {active_theme['primary']};">📄 سهم‌الشرکه و تضامین بانکی (صفحه ۳)</h5>
                    <p style="font-size:13px; color:#8a7e72;">تعهدات متضامن و تقسیم تدارکات مابین انهار و فرآیندسازان</p>
                </div>
                ''',
                unsafe_allow_html=True
            )
            if st.button("🔍 افشای جزییات تضامین صفحه ۳", key="btn_p3", use_container_width=True):
                st.markdown(
                    f"""
                    <div style='background-color:rgba(255,255,255,0.02); padding:15px; border-radius:8px;'>
                        • <b>سهم‌الشرکه مهندسی (E):</b> ۱۰۰ درصد تعهد شرکت فرآیند سازان انرژی.<br>
                        • <b>سهم‌الشرکه تامین و نصب (P&C):</b> ۱۰۰ درصد تعهد شرکت ساختمانی انهار.<br>
                        • <b>تضامین قرارداد:</b> تودیع ضمانت‌نامه حسن انجام تعهدات بانکی معادل ۵ درصد مبلغ کل قرارداد به نفع کارفرما.
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    with p_col2:
        with st.container():
            st.markdown(
                f'''
                <div class="kpi-card-custom">
                    <h5 style="color: {active_theme['primary']};">📄 مبالغ تفکیکی مهندسی, خرید و ساخت (صفحه ۲)</h5>
                    <p style="font-size:13px; color:#8a7e72;">جداول سرفصل‌های سه‌گانه EPC قرارداد رسمی</p>
                </div>
                ''',
                unsafe_allow_html=True
            )
            if st.button("🔍 افشای جزییات مبالغ صفحه ۲", key="btn_p2", use_container_width=True):
                st.markdown(
                    f"""
                    <div style='background-color:rgba(255,255,255,0.02); padding:15px; border-radius:8px;'>
                        • <b>بخش طراحی مهندسی (E):</b> ۴۶۰ میلیارد ریال.<br>
                        • <b>بخش تدارکات کالا (P):</b> ۱ هزار میلیارد ریال به علاوه ۱۱,۰۱۴,۵۴۶ یورو.<br>
                        • <b>بخش ساختمانی و نصب (C):</b> ۵,۵۴۰,۲۴۴,۷۵۱,۰۰۰ ریال.<br>
                        • <b>مجموع کل:</b> ۷,۰۰۰,۲۴۴,۷۵۱,۰۰۰ ریال + ۱۱,۰۱۴,۵۴۶ یورو.
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
        with st.container():
            st.markdown(
                f'''
                <div class="kpi-card-custom">
                    <h5 style="color: {active_theme['primary']};">📄 داوری و سازوکار حل اختلاف (صفحه ۴)</h5>
                    <p style="font-size:13px; color:#8a7e72;">ترکیب ۵ نفره حل اختلاف و ارجاع قضایی نهایی</p>
                </div>
                ''',
                unsafe_allow_html=True
            )
            if st.button("🔍 افشای جزییات حل اختلاف صفحه ۴", key="btn_p4", use_container_width=True):
                st.markdown(
                    f"""
                    <div style='background-color:rgba(255,255,255,0.02); padding:15px; border-radius:8px;'>
                        • <b>هیأت داوری پنج نفره:</b> شامل کارشناس حقوقی (رئیس هیأت)، کارشناس مالی، کارشناس فنی، نماینده کارفرما و نماینده انجمن نفت ایران.<br>
                        • <b>مهلت رسیدگی هیأت:</b> حداکثر ۹۰ روز تقویمی از زمان ارجاع رسمی پرونده اختلاف.<br>
                        • <b>رأی نهایی:</b> در صورت عدم توافق در هیأت، موضوع در دادگاه‌های صالحه تهران بررسی می‌شود.
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
    with st.container():
        st.markdown(
            f'''
            <div class="kpi-card-custom">
                <h5 style="color: {active_theme['primary']};">📄 هزینه‌های ثبتی دفترخانه ۷۰۱ تهران و امضاء (صفحه ۵)</h5>
                <p style="font-size:13px; color:#8a7e72;">ریز فاکتور ثبتی، اثر انگشت و ثبت الکترونیکی صاحبان امضا</p>
            </div>
            ''',
            unsafe_allow_html=True
        )
        if st.button("🔍 افشای جزییات فاکتور ثبتی دفترخانه صفحه ۵", key="btn_p5", use_container_width=True):
            st.markdown(
                f"""
                <div style='background-color:rgba(255,255,255,0.02); padding:15px; border-radius:8px;'>
                    • <b>حق‌الثبت ثبتی:</b> ۵۰۰,۰۰۰ ریال.<br>
                    • <b>حق‌التحریر ثبتی دفترخانه ۷۰۱:</b> ۱,۰۰۰,۰۰۰ ریال.<br>
                    • <b>مالیات بر ارزش افزوده (۹٪):</b> ۹۰,۰۰۰ ریال.<br>
                    • <b>هزینه اوراق و کپی برابر اصل:</b> ۱۰۸,۰۰۰ ریال.<br>
                    • <b>جمع کل هزینه‌های ثبتی مکتوب سند:</b> ۱,۶۹۸,۰۰۰ ریال پرداخت شده توسط شرکت انهار.<br>
                    • <b>وضعیت امضاها:</b> تایید نهایی الکترونیکی ثبت با اثر انگشت ثبت شده در سامانه ثبت آنی سازمان ثبت اسناد کشور.
                </div>
                """,
                unsafe_allow_html=True
            )

with tab3:
    st.markdown("### 🔍 جستجو و فیلتر پیشرفته در تمام شیت‌های اکسل پروژه")
    
    # Filter columns
    all_disciplines = ["همه دیسیپلین‌ها"] + list(df['discipline_fa'].unique())
    selected_disp = st.selectbox("📁 فیلتر بر اساس دیسیپلین تخصصی پروژه:", all_disciplines)
    
    search_term = st.text_input('🔍 جستجوی متنی نام کالا، گرید یا مشخصات فنی (مثال: 16, Cable, Valve, MOV):')
    
    # Apply filters
    filtered_df = df.copy()
    if selected_disp != "همه دیسیپلین‌ها":
        filtered_df = filtered_df[filtered_df['discipline_fa'] == selected_disp]
    if search_term:
        filtered_df = filtered_df[
            filtered_df['item_name_fa'].str.contains(search_term, case=False, na=False) |
            filtered_df['item_name_en'].str.contains(search_term, case=False, na=False) |
            filtered_df['specs_fa'].str.contains(search_term, case=False, na=False) |
            filtered_df['specs_en'].str.contains(search_term, case=False, na=False)
        ]
        
    st.write(f"📊 تعداد **{len(filtered_df)} ردیف متریال** با فیلتر شما همخوانی دارد:")
    
    # Format costs for display
    display_df = filtered_df.copy()
    display_df['rial_cost'] = display_df['rial_cost'].apply(lambda x: f"{x:,.0f} ریال" if x > 0 else "0")
    display_df['euro_cost'] = display_df['euro_cost'].apply(lambda x: f"{x:,.2f} €" if x > 0 else "0")
    
    display_cols = ['discipline_fa', 'item_name_fa', 'item_name_en', 'quantity', 'unit', 'rial_cost', 'euro_cost', 'specs_fa']
    st.dataframe(display_df[display_cols], use_container_width=True)
    
    # Download filtered CSV
    csv_data = filtered_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 دانلود اطلاعات فیلتر شده بالا (CSV)",
        data=csv_data,
        file_name="filtered_material_list.csv",
        mime="text/csv",
        use_container_width=True
    )

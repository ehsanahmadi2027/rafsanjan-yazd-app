import streamlit as st
import pandas as pd
import numpy as np
import io
import os
import base64
import urllib.request
import urllib.parse
import json
import glob
import time

# Try to import pypdf safely
try:
    import pypdf
    pypdf_available = True
except ImportError:
    pypdf_available = False

# ----------------- streamlit set config -----------------
st.set_page_config(
    page_title="پورتال تدارکات و دستیار صوتی رُز | ROSE AI v13",
    page_icon="🌹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- responsive neon css (mobile & desktop) -----------------
if 'app_theme' not in st.session_state:
    st.session_state['app_theme'] = 'Cyberpunk Neon'

themes = {
    'Cyberpunk Neon': {
        'bg': '#08090d',
        'text': '#e0e6ed',
        'primary': '#00f0ff',
        'secondary': '#ff007f',
        'card_bg': 'rgba(255, 255, 255, 0.02)',
        'border': 'rgba(0, 240, 255, 0.15)',
        'bubble_user': 'rgba(255, 0, 127, 0.08)',
        'bubble_rose': 'rgba(0, 240, 255, 0.08)',
        'highlight': '#ff007f',
        'grad': 'linear-gradient(135deg, #00f0ff 0%, #ff007f 100%)'
    },
    'Classic Petroleum Navy-Gold': {
        'bg': '#0a192f',
        'text': '#f4f6f9',
        'primary': '#ffc13b',
        'secondary': '#17a2b8',
        'card_bg': 'rgba(255, 255, 255, 0.03)',
        'border': 'rgba(255, 193, 59, 0.2)',
        'bubble_user': 'rgba(23, 162, 184, 0.1)',
        'bubble_rose': 'rgba(255, 193, 59, 0.1)',
        'highlight': '#ffc13b',
        'grad': 'linear-gradient(135deg, #ffc13b 0%, #17a2b8 100%)'
    },
    'HSE Emerald & Slate': {
        'bg': '#0f172a',
        'text': '#f8fafc',
        'primary': '#10b981',
        'secondary': '#64748b',
        'card_bg': 'rgba(255, 255, 255, 0.02)',
        'border': 'rgba(16, 185, 129, 0.15)',
        'bubble_user': 'rgba(100, 116, 139, 0.1)',
        'bubble_rose': 'rgba(16, 185, 129, 0.1)',
        'highlight': '#10b981',
        'grad': 'linear-gradient(135deg, #10b981 0%, #64748b 100%)'
    },
    'Royal Black & Amethyst': {
        'bg': '#090514',
        'text': '#f5f3ff',
        'primary': '#a78bfa',
        'secondary': '#ec4899',
        'card_bg': 'rgba(255, 255, 255, 0.03)',
        'border': 'rgba(167, 139, 250, 0.2)',
        'bubble_user': 'rgba(236, 72, 153, 0.08)',
        'bubble_rose': 'rgba(167, 139, 250, 0.08)',
        'highlight': '#ec4899',
        'grad': 'linear-gradient(135deg, #a78bfa 0%, #ec4899 100%)'
    }
}

theme = themes[st.session_state['app_theme']]

# Render dynamic CSS
css_code = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;700&display=swap');

html, body, [data-testid="stAppViewContainer"] {{
    background-color: {theme['bg']} !important;
    color: {theme['text']} !important;
    font-family: 'Vazirmatn', sans-serif !important;
    direction: RTL;
    text-align: right;
}}

.stApp {{
    direction: RTL;
    text-align: right;
}}

h1, h2, h3, h4, h5, h6 {{
    color: {theme['primary']} !important;
    font-family: 'Vazirmatn', sans-serif !important;
    text-shadow: 0 0 10px {theme['primary']}40;
}}

.main-title {{
    color: {theme['primary']};
    text-align: center;
    font-size: 2.2rem;
    font-weight: bold;
    margin-top: 10px;
    margin-bottom: 5px;
    text-shadow: 0 0 15px {theme['primary']}60;
}}

.sub-title {{
    color: {theme['secondary']};
    text-align: center;
    font-size: 1.1rem;
    margin-bottom: 25px;
    text-shadow: 0 0 8px {theme['secondary']}40;
}}

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
    width: 170px;
    height: 170px;
    border-radius: 50%;
    background: radial-gradient(circle, {theme['primary']}30 0%, {theme['secondary']}10 70%, transparent 100%);
    animation: pulse-glow 4s infinite ease-in-out;
}}

.svg-avatar {{
    position: relative;
    border-radius: 50%;
    border: 3px solid {theme['primary']};
    box-shadow: 0 0 20px {theme['primary']}50;
    width: 150px;
    height: 150px;
    object-fit: cover;
    z-index: 2;
    animation: breathe 5s infinite ease-in-out;
    transition: transform 0.3s ease-in-out, border-color 0.3s;
}}

.svg-avatar:hover {{
    transform: scale(1.08) rotate(2deg);
    border-color: {theme['secondary']};
    box-shadow: 0 0 30px {theme['secondary']}80;
}}

@keyframes breathe {{
    0% {{ transform: scale(1); }}
    50% {{ transform: scale(1.03) translateY(-3px); }}
    100% {{ transform: scale(1); }}
}}

@keyframes pulse-glow {{
    0% {{ transform: scale(0.9); opacity: 0.5; }}
    50% {{ transform: scale(1.2); opacity: 0.9; }}
    100% {{ transform: scale(0.9); opacity: 0.5; }}
}}

.kpi-card-custom {{
    background: {theme['card_bg']};
    border: 1px solid {theme['border']};
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    backdrop-filter: blur(5px);
    transition: all 0.3s;
    margin-bottom: 12px;
}}

.kpi-card-custom:hover {{
    border-color: {theme['primary']};
    box-shadow: 0 0 15px {theme['primary']}30;
    transform: translateY(-2px);
}}

.chat-bubble-user {{
    background-color: {theme['bubble_user']};
    border-right: 5px solid {theme['secondary']};
    border-left: 1px solid rgba(255, 255, 255, 0.05);
    padding: 14px;
    border-radius: 8px;
    margin-bottom: 15px;
    text-align: right;
    direction: RTL;
    color: {theme['text']};
}}

.chat-bubble-rose {{
    background-color: {theme['bubble_rose']};
    border-right: 5px solid {theme['primary']};
    border-left: 1px solid rgba(255, 255, 255, 0.05);
    padding: 16px;
    border-radius: 8px;
    margin-bottom: 15px;
    text-align: right;
    direction: RTL;
    box-shadow: 0 0 15px {theme['primary']}08;
    color: #f0f4f8;
}}

.equalizer {{
    display: flex;
    justify-content: center;
    align-items: flex-end;
    height: 25px;
    width: 100px;
    margin: 10px auto;
    gap: 3px;
}}

.bar {{
    width: 4px;
    height: 5px;
    background-color: {theme['primary']};
    animation: bounce 0.6s infinite alternate;
    border-radius: 2px;
}}

.bar:nth-child(2) {{ animation-delay: 0.15s; background-color: {theme['secondary']}; }}
.bar:nth-child(3) {{ animation-delay: 0.3s; }}
.bar:nth-child(4) {{ animation-delay: 0.45s; background-color: {theme['secondary']}; }}
.bar:nth-child(5) {{ animation-delay: 0.2s; }}

@keyframes bounce {{
    0% {{ height: 5px; }}
    100% {{ height: 25px; }}
}}

/* Fully Mobile Responsive Rules */
@media (max-width: 1024px) {{
    .main-title {{
        font-size: 1.8rem !important;
    }}
    .sub-title {{
        font-size: 1rem !important;
    }}
}}

@media (max-width: 768px) {{
    .main-title {{
        font-size: 1.4rem !important;
    }}
    .sub-title {{
        font-size: 0.85rem !important;
        margin-bottom: 15px !important;
    }}
    .svg-avatar {{
        width: 120px !important;
        height: 120px !important;
    }}
    .avatar-glow {{
        width: 140px !important;
        height: 140px !important;
    }}
    .kpi-card-custom {{
        padding: 12px !important;
        margin-bottom: 8px !important;
    }}
    div[data-testid="column"] {{
        margin-bottom: 8px !important;
        width: 100% !important;
        flex: 1 1 100% !important;
    }}
    .chat-bubble-user, .chat-bubble-rose {{
        padding: 12px !important;
        font-size: 0.9rem !important;
    }}
}}

@media (max-width: 480px) {{
    .main-title {{
        font-size: 1.2rem !important;
    }}
    .svg-avatar {{
        width: 100px !important;
        height: 100px !important;
    }}
}}
</style>
"""
st.markdown(css_code, unsafe_allow_html=True)

# ----------------- Dynamic SVG Avatar Generation -----------------
def get_svg_avatar(state='idle'):
    blink_anim = """<animate attributeName="scaleY" values="1;1;0.05;1;1" dur="4s" repeatCount="indefinite" />"""
    lip_anim = ""
    wave_anim = ""
    glow_color = theme['primary']
    
    if state == 'listening':
        glow_color = theme['secondary']
        wave_anim = """<animateTransform attributeName="transform" type="rotate" values="0 50 150; 15 50 150; -5 50 150; 0 50 150" dur="1s" repeatCount="indefinite" />"""
    elif state == 'thinking':
        glow_color = '#ffc13b'
        wave_anim = """<animateTransform attributeName="transform" type="rotate" values="0 50 150; 8 50 150; -8 50 150; 0 50 150" dur="1.5s" repeatCount="indefinite" />"""
    elif state == 'speaking':
        glow_color = theme['secondary']
        lip_anim = """<animate attributeName="height" values="4;18;4;12;4" dur="0.25s" repeatCount="indefinite" />"""
        wave_anim = """<animateTransform attributeName="transform" type="rotate" values="0 50 150; 25 50 150; 0 50 150" dur="0.8s" repeatCount="indefinite" />"""
        
    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
        <style>
            @keyframes breathe-svg {{
                0%, 100% {{ transform: translateY(0px); }}
                50% {{ transform: translateY(-4px); }}
            }}
            .breathe-g {{ animation: breathe-svg 4s infinite ease-in-out; transform-origin: 100px 150px; }}
            .eye-el {{ transform-origin: center; }}
        </style>
        
        <!-- Outer Glowing Halo -->
        <circle cx="100" cy="100" r="88" fill="none" stroke="{glow_color}" stroke-width="2.5" opacity="0.75" />
        <circle cx="100" cy="100" r="80" fill="#0d111d" />
        
        <g class="breathe-g">
            <!-- Cybernetic Shoulders & Chest -->
            <path d="M40,160 C50,130 150,130 160,160 L140,195 L60,190 Z" fill="#1b2030" stroke="{theme['primary']}" stroke-width="1.5" />
            <path d="M70,140 Q100,155 130,140" fill="none" stroke="{theme['secondary']}" stroke-width="2" />
            
            <!-- Cyber Neck -->
            <rect x="90" y="115" width="20" height="25" rx="5" fill="#2d354a" stroke="{theme['primary']}" stroke-width="1" />
            
            <!-- Face / Head -->
            <circle cx="100" cy="80" r="35" fill="#242b42" stroke="{theme['primary']}" stroke-width="2" />
            
            <!-- Futuristic Glowing Headphones -->
            <!-- Left Piece -->
            <path d="M55,55 Q40,40 50,30 Q60,35 65,50" fill="{theme['secondary']}" stroke="{theme['primary']}" stroke-width="1.5" />
            <circle cx="65" cy="80" r="10" fill="#1b2030" stroke="{theme['secondary']}" stroke-width="2" />
            <!-- Right Piece -->
            <path d="M145,55 Q160,40 150,30 Q140,35 135,50" fill="{theme['secondary']}" stroke="{theme['primary']}" stroke-width="1.5" />
            <circle cx="135" cy="80" r="10" fill="#1b2030" stroke="{theme['secondary']}" stroke-width="2" />
            <!-- Band -->
            <path d="M65,70 Q100,45 135,70" fill="none" stroke="{theme['primary']}" stroke-width="3" />
            
            <!-- Cyber Eyes with Blinking Animation -->
            <ellipse class="eye-el" cx="85" cy="78" rx="5" ry="5" fill="{theme['primary']}">
                {blink_anim}
            </ellipse>
            <circle cx="83" cy="76" r="1.5" fill="#ffffff" />
            
            <ellipse class="eye-el" cx="115" cy="78" rx="5" ry="5" fill="{theme['primary']}">
                {blink_anim}
            </ellipse>
            <circle cx="113" cy="76" r="1.5" fill="#ffffff" />
            
            <!-- Eyebrows -->
            <path d="M75,70 Q85,67 90,72" fill="none" stroke="{theme['secondary']}" stroke-width="1.5" stroke-linecap="round" />
            <path d="M125,70 Q115,67 110,72" fill="none" stroke="{theme['secondary']}" stroke-width="1.5" stroke-linecap="round" />
            
            <!-- Cute Blushing Cheeks -->
            <circle cx="75" cy="90" r="4" fill="{theme['secondary']}" opacity="0.6" />
            <circle cx="125" cy="90" r="4" fill="{theme['secondary']}" opacity="0.6" />
            
            <!-- Nose -->
            <path d="M100,82 L98,88 L102,88 Z" fill="{theme['secondary']}" />
            
            <!-- Interactive Speaking Mouth -->
            <rect x="90" y="98" width="20" height="4" rx="2" ry="2" fill="#ffffff" stroke="{theme['secondary']}" stroke-width="1.2">
                {lip_anim}
            </rect>
            
            <!-- Sleek Futuristic Hair details -->
            <path d="M70,55 Q100,65 130,55" fill="none" stroke="{theme['primary']}" stroke-width="1" opacity="0.5" />
        </g>
        
        <!-- Animated Gesturing Hand -->
        <g>
            <path d="M40,140 Q25,120 30,105 Q35,110 45,130" fill="none" stroke="{theme['secondary']}" stroke-width="4" stroke-linecap="round">
                {wave_anim}
            </path>
            <circle cx="30" cy="105" r="4" fill="{theme['primary']}">
                {wave_anim}
            </circle>
        </g>
    </svg>"""
    return base64.b64encode(svg_content.encode('utf-8')).decode()

# ----------------- Dynamic Fallback Online Search Engine -----------------
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
            results.append(f"🌐 <b>منبع وب:</b> {text} [<a href='{link}' target='_blank'>لینک مرجع</a>]")
        return "<br><br>".join(results) if results else ""
    except Exception as e:
        return ""

# ----------------- Smart Multi-Sheet Excel Parser -----------------
@st.cache_data
def load_and_index_excel():
    excel_filename = "epc_comprehensive_valuation_v8.xlsx"
    paths_to_excel = [
        excel_filename,
        "artifacts/" + excel_filename,
        "/workspace/artifacts/" + excel_filename,
        "../" + excel_filename
    ]
    
    import glob
    xlsx_files = glob.glob("*.xlsx") + glob.glob("artifacts/*.xlsx")
    for fx in xlsx_files:
        if fx not in paths_to_excel:
            paths_to_excel.append(fx)
            
    df_unified = None
    all_sheets_data = {}
    
    def clean_cols(df):
        df.columns = [str(c).strip() for c in df.columns]
        return df

    for p in paths_to_excel:
        if os.path.exists(p):
            try:
                xls = pd.ExcelFile(p)
                dfs = []
                for sh in xls.sheet_names:
                    if "dash" in sh.lower() or "توضیحات" in sh.lower():
                        continue
                    
                    df_sheet = pd.read_excel(p, sheet_name=sh)
                    if df_sheet.empty:
                        continue
                        
                    header_idx = 0
                    found_header = False
                    for idx, row in df_sheet.iterrows():
                        row_str = " ".join([str(v).lower() for val in row.values for v in [val] if pd.notna(val)])
                        keywords = ["item", "qty", "unit", "rial", "euro", "specs", "ردیف", "عنوان", "شرح", "مقدار", "تعداد", "بهای", "قیمت", "واحد"]
                        matches = sum(1 for kw in keywords if kw in row_str)
                        if matches >= 2:
                            header_idx = idx
                            found_header = True
                            break
                            
                    if found_header:
                        cols = df_sheet.iloc[header_idx].values
                        clean_columns = []
                        for col_idx, c in enumerate(cols):
                            if pd.isna(c) or str(c).strip() == "":
                                clean_columns.append(f"Column_{col_idx}")
                            else:
                                clean_columns.append(str(c).strip())
                        df_clean = df_sheet.iloc[header_idx+1:].copy()
                        df_clean.columns = clean_columns
                    else:
                        df_clean = df_sheet.copy()
                        df_clean = clean_cols(df_clean)
                        
                    df_clean = df_clean.dropna(how='all')
                    df_clean['source_sheet'] = sh
                    
                    all_sheets_data[sh] = df_clean
                    dfs.append(df_clean)
                    
                if dfs:
                    df_unified = pd.concat(dfs, ignore_index=True)
                    
                    def map_cols(df_target):
                        col_mappings = {
                            'rial_cost': ['rial_cost', 'Total Rial', 'بهای کل ریالی', 'جمع کل ریالی', 'بهای کل (ریال)', 'Rial', 'Total Rials'],
                            'euro_cost': ['euro_cost', 'Total Euro', 'بهای کل ارزی', 'جمع کل ارزی', 'بهای کل (یورو)', 'Euro', 'Total Euros'],
                            'item_name': ['item_name', 'عنوان', 'نام کالا', 'Item', 'Title'],
                            'specs': ['specs', 'Description', 'شرح تجهیزات', 'مشخصات', 'Specifications', 'Details'],
                            'quantity': ['quantity', 'Qty', 'مقدار', 'تعداد', 'Quantity'],
                            'unit': ['unit', 'Unit', 'واحد']
                        }
                        for target_col, list_of_names in col_mappings.items():
                            if target_col not in df_target.columns:
                                for name in list_of_names:
                                    found_col = [c for c in df_target.columns if c.lower() == name.lower() or c.lower().startswith(name.lower())]
                                    if found_col:
                                        df_target[target_col] = df_target[found_col[0]]
                                        break
                        return df_target
                        
                    df_unified = map_cols(df_unified)
                    break
            except Exception as e:
                pass
                
    if df_unified is None:
        csv_filename = "consolidated_material_list-v3.csv"
        paths_csv = [csv_filename, "artifacts/" + csv_filename, "/workspace/artifacts/" + csv_filename]
        for cp in paths_csv:
            if os.path.exists(cp):
                try:
                    df_unified = pd.read_csv(cp)
                    break
                except:
                    pass
                    
    if df_unified is None:
        data = {
            'discipline_en': ['Piping & Valves', 'Mechanical Equipment', 'Electrical Equipment', 'Instrumentation & Telecom', 'Cathodic Protection', 'Safety & Fire Fighting', 'Spare Parts'],
            'discipline_fa': ['لوله‌کشی و شیرآلات', 'تجهیزات مکانیکال', 'تجهیزات برقی', 'ابزار دقیق و مخابرات', 'حفاظت کاتدیک', 'ایمنی و آتش‌نشانی', 'لوازم یدکی'],
            'item_name_en': ['Pipe (8" to 28")', 'Main Booster Pumps', 'Armored SWA Cables', 'Motor Actuated Valves (MOV)', 'Smart Rectifiers', 'Flooding Systems (Inert Gas)', 'Two-Year Spares'],
            'item_name_fa': ['لوله فولادی (۵,۲۶۰ متر)', 'پمپ‌های بوستر اصلی (۵ عدد)', 'کابل‌های زره‌دار (۱۵,۶۳۰ متر)', 'شیرآلات موتوردار MOV (۵۴ عدد)', 'رکتیفایرهای هوشمند (۵ عدد)', 'سیستم‌های اطفای حریق سیلابی (۲ ست)', 'لوازم یدکی دو ساله'],
            'quantity': [5260, 5, 15630, 54, 5, 2, 3],
            'unit': ['Meters', 'NO', 'Meters', 'NO', 'NO', 'SET', 'Package'],
            'rial_cost': [0, 0, 812237187000, 26740000000, 29742500000, 0, 313000],
            'euro_cost': [1542923.88, 2337532.60, 1901290.00, 4776150.00, 0.00, 143650.00, 313000.00],
            'specs_en': ['API 5L Gr. B/X52/X60', 'Includes MP-554 Diesel 400K Euro', 'Copper armored lead covered SWA', '400VAC explosion proof', 'Auto potential Smart TR', 'Inert Gas system for control rooms', 'Two-year operating spares package'],
            'specs_fa': ['لوله‌های فولادی گرید X60 خط اصلی رفسنجان-یزد', 'پمپ دیزلی اصلی و متعلقات تلمبه‌خانه‌ها', 'کابل‌های مسی سربی زره‌دار فشار قوی', 'شیرهای توپی ابزار دقیق موتوردار برقی موو', 'رکتیفایر حفاظت کاتدی خودکار هوشمند ایستگاه‌ها', 'سیستم اطفای حریق اتوماتیک گاز بی‌اثر', 'پکیج قطعات یدکی بهره‌برداری دو ساله پروژه']
        }
        df_unified = pd.DataFrame(data)
        
    if 'item_name_fa' not in df_unified.columns:
        df_unified['item_name_en'] = df_unified['item_name'] if 'item_name' in df_unified.columns else "Sample Item"
        df_unified['item_name_fa'] = df_unified['item_name'] if 'item_name' in df_unified.columns else "کالای نمونه"
    if 'discipline_fa' not in df_unified.columns:
        df_unified['discipline_en'] = df_unified['discipline'] if 'discipline' in df_unified.columns else "Sample Discipline"
        df_unified['discipline_fa'] = df_unified['discipline'] if 'discipline' in df_unified.columns else "دیسیپلین نمونه"
    if 'specs_fa' not in df_unified.columns:
        df_unified['specs_en'] = df_unified['specs'] if 'specs' in df_unified.columns else "Sample Specs"
        df_unified['specs_fa'] = df_unified['specs'] if 'specs' in df_unified.columns else "مشخصات نمونه"
    if 'quantity' not in df_unified.columns:
        df_unified['quantity'] = 1
    if 'unit' not in df_unified.columns:
        df_unified['unit'] = "NO"
    if 'rial_cost' not in df_unified.columns:
        df_unified['rial_cost'] = 0
    if 'euro_cost' not in df_unified.columns:
        df_unified['euro_cost'] = 0
        
    return df_unified, all_sheets_data

try:
    df, all_sheets = load_and_index_excel()
    # Force float/int type conversion for financial columns to avoid TypeErrors in Pandas summing when Excel has mixed text/numeric cells
    if 'rial_cost' in df.columns:
        df['rial_cost'] = pd.to_numeric(df['rial_cost'], errors='coerce').fillna(0)
    if 'euro_cost' in df.columns:
        df['euro_cost'] = pd.to_numeric(df['euro_cost'], errors='coerce').fillna(0)
except Exception as e:
    st.error(f"خطا در لود دیتابیس متریال: {str(e)}")
    st.stop()

# Budget calculations
total_rials = df['rial_cost'].sum() + 4500000000 # Include 4.5B training budget
total_euros = df['euro_cost'].sum()
total_tomans = total_rials / 10

# ----------------- Smart Contract PDF Text Extractor -----------------
@st.cache_data
def index_contract_pdf():
    pdf_filename = "پیمان خط لوله رفسنجان یزد 1402.06.01 - Copy.pdf"
    paths_to_pdf = [
        pdf_filename,
        "artifacts/" + pdf_filename,
        "/workspace/artifacts/" + pdf_filename,
        "../" + pdf_filename
    ]
    
    pdf_files = glob.glob("*.pdf") + glob.glob("artifacts/*.pdf")
    for fp in pdf_files:
        if fp not in paths_to_pdf:
            paths_to_pdf.append(fp)
            
    pdf_text_by_page = {}
    if pypdf_available:
        for p in paths_to_pdf:
            if os.path.exists(p):
                try:
                    reader = pypdf.PdfReader(p)
                    for page_idx, page in enumerate(reader.pages):
                        extracted_text = page.extract_text()
                        if extracted_text and len(extracted_text.strip()) > 5:
                            pdf_text_by_page[page_idx + 1] = extracted_text
                    break
                except:
                    pass
    return pdf_text_by_page

pdf_indexed_pages = index_contract_pdf()

# ----------------- Fallback Contract Knowledge Base (Perfect grounding) -----------------
fallback_clauses = [
    {
        "page": 2, "section": "ماده ۳: مبلغ پیمان",
        "text": "مبلغ کل پیمان احداث خط لوله ۱۶ اینچ رفسنجان-یزد برابر است با ۷,۰۰۰,۲۴۴,۷۵۱,۰۰۰ ریال به همراه ۱۱,۰۱۴,۵۴۶ یورو.",
        "keywords": ["مبلغ", "بودجه", "قیمت", "هزینه", "ارزش", "ریال", "یورو", "قرارداد", "پیمان"]
    },
    {
        "page": 5, "section": "ماده ۵۱: نمایندگان مجاز و امضاها",
        "text": "صاحبان امضا و نمایندگان رسمی پیمان شامل: کارفرما (NIOEC): آقای فرهاد احمدی (مدیرعامل) و آقای هادی مشتهر (مدیر مالی). پیمانکار (مشارکت انهار - فرآیندسازان): آقای ستار عزیزیان تفتی (مدیرعامل انهار)، آقای مهدیار شریف شیخ‌الاسلامی (عضو هیئت مدیره انهار) و آقای حسین رهنما (مدیرعامل فرآیندسازان انرژی).",
        "keywords": ["امضا", "نماینده", "ستار عزیزیان", "حسین رهنما", "فرهاد احمدی", "مشتهر", "مدیرعامل", "صاحب", "شرکت"]
    },
    {
        "page": 1, "section": "پیوست ۱۴: مدت پیمان",
        "text": "مدت زمان اجرای خدمات و کارهای ساختمان، نصب و راه‌اندازی پروژه به روش EPC برابر با ۲۰ ماه شمسی از زمان تاریخ ابلاغ شروع به کار مصوب کارگاه‌ها تعیین گردیده است.",
        "keywords": ["مدت", "زمان", "ماه", "تاریخ", "شروع", "اجرا", "بازه"]
    },
    {
        "page": 1, "section": "پیوست ۲۱: سازوکار حل اختلاف",
        "text": "هرگونه اختلاف فنی و حقوقی ابتدا به «هیأت حل اختلاف» شامل ۵ عضو مجرب و واجد صلاحیت (کارشناس حقوقی, مالی، فنی، نماینده کارفرما و نماینده انجمن نفت ایران) ارجاع می‌گردد. در صورت عدم توافق، موضوع به مراجع قضایی ذی‌صلاح ارجاع می‌شود.",
        "keywords": ["اختلاف", "دعوا", "حل اختلاف", "هیأت", "داوری", "قضایی", "دادگاه"]
    },
    {
        "page": 1, "section": "پیوست ۸: الزامات بهداشت و ایمنی (HSE)",
        "text": "تمهیدات بهداشتی کارگاهی شامل: سم‌پاشی ماهیانه منظم کارگاه جهت مقابله با مار و عقرب گزیدگی، تجهیز جبهه‌های کاری فعال به کانکس‌های بهداشتی و مخازن آب شرب، و مجهز بودن کارگاه‌ها به آمبولانس‌های دو دیفرانسیل کوهستانی.",
        "keywords": ["ایمنی", "بهداشت", "سلامت", "hse", "سم‌پاشی", "آمبولانس", "عقرب", "مار", "کانکس"]
    },
    {
        "page": 2, "section": "پیوست ۱۲: انتقال فناوری و سیستم PMIS",
        "text": "پیمانکار متعهد به ارائه برنامه جامع انتقال فناوری و آموزش کارکنان کارفرما (با بودجه مصوب ۴,۵۰۰,۰۰۰,۰۰۰ ریال) است. همچنین راه‌اندازی سیستم مدیریت اطلاعات پروژه (PMIS) تحت وب جهت کنترل آنلاین اسناد مهندسی الزامی است.",
        "keywords": ["آموزش", "فناوری", "انتقال فناوری", "pmis", "سیستم", "مدیریت", "نرم‌افزار"]
    }
]

# ----------------- Universal Semantic Q&A Search Engine -----------------
def answer_user_query(query_text):
    q = query_text.lower().strip()
    if len(q) < 2:
        return "لطفاً سوال خود را با جزئیات بیشتری بنویسید.", "پاسخ عمومی"
        
    results_excel = []
    results_pdf = []
    
    if pdf_indexed_pages:
        for page_num, content in pdf_indexed_pages.items():
            if q in content.lower():
                paragraphs = content.split('\\n')
                for p in paragraphs:
                    if q in p.lower():
                        results_pdf.append({
                            "page": page_num,
                            "section": f"صفحه {page_num} کتابچه پیمان",
                            "text": p.strip()
                        })
    
    for cl in fallback_clauses:
        matches = sum(1 for kw in cl["keywords"] if kw in q)
        if matches >= 1:
            results_pdf.append(cl)
            
    for col in df.columns:
        if df[col].dtype == object:
            matches_df = df[df[col].astype(str).str.lower().str.contains(q, na=False)]
            if not matches_df.empty:
                for idx, r in matches_df.head(5).iterrows():
                    sheet_name = r['source_sheet'] if 'source_sheet' in df.columns else "خلاصه کل"
                    name_fa = r['item_name_fa'] if 'item_name_fa' in df.columns else (r['item_name'] if 'item_name' in df.columns else "کالا")
                    specs_fa = r['specs_fa'] if 'specs_fa' in df.columns else (r['specs'] if 'specs' in df.columns else "")
                    qty = r['quantity'] if 'quantity' in df.columns else "N/A"
                    unit = r['unit'] if 'unit' in df.columns else "واحد"
                    rial = r['rial_cost'] if 'rial_cost' in df.columns else 0
                    euro = r['euro_cost'] if 'euro_cost' in df.columns else 0
                    
                    results_excel.append({
                        "sheet": sheet_name,
                        "item": name_fa,
                        "specs": specs_fa,
                        "qty": qty,
                        "unit": unit,
                        "rial": rial,
                        "euro": euro
                    })
                    
    response_html = ""
    voice_txt = ""
    
    if results_pdf:
        best_pdf = results_pdf[0]
        response_html += f"""
        <div style='border-bottom: 1px dashed rgba(255,255,255,0.1); padding-bottom:10px; margin-bottom: 10px;'>
            <b>📚 مستندات حقوقی پیمان یافت شد ({best_pdf['section']}):</b><br>
            <p style='color: #a78bfa; margin-top:5px;'>« {best_pdf['text']} »</p>
        </div>
        """
        voice_txt += best_pdf['text'] + ". "
        
    if results_excel:
        response_html += "<b>📊 ریز تجهیزات و برآوردهای مالی در ردیف‌های شیت تدارکات:</b><br><ul style='margin-top:5px; padding-right:15px;'>"
        for r_ex in results_excel[:3]:
            cost_str = ""
            if r_ex['rial'] > 0:
                cost_str += f"بهای ریالی: {r_ex['rial']:,.0f} ریال"
            if r_ex['euro'] > 0:
                if cost_str: cost_str += " | "
                cost_str += f"بهای ارزی: {r_ex['euro']:,.2f} یورو"
            response_html += f"""
            <li style='margin-bottom:8px;'>
                <b>شیت اکسل '{r_ex['sheet']}':</b> {r_ex['item']}<br>
                <small style='color: #8a7e72;'>مقدار: {r_ex['qty']} {r_ex['unit']} | {cost_str}</small><br>
                <small style='color: #00f0ff;'><i>مشخصات فنی: {r_ex['specs']}</i></small>
            </li>
            """
        response_html += "</ul>"
        voice_txt += f"ریز اقلام مربوط به دیسیپلین تدارکات و کالا در شیت‌های اکسل پروژه با مبالغ ارزی و ریالی تراز شده یافت گردید."
        
    if not results_pdf and not results_excel:
        web_info = online_search(query_text)
        if web_info:
            response_html = f"""
            🌐 <b>پاسخ یافت شده از موتور جستجوی هوشمند رز در فضای وب:</b><br><br>
            {web_info}<br><br>
            <i>نکته: به دلیل عدم ثبت این موضوع در اسناد محلی تدارکاتی خط لوله رفسنجان-یزد، اطلاعات از فضای وب استخراج گردید.</i>
            """
            voice_txt = "اطلاعات متناظر از شبکه جهانی وب استخراج شد."
        else:
            response_html = """
            ❌ <b>منظور شما را متوجه نشدم. من اطلاعات جامع موافقت‌نامه پیمان خط لوله و ریز تجهیزات ۳۰ شیت اکسل متریال را دارم.</b><br><br>
            <b>چند سوال نمونه:</b><br>
            • 'مبلغ کل قرارداد چقدر است؟'<br>
            • 'چه کسانی نمایندگان مجاز امضا هستند؟'<br>
            • 'مشخصات شیرآلات خودکار (Check Valves) چیست؟'<br>
            • 'الزامات بهداشت و ایمنی کارگاه‌ها شامل چه مواردی است؟'<br>
            • 'سیستم حل اختلاف به چه صورت است؟'
            """
            voice_txt = "منظور شما را متوجه نشدم. لطفا درباره قیمت، امضا کنندگان یا مشخصات کالاها بپرسید."
            
    return response_html, voice_txt

# ----------------- Title Layout -----------------
st.markdown("<h1 class='main-title'>🌹 پورتال سخنگو و متحرک دستیار هوشمند رُز (ROSE AI)</h1>", unsafe_allow_html=True)
st.markdown(f"<h4 class='sub-title'>پورتال تراز تدارکاتی و پیمان احداث خط لوله ۱۶ اینچ رفسنجان-یزد • پوسته فعال: {st.session_state['app_theme']}</h4>", unsafe_allow_html=True)

# ----------------- Sidebar Controls -----------------
with st.sidebar:
    st.markdown("### 🌹 سیمای متحرک رز")
    
    if 'rose_state' not in st.session_state:
        st.session_state['rose_state'] = 'idle'
        
    rose_svg = get_svg_avatar(st.session_state['rose_state'])
    st.markdown(
        f'''
        <div class="avatar-container">
            <div class="avatar-glow"></div>
            <img class="svg-avatar" src="data:image/svg+xml;base64,{rose_svg}" alt="Rose Live">
        </div>
        ''',
        unsafe_allow_html=True
    )
    st.markdown(f"<div style='text-align: center; color: {theme['primary']}; font-weight: bold;'>رُز | ROSE AI v13</div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; color: #8a7e72; font-size: 13px; margin-bottom: 15px;'>دستیار صوتی و حقوقی دوزبانه پروژه</div>", unsafe_allow_html=True)
    
    if st.session_state['rose_state'] == 'speaking':
        st.markdown(
            '''
            <div class="equalizer">
                <div class="bar"></div>
                <div class="bar"></div>
                <div class="bar"></div>
                <div class="bar"></div>
                <div class="bar"></div>
            </div>
            ''',
            unsafe_allow_html=True
        )
        
    st.markdown("---")
    st.markdown("### 🎨 جعبه‌ابزار شخصی‌سازی (تم)")
    theme_choice = st.selectbox("پوسته رنگی پورتال:", list(themes.keys()), index=list(themes.keys()).index(st.session_state['app_theme']))
    if theme_choice != st.session_state['app_theme']:
        st.session_state['app_theme'] = theme_choice
        st.rerun()
        
    st.markdown("---")
    st.markdown("### 🔊 فعال‌سازی سخنگوی صوتی رز")
    voice_enabled = st.toggle("روشن بودن حنجره صوتی رز", value=True)
    
    st.markdown("---")
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Material_Summary_v13')
        
    st.download_button(
        label="📥 دانلود شیت تراز کالاها (Excel)",
        data=buffer.getvalue(),
        file_name="epc_material_valuation_consolidated.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

# ----------------- Dynamic Responsive KPI Indicators -----------------
st.write("")
kpi_html = f'''
<div style="display: flex; flex-wrap: wrap; gap: 15px; width: 100%;">
    <div class="kpi-card-custom" style="flex: 1 1 calc(33.333% - 15px); min-width: 250px;">
        <div style="color: #8a7e72; font-size: 14px; font-weight: bold;">💰 برآورد ریالی پیمان (Rial Value)</div>
        <div style="color: {theme['primary']}; font-size: 22px; font-weight: bold; margin-top: 5px;">{total_rials:,.0f} ریال</div>
        <div style="color: #8a7e72; font-size: 12px;">معادل {total_tomans:,.0f} تومان (۱۰ ریال = ۱ تومان)</div>
    </div>
    <div class="kpi-card-custom" style="flex: 1 1 calc(33.333% - 15px); min-width: 250px;">
        <div style="color: #8a7e72; font-size: 14px; font-weight: bold;">💶 برآورد ارزی پیمان (Euro Value)</div>
        <div style="color: {theme['primary']}; font-size: 22px; font-weight: bold; margin-top: 5px;">{total_euros:,.2f} یورو</div>
        <div style="color: #8a7e72; font-size: 12px;">تأمین ۱۰۰٪ ارزی لوله‌ها و شیرآلات وارداتی</div>
    </div>
    <div class="kpi-card-custom" style="flex: 1 1 calc(33.333% - 15px); min-width: 250px;">
        <div style="color: #8a7e72; font-size: 14px; font-weight: bold;">⏳ مدت زمان پیمان (Duration)</div>
        <div style="color: {theme['secondary']}; font-size: 22px; font-weight: bold; margin-top: 5px;">⏳ ۲۰ ماه شمسی</div>
        <div style="color: #8a7e72; font-size: 12px;">از تاریخ شروع به کار ابلاغی کارگاه‌ها</div>
    </div>
</div>
'''
st.markdown(kpi_html, unsafe_allow_html=True)

st.write("")

# ----------------- Main Interface Tabs -----------------
tab1, tab2, tab3 = st.tabs(["💬 دستیار صوتی و چت هوشمند رز", "🗂️ بندها و پیوست‌های قرارداد رسمی", "🔍 جستجو و فیلتر متریال پروژه"])

# ----------------- TAB 1: Live Chat Bot with Word-by-Word Stream & Voice -----------------
with tab1:
    st.markdown("### 💬 مکالمه صوتی و متنی با دستیار هوشمند رز")
    st.write("دکمه میکروفون زیر را لمس کنید تا مکالمه مداوم و هوشمند (Live Continuous Mode) فعال شود. رز همانند جمینای لایو بدون قطع شدن با شما گفتگو می‌کند:")
    
    st_html_mic_code = f"""
    <div style="text-align: center; direction: rtl; padding: 10px; background-color: rgba(255,255,255,0.01); border-radius: 8px; border: 1px dashed {theme['primary']}50;">
        <button id="mic_btn" style="background-color: {theme['bg']}; border: 2px solid {theme['primary']}; border-radius: 50%; width: 65px; height: 65px; cursor: pointer; box-shadow: 0 0 15px {theme['primary']}40; outline: none; transition: all 0.3s ease-in-out;">
            <span id="mic_icon" style="font-size: 28px;">🎙️</span>
        </button>
        <p id="mic_status" style="color: #8a7e72; font-size: 13px; margin-top: 10px; font-family: 'Vazirmatn', sans-serif; font-weight: bold;">مکالمه مداوم غیرفعال است. جهت شروع کلیک کنید...</p>
        <div id="interim_preview" style="color: {theme['primary']}; font-size: 14px; margin-top: 5px; font-style: italic; min-height: 20px;"></div>
    </div>
    
    <script>
        const btn = document.getElementById('mic_btn');
        const status = document.getElementById('mic_status');
        const icon = document.getElementById('mic_icon');
        const preview = document.getElementById('interim_preview');
        
        let recognition;
        let isListening = false;
        let silenceTimer;
        
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {{
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'fa-IR';
            
            btn.addEventListener('click', () => {{
                if (isListening) {{
                    stopVoiceLoop();
                }} else {{
                    startVoiceLoop();
                }}
            }});
            
            function startVoiceLoop() {{
                try {{
                    recognition.start();
                    isListening = true;
                    status.innerHTML = "🔴 مکالمه زنده و مداوم فعال است. صحبت کنید...";
                    icon.innerHTML = "🛑";
                    btn.style.borderColor = "{theme['secondary']}";
                    btn.style.boxShadow = "0 0 25px {theme['secondary']}80";
                    window.speechSynthesis.cancel();
                }} catch(e) {{
                    console.log(e);
                }}
            }}
            
            function stopVoiceLoop() {{
                recognition.stop();
                isListening = false;
                status.innerHTML = "🎙️ مکالمه مداوم غیرفعال شد.";
                icon.innerHTML = "🎙️";
                btn.style.borderColor = "{theme['primary']}";
                btn.style.boxShadow = "0 0 15px {theme['primary']}40";
                preview.innerHTML = "";
            }}
            
            recognition.onresult = (event) => {{
                let interimTranscript = '';
                let finalTranscript = '';
                
                for (let i = event.resultIndex; i < event.results.length; ++i) {{
                    if (event.results[i].isFinal) {{
                        finalTranscript += event.results[i][0].transcript;
                    }} else {{
                        interimTranscript += event.results[i][0].transcript;
                    }}
                }}
                
                if (interimTranscript) {{
                    preview.innerHTML = "میشنوم: " + interimTranscript;
                }}
                
                if (finalTranscript.trim() || interimTranscript.trim()) {{
                    clearTimeout(silenceTimer);
                    silenceTimer = setTimeout(() => {{
                        const query = finalTranscript || interimTranscript;
                        if (query.trim().length > 1) {{
                            preview.innerHTML = "💬 در حال ارسال درخواست شما...";
                            
                            const streamlitInput = window.parent.document.querySelector('input[data-testid="stTextInput"]');
                            if (streamlitInput) {{
                                streamlitInput.value = query.trim();
                                streamlitInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                streamlitInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            }}
                            stopVoiceLoop();
                        }}
                    }}, 1400); // 1.4 seconds of silence triggers submission
                }}
            }};
            
            recognition.onerror = (event) => {{
                console.log("Error: " + event.error);
                if (event.error === 'no-speech') {{
                    status.innerHTML = "🔴 صدایی شنیده نشد. همچنان گوش به زنگم...";
                }}
            }};
            
            recognition.onend = () => {{
                if (isListening) {{
                    try {{ recognition.start(); }} catch(e) {{}}
                }}
            }};
        }} else {{
            status.innerHTML = "⚠️ مرورگر شما از مکالمه مستقیم صوتی پشتیبانی نمی‌کند. از کیبورد گوشی استفاده کنید.";
            btn.style.opacity = 0.5;
            btn.style.cursor = "not-allowed";
        }}
    </script>
    """
    st.components.v1.html(st_html_mic_code, height=140)
    
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
        
    user_query = st.text_input("📝 پیام متنی یا صوتی تبدیل شده شما:", key="rose_user_query", placeholder="اینجا بنویسید یا دکمه میکروفون بالا را لمس کنید...")
    
    if user_query:
        if not st.session_state['chat_history'] or st.session_state['chat_history'][-1]['user'] != user_query:
            st.session_state['rose_state'] = 'thinking'
            
            answer_html, voice_text = answer_user_query(user_query)
            
            st.session_state['chat_history'].append({
                "user": user_query,
                "rose_html": answer_html,
                "voice_text": voice_text
            })
            
            st.session_state['rose_state'] = 'speaking'
            st.rerun()

    for chat in reversed(st.session_state['chat_history']):
        st.markdown(f"<div class='chat-bubble-user'>👤 <b>سوال شما:</b> {chat['user']}</div>", unsafe_allow_html=True)
        
        if chat == st.session_state['chat_history'][-1] and st.session_state['rose_state'] == 'speaking':
            placeholder = st.empty()
            import re
            # Clean HTML tags safely using regex to prevent any syntax errors
            raw_text = chat['rose_html'].replace('<br>', '\n').replace('<li>', '\n • ')
            raw_text = re.sub(r'<[^>]+>', '', raw_text)
            words = raw_text.split()
            streamed_text = ""
            for word in words:
                streamed_text += word + " "
                placeholder.markdown(f"<div class='chat-bubble-rose'>🌹 <b>دستیار رز:</b><br><br>{streamed_text.replace('\\n', '<br>')} ▌</div>", unsafe_allow_html=True)
                time.sleep(0.03)
            placeholder.markdown(f"<div class='chat-bubble-rose'>🌹 <b>دستیار رز:</b><br><br>{chat['rose_html']}</div>", unsafe_allow_html=True)
            
            if voice_enabled and chat['voice_text']:
                cleaned_voice = chat['voice_text'].replace('"', '\\"').replace('\\n', ' ')
                tts_js_code = f"""
                <script>
                    const utterance = new SpeechSynthesisUtterance("{cleaned_voice}");
                    utterance.lang = 'fa-IR';
                    utterance.rate = 1.05;
                    utterance.pitch = 1.0;
                    
                    utterance.onend = function() {{
                        // Notify Streamlit speech finished and restart listening automatically
                        console.log("Speech synthesis finished");
                    }};
                    window.speechSynthesis.speak(utterance);
                </script>
                """
                st.components.v1.html(tts_js_code, height=0)
            
            st.session_state['rose_state'] = 'idle'
        else:
            st.markdown(f"<div class='chat-bubble-rose'>🌹 <b>دستیار رز:</b><br><br>{chat['rose_html']}</div>", unsafe_allow_html=True)

# ----------------- TAB 2: Interactive Contract Clauses -----------------
with tab2:
    st.markdown("### 🗂️ بندها و پیوست‌های قرارداد رسمی احداث خط لوله ۱۶ اینچ رفسنجان-یزد")
    st.write("پنج صفحه حقوقی و اسناد تصویری پیمان به صورت کارت‌های تعاملی شیشه‌ای و دکمه‌های پاسخگو برنامه‌نویسی شده‌اند. برای مشاهده بندها کلیک کنید:")
    
    c_page1, c_page2, c_page3 = st.columns(3)
    with c_page1:
        with st.expander("📄 صفحه ۱: مشخصات ثبتی و ارگان‌ها"):
            st.write("**شرکت ساختمانی انهار (رهبر مشارکت):** شماره ثبت ۸۳۲ و کد ثبتی ۱۰۸۶.")
            st.write("**مهندسین مشاور فرآیند سازان انرژی:** شماره ثبت ۱۸۷۸۶۶.")
            st.write("**موضوع دقیق قرارداد:** طراحی، خرید و ساخت (EPC) خط لوله ۱۶ اینچ و تاسیسات جانبی تلمبه‌خانه‌ها.")
            if st.button("🔍 ارسال سوال مربوطه به رز", key="btn_c1"):
                st.session_state['rose_user_query'] = "چه کسانی قرارداد را امضا کرده‌اند؟"
                st.rerun()
                
    with c_page2:
        with st.expander("📄 صفحه ۲: مبالغ و زمان‌بندی کلان"):
            st.write("**مبلغ ریالی کل:** ۷,۰۰۰,۲۴۴,۷۵۱,۰۰۰ ریال")
            st.write("**مبلغ ارزی کل:** ۱۱,۰۱۴,۵۴۶ یورو")
            st.write("**مدت زمان پروژه:** ۲۰ ماه شمسی")
            if st.button("🔍 ارسال سوال مربوطه به رز", key="btn_c2"):
                st.session_state['rose_user_query'] = "مبلغ قرارداد چقدر است؟"
                st.rerun()
                
    with c_page3:
        with st.expander("📄 صفحه ۳: تضامین و سهم‌الشرکه"):
            st.write("**سهم‌الشرکه طراحی مهندسی (E):** ۱۰۰٪ فرآیندسازان انرژی.")
            st.write("**سهم‌الشرکه خرید و ساخت (P&C):** ۱۰۰٪ شرکت ساختمانی انهار.")
            st.write("**ضمانت‌نامه حسن انجام تعهدات:** ۵٪ مبلغ کل پیمان از بانک ملت.")
            if st.button("🔍 ارسال سوال مربوطه به رز", key="btn_c3"):
                st.session_state['rose_user_query'] = "ضمانت‌نامه قرارداد چیست؟"
                st.rerun()
                
    c_page4, c_page5 = st.columns(2)
    with c_page4:
        with st.expander("📄 صفحه ۴: حل اختلاف و داوری"):
            st.write("**ارجاع به هیأت حل اختلاف:** طبق پیوست ۲۱ پیمان.")
            st.write("**تعداد اعضا:** ۵ نفر متشکل از کارشناس حقوقی، مالی، فنی، نماینده کارفرما و نماینده انجمن نفت ایران.")
            if st.button("🔍 ارسال سوال مربوطه به رز", key="btn_c4"):
                st.session_state['rose_user_query'] = "سازوکار حل اختلاف چیست؟"
                st.rerun()
                
    with c_page5:
        with st.expander("📄 صفحه ۵: هزینه‌های دفترخانه ثبتی"):
            st.write("**محل ثبت:** دفتر اسناد رسمی شماره ۷۰۱ تهران.")
            st.write("**مجموع هزینه‌های دفتری:** ۱,۶۹۸,۰۰۰ ریال شامل حق‌الثبت و حق‌التحریر.")
            st.write("**امضاکنندگان:** فرهاد احمدی، ستار عزیزیان تفتی، حسین رهنما.")
            if st.button("🔍 ارسال سوال مربوطه به رز", key="btn_c5"):
                st.session_state['rose_user_query'] = "هزینه‌های ثبتی دفترخانه چقدر است؟"
                st.rerun()

# ----------------- TAB 3: Advanced Material Grid Search -----------------
with tab3:
    st.markdown("### 🔍 جستجو و فیلتر پیشرفته در تمام ۳۰ شیت اکسل متریال پروژه")
    st.write("این ابزار به شما اجازه می‌دهد ریز اقلام لود شده را فیلتر کنید:")
    
    sheet_list = ["همه شیت‌ها"] + list(all_sheets.keys() if all_sheets else ["Piping & Valves", "Mechanical", "Electrical", "Instrumentation", "Cathodic Protection", "Safety & Fire Fighting", "Spare Parts"])
    selected_sh = st.selectbox("📂 انتخاب شیت اکسل تفصیلی:", sheet_list)
    
    term = st.text_input("🔍 جستجوی متنی کالا (مثال: 16, Cable, Valve, MOV):", key="grid_search_term")
    
    filtered_df = df.copy()
    if selected_sh != "همه شیت‌ها":
        if 'source_sheet' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['source_sheet'] == selected_sh]
            
    if term:
        filtered_df = filtered_df[
            filtered_df['item_name_fa'].str.contains(term, case=False, na=False) |
            filtered_df['item_name_en'].str.contains(term, case=False, na=False) |
            filtered_df['specs_fa'].str.contains(term, case=False, na=False) |
            filtered_df['specs_en'].str.contains(term, case=False, na=False)
        ]
        
    st.write(f"📊 تعداد **{len(filtered_df)} ردیف متریال** با فیلتر شما همخوانی دارد:")
    
    display_df = filtered_df.copy()
    display_df['rial_cost'] = display_df['rial_cost'].apply(lambda x: f"{x:,.0f} ریال" if x > 0 else "0")
    display_df['euro_cost'] = display_df['euro_cost'].apply(lambda x: f"{x:,.2f} €" if x > 0 else "0")
    
    display_cols = ['discipline_fa', 'item_name_fa', 'item_name_en', 'quantity', 'unit', 'rial_cost', 'euro_cost', 'specs_fa']
    available_cols = [c for c in display_cols if c in display_df.columns]
    st.dataframe(display_df[available_cols], use_container_width=True)
    
    csv_data = filtered_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 دانلود اطلاعات فیلتر شده بالا (CSV)",
        data=csv_data,
        file_name="filtered_material_list.csv",
        mime="text/csv",
        use_container_width=True
    )

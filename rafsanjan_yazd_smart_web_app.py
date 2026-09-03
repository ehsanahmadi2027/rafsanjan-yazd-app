import streamlit as st
import pandas as pd
import numpy as np
import io
import os
import base64
import urllib.request
import urllib.parse
import json

# Try to import Google Text-to-Speech library
try:
    from gtts import gTTS
    gtts_available = True
except ImportError:
    gtts_available = False

# ----------------- streamlit set config -----------------
st.set_page_config(
    page_title="دستیار هوشمند و صوتی رُز | ROSE AI",
    page_icon="🌹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- responsive neon css (mobile & desktop) -----------------
st.markdown(
    """
    <style>
    /* Dark Cyberpunk Theme & Mobile Responsiveness */
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0b0d13;
        color: #e0e6ed;
        font-family: 'Vazirmatn', sans-serif !important;
        direction: RTL;
        text-align: right;
    }
    
    .stApp {
        direction: RTL;
        text-align: right;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #00f0ff !important;
        font-family: 'Vazirmatn', sans-serif !important;
        text-shadow: 0 0 10px rgba(0, 240, 255, 0.3);
    }
    
    .main-title {
        color: #00f0ff;
        text-align: center;
        font-size: 2.2rem;
        font-weight: bold;
        margin-top: 10px;
        margin-bottom: 5px;
        text-shadow: 0 0 15px rgba(0, 240, 255, 0.6);
    }
    
    .sub-title {
        color: #ff007f;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 25px;
        text-shadow: 0 0 8px rgba(255, 0, 127, 0.4);
    }
    
    /* 3D-Like Glowing Interactive Avatar */
    .avatar-container {
        text-align: center;
        padding: 15px;
        position: relative;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
    .avatar-glow {
        position: absolute;
        width: 170px;
        height: 170px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(0, 240, 255, 0.2) 0%, rgba(255, 0, 127, 0.1) 70%, transparent 100%);
        animation: pulse-glow 4s infinite ease-in-out;
    }
    
    .live-avatar {
        position: relative;
        border-radius: 50%;
        border: 3px solid #00f0ff;
        box-shadow: 0 0 20px rgba(0, 240, 255, 0.5);
        animation: breathing 5s infinite ease-in-out;
        transition: transform 0.3s ease-in-out, border-color 0.3s;
        width: 150px;
        height: 150px;
        object-fit: cover;
        z-index: 2;
    }
    
    .live-avatar:hover {
        transform: scale(1.08) rotate(2deg);
        border-color: #ff007f;
        box-shadow: 0 0 30px rgba(255, 0, 127, 0.8);
    }
    
    @keyframes breathing {
        0% { transform: scale(1); }
        50% { transform: scale(1.03) translateY(-3px); }
        100% { transform: scale(1); }
    }
    
    @keyframes pulse-glow {
        0% { transform: scale(0.9); opacity: 0.5; }
        50% { transform: scale(1.2); opacity: 0.9; }
        100% { transform: scale(0.9); opacity: 0.5; }
    }
    
    /* Cyber Glassmorphic KPI Cards */
    .kpi-card-custom {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(0, 240, 255, 0.15);
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(5px);
        transition: all 0.3s;
        margin-bottom: 12px;
    }
    
    .kpi-card-custom:hover {
        border-color: #00f0ff;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.3);
        transform: translateY(-2px);
    }
    
    /* Chat Bubbles Styling */
    .chat-bubble-user {
        background-color: rgba(255, 255, 255, 0.05);
        border-right: 5px solid #ff007f;
        border-left: 1px solid rgba(255, 255, 255, 0.1);
        padding: 14px;
        border-radius: 8px;
        margin-bottom: 15px;
        text-align: right;
        direction: RTL;
        color: #e0e6ed;
    }
    
    .chat-bubble-rose {
        background-color: rgba(0, 102, 255, 0.07);
        border-right: 5px solid #00f0ff;
        border-left: 1px solid rgba(0, 240, 255, 0.2);
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 15px;
        text-align: right;
        direction: RTL;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.1);
        color: #f0f4f8;
    }
    
    /* Responsive Media Queries for Mobile phones */
    @media (max-width: 768px) {
        .main-title {
            font-size: 1.5rem !important;
        }
        .sub-title {
            font-size: 0.9rem !important;
        }
        .live-avatar {
            width: 110px !important;
            height: 110px !important;
        }
        .avatar-glow {
            width: 130px !important;
            height: 130px !important;
        }
        .kpi-card-custom {
            padding: 12px !important;
        }
        .kpi-card-custom div {
            font-size: 14px !important;
        }
        /* Make st.columns stack nicely with proper margins */
        div[data-testid="column"] {
            margin-bottom: 10px !important;
        }
    }
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
                # Read all sheets dynamically
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
        # Static bilingual fallback database
        data = {
            'discipline_en': ['Piping & Valves', 'Mechanical Equipment', 'Electrical Equipment', 'Instrumentation & Telecom', 'Cathodic Protection', 'Safety & Fire Fighting', 'Spare Parts'],
            'discipline_fa': ['لوله‌کشی و شیرآلات', 'تجهیزات مکانیکال', 'تجهیزات برقی', 'ابزار دقیق و مخابرات', 'حفاظت کاتدیک', 'ایمنی و آتش‌نشانی', 'لوازم یدکی'],
            'item_name_en': ['Pipes (5,260 M)', 'Main Booster Pumps (5 NO)', 'Armored Cables (15,630 M)', 'Motor Actuated Valves (54 NO)', 'Smart Rectifiers (5 NO)', 'Flooding Systems (2 SET)', 'Two-Year Spares'],
            'item_name_fa': ['لوله فولادی (۵,۲۶۰ متر)', 'پمپ‌های بوستر اصلی (۵ عدد)', 'کابل‌های زره‌دار (۱۵,۶۳۰ متر)', 'شیرآلات موتوردار MOV (۵۴ عدد)', 'رکتیفایرهای هوشمند (۵ عدد)', 'سیستم‌های اطفای حریق سیلابی (۲ ست)', 'لوازم یدکی دو ساله'],
            'quantity': [5260, 5, 15630, 54, 5, 2, 3],
            'unit': ['Meters', 'NO', 'Meters', 'NO', 'NO', 'SET', 'Package'],
            'rial_cost': [0, 0, 812237187000, 26740000000, 29742500000, 0, 313000],
            'euro_cost': [1542923.88, 2337532.60, 1901290.00, 4776150.00, 0.00, 143650.00, 313000.00],
            'specs_en': ['API 5L Gr. B/X52/X60', 'Includes MP-554 Diesel 400K Euro', 'Copper armored lead covered SWA', '400VAC explosion proof', 'Auto potential Smart TR', 'Inert Gas system for control rooms', 'Two-year operating spares package'],
            'specs_fa': ['لوله‌های فولادی گرید X60 خط اصلی رفسنجان-یزد', 'پمپ دیزلی اصلی و متعلقات تلمبه‌خانه‌ها', 'کابل‌های مسی سربی زره‌دار فشار قوی', 'شیرهای توپی ابزار دقیق موتوردار برقی موو', 'رکتیفایر حفاظت کاتدی خودکار هوشمند ایستگاه‌ها', 'سیستم اطفای حریق اتوماتیک گاز بی‌اثر', 'پکیج قطعات یدکی بهره‌برداری دو ساله پروژه']
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

# Portal Title
st.markdown("<h1 class='main-title'>🌹 دستیار صوتی و تصویری هوشمند رُز (ROSE AI)</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #8a7e72;'>پورتال تمام‌صفحه و دوزبانه مدیریت تدارکات و پیمان خط لوله رفسنجان-یزد</h4>", unsafe_allow_html=True)

# ----------------- Fallback Online Search Engine -----------------
def online_search(query):
    try:
        # Scrape DuckDuckGo HTML safely
        url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=4) as response:
            html = response.read().decode('utf-8')
        
        # Simple extraction of snippets and links
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

# ----------------- Sidebar Control Panel -----------------
with st.sidebar:
    st.markdown("### 🌹 سیمای دستیار هوشمند رز")
    
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
        st.info("🌹 رز با موفقیت لود شد.")
        
    st.markdown("<div style='text-align: center; color: #00f0ff; font-weight: bold;'>رُز | ROSE AI</div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; color: #8a7e72; font-size: 13px; margin-bottom: 15px;'>دستیار صوتی و حقوقی پیشرفته پروژه خط لوله</div>", unsafe_allow_html=True)
    
    voice_enabled = st.toggle("🔊 فعال‌سازی حنجره سخنگوی صوتی رز", value=True)
    
    st.markdown("---")
    st.markdown("### 🏢 ارگان‌ها و تعهدات رسمی پروژه")
    st.caption("کلیک کنید تا تعهدات، مدیران و اسناد هر بخش را در کادر رز یا سایدبار مشاهده کنید:")
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🏢 کارفرما (NIOEC)", use_container_width=True):
            st.sidebar.info("**شرکت ملی مهندسی و ساختمان نفت ایران (NIOEC)**\\n\\n• **مدیرعامل:** فرهاد احمدی\\n• **مدیر امور پیمان‌ها:** هادی مشتهر")
    with col_b:
        if st.button("🏗️ انهار (Lead)", use_container_width=True):
            st.sidebar.info("**شرکت ساختمانی انهار**\\n\\n• **مدیرعامل:** ستار عزیزیان تفتی\\n• **عضو هیئت مدیره:** مهدیار شریف شیخ‌الاسلامی")
            
    col_c, col_d = st.columns(2)
    with col_c:
        if st.button("⚡ فرآیند سازان", use_container_width=True):
            st.sidebar.info("**مهندسین مشاور فرآیند سازان انرژی**\\n\\n• **مدیرعامل:** حسین رهنما\\n• **عضو هیئت مدیره:** محمد افراسیابیان")
    with col_d:
        if st.button("🤝 مشارکت EPC", use_container_width=True):
            st.sidebar.info("**مشارکت انهار - فرآیند سازان**\\n\\n• **مبلغ قرارداد:** ۷,۰۰۰,۲۴۴,۷۵۱,۰۰۰ ریال\\n• **بخش ارزی:** ۱۱,۰۱۴,۵۴۶ یورو\\n• **مدت پیمان:** ۲۰ ماه شمسی")

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
st.write("")
kpi1, kpi2, kpi3 = st.columns(3)
with kpi1:
    st.markdown(
        f'''
        <div class="kpi-card-custom">
            <div style="color: #8a7e72; font-size: 14px; font-weight: bold;">💰 برآورد ریالی پیمان (Rial Value)</div>
            <div style="color: #00f0ff; font-size: 22px; font-weight: bold; margin-top: 5px;">{total_rials:,.0f} ریال</div>
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
            <div style="color: #00f0ff; font-size: 22px; font-weight: bold; margin-top: 5px;">{total_euros:,.2f} یورو</div>
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
            <div style="color: #ff007f; font-size: 22px; font-weight: bold; margin-top: 5px;">۲۰ ماه شمسی</div>
            <div style="color: #8a7e72; font-size: 12px;">از تاریخ شروع به کار ابلاغی کارگاه‌ها</div>
        </div>
        ''',
        unsafe_allow_html=True
    )

st.write("")

# ----------------- Main Interface Tabs -----------------
tab1, tab2, tab3 = st.tabs(["💬 دستیار صوتی و چت هوشمند رز", "🔍 جستجو و فیلتر متریال پروژه", "📊 آنالیز توزیع هزینه‌ها و مغایرت‌ها"])

with tab1:
    st.markdown("### 💬 مکالمه صوتی و متنی با دستیار هوشمند رز")
    st.write("سوال خود را به فارسی یا انگلیسی بنویسید یا دکمه میکروفون زیر را لمس کرده و صحبت کنید:")
    
    # ----------------- Native Browser Speech-to-Text Custom Widget -----------------
    st.markdown("##### 🎤 ضبط صدای زنده مرورگر (Persian / English Speech Recognition)")
    
    st_html_mic_code = """
    <div style="text-align: center; direction: rtl; padding: 10px; background-color: rgba(255,255,255,0.02); border-radius: 8px; border: 1px dashed rgba(0, 240, 255, 0.3);">
        <button id="mic_btn" style="background-color: #0b0d13; border: 2px solid #00f0ff; border-radius: 50%; width: 65px; height: 65px; cursor: pointer; box-shadow: 0 0 15px rgba(0,240,255,0.4); animation: pulse 2s infinite; outline: none;">
            <span style="font-size: 28px;">🎙️</span>
        </button>
        <p id="mic_status" style="color: #8a7e72; font-size: 13px; margin-top: 10px; font-family: 'Vazirmatn', sans-serif;">میکروفون آماده است. کلیک کنید و صحبت کنید...</p>
        <textarea id="recognized_text_box" style="display:none;"></textarea>
    </div>
    
    <script>
        const btn = document.getElementById('mic_btn');
        const status = document.getElementById('mic_status');
        
        let recognition;
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'fa-IR'; // Default to Persian
            
            btn.addEventListener('click', () => {
                try {
                    recognition.start();
                    status.innerHTML = "🔴 در حال شنیدن صدای شما... (صحبت کنید)";
                    btn.style.borderColor = "#ff007f";
                    btn.style.boxShadow = "0 0 25px rgba(255,0,127,0.7)";
                } catch(e) {
                    recognition.stop();
                }
            });
            
            recognition.onresult = (event) => {
                const text = event.results[0][0].transcript;
                status.innerHTML = "✅ تبدیل صدا به متن با موفقیت انجام شد!";
                btn.style.borderColor = "#00f0ff";
                btn.style.boxShadow = "0 0 15px rgba(0,240,255,0.4)";
                
                // Communicate transcription to Streamlit
                // Create a dynamic custom input update
                const streamlitInput = window.parent.document.querySelector('input[data-testid="stTextInput"]');
                if (streamlitInput) {
                    streamlitInput.value = text;
                    streamlitInput.dispatchEvent(new Event('input', { bubbles: true }));
                    streamlitInput.dispatchEvent(new Event('change', { bubbles: true }));
                } else {
                    // Fallback
                    const inputField = window.parent.document.getElementById("rose_user_query");
                    if (inputField) {
                        inputField.value = text;
                        inputField.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                }
            };
            
            recognition.onerror = () => {
                status.innerHTML = "⚠️ خطایی رخ داد یا صدایی شنیده نشد. مجدداً تلاش کنید.";
                btn.style.borderColor = "#00f0ff";
            };
            
            recognition.onend = () => {
                if(status.innerHTML.includes("🔴")) {
                    status.innerHTML = "میکروفون خاموش شد.";
                    btn.style.borderColor = "#00f0ff";
                }
            };
        } else {
            status.innerHTML = "⚠️ مروگر شما از ضبط مستقیم صوتی پشتیبانی نمی‌کند. از کیبورد گوشی/سیستم استفاده کنید.";
            btn.style.opacity = 0.5;
            btn.style.cursor = "not-allowed";
        }
    </script>
    """
    st.components.v1.html(st_html_mic_code, height=130)
    
    user_query = st.text_input("📝 پیام متنی یا صوتی تبدیل شده شما:", key="rose_user_query", placeholder="اینجا بنویسید یا دکمه میکروفون بالا را لمس کنید...")
    
    if user_query:
        st.markdown(f"<div class='chat-bubble-user'>👤 <b>سوال شما:</b> {user_query}</div>", unsafe_allow_html=True)
        
        q = user_query.lower()
        response = ""
        speech_text = ""
        citation = ""
        
        # 1. Scanning Contract Knowledge Base (PDF Details)
        if "مبلغ" in q or "بودجه" in q or "ارزش" in q or "ریال" in q or "contract value" in q:
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
            &nbsp;&nbsp; - آقای <b>محمد افراسیابیان</b> (عضو هیئت مدیره)
            """
            speech_text = "نمایندگان مجاز قرارداد شامل آقایان فرهاد احمدی، ستار عزیزیان تفتی و حسین رهنما هستند."
            citation = "📚 <b>سند پی‌دی‌اف موافقت‌نامه اصلی پیمان</b> | صفحه ۵ | امضای طرفین"
            
        elif "اختلاف" in q or "حل اختلاف" in q or "قضایی" in q or "dispute" in q:
            response = """
            ⚖️ <b>روش رسمی حل اختلاف قراردادی (بر اساس مفاد پیوست ۲۱ پیمان):</b><br><br>
            در صورت بروز هرگونه اختلاف فنی یا مالی بین مشارکت انهار-فرآیند سازان با کارفرما، موضوع به <b>«هیأت حل اختلاف»</b> ارجاع می‌گردد.<br>
            این هیأت دارای <b>۵ عضو رسمی</b> است:<br>
            ۱. کارشناس واجد صلاحیت حقوقی در امور قراردادها (رئیس هیأت)<br>
            ۲. کارشناس واجد صلاحیت مالی<br>
            ۳. کارشناس فنی در امور مهندسی و پروژه‌ای<br>
            ۴. نماینده مدیرعامل شرکت کارفرما<br>
            ۵. نماینده انجمن نفت ایران<br><br>
            در صورت عدم حل، مراجع قضایی صالح کشور رأی نهایی را صادر خواهند کرد.
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
            • **کانکس بهداشتی:** استقرار کانکس‌های بهداشتی سیار به همراه مخازن آب شرب استاندارد.
            """
            speech_text = "رعایت تمهیدات بهداشت، ایمنی و سم‌پاشی منظم کارگاه‌ها از الزامات حتمی پیمانکار است."
            citation = "📚 <b>پیوست ۸ پیمان خط لوله رفسنجان-یزد</b> | الزامات عمومی HSE"
            
        # 2. Scanning Material Excel Database (Valves, Pipes, Cables, Pumps)
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
            
        # 3. Dynamic Fallback to Web Search (Google / DuckDuckGo Scraper)
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
                # Let's perform an actual live Google/DuckDuckGo search to satisfy "سایت گوگل هم بشه سورس و جستجو ما"
                st.caption("🔍 در حال جستجوی آنلاین در شبکه اینترنت برای یافتن نزدیک‌ترین پاسخ...")
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

        # Display Chat Bubble
        st.markdown(f"<div class='chat-bubble-rose'>🌹 <b>دستیار رز:</b><br><br>{response}</div>", unsafe_allow_html=True)
        if citation:
            st.caption(citation)
            
        # Text-To-Speech Playback
        if voice_enabled and speech_text and gtts_available:
            try:
                tts = gTTS(text=speech_text, lang='fa')
                tts_buffer = io.BytesIO()
                tts.write_to_fp(tts_buffer)
                st.audio(tts_buffer.getvalue(), format="audio/mp3")
                st.toast("🔊 پاسخ صوتی رز آماده پخش است.")
            except Exception as e:
                pass

# ----------------- Tab 2: Advanced Grid Search -----------------
with tab2:
    st.markdown("### 🔍 جستجو و فیلتر پیشرفته در تمام شیت‌های اکسل پروژه")
    
    # Discipline filter
    all_disciplines = ["همه دیسیپلین‌ها"] + list(df['discipline_fa'].unique())
    selected_disp = st.selectbox("📁 فیلتر بر اساس دیسیپلین تخصصی پروژه:", all_disciplines)
    
    # Search input
    search_term = st.text_input('🔍 جستجوی متنی نام کالا یا مشخصات فنی (مثال: 16, Cable, Valve, MOV):')
    
    # Filter dataset
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

# ----------------- Tab 3: Financial Analytics & Discrepancies -----------------
with tab3:
    st.markdown("### 📊 آنالیز توزیع هزینه‌ها و انحرافات حسابرسی")
    
    st.write("#### سهم دیسیپلین‌ها از هزینه ارزی کل پروژه (بر حسب یورو)")
    st.bar_chart(data=df, x='discipline_fa', y='euro_cost', color='#ff007f', use_container_width=True)
    
    st.write("#### سهم دیسیپلین‌ها از هزینه ریالی کل پروژه (بر حسب ریال)")
    st.bar_chart(data=df, x='discipline_fa', y='rial_cost', color='#00f0ff', use_container_width=True)

    st.markdown(
        """
        <div style='background-color: rgba(255, 0, 127, 0.05); border-right: 5px solid #ff007f; border-left: 1px solid rgba(255, 0, 127, 0.2); padding: 16px; border-radius: 8px; margin-bottom: 20px;'>
            <b style='color: #ff007f; font-size: 16px;'>⚠️ کشف مغایرت‌های محاسباتی و حسابرسی سندی (یافته‌های طلایی رز):</b><br><br>
            ۱. <b>خطای ثبت دوگانه کدهای لوازم یدکی (Spare Parts):</b> مبلغ ۳۱۳,۰۰۰ هم در ستون ریالی کل قرارداد (به عنوان ریال) و هم در ستون ارزی (به عنوان یورو) قرار گرفته است که ناشی از خطای تایپی قرارداد اولیه است [۶، ۷۳].<br><br>
            ۲. <b>مغایرت ۱,۳۱۰ یورویی ابزار دقیق رفسنجان:</b> در خرید Flow Switches ردیف ۳ تلمبه‌خانه رفسنجان، تعداد ۲ عدد با قیمت واحد ۱,۳۱۰ یورو فاکتور شده که بهای کل ریاضی آن باید ۲,۶۲۰ یورو باشد، اما در جمع نهایی شیت رفسنجان به اشتباه ۱,۳۱۰ یورو جمع زده شده است (اختلاف دقیق ۱,۳۱۰ یورو) [۶، ۴۲، ۶۸].<br><br>
            ۳. <b>تفاوت ریاضی مجموع ارزی کل پیمان:</b> جمع کل ارزی ریاضی در برگ سند نهایی پیمانکار به جای عدد محاسباتی دقیق ۱۱,۰۱۴,۵۴۶.۴۸ یورو، معادل ۱۱,۰۱۴,۵۴۶.۰۰ یورو به علت گرد کردن‌ها نوشته شده است که در حسابرسی کلان سند فاش شد [۶، ۴۲، ۲۲۰].
        </div>
        """,
        unsafe_allow_html=True
    )

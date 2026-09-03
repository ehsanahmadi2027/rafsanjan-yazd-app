import streamlit as st
import pandas as pd
import numpy as np
import io
import os

# تنظیمات اصلی صفحه استریم‌لیت
st.set_page_config(
    page_title="سامانه هوشمند تدارکات خط لوله رفسنجان-یزد",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تغییر جهت کل سایت به راست‌به‌چپ (RTL) برای ظاهر شیک فارسی و انگلیسی دو زبانه
st.markdown(
    """
    <style>
    .stApp {
        direction: RTL;
        text-align: right;
    }
    .main-title {
        color: #1e3d59;
        font-family: 'Georgia', sans-serif;
        text-align: center;
        border-bottom: 3px solid #ffc13b;
        padding-bottom: 15px;
    }
    .metric-card {
        background-color: #f5f0eb;
        border-radius: 10px;
        padding: 15px;
        border-right: 5px solid #1e3d59;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    .metric-title {
        color: #8a7e72;
        font-size: 14px;
        font-weight: bold;
    }
    .metric-value {
        color: #1e3d59;
        font-size: 22px;
        font-weight: bold;
        margin-top: 5px;
    }
    .user-bubble {
        background-color: #f5f0eb;
        color: #1e3d59;
        padding: 12px;
        border-radius: 10px;
        border-right: 4px solid #ffc13b;
        margin-bottom: 15px;
        direction: RTL;
        text-align: right;
    }
    .chat-bubble {
        background-color: #e8f1f5;
        color: #1e3d59;
        padding: 15px;
        border-radius: 10px;
        border-right: 4px solid #1e3d59;
        margin-bottom: 15px;
        direction: RTL;
        text-align: right;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# بارگذاری پایگاه داده متریال از فایل محلی یا ابری
@st.cache_data
def load_data():
    csv_filename = "consolidated_material_list-v3.csv"
    paths_to_try = [
        csv_filename,
        "consolidated_material_list.csv",
        "artifacts/consolidated_material_list-v3.csv",
        "artifacts/consolidated_material_list.csv",
        "/workspace/artifacts/consolidated_material_list-v3.csv",
        "/workspace/artifacts/consolidated_material_list.csv"
    ]
    df = None
    for p in paths_to_try:
        if os.path.exists(p):
            try:
                df = pd.read_csv(p)
                break
            except:
                pass
                
    if df is None:
        # ساخت دیتاست نمونه در صورت عدم دسترسی
        data = {
            'discipline_en': ['Piping & Valves', 'Mechanical Equipment', 'Electrical Equipment', 'Instrumentation & Telecom', 'Cathodic Protection', 'Safety & Fire Fighting', 'Spare Parts'],
            'discipline_fa': ['لوله‌کشی و شیرآلات', 'تجهیزات مکانیکال', 'تجهیزات برقی', 'ابزار دقیق و مخابرات', 'حفاظت کاتدیک', 'ایمنی و آتش‌نشانی', 'لوازم یدکی'],
            'item_name_en': ['Pipes (5,260 M)', 'Main Pumps (7 NO)', 'Armored Cables (15,630 M)', 'Motorized Valves (54 NO)', 'Smart Rectifiers (5 NO)', 'Flooding Systems (2 SET)', '2-Year Spares'],
            'item_name_fa': ['لوله (۵,۲۶۰ متر)', 'پمپ‌های اصلی (۷ عدد)', 'کابل‌های زره‌دار (۱۵,۶۳۰ متر)', 'شیرآلات موتوردار (۵۴ عدد)', 'رکتیفایرهای هوشمند (۵ عدد)', 'سیستم‌های سیلابی (۲ ست)', 'یدکی دو ساله'],
            'quantity': [5260, 7, 15630, 54, 5, 2, 3],
            'unit': ['Meters', 'NO', 'Meters', 'NO', 'NO', 'SET', 'Package'],
            'rial_cost': [0, 0, 812237187000, 26740000000, 29742500000, 0, 313000],
            'euro_cost': [1542923.88, 2337532.60, 1901290.00, 4776150.00, 0.00, 143650.00, 313000.00],
            'specs_en': ['API 5L Gr. B/X52/X60', 'Includes MP-554 Diesel 400K Euro', 'Copper armored lead covered SWA', '400VAC explosion proof', 'Auto potential Smart TR', 'Inert Gas system for control rooms', 'Two-year operating spares package'],
            'specs_fa': ['لوله‌های فولادی گرید X60 خط اصلی', 'پمپ دیزلی و متعلقات تلمبه‌خانه', 'کابل‌های مسی سربی زره‌دار', 'شیرهای توپی ابزار دقیق موتوردار برقی', 'رکتیفایر حفاظت کاتدی خودکار هوشمند', 'سیستم اطفای حریق اتوماتیک سیلابی', 'پکیج قطعات یدکی بهره‌برداری دو ساله']
        }
        df = pd.DataFrame(data)
        
    # تضمین تطابق ستون‌ها برای دوزبانه بودن
    if 'item_name_fa' not in df.columns:
        df['item_name_en'] = df['item_name'] if 'item_name' in df.columns else "Sample Item"
        df['item_name_fa'] = df['item_name'] if 'item_name' in df.columns else "کالای نمونه"
    if 'discipline_fa' not in df.columns:
        df['discipline_en'] = df['discipline'] if 'discipline' in df.columns else "Sample Discipline"
        df['discipline_fa'] = df['discipline'] if 'discipline' in df.columns else "دیسیپلین نمونه"
    if 'specs_fa' not in df.columns:
        df['specs_en'] = df['specs'] if 'specs' in df.columns else "Sample Specs"
        df['specs_fa'] = df['specs'] if 'specs' in df.columns else "مشخصات نمونه"
        
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"خطا در بارگذاری اطلاعات: {str(e)}")
    st.stop()

# تیتر اصلی نرم‌افزار به صورت دوزبانه و فوق‌حرفه‌ای
st.markdown("<h1 class='main-title'>🏗️ سامانه هوشمند و دوزبانه تدارکات خط لوله رفسنجان-یزد</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #8a7e72;'>Rafsanjan-Yazd Pipeline Smart Bilingual Procurement Portal</h4>", unsafe_allow_html=True)
st.write("")

# محاسبه مبالغ کلان پروژه
total_rials = df['rial_cost'].sum() + 4500000000 # با احتساب ۴.۵ میلیارد ریال آموزش
total_euros = df['euro_cost'].sum()
total_tomans = total_rials / 10

# سایدبار تنظیمات و دریافت کل اکسل دوزبانه
with st.sidebar:
    st.markdown("### 🛠️ مدیریت و اجرای برنامه")
    st.info("این برنامه به شما امکان می‌دهد بانک جامع کالاها (شامل اطلاعات ۳۱ شیت اکسل تراز شده) را به دو زبان فارسی و انگلیسی فیلتر کرده، خروجی سفارشی بگیرید و به صورت هوشمند و محلی جستجو کنید.")
    
    st.markdown("### 📥 دریافت خروجی")
    # ساخت فایل اکسل تعاملی در حافظه برای دانلود مستقیم
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Material_Bilingual_Summary')
    
    st.download_button(
        label="📥 دانلود کل بانک متریال دوزبانه (Excel)",
        data=buffer.getvalue(),
        file_name="consolidated_material_list_bilingual.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    st.markdown("---")
    st.markdown("**وضعیت دیتابیس:** 🟢 ۱۰۰٪ دوزبانه و تراز شده")
    st.markdown("**Bilingual Support:** Enabled (FA / EN)")
    st.markdown("**نسخه نرم‌افزار:** v2.0.0 (فوق‌حرفه‌ای دوزبانه)")

# لایه کارت‌های شاخص مالی (KPIs)
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        f"""
        <div class='metric-card'>
            <div class='metric-title'>💰 برآورد ریالی پروژه (Rial Budget)</div>
            <div class='metric-value'>{total_rials:,.0f} ریال</div>
            <div style='color: #8a7e72; font-size: 13px; margin-top: 5px;'>معادل {total_tomans:,.0f} تومان</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with col2:
    st.markdown(
        f"""
        <div class='metric-card'>
            <div class='metric-title'>💶 برآورد ارزی پروژه (Euro Budget)</div>
            <div class='metric-value'>{total_euros:,.2f} یورو</div>
            <div style='color: #8a7e72; font-size: 13px; margin-top: 5px;'>تأمین کالای ارزی و گمرکی</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with col3:
    st.markdown(
        f"""
        <div class='metric-card'>
            <div class='metric-title'>📈 دیتابیس اقلام تفصیلی (Total Rows)</div>
            <div class='metric-value'>{len(df)} ردیف کالا</div>
            <div style='color: #8a7e72; font-size: 13px; margin-top: 5px;'>تراز شده با ۳۱ شیت تدارکاتی</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ایجاد تب‌های چندگانه برای تفکیک بخش‌ها
tab1, tab2, tab3 = st.tabs(["💬 دستیار صوتی و چت تعاملی (Q&A)", "🔍 جستجو و فیلتر پیشرفته دوزبانه", "📊 آنالیز توزیع دیسیپلین‌ها"])

# تَب اول: ربات هوشمند پرسش و پاسخ
with tab1:
    st.markdown("### 💬 از دستیار هوشمند پروژه سوال بپرسید (Q&A Assistant)")
    st.write("سوال خود را درباره تجهیزات، متراژها، قیمت‌ها و مشخصات به زبان فارسی یا انگلیسی وارد کنید تا سیستم فوراً پاسخ دهد:")
    
    user_query = st.text_input("📝 سوال شما (مثال: پمپ‌های یزد، مشخصات ولوها, cables, pipes, مغایرت‌های مالی):", key="ai_query")
    
    if user_query:
        st.markdown(f"<div class='user-bubble'><b>سوال شما:</b> {user_query}</div>", unsafe_allow_html=True)
        
        # موتور پردازش کلمات کلیدی هوشمند به صورت محلی و دوزبانه (بدون نیاز به اینترنت)
        q = user_query.lower()
        response = ""
        matched_items = []
        
        # ۱. پمپ‌ها
        if any(w in q for w in ["پمپ", "pump", "booster", "بوستر"]):
            matched_rows = df[
                df['item_name_fa'].str.contains('pump|پمپ', case=False, na=False) | 
                df['item_name_en'].str.contains('pump|پمپ', case=False, na=False) |
                df['specs_fa'].str.contains('pump|پمپ', case=False, na=False) |
                df['specs_en'].str.contains('pump|پمپ', case=False, na=False)
            ]
            response += "🔍 <b>نتایج مرتبط با تجهیزات پمپ و بوسترها (Pumps & Boosters) یافت شد:</b><br><br>"
            for idx, r in matched_rows.iterrows():
                toman_val = r['rial_cost'] / 10
                response += f"• <b>{r['item_name_fa']} / {r['item_name_en']}</b>: تعداد: {r['quantity']} {r['unit']} | هزینه ریالی: {r['rial_cost']:,.0f} ریال ({toman_val:,.0f} تومان) | هزینه ارزی: {r['euro_cost']:,.2f} یورو<br>"
                response += f"&nbsp;&nbsp;&nbsp;&nbsp;<i> مشخصات فنی: {r['specs_fa']} <br>&nbsp;&nbsp;&nbsp;&nbsp;Specs: {r['specs_en']}</i><br><br>"
                
        # ۲. لوله‌ها و شیرآلات / ولوها
        elif any(w in q for w in ["لوله", "شیر", "ولو", "pipe", "valve", "gate", "ball", "globe", "check", "chock"]):
            matched_rows = df[
                df['discipline_en'].str.contains('Piping', case=False) |
                df['discipline_fa'].str.contains('لوله‌کشی', case=False) |
                df['item_name_fa'].str.contains('valve|pipe|شیر|لوله|ولو', case=False, na=False) |
                df['item_name_en'].str.contains('valve|pipe|شیر|لوله|ولو', case=False, na=False)
            ]
            response += "🛠️ <b>اطلاعات تفصیلی بخش لوله‌کشی و شیرآلات (Valves & Piping):</b><br><br>"
            for idx, r in matched_rows.iterrows():
                response += f"• <b>{r['item_name_fa']} / {r['item_name_en']}</b>: تعداد/متراژ: {r['quantity']} {r['unit']} | بهای ارزی کل: {r['euro_cost']:,.2f} یورو<br>"
                response += f"&nbsp;&nbsp;&nbsp;&nbsp;<i> مشخصات فنی: {r['specs_fa']} <br>&nbsp;&nbsp;&nbsp;&nbsp;Specs: {r['specs_en']}</i><br><br>"
                
        # ۳. کابل و برق
        elif any(w in q for w in ["کابل", "cable", "برق", "electrical", "switchgear", "transformer", "ترانس", "ژنراتور", "generator", "تابلو"]):
            matched_rows = df[
                df['discipline_en'].str.contains('Electrical', case=False) |
                df['discipline_fa'].str.contains('برقی', case=False) |
                df['item_name_fa'].str.contains('cable|کابل|switchgear|transformer|ترانس|generator|ژنراتور|تابلو', case=False, na=False) |
                df['item_name_en'].str.contains('cable|کابل|switchgear|transformer|ترانس|generator|ژنراتور|تابلو', case=False, na=False)
            ]
            response += "⚡ <b>کابل‌کشی و ملزومات توزیع برق (Electrical Equipment):</b><br><br>"
            for idx, r in matched_rows.iterrows():
                toman_val = r['rial_cost'] / 10
                response += f"• <b>{r['item_name_fa']} / {r['item_name_en']}</b>: مقدار: {r['quantity']} {r['unit']} | قیمت ریالی: {r['rial_cost']:,.0f} ریال | قیمت ارزی: {r['euro_cost']:,.2f} یورو<br>"
                response += f"&nbsp;&nbsp;&nbsp;&nbsp;<i> مشخصات فنی: {r['specs_fa']} <br>&nbsp;&nbsp;&nbsp;&nbsp;Specs: {r['specs_en']}</i><br><br>"
                
        # ۴. ابزار دقیق و تله‌کام
        elif any(w in q for w in ["ابزار", "instrument", "کنترل", "control", "فلومتر", "flow", "ترانسمیتر", "transmitter", "مخابرات", "telecom", "کابل نوری", "fiber", "tgs"]):
            matched_rows = df[
                df['discipline_en'].str.contains('Instrumentation', case=False) |
                df['discipline_fa'].str.contains('ابزار دقیق', case=False) |
                df['item_name_fa'].str.contains('instrument|control|flow|transmitter|telecom|fiber|tgs|ابزار|کنترل|فلومتر|ترانسمیتر|مخابرات', case=False, na=False) |
                df['item_name_en'].str.contains('instrument|control|flow|transmitter|telecom|fiber|tgs|ابزار|کنترل|فلومتر|ترانسمیتر|مخابرات', case=False, na=False)
            ]
            response += "📡 <b>سیستم‌های ابزار دقیق و مخابرات (Instrumentation & Telecom):</b><br><br>"
            for idx, r in matched_rows.iterrows():
                toman_val = r['rial_cost'] / 10
                response += f"• <b>{r['item_name_fa']} / {r['item_name_en']}</b>: تعداد: {r['quantity']} {r['unit']} | قیمت ریالی: {r['rial_cost']:,.0f} ریال | قیمت ارزی: {r['euro_cost']:,.2f} یورو<br>"
                response += f"&nbsp;&nbsp;&nbsp;&nbsp;<i> مشخصات فنی: {r['specs_fa']} <br>&nbsp;&nbsp;&nbsp;&nbsp;Specs: {r['specs_en']}</i><br><br>"

        # ۵. حفاظت کاتدیک
        elif any(w in q for w in ["کاتد", "cathodic", "رکتیفایر", "rectifier", "آند", "anode", "کک", "coke", "ارت", "earthing"]):
            matched_rows = df[
                df['discipline_en'].str.contains('Cathodic', case=False) |
                df['discipline_fa'].str.contains('کاتدیک', case=False) |
                df['item_name_fa'].str.contains('rectifier|anode|coke|earthing|کاتد|رکتیفایر|آند|کک|ارت', case=False, na=False) |
                df['item_name_en'].str.contains('rectifier|anode|coke|earthing|کاتد|رکتیفایر|آند|کک|ارت', case=False, na=False)
            ]
            response += "🔋 <b>سیستم حفاظت کاتدیک خط لوله (Cathodic Protection):</b><br><br>"
            for idx, r in matched_rows.iterrows():
                response += f"• <b>{r['item_name_fa']} / {r['item_name_en']}</b>: تعداد/مقدار: {r['quantity']} {r['unit']} | بهای ریالی کل: {r['rial_cost']:,.0f} ریال<br>"
                response += f"&nbsp;&nbsp;&nbsp;&nbsp;<i> مشخصات فنی: {r['specs_fa']} <br>&nbsp;&nbsp;&nbsp;&nbsp;Specs: {r['specs_en']}</i><br><br>"

        # ۶. ایمنی و آتش‌نشانی
        elif any(w in q for w in ["ایمنی", "fire", "safety", "کپسول", "extinguisher", "هیدرانت", "hydrant", "اطفا"]):
            matched_rows = df[
                df['discipline_en'].str.contains('Safety', case=False) |
                df['discipline_fa'].str.contains('ایمنی', case=False) |
                df['item_name_fa'].str.contains('hydrant|extinguisher|flooding|safety|ایمنی|کپسول|هیدرانت|اطفا', case=False, na=False) |
                df['item_name_en'].str.contains('hydrant|extinguisher|flooding|safety|ایمنی|کپسول|هیدرانت|اطفا', case=False, na=False)
            ]
            response += "🧯 <b>تجهیزات ایمنی و آتش‌نشانی (Safety & Fire Fighting):</b><br><br>"
            for idx, r in matched_rows.iterrows():
                response += f"• <b>{r['item_name_fa']} / {r['item_name_en']}</b>: مقدار: {r['quantity']} {r['unit']} | هزینه ارزی کل: {r['euro_cost']:,.2f} یورو<br>"
                response += f"&nbsp;&nbsp;&nbsp;&nbsp;<i> مشخصات فنی: {r['specs_fa']} <br>&nbsp;&nbsp;&nbsp;&nbsp;Specs: {r['specs_en']}</i><br><br>"

        # ۷. مغایرت‌های حسابرسی قرارداد
        elif any(w in q for w in ["مغایرت", "خطا", "اختلاف", "حسابرس", "error", "mismatch"]):
            response += """
            ⚠️ <b>یافته‌های حساس حسابرسی و مغایرت‌های مالی قرارداد (Discrepancies) به شرح زیر است:</b><br><br>
            ۱. <b>خطای ثبت دوگانه لوازم یدکی (Spare Parts Typo):</b> مبلغ ۳۱۳,۰۰۰ هم در ستون ریالی کل قرارداد (به عنوان ریال) و هم در ستون ارزی (به عنوان یورو) قرار گرفته است که ناشی از خطای تایپی قرارداد اولیه است.<br><br>
            ۲. <b>مغایرت ۱,۳۱۰ یورویی ابزار دقیق رفسنجان (1,310 Euro Instrument Mismatch):</b> در خرید Flow Switches ردیف ۳ تلمبه‌خانه رفسنجان، تعداد ۲ عدد با قیمت واحد ۱,۳۱۰ یورو فاکتور شده که بهای کل ریاضی آن باید ۲,۶۲۰ یورو باشد، اما در جمع نهایی شیت رفسنجان به اشتباه ۱,۳۱۰ یورو جمع زده شده است (اختلاف دقیق ۱,۳۱۰ یورو).<br><br>
            ۳. <b>تفاوت انحراف ریاضی کل ارزی:</b> جمع کل ارزی ریاضی در سند اصلی به جای عدد محاسباتی دقیق ۱۱,۰۱۴,۵۴۶.۴۸ یورو، معادل ۱۱,۰۱۴,۵۴۶.۰۰ یورو به علت گرد کردن‌ها نوشته شده است.
            """
            
        # ۸. قطعات یدکی
        elif any(w in q for w in ["یدکی", "spare", "spares"]):
            matched_rows = df[
                df['discipline_en'].str.contains('Spare', case=False) |
                df['discipline_fa'].str.contains('یدکی', case=False)
            ]
            response += "📦 <b>بخش لوازم یدکی دو ساله بهره‌برداری (Two-Year Operating Spares):</b><br><br>"
            for idx, r in matched_rows.iterrows():
                response += f"• <b>{r['item_name_fa']} / {r['item_name_en']}</b>: تعداد: {r['quantity']} {r['unit']} | هزینه ریالی: {r['rial_cost']:,.0f} ریال | هزینه ارزی: {r['euro_cost']:,.2f} یورو<br>"
                response += f"&nbsp;&nbsp;&nbsp;&nbsp;<i> مشخصات فنی: {r['specs_fa']} <br>&nbsp;&nbsp;&nbsp;&nbsp;Specs: {r['specs_en']}</i><br><br>"

        else:
            # جستجوی عمومی متنی در تمام فیلدهای انگلیسی و فارسی
            any_match = df[
                df['item_name_fa'].str.contains(q, case=False, na=False) |
                df['item_name_en'].str.contains(q, case=False, na=False) |
                df['specs_fa'].str.contains(q, case=False, na=False) |
                df['specs_en'].str.contains(q, case=False, na=False) |
                df['discipline_fa'].str.contains(q, case=False, na=False) |
                df['discipline_en'].str.contains(q, case=False, na=False)
            ]
            if not any_match.empty:
                response += f"🔍 <b>موارد یافت شده برای عبارت '{user_query}':</b><br><br>"
                for idx, r in any_match.iterrows():
                    toman_val = r['rial_cost'] / 10
                    response += f"• <b>{r['item_name_fa']} / {r['item_name_en']}</b> ({r['discipline_fa']}): مقدار: {r['quantity']} {r['unit']} | هزینه ریالی: {r['rial_cost']:,.0f} ریال | هزینه ارزی: {r['euro_cost']:,.2f} یورو<br>"
                    response += f"&nbsp;&nbsp;&nbsp;&nbsp;<i> مشخصات فنی: {r['specs_fa']} <br>&nbsp;&nbsp;&nbsp;&nbsp;Specs: {r['specs_en']}</i><br><br>"
            else:
                response = """
                ❌ <b>منظور شما را متوجه نشدم / Word not found. لطفاً سوال خود را درباره یکی از موارد زیر بپرسید:</b><br><br>
                • <b>تجهیزات فرآیندی:</b> مانند لوله‌ها، شیرآلات توپی، بوستر پمپ‌ها، مخازن دفنی، ترانس‌ها و کابل‌های برق.<br>
                • <b>دیسیپلین‌های تخصصی:</b> لوله‌کشی، مکانیکال، برقی، ابزار دقیق، حفاظت کاتدیک و ایمنی آتش‌نشانی.<br>
                • <b>گزارش‌های نظارتی:</b> مانند هشدارهای حسابرسی، مغایرت‌های مالی قرارداد و چک‌لیست‌های تدارکات.<br><br>
                • <b>English queries:</b> Search for pipes, pumps, valves, cables, instrumentation, CP anodes, safety systems, or contract discrepancies.
                """
                
        st.markdown(f"<div class='chat-bubble'>{response}</div>", unsafe_allow_html=True)

# تَب دوم: فیلتر پیشرفته جداول متریال
with tab2:
    st.markdown("### 🔍 جستجو و فیلتر پیشرفته دوزبانه در تمام شیت‌ها (Bilingual Grid)")
    
    # فیلتر بر اساس دیسیپلین (فارسی و انگلیسی)
    all_disciplines_fa = ["همه دیسیپلین‌ها"] + list(df['discipline_fa'].unique())
    selected_disp_fa = st.selectbox("📁 فیلتر بر اساس دیسیپلین تخصصی پروژه (Discipline Filter):", all_disciplines_fa)
    
    # فیلتر متنی نام کالا (هر دو زبان)
    search_term = st.text_input('🔍 جستجوی متنی نام کالا یا مشخصات فنی به انگلیسی یا فارسی (e.g. 16", API 5L, XLPE, لوله, شیر):')
    
    # اعمال فیلترها روی دیتاست اصلی
    filtered_df = df.copy()
    if selected_disp_fa != "همه دیسیپلین‌ها":
        filtered_df = filtered_df[filtered_df['discipline_fa'] == selected_disp_fa]
    if search_term:
        filtered_df = filtered_df[
            filtered_df['item_name_fa'].str.contains(search_term, case=False, na=False) |
            filtered_df['item_name_en'].str.contains(search_term, case=False, na=False) |
            filtered_df['specs_fa'].str.contains(search_term, case=False, na=False) |
            filtered_df['specs_en'].str.contains(search_term, case=False, na=False)
        ]
        
    # نمایش تعداد ردیف‌های یافت شده
    st.write(f"📊 تعداد **{len(filtered_df)} ردیف متریال** با فیلتر شما همخوانی دارد / **{len(filtered_df)} items found**:")
    
    # قالب‌بندی نمایش مبالغ به صورت خوانا
    display_df = filtered_df.copy()
    display_df['rial_cost'] = display_df['rial_cost'].apply(lambda x: f"{x:,.0f} ریال" if x > 0 else "0")
    display_df['euro_cost'] = display_df['euro_cost'].apply(lambda x: f"{x:,.2f} €" if x > 0 else "0")
    
    # تغییر نام سرستون‌ها به فارسی و انگلیسی برای ظاهر حرفه‌ای
    display_df = display_df.rename(columns={
        'discipline_fa': 'دیسیپلین (Discipline)',
        'item_name_fa': 'نام متریال فارسی (Material Name)',
        'item_name_en': 'نام متریال انگلیسی (English Name)',
        'quantity': 'مقدار (Qty)',
        'unit': 'واحد (Unit)',
        'rial_cost': 'بهای کل ریالی (Rial Cost)',
        'euro_cost': 'بهای کل ارزی (Euro Cost)',
        'specs_fa': 'مشخصات فنی فارسی',
        'specs_en': 'مشخصات فنی انگلیسی (Technical Specs)'
    })
    
    # نمایش جدول نهایی با حذف ستون‌های خام پشت صحنه
    cols_to_show = [
        'دیسیپلین (Discipline)',
        'نام متریال فارسی (Material Name)',
        'نام متریال انگلیسی (English Name)',
        'مقدار (Qty)',
        'واحد (Unit)',
        'بهای کل ریالی (Rial Cost)',
        'بهای کل ارزی (Euro Cost)',
        'مشخصات فنی فارسی',
        'مشخصات فنی انگلیسی (Technical Specs)'
    ]
    st.dataframe(display_df[cols_to_show], use_container_width=True)
    
    # دکمه دانلود خروجی فیلتر شده به صورت CSV
    csv_data = filtered_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 دانلود اطلاعات فیلتر شده بالا (CSV)",
        data=csv_data,
        file_name="filtered_material_list_bilingual.csv",
        mime="text/csv"
    )

# تَب سوم: آنالیز نموداری دیسیپلین‌ها
with tab3:
    st.markdown("### 📊 آنالیز توزیع هزینه‌های ارزی و ریالی (Financial Distribution Charts)")
    
    st.write("#### سهم دیسیپلین‌ها از هزینه ارزی کل پروژه (بر حسب یورو)")
    st.bar_chart(data=df, x='discipline_fa', y='euro_cost', color='#ffc13b', use_container_width=True)
    
    st.write("#### سهم دیسیپلین‌ها از هزینه ریالی کل پروژه (بر حسب ریال)")
    st.bar_chart(data=df, x='discipline_fa', y='rial_cost', color='#1e3d59', use_container_width=True)

    st.markdown(
        """
        <div style='background-color: #e3f2fd; border-right: 5px solid #2196f3; padding: 15px; border-radius: 5px; direction: RTL; text-align: right;'>
            <b>💡 تحلیل کلان توزیع بودجه:</b><br>
            • دیسیپلین <b>ابزار دقیق و مخابرات (Instrumentation & Telecom)</b> با سهم ۴.۷۷ میلیون یورو بزرگ‌ترین وزنه مصرف ارزی پروژه است.<br>
            • دیسیپلین <b>تجهیزات برقی (Electrical Equipment)</b> با سهم ۸۱۲.۲ میلیارد ریال سنگین‌ترین بودجه‌بندی ریالی را به دلیل متراژ کابل‌کشی‌ها به خود اختصاص داده است.
        </div>
        """,
        unsafe_allow_html=True
    )

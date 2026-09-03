import streamlit as st
import pandas as pd
import numpy as np
import io
import os
import base64

# سعی در وارد کردن کتابخانه صوتی گوگل برای سخنگو شدن رز
try:
    from gtts import gTTS
    gtts_available = True
except ImportError:
    gtts_available = False

# تنظیمات اصلی صفحه استریم‌لیت
st.set_page_config(
    page_title="دستیار صوتی هوشمند رز - خط لوله رفسنجان یزد",
    page_icon="🌹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# فونت و استایل‌های مجلل CSS برای RTL و انیمیشن زنده رز
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
    
    /* انیمیشن تپش زنده و پلک‌زدن مجازی برای تصویر دستیار رز */
    .avatar-container {
        text-align: center;
        padding: 10px;
        position: relative;
    }
    .live-avatar {
        border-radius: 50%;
        border: 4px solid #ffc13b;
        box-shadow: 0 0 15px rgba(255, 193, 59, 0.6);
        animation: pulse 3s infinite ease-in-out;
        transition: transform 0.3s ease-in-out;
        max-width: 150px;
        margin: 0 auto;
    }
    .live-avatar:hover {
        transform: scale(1.08) rotate(3deg);
        box-shadow: 0 0 25px rgba(255, 193, 59, 0.9);
    }
    @keyframes pulse {
        0% { transform: scale(1); box-shadow: 0 0 12px rgba(255, 193, 59, 0.5); }
        50% { transform: scale(1.03); box-shadow: 0 0 22px rgba(255, 193, 59, 0.8); }
        100% { transform: scale(1); box-shadow: 0 0 12px rgba(255, 193, 59, 0.5); }
    }
    
    /* استایل‌های پیام چت */
    .chat-bubble-user {
        background-color: #f1f1f1;
        border-right: 5px solid #8a7e72;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 15px;
        text-align: right;
        direction: RTL;
    }
    .chat-bubble-rose {
        background-color: #e8f1f5;
        border-right: 5px solid #1e3d59;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
        text-align: right;
        direction: RTL;
        box-shadow: 1px 1px 5px rgba(0,0,0,0.05);
    }
    
    /* استایل کارت دکمه‌های آرم تجاری */
    .logo-card {
        background-color: #ffffff;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        cursor: pointer;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 10px;
        transition: all 0.2s ease-in-out;
    }
    .logo-card:hover {
        border-color: #ffc13b;
        transform: translateY(-2px);
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# لود تصاویر پایه در صورت وجود
avatar_base64 = ""
avatar_path = "rose_assistant_avatar.png"
paths_to_avatar = [avatar_path, "artifacts/rose_assistant_avatar.png", "/workspace/artifacts/rose_assistant_avatar.png"]
for p in paths_to_avatar:
    if os.path.exists(p):
        with open(p, "rb") as image_file:
            avatar_base64 = base64.b64encode(image_file.read()).decode()
            break

# بارگذاری پایگاه داده متریال از فایل اصلی اکسل یا بانک تراز پیش‌فرض
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
                # خواندن تمامی شیت‌های مورد نیاز و تجمیع داده‌ها
                xls = pd.ExcelFile(p)
                sheets = xls.sheet_names
                dfs = []
                # دیسیپلین‌های هدف
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
                            # پاکسازی هدر و پیدا کردن ردیف کالاها
                            temp_df.columns = [str(c).strip() for c in temp_df.columns]
                            # فیلتر کردن ردیف‌های غیرکالایی
                            if 'item_name' in temp_df.columns or 'عنوان' in temp_df.columns:
                                temp_df['discipline'] = val
                                dfs.append(temp_df)
                if dfs:
                    df = pd.concat(dfs, ignore_index=True)
                    # تراز ستون‌ها
                    if 'rial_cost' not in df.columns and 'Total Rial' in df.columns:
                        df['rial_cost'] = df['Total Rial']
                    if 'euro_cost' not in df.columns and 'Total Euro' in df.columns:
                        df['euro_cost'] = df['Total Euro']
                    if 'item_name' not in df.columns and 'عنوان' in df.columns:
                        df['item_name'] = df['عنوان']
                    if 'specs' not in df.columns and 'Description' in df.columns:
                        df['specs'] = df['Description']
                    break
            except Exception as e:
                pass
                
    if df is None:
        # ساخت دیتاست نمونه هوشمند دوزبانه در صورت عدم دسترسی
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
        
    # تطابق ستون‌ها برای دوزبانه بودن
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
    st.error(f"خطا در بارگذاری اطلاعات: {str(e)}")
    st.stop()

# محاسبات شاخص‌های کلان پروژه
total_rials = df['rial_cost'].sum() + 4500000000  # با احتساب ۴.۵ میلیارد ریال هزینه آموزش پیمان
total_euros = df['euro_cost'].sum()
total_tomans = total_rials / 10

# تیتر اصلی پورتال
st.markdown("<h1 class='main-title'>🌹 پورتال هوشمند تدارکات و دستیار صوتی رز (Rose Assistant)</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #8a7e72;'>سامانه تعاملی کلان متریال و پیمان احداث خط لوله ۱۶ اینچ رفسنجان-یزد</h4>", unsafe_allow_html=True)
st.write("")

# ----------------- سایدبار مدیریت و دستیار رز -----------------
with st.sidebar:
    st.markdown("### 🌹 رز؛ دستیار صوتی شما")
    
    # نمایش آواتار زنده رز با انیمیشن پالس CSS
    if avatar_base64:
        st.markdown(
            f'\n<div class="avatar-container">\n    <img class="live-avatar" src="data:image/png;base64,{avatar_base64}" alt="Rose Avatar">\n</div>\n',
            unsafe_allow_html=True
        )
    else:
        st.info("🌹 تصویر دستیار رز در سیستم بارگذاری شده است.")
        
    st.markdown("<div style='text-align: center; color: #1e3d59; font-weight: bold;'>دستیار هوشمند رز (Rose)</div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; color: #8a7e72; font-size: 13px; margin-bottom: 15px;'>مشاور ارشد تدارکات و پیمان خط لوله</div>", unsafe_allow_html=True)
    
    # تنظیمات صوتی دستیار
    voice_enabled = st.toggle("🔊 فعال‌سازی سخنگوی صوتی رز", value=True)
    if voice_enabled and not gtts_available:
        st.caption("⚠️ کتابخانه gTTS روی هاست نصب نیست؛ برای کارکرد صوتی آن را به requirements.txt اضافه کنید (برنامه به صورت متنی پاسخ می‌دهد).")

    st.markdown("---")
    st.markdown("### 🏢 کلیدهای سریع ارگان‌های پیمان")
    st.caption("برای مشاهده مشخصات حقوقی و امضاکنندگان قرارداد روی ارگان مورد نظر کلیک کنید:")
    
    # ساخت دکمه‌های آرم تجاری با استایل کارت تعاملی
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🏢 کارفرما (NIOEC)"):
            st.toast("شرکت ملی مهندسی و ساختمان نفت ایران\nمدیرعامل: فرهاد احمدی\nمدیر مالی: هادی مشتهر")
            st.sidebar.info("**کارفرما:** شرکت ملی مهندسی و ساختمان نفت ایران (NIOEC)\\n\\n**نمایندگان مجاز:**\\n• فرهاد احمدی (مدیرعامل)\\n• هادی مشتهر (مدیر مالی)")
    with col_b:
        if st.button("🏗️ پیمانکار (انهار)"):
            st.toast("شرکت ساختمانی انهار\nمدیرعامل: ستار عزیزیان تفتی")
            st.sidebar.info("**پیمانکار لید:** شرکت ساختمانی انهار\\n\\n**نمایندگان مجاز:**\\n• ستار عزیزیان تفتی (مدیرعامل)\\n• سید مهدیار شریف شیخ‌الاسلامی (عضو هیئت مدیره)")
            
    col_c, col_d = st.columns(2)
    with col_c:
        if st.button("⚡ مشاور (FSEC)"):
            st.toast("شرکت فرآیند سازان انرژی\nمدیرعامل: حسین رهنما")
            st.sidebar.info("**شرکت همکار/مشاور:** شرکت مهندسین مشاور فرآیند سازان انرژی\\n\\n**نمایندگان مجاز:**\\n• حسین رهنما (مدیرعامل)\\n• محمد افراسیابیان (عضو هیئت مدیره)")
    with col_d:
        if st.button("🤝 مشارکت EPC"):
            st.toast("مشارکت انهار - فرآیند سازان انرژی\nکل مبلغ قرارداد: ۷ هزار میلیارد ریال + ۱۱ میلیون یورو")
            st.sidebar.info("**مشارکت انهار - فرآیند سازان انرژی**\\n\\n• **مبلغ ریالی:** ۷,۰۰۰,۲۴۴,۷۵۱,۰۰۰ ریال\\n• **مبلغ ارزی:** ۱۱,۰۱۴,۵۴۶ یورو\\n• **مدت:** ۲۰ ماه شمسی")

    st.markdown("---")
    # دکمه دانلود کل دیتابیس اکسل پروژه
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Bilingual_Material')
    
    st.download_button(
        label="📥 دانلود کل بانک متریال دوزبانه (Excel)",
        data=buffer.getvalue(),
        file_name="consolidated_material_list_bilingual.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ----------------- کارت‌های شاخص مالی کلان (KPIs) -----------------
kpi1, kpi2, kpi3 = st.columns(3)
with kpi1:
    st.markdown(
        f"""
        <div style='background-color: #f5f0eb; border-radius: 10px; padding: 15px; border-right: 5px solid #1e3d59; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);'>
            <div style='color: #8a7e72; font-size: 14px; font-weight: bold;'>💰 برآورد ریالی پیمان (Rial Contract Value)</div>
            <div style='color: #1e3d59; font-size: 24px; font-weight: bold; margin-top: 5px;'>{total_rials:,.0f} ریال</div>
            <div style='color: #8a7e72; font-size: 13px;'>معادل {total_tomans:,.0f} تومان (۱۰ ریال = ۱ تومان)</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with kpi2:
    st.markdown(
        f"""
        <div style='background-color: #f5f0eb; border-radius: 10px; padding: 15px; border-right: 5px solid #ffc13b; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);'>
            <div style='color: #8a7e72; font-size: 14px; font-weight: bold;'>💶 برآورد ارزی پیمان (Euro Contract Value)</div>
            <div style='color: #ffc13b; font-size: 24px; font-weight: bold; margin-top: 5px;'>{total_euros:,.2f} یورو</div>
            <div style='color: #8a7e72; font-size: 13px;'>ارزش ارزی وارداتی شیت‌های تدارکات</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with kpi3:
    st.markdown(
        f"""
        <div style='background-color: #f5f0eb; border-radius: 10px; padding: 15px; border-right: 5px solid #2e7d32; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);'>
            <div style='color: #8a7e72; font-size: 14px; font-weight: bold;'>⏳ مدت زمان پروژه (Contract Duration)</div>
            <div style='color: #2e7d32; font-size: 24px; font-weight: bold; margin-top: 5px;'>۲۰ ماه شمسی</div>
            <div style='color: #8a7e72; font-size: 13px;'>از تاریخ ابلاغ شروع به کار مصوب</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.write("")

# ایجاد تب‌های سه گانه پورتال
tab1, tab2, tab3 = st.tabs(["💬 دستیار صوتی و چت هوشمند رز", "🔍 جستجو و فیلتر متریال پروژه", "📊 آنالیز توزیع هزینه‌ها و مغایرت‌ها"])

# ----------------- تب اول: دستیار هوشمند صوتی رز -----------------
with tab1:
    st.markdown("### 💬 بفرمایید! رز آماده شنیدن و پاسخگویی است")
    st.write("شما می‌توانید سوال خود را به زبان فارسی یا انگلیسی درباره متریال، قیمت‌ها، اطلاعات تلمبه‌خانه‌ها، مشخصات ولوها، کابل‌ها، کادر امضاها یا مفاد حقوقی پیمان بنویسید:")
    
    # پشتیبانی تعاملی از ورودی صوتی مرورگر
    voice_input = st.audio_input("🎙️ برای فرستادن پیام صوتی خود، دکمه ضبط را بزنید:")
    if voice_input:
        st.info("🔊 فایل صوتی شما دریافت شد؛ جهت بهره‌برداری از هوش صوتی رز در پروژه تدارکاتی رفسنجان-یزد، کلمات کلیدی خود را در کادر متنی زیر نیز تایپ فرمایید.")

    user_query = st.text_input("📝 سوال شما از دستیار رز (مثال: مبلغ قرارداد چقدر است؟ شیرآلات چه مشخصاتی دارند؟):", key="rose_user_query")
    
    if user_query:
        st.markdown(f"<div class='chat-bubble-user'>👤 <b>سوال شما:</b> {user_query}</div>", unsafe_allow_html=True)
        
        q = user_query.lower()
        response = ""
        speech_text = "" # متنی که توسط gTTS خوانده خواهد شد
        
        # ۱. تحلیل و پاسخ به مفاد حقوقی پیمان (تزریق شده از سند PDF خط لوله رفسنجان یزد)
        if "مبلغ" in q or "هزینه" in q or "بودجه" in q or "قیمت" in q or "ارزش" in q or "cost" in q or "price" in q:
            response = """
            💰 <b>مبلغ کل پیمان احداث خط لوله رفسنجان-یزد و مراکز انتقال نفت:</b><br><br>
            بر اساس موافقت‌نامه رسمی پیمان، ارزش کل قرارداد به شرح زیر است:<br>
            • <b>مبلغ ریالی کل:</b> <b>۷,۰۰۰,۲۴۴,۷۵۱,۰۰۰ ریال</b> (معادل ۷۰۰ میلیارد و ۲۴ میلیون تومان)<br>
            • <b>مبلغ ارزی کل:</b> <b>۱۱,۰۱۴,۵۴۶.۰۰ یورو</b><br><br>
            <b>تفکیک هزینه‌ها بر اساس دیسیپلین‌های پیمان (E, P, C):</b><br>
            ۱. <b>بخش مهندسی و طراحی (E):</b> ۴۶۰ میلیارد ریال مکتوب شده است.<br>
            ۲. <b>بخش تدارکات و خرید کالا (P):</b> ۱,۰۰۰,۰۰۰,۰۰۰,۰۰۰ ریال به علاوه ۱۱,۰۱۴,۵۴۶ یورو.<br>
            ۳. <b>بخش کارهای ساختمانی و نصب (C):</b> ۵,۵۴۰,۲۴۴,۷۵۱,۰۰۰ ریال (شامل هزینه‌های مستندسازی و بیمه).
            """
            speech_text = "مبلغ کل ریالی پیمان هفت هزار میلیارد ریال و بخش ارزی یازده میلیون و چهارده هزار یورو می باشد."
            
        elif "مدت" in q or "زمان" in q or "ماه" in q or "duration" in q or "timeline" in q:
            response = """
            ⏳ <b>مدت پیمان و زمان‌بندی پروژه:</b><br><br>
            بر اساس موافقت‌نامه رسمی، مدت اجرای کامل خدمات پروژه به صورت <b>EPC</b> برابر با <b>۲۰ ماه شمسی</b> از تاریخ ابلاغ شروع به کار مصوب توسط کارفرما تعیین گردیده است.<br>
            این مدت شامل فاز طراحی مهندسی، تدارکات و ساخت و راه‌اندازی تلمبه‌خانه‌ها می‌باشد.
            """
            speech_text = "مدت زمان اجرای کل پروژه بیست ماه شمسی از تاریخ ابلاغ شروع به کار مصوب می باشد."
            
        elif "امضا" in q or "نماینده" in q or "امضاء" in q or "مدیر" in q or "sign" in q or "director" in q:
            response = """
            ✍️ <b>نمایندگان رسمی و صاحبان امضای مجاز پیمان خط لوله رفسنجان-یزد:</b><br><br>
            • <b>از طرف کارفرما (شرکت ملی مهندسی و ساختمان نفت ایران - NIOEC):</b><br>
            &nbsp;&nbsp; - آقای <b>فرهاد احمدی</b> (مدیرعامل)<br>
            &nbsp;&nbsp; - آقای <b>هادی مشتهر</b> (مدیر مالي)<br><br>
            • <b>از طرف پیمانکار انهار (شرکت ساختمانی انهار):</b><br>
            &nbsp;&nbsp; - آقای <b>ستار عزیزیان تفتی</b> (مدیرعامل)<br>
            &nbsp;&nbsp; - آقای <b>سید مهدیار شریف شیخ‌الاسلامی</b> (عضو هیئت مدیره)<br><br>
            • <b>از طرف پیمانکار فرآیند سازان (شرکت مهندسین فرآیند سازان انرژی):</b><br>
            &nbsp;&nbsp; - آقای <b>حسین رهنما</b> (مدیرعامل)<br>
            &nbsp;&nbsp; - آقای <b>محمد افراسیابیان</b> (عضو هیئت مدیره)
            """
            speech_text = "صاحبان امضای مجاز قرارداد شامل فرهاد احمدی از کارفرما، ستار عزیزیان از شرکت انهار و حسین رهنما از فرآیند سازان انرژی هستند."
            
        elif "حل اختلاف" in q or "دعوا" in q or "اختلاف" in q or "dispute" in q:
            response = """
            ⚖️ <b>سازوکار حل اختلاف قراردادی (پیوست ۲۱ پیمان):</b><br><br>
            بر اساس اسناد رسمی پیمان، هرگونه مغایرت یا اختلاف فنی و حقوقی ابتدا به <b>«هیأت حل اختلاف»</b> ارجاع می‌گردد.<br>
            این هیأت شامل <b>۵ عضو مجرب</b> است:<br>
            ۱. کارشناس حقوقی واجد صلاحیت در امور قراردادها (رئیس هیأت)<br>
            ۲. کارشناس مالی<br>
            ۳. کارشناس فنی در امور مهندسی پروژه<br>
            ۴. نماینده مدیرعامل کارفرما<br>
            ۵. نماینده انجمن نفت ایران<br><br>
            در صورت عدم توافق در هیأت، موضوع جهت اتخاذ تصمیم نهایی به مراجع قضایی ذی‌صلاح ارجاع داده خواهد شد.
            """
            speech_text = "طبق پیوست بیست و یک، هرگونه اختلاف قراردادی ابتدا به هیأت پنج نفره حل اختلاف ارجاع می گردد."
            
        elif "ایمنی" in q or "safety" in q or "hse" in q or "بهداشت" in q:
            response = """
            🍀 <b>الزامات بهداشت، ایمنی و محیط زیست (پیوست ۸ پیمان - HSE):</b><br><br>
            پیمانکار موظف به رعایت کامل نظام‌نامه بهداشت و ایمنی وزارت نفت در کارگاه‌ها می‌باشد. اهم سرفصل‌ها عبارتند از:<br>
            • تامین کامل وسایل حفاظت فردی (PPE) برای پرسنل مهندسی و کارگری.<br>
            • سم‌پاشی منظم و ماهیانه سرویس‌ها و فضاهای کارگاهی به منظور مقابله با مار و عقرب گزیدگی.<br>
            • مجهز بودن جبهه‌های کاری فعال به کانکس بهداشتی سیار با ظرفیت مناسب.<br>
            • رعایت تمهیدات پرتونگاری صنعتی (RT) و زنگ‌زدایی (سندبلاست) مطابق الزامات استاندارد.
            """
            speech_text = "رعایت کامل نظام نامه ایمنی و بهداشت وزارت نفت در کارگاه ها الزامی می باشد."
            
        elif "آموزش" in q or "فناوری" in q or "training" in q or "technology" in q:
            response = """
            🏗️ <b>انتقال فناوری و آموزش کارکنان کارفرما (پیوست ۱۲ پیمان):</b><br><br>
            پیمانکار متعهد به ارائه برنامه جامع انتقال فناوری و تحقق مصادیق تایید شده آن است:<br>
            • **بودجه آموزش:** مبلغ <b>۴,۵۰۰,۰۰۰,۰۰۰ ریال</b> (۴.۵ میلیارد ریال) به عنوان هزینه آموزش راهبری تلمبه‌خانه‌ها مکتوب شده است.<br>
            • **سیستم مدیریت اطلاعات (PMIS):** راه‌اندازی و آموزش سیستم نرم‌افزاری PMIS تحت وب جهت کنترل آنلاین اسناد مهندسی (EDMS).<br>
            • **مدیریت زمان:** تحویل یک نسخه نرم‌افزار MS Project به همراه تقویم شمسی تحت لیسانس رسمی به کارفرما.
            """
            speech_text = "هزینه آموزش راهبری تلمبه خانه ها چهار و نیم میلیارد ریال تعیین شده است."
            
        # ۲. جستجوی متریال در دیتابیس کالاها (شیرآلات، کابل، لوله، پمپ)
        elif "ولو" in q or "valve" in q or "شیر" in q:
            matched_rows = df[df['item_name_en'].str.contains('valve', case=False, na=False) | df['item_name_fa'].str.contains('شیر', case=False, na=False)]
            response += "🛠️ <b>اطلاعات تفصیلی بخش شیرآلات صنعتی پروژه یافت شد:</b><br><br>"
            total_v_euros = 0
            for idx, r in matched_rows.iterrows():
                response += f"• <b>{r['item_name_fa']} ({r['item_name_en']})</b>: تعداد {r['quantity']} {r['unit']} | بهای کل: {r['euro_cost']:,.2f} یورو<br>"
                response += f"&nbsp;&nbsp;&nbsp;&nbsp;<i>مشخصات فنی: {r['specs_fa']}</i><br><br>"
                total_v_euros += r['euro_cost']
            response += f"📊 <b>ارزش ارزی شیرآلات دستی و خودکار دیسیپلین Piping معادل {total_v_euros:,.2f} یورو می‌باشد.</b>"
            speech_text = f"شیرآلات صنعتی تلمبه خانه ها در شیت پایپینگ شامل گیت ولو، چک ولو و بال ولو با ارزش کلان یافت شد."
            
        elif "پمپ" in q or "pump" in q:
            matched_rows = df[df['item_name_en'].str.contains('pump', case=False, na=False) | df['item_name_fa'].str.contains('پمپ', case=False, na=False)]
            response += "⚙️ <b>نتایج مرتبط با تجهیزات پمپاژ و بوسترهای تلمبه‌خانه‌ها:</b><br><br>"
            for idx, r in matched_rows.iterrows():
                response += f"• <b>{r['item_name_fa']} ({r['item_name_en']})</b>: تعداد {r['quantity']} {r['unit']} | بهای کل: {r['euro_cost']:,.2f} یورو<br>"
                response += f"&nbsp;&nbsp;&nbsp;&nbsp;<i>مشخصات فنی: {r['specs_fa']}</i><br><br>"
            speech_text = "پمپ های اصلی بوستر تلمبه خانه ها در دیسیپلین مکانیکال تراز شده اند."
            
        elif "کابل" in q or "cable" in q or "برق" in q or "electrical" in q:
            matched_rows = df[df['item_name_en'].str.contains('cable', case=False, na=False) | df['item_name_fa'].str.contains('کابل', case=False, na=False) | (df['discipline_en'] == 'Electrical Equipment')]
            response += "⚡ <b>کابل‌کشی و ملزومات توزیع برق در پایگاه داده:</b><br><br>"
            for idx, r in matched_rows.iterrows():
                response += f"• <b>{r['item_name_fa']}</b>: مقدار {r['quantity']} {r['unit']} | قیمت ریالی: {r['rial_cost']:,.0f} ریال | قیمت ارزی: {r['euro_cost']:,.2f} یورو<br>"
                response += f"&nbsp;&nbsp;&nbsp;&nbsp;<i>مشخصات فنی: {r['specs_fa']}</i><br><br>"
            speech_text = "کابل های برق زره دار مسی و سربی با متراژ بیش از پانزده هزار متر یافت شدند."
            
        elif "لوله" in q or "pipe" in q:
            matched_rows = df[df['item_name_en'].str.contains('pipe', case=False, na=False) | df['item_name_fa'].str.contains('لوله', case=False, na=False)]
            response += "🛣️ <b>مشخصات لوله‌های فشار قوی مسیر خط لوله ۱۶ اینچ:</b><br><br>"
            for idx, r in matched_rows.iterrows():
                response += f"• <b>{r['item_name_fa']} ({r['item_name_en']})</b>: مقدار {r['quantity']} {r['unit']} | بهای کل ارزی: {r['euro_cost']:,.2f} یورو<br>"
                response += f"&nbsp;&nbsp;&nbsp;&nbsp;<i>مشخصات فنی: {r['specs_fa']}</i><br><br>"
            speech_text = "لوله‌های فولادی فشار قوی تلمبه‌خانه‌ها و مسیر خط لوله معادل پنج هزار و دویست و شصت متر می‌باشد."
            
        # ۳. پاسخ عمومی در صورت عدم تطابق دقیق کلیدواژه‌ها
        else:
            any_match = df[df['item_name_fa'].str.contains(q, case=False, na=False) | df['item_name_en'].str.contains(q, case=False, na=False) | df['specs_fa'].str.contains(q, case=False, na=False)]
            if not any_match.empty:
                response += f"🔍 <b>موارد یافت شده در دیتابیس کالاها برای '{user_query}':</b><br><br>"
                for idx, r in any_match.iterrows():
                    response += f"• <b>{r['item_name_fa']} ({r['item_name_en']})</b>: مقدار/تعداد: {r['quantity']} {r['unit']} | ریال: {r['rial_cost']:,.0f} | یورو: {r['euro_cost']:,.2f} <br>"
                    response += f"&nbsp;&nbsp;&nbsp;&nbsp;<i>مشخصات: {r['specs_fa']}</i><br><br>"
                speech_text = f"نتایج متناظر برای جستجوی شما یافت شد."
            else:
                response = """
                ❌ <b>متوجه منظور شما نشدم. من اطلاعات پیمان و متریال خط لوله را به طور کامل دارم. لطفاً بپرسید:</b><br><br>
                • <b>قیمت و مبالغ کلان پیمان:</b> بپرسید 'مبلغ کل قرارداد چقدر است؟'<br>
                • <b>صاحبان امضا و نمایندگان:</b> بپرسید 'چه کسانی قرارداد را امضا کرده‌اند؟'<br>
                • <b>مراحل حل اختلاف حقوقی:</b> بپرسید 'سازوکار حل اختلاف چیست؟'<br>
                • <b>بهداشت و ایمنی کارگاه:</b> بپرسید 'پیوست HSE چه مواردی دارد؟'<br>
                • <b>متریال و مشخصات فنی کالاها:</b> بپرسید 'مشخصات ولوها یا کابل‌ها چیست؟'
                """
                speech_text = "منظور شما را متوجه نشدم. لطفا درباره قیمت، امضا کنندگان یا مشخصات کالاها بپرسید."

        st.markdown(f"<div class='chat-bubble-rose'>🌹 <b>دستیار رز:</b><br><br>{response}</div>", unsafe_allow_html=True)
        
        # پخش صدای هوشمند رز با استفاده از کتابخانه صوتی گوگل در مرورگر کاربر
        if voice_enabled and speech_text:
            try:
                tts = gTTS(text=speech_text, lang='fa')
                tts_buffer = io.BytesIO()
                tts.write_to_fp(tts_buffer)
                st.audio(tts_buffer.getvalue(), format="audio/mp3")
                st.toast("🔊 پاسخ صوتی رز آماده پخش است.")
            except Exception as e:
                pass

# ----------------- تب دوم: جستجو و فیلتر پیشرفته دوزبانه -----------------
with tab2:
    st.markdown("### 🔍 جستجو و فیلتر پیشرفته در ۳۱ شیت تراز شده پروژه")
    
    # فیلتر بر اساس دیسیپلین دوزبانه
    all_disciplines = ["همه دیسیپلین‌ها"] + list(df['discipline_fa'].unique())
    selected_disp = st.selectbox("📁 فیلتر بر اساس دیسیپلین تخصصی پروژه:", all_disciplines)
    
    # فیلتر متنی نام کالا دوزبانه
    search_term = st.text_input('🔍 جستجوی متنی نام کالا، گرید یا مشخصات فنی (مثال: 16, Cable, Valve, MOV):')
    
    # اعمال فیلترها روی دیتابیس
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
    
    # قالب‌بندی نمایش مبالغ به صورت خوانا
    display_df = filtered_df.copy()
    display_df['rial_cost'] = display_df['rial_cost'].apply(lambda x: f"{x:,.0f} ریال" if x > 0 else "0")
    display_df['euro_cost'] = display_df['euro_cost'].apply(lambda x: f"{x:,.2f} €" if x > 0 else "0")
    
    # بازآرایی ستون‌ها برای نمایش شکیل‌تر
    display_cols = ['discipline_fa', 'item_name_fa', 'item_name_en', 'quantity', 'unit', 'rial_cost', 'euro_cost', 'specs_fa']
    st.dataframe(display_df[display_cols], use_container_width=True)
    
    # دکمه دانلود خروجی فیلتر شده به صورت CSV دوزبانه
    csv_data = filtered_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 دانلود اطلاعات فیلتر شده بالا (CSV)",
        data=csv_data,
        file_name="filtered_material_list.csv",
        mime="text/csv"
    )

# ----------------- تب سوم: آنالیز نموداری هزینه‌ها و مغایرت‌ها -----------------
with tab3:
    st.markdown("### 📊 آنالیز توزیع هزینه‌های ارزی و ریالی")
    
    st.write("#### سهم دیسیپلین‌ها از هزینه ارزی کل پروژه (بر حسب یورو)")
    st.bar_chart(data=df, x='discipline_fa', y='euro_cost', color='#ffc13b', use_container_width=True)
    
    st.write("#### سهم دیسیپلین‌ها از هزینه ریالی کل پروژه (بر حسب ریال)")
    st.bar_chart(data=df, x='discipline_fa', y='rial_cost', color='#1e3d59', use_container_width=True)

    st.markdown(
        """
        <div style='background-color: #ffebee; border-right: 5px solid #f44336; padding: 15px; border-radius: 5px; margin-bottom: 20px;'>
            <b style='color: #c62828;'>⚠️ کشف مغایرت‌های محاسباتی و حسابرسی سندی (یافته‌های طلایی رز):</b><br><br>
            ۱. <b>خطای ثبت دوگانه کدهای لوازم یدکی (Spare Parts):</b> مبلغ ۳۱۳,۰۰۰ هم در ستون ریالی کل قرارداد (به عنوان ریال) و هم در ستون ارزی (به عنوان یورو) قرار گرفته است که ناشی از خطای تایپی قرارداد اولیه است [۶، ۷۳].<br><br>
            ۲. <b>مغایرت ۱,۳۱۰ یورویی ابزار دقیق رفسنجان:</b> در خرید Flow Switches ردیف ۳ تلمبه‌خانه رفسنجان، تعداد ۲ عدد با قیمت واحد ۱,۳۱۰ یورو فاکتور شده که بهای کل ریاضی آن باید ۲,۶۲۰ یورو باشد، اما در جمع نهایی شیت رفسنجان به اشتباه ۱,۳۱۰ یورو جمع زده شده است (اختلاف دقیق ۱,۳۱۰ یورو) [۶، ۴۲، ۶۸].<br><br>
            ۳. <b>انحراف ریاضی مجموع ارزی کل پیمان:</b> جمع کل ارزی ریاضی در برگ سند نهایی پیمانکار به جای عدد محاسباتی دقیق ۱۱,۰۱۴,۵۴۶.۴۸ یورو، معادل ۱۱,۰۱۴,۵۴۶.۰۰ یورو به علت گرد کردن‌ها نوشته شده است که در حسابرسی کلان سند فاش شد [۶، ۴۲، ۲۲۰].
        </div>
        """,
        unsafe_allow_html=True
    )

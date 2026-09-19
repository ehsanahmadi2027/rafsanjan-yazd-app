# ROSE — Project Intelligence System

MVP دستیار مهندسی پروژه خط لوله رفسنجان–یزد.

### امکانات
- رابط فارسی RTL با ظاهر Dark/Futuristic
- چت متنی
- بارگذاری PDF
- استخراج متن با حفظ شماره صفحه
- جستجوی فارسی/انگلیسی
- نمایش منبع و صفحه
- API آماده توسعه به RAG/LLM/Voice/Vector DB

### اجرا در Windows
```bat
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```
سپس `http://127.0.0.1:8000` را باز کنید.

### نکته امنیتی
قرارداد و اسناد محرمانه را داخل GitHub عمومی قرار ندهید؛ آنها را فقط از داخل پنل برنامه بارگذاری کنید.

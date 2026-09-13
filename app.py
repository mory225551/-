import os
import json
import io
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import google.generativeai as genai
from PIL import Image

app = FastAPI(title="أستاذ اليمن AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ضع مفتاحك الفعلي من Google Gemini هنا لكي يعمل التطبيق فوراً
GENAI_KEY = os.getenv("GEMINI_API_KEY", "ضع_مفتاحك_هنا")
genai.configure(api_key=GENAI_KEY)

@app.post("/api/ask")
async def ask_professor(
    text_question: str = Form(None), 
    image_file: UploadFile = File(None),
    follow_up_type: str = Form(None),
    previous_context: str = Form(None)
):
    try:
        base_prompt = """
        أنت "أستاذ اليمن AI"، مدرس خصوصي ذكي في منهج الثالث الثانوي بالجمهورية اليمنية.
        أجب بصيغة JSON حصراً كالتالي:
        {
          "classification": {"subject": "المادة هنا", "unit": "اسم الوحدة"},
          "steps": ["الخطوة 1", "الخطوة 2", "الخطوة 3"],
          "voice_script": "الشرح الصوتي المفترض هنا"
        }
        """
        contents = [base_prompt]
        if text_question: contents.append(f"السؤال: {text_question}")
        if image_file:
            image_data = await image_file.read()
            contents.append(Image.open(io.BytesIO(image_data)))

        model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})
        response = model.generate_content(contents)
        return JSONResponse(content=json.loads(response.text))
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

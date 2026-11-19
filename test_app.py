import os
import json
from flask import Flask
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from whatsapp import register

load_dotenv()
app = Flask(__name__)
ai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


class WorstBiomarker(BaseModel):
    name: str = Field(description="Most abnormal test name, or main test if all are normal")
    value: float = Field(description="Numeric result value")
    range_low: float = Field(description="Lower bound of printed normal range")
    range_high: float = Field(description="Upper bound of printed normal range")


class ReportAnalysis(BaseModel):
    patient_id: str = Field(description="Patient name or ID printed on report, or 'Unknown Patient'")
    level: str = Field(description="'urgent' if any value is dangerously abnormal, otherwise 'normal'")
    worst: WorstBiomarker


def detect_mime(data: bytes) -> str:
    if data.startswith(b"\x89PNG"):
        return "image/png"
    if data.startswith(b"%PDF"):
        return "image/pdf"
    return "image/jpeg"


def process_report(img, source, message_id, caption):
    prompt = (
        "Read this medical lab report screenshot or PDF for Dr. Rao. "
        "Extract the patient's name/ID and compare every test value against the normal reference range "
        "printed on the report. Set level to 'urgent' ONLY if a value is critically/dangerously outside "
        "normal range (e.g., high/low potassium, severe anemia, very high sugar/creatinine, low platelets); "
        "otherwise set level to 'normal'."
    )
    response = ai_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[types.Part.from_bytes(data=img, mime_type=detect_mime(img)), prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ReportAnalysis,
        ),
    )
    result = json.loads(response.text)
    result["id"] = 1
    print(f"\n[GEMINI RESULT]\n{json.dumps(result, indent=2)}\n")
    return result


register(app, process_report)

if __name__ == "__main__":
    app.run(port=5000)

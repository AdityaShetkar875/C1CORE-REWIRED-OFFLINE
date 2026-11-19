import os
import threading
import requests
from flask import request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client


def register(app, process_report):
    @app.post("/webhook/whatsapp")
    def whatsapp_webhook():
        reply = MessagingResponse()
        if int(request.form.get("NumMedia", 0)) == 0:
            reply.message("Please send a screenshot or photo of the report.")
            return str(reply)

        sid = request.form.get("MessageSid")
        caption = request.form.get("Body", "")
        url = request.form.get("MediaUrl0")

        def work():
            try:
                img = requests.get(
                    url,
                    auth=(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN")),
                    timeout=30,
                ).content
                r = process_report(img, "whatsapp", sid, caption)
                if r.get("level") == "urgent":
                    w = r.get("worst", {})
                    Client(
                        os.getenv("TWILIO_ACCOUNT_SID"),
                        os.getenv("TWILIO_AUTH_TOKEN"),
                    ).messages.create(
                        from_=os.getenv("TWILIO_WHATSAPP_FROM"),
                        to=os.getenv("DOCTOR_WHATSAPP"),
                        body=(
                            f"URGENT: {r.get('patient_id')} - {w.get('name')} {w.get('value')} "
                            f"(range {w.get('range_low')}-{w.get('range_high')}). Open Nabz."
                        ),
                    )
            except Exception as e:
                print(f"[whatsapp.py] Error processing {sid}: {e}")

        threading.Thread(target=work, daemon=True).start()
        reply.message("Received. Your doctor will review it.")
        return str(reply)

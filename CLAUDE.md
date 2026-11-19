# Nabz

Lab-report triage for busy doctors. Patients send lab reports as screenshots
(WhatsApp, in the demo Telegram). Nabz reads each one, ranks patients by
urgency, stores patient history, and alerts the doctor to urgent results.
It orders the doctor's queue. It never diagnoses.

Built from scratch at the Rewired offline round (Theme B: Mirror), 19 Nov 2026,
10 AM to 4 PM. Team C1CORE. All data is synthetic.

# Flow
1. Patient sends a screenshot to the bot (or the doctor uploads it on the site).
2. App converts PDFs to images, then reads the image with the Gemini vision API:
   patient, date, tests (name, value, unit, printed range), message text.
3. rules.py sets each test to normal / watch / urgent from how far the value is
   outside the range printed on the report. Bands are editable settings.
   Keywords (chest pain, breathless, fainted) raise priority.
4. Everything is saved in SQLite. A human confirms or corrects the reading.
5. The website shows an inbox sorted by urgency. Urgent reports trigger a
   Telegram alert to the doctor.

# Stack
Flask (Python), SQLite (sqlite3), vanilla HTML/CSS/JS served from /static,
Gemini API (google-genai), pypdfium2 (PDF to image), python-telegram-bot.
One app serves both the site and the API.

# Database tables
patients, reports, test_results, messages, alerts, settings

# Routes
POST /api/reports (image or PDF) | GET /api/inbox |
POST /api/reports/<id>/confirm | GET /api/patients | GET /api/patients/<id> |
GET /api/reports/<id>/reply | GET /api/compare | POST /api/reset |
GET /api/health

# Coding rules
- Keep code short, simple and readable. Small functions, short comments.
- Put rules and thresholds in one file (rules.py) so they are easy to explain.
- Explain every new piece of code in plain words in 2-3 sentences after writing it.
- No new libraries without asking first.
- Validate inputs. Return clear JSON errors. Never crash the demo path.
- Write unit tests for rules.py. Run `python -m unittest` after each change.

# Safety and data
- Synthetic data only: fictional "Lab X", invented patients. No real health data.
- Never tell a patient a result is fine or critical. Patients only get
  "Received. Your doctor will review it."
- The AI can misread digits, so every reading has a human confirm step.
- Keys live in .env. Never commit keys, .env, uploads or the database.

# Demo path (must never break)
Send screenshot -> reading appears -> inbox reorders -> red card on top ->
patient history with trend -> drafted reply -> proof panel (arrival order vs Nabz).

# Git
Commit small and often with clear messages. Push after every working step.
All work happens inside the build window. No code copied from older projects.

# Declarations
AI tools: Claude, Claude Code. APIs: Gemini, Telegram Bot API. Libraries:
Flask, python-dotenv, google-genai, pypdfium2, pillow, python-telegram-bot.

# Status
Done: nothing yet.
Working on: Flask skeleton, database, upload route.
Next: rules, inbox, confirm, patient history, bot.
# AIVOA Complaint Management System

An AI-powered Customer Complaint Management module for pharmaceutical manufacturers
(API and FDF), built for the AIVOA take-home assignment.

Analysts log a complaint by dropping in a source document (email, PDF, DOCX) or
pasting text. A LangGraph agent (backed by Groq LLMs) extracts the structured
complaint fields, checks completeness, classifies risk, drafts a summary and a
CAPA recommendation, and flags likely duplicates — auto-populating the intake
form so the analyst just has to review, correct, and save.

## Tech stack

| Layer            | Choice                                              |
|-------------------|------------------------------------------------------|
| Frontend          | React + Redux Toolkit                                |
| Backend           | Python, FastAPI                                       |
| AI orchestration  | LangGraph                                             |
| LLMs              | Groq — `gemma2-9b-it` (extraction/completeness), `llama-3.3-70b-versatile` (risk/summary/root-cause/CAPA) |
| Database          | PostgreSQL (SQLite fallback for local dev)            |
| Font              | Google Inter                                          |

## How it maps to the demo workflow

1. **Log Customer Complaint form** (left panel) — four sections: Origin &
   Customer Details, Product & Batch Identification, Complaint Details, and
   Initial Assessment & Priority. Fields start empty ("Awaiting AI
   extraction...") and light up once the AI populates them.
2. **AI Complaint Intake Assistant** (right panel) — drag-and-drop a document
   or paste complaint text, watch the extraction progress bar, and chat with
   the assistant to ask questions or manually correct/add details.
3. **Save Complaint** persists the record (plus whatever AI analysis has run)
   to the database and it shows up under **All Complaints** with its AI risk
   classification and status.

## AI pipeline (LangGraph)

`backend/app/agents/langgraph_agent.py` defines a `StateGraph`:

```
START -> extract -> completeness -> risk -> summary -> root_cause_capa -> END
```

- **extract** (`gemma2-9b-it`) — reads the raw document/email text and returns
  the 13 structured form fields as JSON.
- **completeness** (`gemma2-9b-it`) — scores 0–100 how ready the record is for
  a formal investigation and lists missing/weak fields.
- **risk** (`llama-3.3-70b-versatile`) — classifies Critical/High/Medium/Low
  risk with a rationale (patient safety / GMP impact / business impact).
- **summary** (`llama-3.3-70b-versatile`) — 2–3 sentence QA-manager-ready
  summary.
- **root_cause_capa** (`llama-3.3-70b-versatile`) — root-cause hypotheses plus
  a CAPA (correction / corrective action / preventive action) recommendation.

**Duplicate detection** runs as a deterministic post-step (`agents/tools.py`)
against existing DB records (same product + batch, similar description) rather
than as a graph node, since it needs a DB session — kept dependency-free for
the demo using `difflib`; a production version would use embeddings + a
vector store.

**Chat assistant** (`run_chat_turn`) is a single-turn reactive call (not part
of the fixed pipeline) that can answer questions about the on-screen complaint
and update fields the analyst mentions in chat.

## Bonus AI features implemented

- ✅ Complaint Completeness Checker
- ✅ AI Risk Classification
- ✅ Complaint Summary
- ✅ Root Cause Recommendation
- ✅ CAPA Recommendation
- ✅ Duplicate Complaint Detection
- ✅ Conversational assistant that can extract/update fields from free-form chat

## Project structure

```
aivoa-complaint-system/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app
│   │   ├── config.py          # env settings
│   │   ├── database.py        # SQLAlchemy engine/session
│   │   ├── models.py          # Complaint, ChatMessage
│   │   ├── schemas.py         # Pydantic request/response models
│   │   ├── routers/
│   │   │   ├── complaints.py  # CRUD for complaints
│   │   │   └── ai.py          # /ai/extract, /ai/chat, /ai/save-with-ai
│   │   ├── agents/
│   │   │   ├── langgraph_agent.py  # the StateGraph pipeline + chat turn
│   │   │   ├── prompts.py          # all LLM system prompts
│   │   │   └── tools.py            # duplicate-detection helper
│   │   ├── services/
│   │   │   ├── groq_client.py      # Groq API wrapper
│   │   │   └── document_parser.py  # PDF/DOCX/TXT/EML text extraction
│   │   └── sample_data/
│   │       └── generate_samples.py # generates demo complaint PDFs/emails
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.js
│   │   ├── store/              # Redux Toolkit slices (complaint, chat)
│   │   ├── components/         # ComplaintForm, AIAssistantPanel, FileUpload, ChatBox, ComplaintsListPage
│   │   ├── api/client.js       # axios API client
│   │   └── styles/index.css
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Setup & run

### 1. Get a Groq API key

Create a free key at https://console.groq.com and note it down.

### Option A — Docker Compose (recommended)

```bash
cp backend/.env.example backend/.env
# edit backend/.env and set GROQ_API_KEY=...

docker compose up --build
```

- Frontend: http://localhost:3000
- Backend docs (Swagger UI): http://localhost:8000/docs
- Postgres runs in its own container automatically.

### Option B — Run locally without Docker

**Backend** (uses SQLite by default so you don't need Postgres running):

```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # edit and add your GROQ_API_KEY
uvicorn app.main:app --reload --port 8000
```

**Frontend** (in a separate terminal):

```bash
cd frontend
npm install
npm start
```

Visit http://localhost:3000.

### 3. Generate sample complaint documents (optional)

To try the drag-and-drop extraction with realistic sample data:

```bash
cd backend
python -m app.sample_data.generate_samples
```

This writes a few sample PDFs/emails to `backend/app/sample_data/samples/`
(discoloration report, an adverse-event escalation, a packaging defect email,
and a labeling-discrepancy email) — drag any of them into the AI Assistant
panel to see the full extraction → completeness → risk → summary → CAPA
pipeline run end to end.

## API overview

| Method | Path                              | Description                                   |
|--------|------------------------------------|------------------------------------------------|
| GET    | `/api/complaints`                  | List complaints (optional `?status=`)          |
| POST   | `/api/complaints`                  | Create a complaint                              |
| GET    | `/api/complaints/{id}`             | Get one complaint                               |
| PUT    | `/api/complaints/{id}`             | Update a complaint                              |
| DELETE | `/api/complaints/{id}`             | Delete a complaint                              |
| POST   | `/api/ai/extract`                  | Upload a file OR paste text → run the LangGraph intake pipeline |
| POST   | `/api/ai/chat`                     | Send a chat message to the assistant            |
| POST   | `/api/ai/save-with-ai/{id}`        | Attach the latest AI analysis to a saved complaint |

Full interactive docs at `/docs` once the backend is running.

## Key design decisions

- **Why a fixed LangGraph pipeline instead of a single mega-prompt?** Splitting
  extraction / completeness / risk / summary / CAPA into separate nodes keeps
  each prompt focused (better accuracy), lets us pick a cheaper/faster model
  for the mechanical steps and a stronger model for the reasoning steps, and
  makes the `progress_log` on each node a natural source for the UI's
  extraction progress bar.
- **Why gemma2-9b-it for extraction/completeness?** Both are close to
  information-retrieval tasks (pull values out of text, check which keys are
  empty) where a smaller, fast/cheap model is sufficient and keeps the UI's
  progress bar feeling snappy.
- **Why llama-3.3-70b-versatile for risk/summary/root-cause/CAPA?** These need
  actual domain reasoning (what does this defect imply for patient safety and
  regulatory exposure) where a larger model gives materially better output.
- **Why SQLite fallback?** Postgres is the mandated production DB (see
  `docker-compose.yml`), but a SQLite fallback via `DATABASE_URL` means a
  reviewer can run the backend with zero extra setup.
- **Duplicate detection kept simple on purpose.** A real system would embed
  complaint descriptions and do a vector similarity search; for this scoped
  assignment a same-product/same-batch + text-similarity check demonstrates
  the concept without adding a vector DB dependency.

## Notes

- Production-grade OCR is intentionally out of scope per the assignment; text
  extraction covers PDF, DOCX, TXT and EML.
- No real customer/patient data is used — sample documents in
  `backend/app/sample_data/` are synthetic.

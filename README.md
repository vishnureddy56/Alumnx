# RouteIQ — AI-Powered Sales Inbox & Task Routing

**Candidate ID**: `saisradha888@gmail.com`  
**Deployed Backend URL**: `https://routeiq-backend.onrender.com`  
**Deployed Frontend URL**: `https://routeiq-qpw1.vercel.app`  
**Conversational Chat Endpoint**: `https://routeiq-backend.onrender.com/api/chat`  

---

## 1. Executive Summary

**RouteIQ** is an enterprise-grade AI-powered sales inbox and task routing system built for the **Alumnx AI Labs FDE Intern Hiring Challenge**.

Modern sales inboxes receive 150–250+ emails a day containing high-value enterprise RFPs, event sponsorships, payment reminders, partnership inquiries, and noise (spam, newsletters, out-of-office bounces). RouteIQ parses incoming emails using Google Gemini semantic understanding, applies deterministic business routing rules, enforces strict database idempotency and thread reconciliation, and exposes a high-performance React dashboard with grounded analytics and natural-language querying.

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend (Vite)                    │
│  - JSON Input / 250 Sample Email Loader                     │
│  - Raw Inbox Table (Pre-routing sanity verification)        │
│  - Real-time Processing Results & Action Badges             │
│  - Live Analytics Cards (/api/stats)                        │
│  - Grounded Conversational Assistant (/api/chat)            │
└─────────────────────────────┬───────────────────────────────┘
                              │ HTTP / REST
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend Service                   │
│                                                             │
│  ┌───────────────────────┐     ┌──────────────────────────┐ │
│  │   Task API (§5)       │     │ Extended API (§7.2)      │ │
│  │   - POST /tasks       │     │ - POST /ingest           │ │
│  │   - GET /tasks        │     │ - GET /api/tasks         │ │
│  │   - PATCH /tasks/{id} │     │ - GET /api/stats         │ │
│  │   - DELETE /tasks/{id}│     │ - POST /api/chat         │ │
│  │   - GET /users        │     │ - GET /health            │ │
│  └──────────┬────────────┘     └────────────┬─────────────┘ │
│             │                               │               │
│  ┌──────────▼───────────────────────────────▼─────────────┐ │
│  │ Processing & Business Routing Pipeline                 │ │
│  │ 1. Reply Cleaner (Strips quoted reply chains)          │ │
│  │ 2. Semantic Extraction (Gemini Structured Output)       │ │
│  │ 3. Deterministic Python Rules Engine                   │ │
│  │ 4. Idempotency & Thread Reconciliation (Run 1, 2, 3)   │ │
│  │ 5. Database Persistence & Audit Log                    │ │
│  └──────────┬───────────────────────────────┬─────────────┘ │
└─────────────┼───────────────────────────────┼───────────────┘
              │                               │
              ▼                               ▼
┌───────────────────────────┐   ┌─────────────────────────────┐
│  PostgreSQL / Supabase    │   │      Google Gemini API      │
│  - tasks                  │   │  - Structured Extraction    │
│  - processed_emails       │   │  - Grounded Chat Synthesis  │
│  - thread_history         │   └─────────────────────────────┘
└───────────────────────────┘
```

---

## 3. Quick Start (≤3 Commands)

### 1. Setup Backend
```bash
cd backend && pip install -r requirements.txt && python -m uvicorn app.main:app --reload --port 8000
```

### 2. Setup Frontend
```bash
cd frontend && npm install && npm run dev
```

### 3. Run Automated Tests (All 12 Worked Examples + API Contracts)
```bash
cd backend && python -m pytest -v
```

---

## 4. Technology Stack

- **Backend**: Python 3.11, FastAPI, Pydantic v2, SQLAlchemy 2.0
- **Database**: PostgreSQL (Supabase) / SQLite for local offline testing
- **AI / LLM**: Google Gemini API (`gemini-2.5-flash`)
- **Frontend**: React 18, Vite, Modern CSS Design System with Glassmorphism
- **Icons**: Lucide React
- **Testing**: Pytest, HTTPX, FastAPI TestClient

---

## 5. Routing Rules Matrix

| Assignee ID | Assignee Name | Department | Routing Scope |
|---|---|---|---|
| `u_aarti` | Aarti Menon | Sales — Enterprise | RFPs, RFIs, tenders, inbound deals > ₹10,00,000, and **all PSU/Govt tenders** (Rule 3). |
| `u_rohit` | Rohit Sharma | Sales — SMB | Product enquiries, demo requests, deals ≤ ₹10,00,000. |
| `u_meera` | Meera Iyer | Marketing | Webinars, event/conference sponsorships, content collaborations, PR/media. |
| `u_karan` | Karan Doshi | Alliances | Reseller, channel partner, and technology integration proposals. |
| `u_divya` | Divya Rao | Finance | Invoices, purchase orders, payment reminders, GST, and vendor billing. *(Invoice amount excluded from deal value)*. |
| `u_triage` | Triage Queue | Operations | Ambiguous items, conflicting cross-department asks, and budget TBD. |

### Key Business Policies:
1. **72-Hour Deadline Escalation**: Any email with a stated deadline `<= 72 hours` from `received_at` is marked `priority: "high"`.
2. **Noise Skipping (Rule 4)**: Out-of-office auto-replies, newsletters (`[Unsubscribe]`), and unsolicited vendor sales pitches are skipped (**no task created**).
3. **Idempotency & Thread Reconciliation**: Repeated ingestion of the same email does not duplicate tasks. Follow-up emails on existing threads update the existing task and preserve history.

---

## 6. API Reference

### Task API (§5)
- `POST /tasks`: Creates a task. Strictly validates enum values and returns `400 invalid_enum_value` on mismatch.
- `GET /tasks?candidate_id={email}`: Lists tasks for candidate with optional filters (`&thread_id=`, `&source_email_id=`, `&assignee_id=`).
- `PATCH /tasks/{task_id}`: Partially updates a task.
- `DELETE /tasks/{task_id}`: Deletes a task.
- `GET /users`: Returns the 6-member team roster.

### Extended Service API (§7.2)
- `POST /ingest`: Synchronously processes and persists a batch of up to 100 emails. Returns `{ processed, tasks_created, tasks_updated, skipped, errors }`.
- `GET /api/tasks`: Returns tasks enriched with audit records and skip metadata.
- `GET /api/stats`: Real-time aggregate counts (created, updated, skipped, spurious rate, pipeline totals).
- `POST /api/chat`: Grounded natural-language conversational assistant querying PostgreSQL with zero hallucination.
- `GET /health`: Health check endpoint.

---

## 7. Environment Variables

Create `.env` in `backend/`:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
DATABASE_URL=sqlite:///./routeiq.db
CANDIDATE_ID=priya.sharma@gmail.com
FRONTEND_URL=http://localhost:5173
PORT=8000
HOST=0.0.0.0
```

---

## 8. Deployment Guide

### Database (Supabase)
1. Create a free PostgreSQL project on [Supabase](https://supabase.com).
2. Copy the Connection URI (e.g. `postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres`).
3. Set `DATABASE_URL` in backend environment variables.

### Backend (Render)
1. Create a **Web Service** on [Render](https://render.com) connected to the repository.
2. Root Directory: `backend`
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variables: `GEMINI_API_KEY`, `DATABASE_URL`, `CANDIDATE_ID`, `FRONTEND_URL`.

### Frontend (Vercel)
1. Create a project on [Vercel](https://vercel.com).
2. Root Directory: `frontend`
3. Build Command: `npm run build`
4. Output Directory: `dist`
5. Add Environment Variable: `VITE_API_URL=https://your-backend.onrender.com`

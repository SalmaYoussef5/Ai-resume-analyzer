# Project Report — AI Resume Analyzer

## 1. Overview

A web application where a job seeker uploads a résumé, gets it analyzed by an LLM,
is matched against a database of jobs using Retrieval-Augmented Generation, and
receives personalized career advice grounded in a local knowledge base.

Built exactly to the technology constraints in the SRS: **Python + FastAPI**
backend, **SQLite** database, **HTML/CSS/Vanilla JavaScript** frontend — no
React/Angular/Vue.

## 2. Architecture at a glance

```
Browser (frontend/*.html, Vanilla JS)
        │  fetch() + JWT bearer token
        ▼
FastAPI app (main.py)
  ├── routers/          → HTTP layer (validation, auth, status codes)
  ├── agents/            → AI logic (3 agents, each one responsibility)
  ├── rag/                → embeddings + knowledge base retrieval
  ├── utils/               → file parsing (PDF/DOCX)
  └── models.py, database.py → SQLAlchemy ORM over SQLite
```

See `docs/ER_DIAGRAM.md` for the full data model and `docs/API_DOCUMENTATION.md`
for every endpoint.

## 3. Evaluation criteria mapping (100 marks, per the SRS)

| Criterion | Marks | Where it's satisfied |
|---|---|---|
| Backend Development (Python + FastAPI) | 20 | `main.py`, `routers/*` — 4 routers, full CRUD, dependency-injected auth (`auth.py`), SQLAlchemy sessions (`database.py`) |
| Frontend Development (HTML/CSS/JS) | 10 | `frontend/` — 4 pages, plain Vanilla JS (`frontend/js/*.js`), no framework, served directly by FastAPI (`StaticFiles` mount in `main.py`) |
| Database Design (SQLite) | 10 | `models.py` — 4 tables with real foreign keys and a cascade delete; see `docs/ER_DIAGRAM.md` for the reasoning behind each modeling decision |
| Resume Analysis | 15 | `agents/resume_analyzer_agent.py` + `utils/file_parser.py` — PDF/DOCX text extraction → structured LLM extraction (skills/education/experience/summary) |
| AI Agents | 20 | Three distinct agents, each with one job: `resume_analyzer_agent.py`, `job_matching_agent.py`, `career_advisor_agent.py` |
| RAG Implementation | 10 | Used **twice**, two different ways: (1) embedding-based job ranking in `rag/embeddings.py` + `job_matching_agent.py`; (2) knowledge-base retrieval in `rag/retriever.py` + `career_advisor_agent.py`, grounded in `rag/knowledge_base/*.txt` |
| Code Quality & Error Handling | 10 | Ownership checks on every resource, typed Pydantic schemas, meaningful 400/401/403/404 responses (see `docs/API_DOCUMENTATION.md` → Status code summary), `.gitignore` for secrets |
| Documentation | 5 | This report + `docs/ER_DIAGRAM.md` + `docs/API_DOCUMENTATION.md` + `docs/DEMO_SCRIPT.md` + inline Arabic comments throughout the code explaining *why*, not just *what* |

## 4. AI provider note

The SRS doesn't mandate a specific LLM provider. This project uses
**Hugging Face Inference Providers** (`meta-llama/Llama-3.1-8B-Instruct`) instead
of a paid API, so the whole project runs on a free tier with no billing setup
required — see `README.md` for how to get a free token.

## 5. Known limitations / honest trade-offs

Worth mentioning proactively in the defense — reviewers respect this more than
pretending they don't exist:

- **Job embeddings are recomputed on every match request**, not cached. Fine at
  the scale of a student project (tens of jobs); documented as a scaling
  consideration in `docs/ER_DIAGRAM.md` and `README.md`.
- **Llama 3.1 8B is a small open model** — occasionally its JSON output needs the
  fallback parser in `resume_analyzer_agent.py`. A paid model (GPT-4o, Gemini)
  would be more reliable but isn't free; swapping it is a one-line change
  (`MODEL_NAME` in the `agents/` files).
- **Logout is client-side only** (JWTs are stateless by design) — documented in
  `auth_router.py` and `docs/API_DOCUMENTATION.md` rather than left unexplained.

## 6. Deliverables checklist (per SRS section 7)

- [x] Complete source code — this repository
- [x] API documentation — `docs/API_DOCUMENTATION.md` + live Swagger at `/docs`
- [x] Demo — `docs/DEMO_SCRIPT.md`
- [x] ER Diagram — `docs/ER_DIAGRAM.md` + `docs/er_diagram.png`

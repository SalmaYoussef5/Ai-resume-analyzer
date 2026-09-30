# Demo Script — AI Resume Analyzer

Follow this order. It's built to touch every evaluation criterion in the SRS
(Backend, Frontend, Database, Resume Analysis, AI Agents, RAG, Error Handling)
in one continuous walkthrough, so nothing gets forgotten under pressure.

**Before you start:** run `uvicorn main:app --reload`, open `http://127.0.0.1:8000`,
and make sure `.env` has a real `HF_TOKEN` (résumé analysis and matching need it live).

---

## 1. Authentication (1 min)
1. On the landing page, click **Create account** → register with a real name/email.
2. You're redirected straight into the app (token stored automatically).
3. *Say:* "Passwords are hashed with bcrypt, never stored in plain text; sessions use JWT."

## 2. Jobs — CRUD + Search (1–2 min)
1. Go to **Open roles** → **Post a role**. Add 2–3 different jobs (e.g. a Backend role,
   an ML role, a Frontend role) with different `required_skills`.
2. Use the search bar to filter by `category` or `skill` — show it narrowing the list live.
3. *Say:* "This is a full REST CRUD layer — the same pattern used for jobs is reused
   for résumés and recommendations underneath."

## 3. Résumé upload + AI analysis (1–2 min)
1. Go to **My résumés** → upload a real PDF or DOCX résumé.
2. While it processes, *say:* "This is the **Resume Analyzer Agent** — it extracts text
   from the file, sends it to an LLM (Llama 3.1 via Hugging Face) with a structured
   prompt, and gets back skills, education, experience, and a summary as JSON."
3. Point out the parsed skills/education/experience once it appears.

## 4. Job Matching — RAG in action (2 min)
1. Click **Find matching roles** on the uploaded résumé.
2. *Say while it loads:* "This is Retrieval-Augmented Generation: the résumé and every
   job are converted to embeddings locally with `sentence-transformers`, ranked by
   cosine similarity — that's the *retrieval* step — then the top matches are sent to
   the LLM to *generate* a plain-English explanation of the fit."
3. Point out the match scores are clearly different and make sense (a Python/FastAPI
   résumé should score much higher against a Backend role than a Marketing one).
4. Reload the page and revisit the résumé — matches are still there instantly.
   *Say:* "Results are persisted in the `Recommendation` table, not recomputed
   every time — that's the `GET /matches` endpoint."

## 5. Career Advisor — RAG with a real knowledge base (2 min)
1. Go to **Advisor**. On the right ("Improvement report"), pick the uploaded résumé
   and one of the jobs that scored lower in step 4.
2. Click **Generate report** → point out the **Missing skills** chips are calculated
   directly (set difference — not the LLM's opinion), while the advice paragraph
   below is grounded in `rag/knowledge_base/*.txt` (roadmaps, learning resources,
   resume-writing guidelines) — not invented by the model.
3. On the left, ask a free question, e.g. *"What's the roadmap to become an ML engineer?"*
   — show the answer traces back to `roadmaps.txt`.

## 6. Error handling (30 sec — do this quickly, it's easy marks)
1. Try uploading a `.txt` file → clean 400 error, not a crash.
2. Open dev tools → Network tab, or just try visiting `/resumes/999` — show the 404.
3. *Say:* "Every endpoint validates ownership too — a second account can't see or
   edit another user's résumés or jobs; that's tested in the code, not just assumed."

## 7. API documentation (30 sec)
1. Open `http://127.0.0.1:8000/docs` in a new tab.
2. *Say:* "This is auto-generated directly from the FastAPI route definitions and
   Pydantic schemas — it can't drift out of sync with the actual code."

## 8. Wrap-up talking points
- **3 distinct AI agents**, each with a single responsibility (Resume Analyzer,
  Job Matching, Career Advisor) — not one giant prompt doing everything.
- **RAG used twice, two different ways**: embeddings-based ranking for job matching,
  and knowledge-base retrieval for career advice — shows the concept is understood,
  not just copy-pasted once.
- **SQLite + SQLAlchemy**, 4 tables, one real foreign-key chain
  (`User → Resume → Recommendation ← Job`) — see `docs/ER_DIAGRAM.md`.
- **Frontend is plain HTML/CSS/Vanilla JS** as required — no build step, no framework;
  open any `.html` file and read it directly.

---

## If something breaks live (backup plan)
- No internet for the Hugging Face call? Show a résumé/job pair uploaded **before** the
  demo (upload one the night before) — the saved analysis/matches are already in the
  database and load instantly via `GET /resumes` and `GET /resumes/{id}/matches`,
  no live API call needed.
- Keep one browser tab already logged in with a résumé and matches pre-computed, as a
  fallback if live upload fails for any reason (rate limit, flaky connection, etc.).

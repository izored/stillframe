# Stillframe

When life won't pause, your thoughts still can.

Stillframe is a self-hosted, local-first space for guided reflection. Frame a moment, sit with it safely, reframe what it means. Your thoughts stay on your machine. Local AI runs through Ollama. Cloud providers are optional and opt-in.

Stillframe supports reflection. It is not therapy, diagnosis, or crisis care. If you are in danger, contact a crisis line. Resources are built in.

---

## Status

Early build. Phase 1 backend is in place: health checks, provider abstraction (Ollama first), the Safe Set safety layer, Frames / Scenes / Scripts, and a safety-wrapped streaming reflect endpoint. The frontend (React + Vite, Apple-grade, Framer Motion) and the native Swift macOS app come next.

## Architecture

API-first. The FastAPI backend holds all business, safety, memory, and evolution logic. The web client and the planned Swift macOS app are thin clients over the same API.

```
backend/app/
  main.py            FastAPI app + routers
  config.py          env-driven settings
  db.py              SQLite: scenes, frames, arcs, facts, summaries
  safety/            Safe Set: crisis detection, policy blocks, stream buffer
  providers/         HTTP adapters: ollama, openai_compat, anthropic
  prompts/           the Editor's system prompt (presence + boundaries)
  scripts/           guided flows (JSON) + loader
  routes/            health, providers, scenes, frames, scripts, reflect
```

## Run (backend, Docker)

```bash
cp .env.example .env
# adjust .env if needed (OLLAMA_BASE_URL, ACTIVE_PROVIDER, ...)
docker compose up --build
```

Backend is bound to `127.0.0.1:5181` (never exposed directly; public access goes through a Cloudflare Tunnel). Open API docs at http://127.0.0.1:5181/docs.

### Run without Docker

```bash
cd backend
pip install -r requirements.txt
# point Ollama at the host
set OLLAMA_BASE_URL=http://localhost:11434   # PowerShell: $env:OLLAMA_BASE_URL="http://localhost:11434"
uvicorn app.main:app --reload --port 8000
```

## Key endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | liveness |
| GET | `/health/provider` | active provider reachability + models |
| GET | `/providers` | all providers ("Choose your editor") |
| GET/POST | `/scenes` | context buckets |
| GET/POST/PATCH/DELETE | `/frames` | the core unit |
| GET | `/scripts` | guided flows |
| POST | `/reflect` | safety-wrapped streaming reflection (NDJSON) |

## Safety

No provider call bypasses the Safe Set. Inbound text is screened for crisis and policy violations before any model runs; streamed output is held in a buffer and blocked if it breaches policy. Crisis input returns resources immediately and the model is not called. Logic ported from the foundation repo (joebwd/mental-wellness-prompts), MIT licensed.

## Providers

- `ollama` (default, local, no key) — your thoughts never leave the machine
- `openai_compat` (llama.cpp / LM Studio / OpenAI) — optional
- `anthropic` (Claude, cloud) — optional, opt-in, key required

Local-only scenes block cloud providers automatically.

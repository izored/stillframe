# Stillframe — Engineering Spec

**Status:** v0.1 · 2026-06-15 · living document
The single technical spec for the codebase. Product/brand/design context lives in the project root resource folders; this file is what an engineer (or a future you) builds from.

---

## 1. What it is
Self-hosted, local-first mental wellness workspace. Guided reflection in frames, not a chat box. Not therapy, diagnosis, or crisis care. Tagline: "When life won't pause, your thoughts still can."

## 2. Principles
- **Local-first, privacy by default.** Thoughts stay on the machine. Cloud AI is opt-in and never silent.
- **API-first.** All logic in the backend. Web (React) and native (Swift macOS) are thin clients over one contract.
- **Safety is non-negotiable.** No provider call bypasses the Safe Set. Behaviour rules are non-removable.
- **Glass box.** Prompts, safety logic, storage are readable and editable.
- **Ships empty.** The repo contains no personal data. Personal use is a separate profile.

## 3. Platforms
- Docker web app (Windows / self-hosted) — current.
- Native Swift / SwiftUI macOS app — planned, same API.

## 4. Stack
| Layer | Choice |
|---|---|
| Backend | Python 3.12, FastAPI, httpx, Pydantic |
| Storage | SQLite (SQLCipher encryption later) + sqlite-vec for embeddings (phased) |
| AI | Ollama (default, local) · OpenAI-compatible · Anthropic (opt-in cloud) |
| Embeddings | Ollama `nomic-embed-text` (local) |
| Voice | Whisper STT (faster-whisper / whisper.cpp, local) |
| Frontend | Vite + React 19 + TS + Tailwind v4 + Framer Motion |
| Infra | Docker Compose; backend bound to localhost; Cloudflare Tunnel for public access |

## 5. Profiles & data separation (ship empty, use personally)
Two profiles via `STILLFRAME_PROFILE`:
- **public** (default) — what is committed and released. No personal data. DB = empty gitignored `./data/`. Identity = packaged `prompts/presence.md` + `prompts/boundaries.md`.
- **creator** — personal use. `DB_PATH` and `PRESENCE_PATH` / `BOUNDARIES_PATH` point into `instance/` (gitignored). The creator's database, identity overrides, and secrets live here and never touch git.

**Never committed** (enforced by `.gitignore`): `.env` and `.env.*` (except `.env.example`), `*.db` / `*.sqlite*` / wal / shm, `instance/`, `/data/`, `/backend/data/`, `*.key` / `*.pem`, `secrets/`, `*.personal.md`. The repo ships with no database and no secrets.

Identity override never weakens the care rules; it may only extend tone.

## 6. Security (see ../../05_Product/foundation/Security-and-Privacy.md)
Defense in depth: Cloudflare Tunnel + Access (who) → app login gate (you) → scene passcode (which thoughts) → encryption at rest (the bytes). Encrypted SQLite (SQLCipher); private scenes use a passcode-derived key (Argon2id) so locked scenes are unreadable without the passcode. Local-only scenes block cloud providers. Auth/session must serve a browser (cookie) and a native app (token). Fail closed.

## 7. Data model (SQLite, source of truth)
- `scenes` — id, name, mood, private, local_only, created_at
- `frames` — id, scene_id, title, captured, reflection, reframe, mood_score, timestamps
- `arcs` — id, name, model, current_stage, confidence, active, timestamps
- `arc_stage_history` — arc_id, stage, confirmed, created_at
- `user_facts` — key, value, confidence, timestamps (upsert; recurrence raises confidence/recency)
- `session_summaries` — frame_id, summary, created_at
- `governance_events` — action, status, detail, created_at (audit for proposed/confirmed evolution actions)

## 8. Memory architecture
Four tiers. Structured = SQLite (exact, encrypted). Semantic = sqlite-vec (phased).

1. **Working** — current frame messages, in-process.
2. **Structured (SQLite)** — facts, summaries, mood, arcs/stages.
3. **Semantic (sqlite-vec)** — embeddings of frame text + summaries, in the same encrypted DB file. Local embeddings via Ollama. Added when frames accumulate; v1 uses SQLite FTS5 keyword search first.
4. **Episodic** — the Reel (chronological).

**Post-frame pipeline:** extract facts (upsert) + write a summary + (later) embed. **Retrieval for a new frame:** recency (last N summaries) + relevance (top-k semantic, scene-filtered) + state (active arc/stage + high-confidence facts) → `memory_context` → injected via `build_system_prompt()`. Private-scene text and embeddings are excluded from any cloud provider context.

## 9. API (current + planned)
Response shape `{ data, error }` for CRUD; NDJSON stream for reflect.
- `GET /health`, `GET /health/provider`
- `GET /providers` — "Choose your editor"
- `GET/POST /scenes`, `GET /scenes/{id}`
- `GET/POST/PATCH/DELETE /frames`
- `GET /scripts`, `GET /scripts/{id}`
- `POST /reflect` — safety-wrapped NDJSON stream (`delta` / `safety` / `error` / `done`)
- `POST /transcribe` (planned) — audio → text (Whisper, local)
- Memory/arcs/auth endpoints — planned per phase.

## 10. Providers
HTTP adapters behind one interface (`ProviderAdapter`): `info()` + `stream()`. `ollama` (local, default, auto-detects model), `openai_compat` (llama.cpp / LM Studio / OpenAI), `anthropic` (cloud, opt-in, key-gated). Registry resolves by name. Local-only scenes reject non-local providers.

## 11. Voice input (Whisper)
`POST /transcribe`: audio blob → text, local model, audio never leaves the machine. Web records via MediaRecorder; Swift may use native Speech or the same endpoint. Fills the Frame input; user edits before save/send. Transcribed text flows through the same Safe Set as typed text.

## 12. Evolution Engine (see ../../05_Product/features/Evolution-Engine.md)
Arcs span weeks. Stage detection is gradual + consensual (LLM proposes, user confirms; logged in `governance_events`). On a confirmed shift: scene palette crossfades, greeting + offered scripts adapt, system prompt gets arc/stage context. Stage models are research-backed reflective scaffolds, never diagnoses. The whole engine can be turned off.

## 13. Frontend
Screens (see ../../05_Product/user-flows/Screen-Map.md): Welcome, Setup tour, Choose your editor, Security setup, Unlock, Home, Frame, Sit, Reframe, Saved, Reel, Frame detail, Scripts list, Script runner, Scenes, Scene detail, Crisis interrupt, Settings (Editor's notes). Calm motion via Framer Motion; one primary action per screen; non-dismissable disclaimer; `prefers-reduced-motion` respected. Design tokens (warm sand + teal draft) in `src/index.css`.

### Onboarding / Welcome tour (new-user experience)
First run only, skippable, replayable from Settings. Calm, low-stimulus, one idea per screen.
1. **Welcome** — wordmark + tagline + "Begin". Slow fade-up, soft still, breathing scale.
2. **What is a Frame** — capture a moment, sit with it, reframe. Three quiet lines.
3. **The Editor** — editor, not director. It suggests, never prescribes. Plain language.
4. **Your thoughts stay here** — local-first; cloud is opt-in. Privacy as dignity, not fear.
5. **Choose your editor** — pick provider; Local (Ollama) preselected.
6. **Set your lock** — passkey/passcode; optional now.
7. **First frame nudge** — land on Home with a gentle "Frame a thought."
State: an onboarding-complete flag persisted locally (per profile). Tour never blocks; a Skip is always present. Crisis disclaimer visible throughout.

## 14. Build phases
1. **Backend foundation** — done (safety, providers, frames/scenes/scripts, reflect).
2. **Memory layer** — next. Structured facts + summaries + retrieval + FTS5; sqlite-vec after.
3. **Frontend core** — onboarding tour, Frame loop wired to reflect, Reel.
4. **Security** — login, scene passcodes, encrypted SQLite.
5. **Evolution Engine** — arcs, stage detection, scene evolution.
6. **Voice** — `/transcribe` + Whisper service.
7. **Swift macOS app** — native client over the same API.

## 15. What never ships / never commits
No personal database, no `.env`, no secrets, no keys, no `instance/`, no clear passwords or personal data dirs. Code is OSS; personal data is encrypted and local. Verify `git status` before every commit.

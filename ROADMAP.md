# Stillframe — Roadmap

Status as of 2026-06-15. Living document. Full engineering detail in `docs/SPEC.md`.

Legend: ✅ done · 🟡 in progress · ⬜ planned

| Phase | Scope | Status |
|---|---|---|
| 1 | **Backend foundation** — Safe Set safety layer, HTTP providers (Ollama default), frames/scenes/scripts, safety-wrapped reflect | ✅ |
| 2 | **Memory layer** — post-frame fact + summary extraction, recall (FTS5 now, sqlite-vec next) | ✅ |
| 3 | **Frontend core** — onboarding tour, Frame loop wired to reflect, Reel | 🟡 |
| 4 | **Security** — login gate, scene passcodes, encrypted SQLite (SQLCipher) | ⬜ |
| 5 | **Evolution Engine** — Arcs, gradual + consensual stage detection, scene evolution | ⬜ |
| 6 | **Voice input** — Whisper STT, `/transcribe`, local | ⬜ |
| 7 | **Swift macOS app** — native client over the same API | ⬜ |

## Near-term tail items
- sqlite-vec semantic recall (memory phase 2 tail).
- Behaviour-rules evidence backlog (cite the constitution to research).

## Platforms
- Docker web app (Windows / self-hosted) — current build.
- Native Swift / SwiftUI macOS app — planned.

## Distribution (undecided, interim restrictive license)
- **macOS app: paid, €/$4.99.** Confirmed direction.
- **Self-hosted / web: model undecided** (freemium vs other). Until decided, the
  repo ships under an interim all-rights-reserved license (see `LICENSE`): source
  is viewable for transparency, not licensed for use or redistribution.

## Principles that do not change
Local-first, privacy by default. API-first (one backend, web + native clients).
Safety is non-negotiable; the behaviour constitution is non-removable and
reviewed monthly. Not therapy, diagnosis, or crisis care.

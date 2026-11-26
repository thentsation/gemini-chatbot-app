[🇧🇷 Português](README.pt-br.md) | 🇺🇸 English

# Gemini Chatbot App

[![Python CI](https://github.com/ntsation/gemini-chatbot-app/actions/workflows/pipeline_python.yaml/badge.svg)](https://github.com/ntsation/gemini-chatbot-app/actions/workflows/pipeline_python.yaml)
[![Docker CI/CD](https://github.com/ntsation/gemini-chatbot-app/actions/workflows/pipeline_docker.yaml/badge.svg)](https://github.com/ntsation/gemini-chatbot-app/actions/workflows/pipeline_docker.yaml)
[![Release](https://github.com/ntsation/gemini-chatbot-app/actions/workflows/release.yaml/badge.svg)](https://github.com/ntsation/gemini-chatbot-app/actions/workflows/release.yaml)

A Streamlit chat app for Google's Gemini models, with real multi-turn memory, a model picker, per-message feedback, and a "bring your own key" flow so anyone can try it without you paying for their usage.

> Full write-up (journey from prototype to product) in [Portuguese](ARTIGO.md) / [English](ARTIGO.en-us.md).

## Features

- **Real conversational memory** — built on `google-genai`'s `Chat` session, so the model actually remembers earlier turns instead of answering each message in isolation.
- **Model picker** — switch between `gemini-3.8-flash`, `gemini-2.5-flash`, `gemini-2.5-pro` and `gemini-3.1-pro-preview` from the sidebar; switching resets the session cleanly.
- **BYOK by default** — visitors paste their own Google API key in the sidebar (never stored on disk or logged); set `GOOGLE_API_KEY` as a server secret to skip the prompt entirely.
- **Persisted per-message feedback** — rate any assistant reply ("Useful" / "Partially useful" / "Not relevant"); ratings survive reruns and reappear when history re-renders.
- **Friendly error handling** — invalid keys, quota limits and unavailable models surface as a clear message instead of a stack trace.

## Requirements

- Python 3.11+
- A Google API key ([get one here](https://aistudio.google.com/apikey))

## Installation

```bash
git clone https://github.com/ntsation/gemini-chatbot-app.git
cd gemini-chatbot-app
make install
```

## Usage

```bash
make run
```

Open `http://localhost:8501`, paste your API key in the sidebar, pick a model, and start chatting.

### Docker

```bash
make docker-build
make docker-run
```

Or via Compose: `docker compose up --build`. The image is multi-stage (non-root runtime), ships a `HEALTHCHECK` against Streamlit's own `/_stcore/health` endpoint, and is scanned with **Trivy** + published to **GHCR** on every push to `main`.

## Configuration

| Variable | Required | Description |
| --- | --- | --- |
| `GOOGLE_API_KEY` | No | If set, the app uses this key for everyone and skips the sidebar prompt ("server key" mode). Leave unset for BYOK. |

## Development

```bash
make lint        # ruff check
make format      # ruff format
make typecheck    # mypy (strict)
make test         # pytest
make coverage     # pytest with coverage report
```

Tests include unit tests per module plus an end-to-end smoke test using Streamlit's own `AppTest` utility, which drives the whole app (sidebar, chat input, feedback, clear-chat) with the `google-genai` SDK faked out — no real API key or network call needed.

## Telvax version

`telvax/` has the same chat written in [Telvax](https://github.com/telvax/telvax), as one service:
* **The page** (`src/page.html`, built into the binary) is plain HTML and JavaScript instead of Streamlit. It has the same
  sidebar (the key or the notice of the server's key, the model picker, clearing the chat), the messages, the "Pensando..."
  wait, and the rating of each answer.
* **The chat** goes to Gemini's OpenAI-compatible endpoint with the chat client of Telvax's standard library.
  * The answer is streamed to the page piece by piece as server-sent events, as the model writes it; the Streamlit app
    streams a finished answer word by word.
  * Each browser session keeps its messages and the model's memory in the server's memory, with a cookie.
  * A new key or model starts a new memory, as the app recreates its Gemini chat session.
  * The errors are the messages of the app.
* **The key** is `GOOGLE_API_KEY` on the server, or the one a visitor pastes. That one is kept only in the page and sent
  with each message, never written to disk or to a log.

```sh
cd telvax
GOOGLE_API_KEY=... telvax serve src/main.tvx --live          # http://localhost:8080
telvax serve src/main.tvx                                    # offline: a stand-in model that quotes the question
telvax build --serve src/main.tvx -o gemini-chatbot          # one binary with the page
```

`GEMINI_BASE_URL` points the service at another OpenAI-compatible server.

**Tests.** `telvax test src/errors_test.tvx` and `src/sessions_test.tvx` cover the messages, the sessions, the memory of a
key and model, the ratings and clearing. `sh tests/e2e.sh` runs the service against `tests/fake_gemini.py`, a stand-in for
Gemini's endpoint, and checks over HTTP:
* the streamed pieces, and the history sent back to the model;
* the model picker, and a new memory for a new model;
* the three errors (key, model, quota) and the missing key;
* the ratings and clearing;
* the key of the server, and the offline mode.

`.github/workflows/telvax.yml` runs both.

**Differences from the Streamlit app**
* **The key is not checked when it is entered:** a wrong key is reported at the first message instead (the app lists the
  models first).
* **No Markdown:** answers are shown as plain text with their line breaks, not as Markdown.

## Repository structure

```
├── src/                   # app source (components/services/utils + entrypoint)
├── tests/                 # unit tests + full-app AppTest smoke test
├── config/                # pinned requirements + lockfile
├── docker/                # Dockerfile
└── .github/workflows/     # CI, Docker build+scan+publish, release, deploy
```

## CI/CD

- **CI**: ruff (lint + format), mypy (strict), pytest matrix (3.11/3.12) with coverage gate, a live Streamlit smoke test, and `pip-audit` against the lockfile.
- **Release**: `python-semantic-release` tags a new version and updates `CHANGELOG.md` automatically on every push to `main`.
- **Docker**: multi-arch build, Trivy scan, publish to GHCR with `latest`/semver/sha tags.
- **Deploy**: on a successful Docker build on `main`, the image is deployed automatically to a long-running container.

[🇧🇷 Português](README.pt-br.md) | 🇺🇸 English

# Gemini Chatbot App

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

The image is multi-stage (non-root runtime) and ships a `HEALTHCHECK` against Streamlit's own `/_stcore/health` endpoint. `docker-compose.yml` is the production compose used by Jenkins (Traefik labels, no published ports, `GOOGLE_API_KEY` from `/opt/apps/gemini-chatbot-app/.env` on the server).

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

## Repository structure

```
├── src/                   # app source (components/services/utils + entrypoint)
├── tests/                 # unit tests + full-app AppTest smoke test
├── config/                # pinned requirements + lockfile
└── docker/                # Dockerfile
```

## CI/CD

CI and deploy run on the platform's Jenkins (`Jenkinsfile` → `appPipeline` from the `platform` Shared Library, repo devops-platform), triggered by webhooks; there are no GitHub Actions.

- **PRs and branches** — contract validation; `docker build --target test` (`ruff check`, `ruff format --check`, `mypy`, `pytest` with ≥90% coverage on Python 3.11 and 3.12, Streamlit app driven end to end by `AppTest`, tool versions from `config/requirements-dev.txt`); `pip-audit` on `config/requirements.lock`; Trivy (CRITICAL/HIGH) on the runtime image.
- **main** — all of the above, then build, smoke test, push to OCIR, deploy behind Traefik at https://gemini-chatbot.137-131-175-7.sslip.io with automatic rollback, release with python-semantic-release (version, CHANGELOG, tag and GitHub release) and a rebuild of the portfolio. Also rebuilt every Monday to pick up security patches.
- **Dependencies** — Renovate (Jenkins job `platform/renovate`, `renovate.json` → devops-platform preset): daily updates, weekly lockfile maintenance, Dependency Dashboard issue and auto-merge of patch/minor after Jenkins passes.


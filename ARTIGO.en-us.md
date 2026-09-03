[🇧🇷 Português](ARTIGO.md) | 🇺🇸 English

# From prototype to product: productizing a Streamlit chatbot for Gemini

How a weekend chatbot — no tests, no conversation memory, running on an already-deprecated SDK — turned into an app with full CI/CD, automated deployment, and a fix that actually changes the product: it now remembers the conversation.

## The starting point

The project was seven Streamlit files: a sidebar to paste the API key, a chat component, and a call into `google-generativeai`. It worked for a quick demo, but hid two product bugs that only show up once someone actually uses the app:

1. **The history disappeared.** `st.session_state.messages` was populated on every message, but nothing at the top of the app looped over that list to redraw it. Every Streamlit rerun — which happens on every interaction — only the latest exchange stayed visible. A chat that visually "forgot" everything before the last message.
2. **The chat had no memory at all.** Every question turned into an isolated call to `model.generate_content(prompt)`. The model never saw earlier messages — the UI looked like a continuous conversation, but under the hood every reply started from zero.

On top of that: zero tests, zero CI, an unpinned `requirements.txt` (with `IPython` listed and never used anywhere), and — the most consequential discovery of the whole process — the library in use, `google-generativeai`, is officially marked `Development Status :: 7 - Inactive` on PyPI. Its own README recommends migrating to `google-genai`.

This article is the path from there to something that feels like a real product.

## First stop: fix what was already there

Before any new feature, the two bugs.

### Real history

The fix is simple to describe and easy to forget: at the top of `chat_interface`, loop over `st.session_state.messages` and redraw each one with `st.chat_message` before handling new input. After any new reply, an explicit `st.rerun()` normalizes state — the message that was just generated disappears from the "live" render and reappears, feedback widget included, from the history loop. One rendering path, no duplicated logic.

### Memory via the SDK, not reinvented

The tempting fix would be to manually assemble a list of turns and resend it on every call. But the SDK already solves this: `client.chats.create(model=...)` returns a `Chat` object that keeps history internally — it was enough to stash that session in `st.session_state` and swap `generate_content` for `chat.send_message()`. The session is only recreated when the key or model changes, so switching models mid-conversation resets cleanly instead of mixing contexts.

### The SDK migration that wasn't in the original plan

While researching the multi-turn chat API, `google-generativeai`'s PyPI page surfaced the deprecation notice. Switching SDKs mid-productization could have been a detour if the API had changed drastically — but the official migration guide shows the swap is nearly mechanical:

```python
# before (google-generativeai, deprecated)
genai.configure(api_key=key)
model = genai.GenerativeModel('gemini-1.5-flash')
chat = model.start_chat()
chat.send_message(prompt)

# after (google-genai)
client = genai.Client(api_key=key)
chat = client.chats.create(model='gemini-3.8-flash')
chat.send_message(prompt)
```

Alongside the swap, the available models had moved on too — generation 3.x (`gemini-3.8-flash`, `gemini-3.1-pro-preview`) now sits alongside 2.5, so the sidebar's model picker offers both generations.

## The features: giving the app a product feel

With the foundation fixed, the rest was closing the gaps that separate a prototype from something publishable.

- **Model picker.** An `st.selectbox` in the sidebar with four options, from fastest to highest-quality — switching models automatically recreates the chat session.
- **BYOK with immediate feedback.** Visitors still paste their own key (nothing is ever stored server-side), but it's now validated as soon as it's set — a lightweight `client.models.list()` call — instead of silently failing on the first message. If `GOOGLE_API_KEY` is set in the environment, the sidebar skips the field and shows a "server key" notice instead.
- **Errors that make sense.** The SDK's `APIError` is translated into specific messages by HTTP code — invalid key, unavailable model, quota exceeded — instead of a generic `RuntimeError`.
- **Feedback that persists.** The original feedback widgets didn't even have a `key` — rendering more than one message would have collided. Now every message gets its own rating, stored in `st.session_state.feedback_log` with a timestamp, and reappears as a caption when scrolling through history.
- **A title and icon in the browser tab.** A small detail that was entirely missing: `st.set_page_config` was never called.

## Actually testing a Streamlit app

Testing UI is usually the weak spot of prototypes like this one. The answer wasn't to mock everything by hand — Streamlit itself ships `streamlit.testing.v1.AppTest`, which runs the whole app (no server needed) and lets you interact with widgets the way a user would. With the Gemini SDK swapped for a fake in the pytest fixture, it's possible to simulate the full journey: set the key, send two messages in a row and confirm the first one is still on screen (the exact test that would have caught bug #1), leave feedback on a reply and confirm it survives another turn, and verify that an API error doesn't corrupt the history.

Alongside that, isolated unit tests cover `config.py` (environment variable fallback), `services/response.py` and `services/google_api.py` (error mapping and session caching), and `utils/state_manager.py`.

## Lessons

1. **A product bug isn't always a code bug.** The two most important failures here never raised an exception — the app "worked." They only became obvious by using the chat the way a user would, message after message.
2. **Checking a dependency's health is part of the job.** No amount of old documentation would have warned that `google-generativeai` had become "Inactive" — that only surfaced by checking PyPI itself while researching the chat API.
3. **Testing Streamlit doesn't need Selenium.** `AppTest` runs in milliseconds and tests real rerun behavior — exactly the category of bug that isolated unit tests miss.
4. **Good BYOK is UX, not just security.** Validating the key the moment it's configured, instead of only on the first message, saves a visitor from typing a whole paragraph just to discover they pasted the wrong key.

## Final state

- 28 tests, 100% coverage on `src/`, a 90% threshold gating CI
- ruff (lint + format) and mypy (`disallow_untyped_defs`) clean, running on every push
- CI across a Python matrix, a real Streamlit smoke test (`/_stcore/health`), Docker image scanned with Trivy and published to GHCR
- Automatic versioning via `python-semantic-release` — every change on `main` becomes a tag and a `CHANGELOG.md` entry
- Automated deploy: build → GHCR → mirror to OCIR → SSH into the instance → HTTP smoke test

[🇧🇷 Português](ARTIGO.md) | 🇺🇸 English

# A weekend chatbot I never quite let go of

I started this on a Saturday just to see if I could bolt a UI onto Gemini in one afternoon. It worked. What I didn't notice for a few days was that the chat "forgot" everything and was running on a library Google itself had already abandoned.

## Why Streamlit and not something else

I wanted the shortest possible distance between "I have a Gemini API key" and "I have a screen to talk to it from." Streamlit gets you there in seven files: a sidebar to paste the key, a chat component, a call into `google-generativeai`. It ran, it worked, I closed the laptop satisfied. I only actually used the app — sending more than one message in a row — a few days later.

## The two bugs that only show up when you use your own app

Neither one crashed the process. Neither showed up in the logs. They only surfaced once I, as a user, tried to have an actual conversation.

**The history vanished visually.** `st.session_state.messages` got every new message just fine, but nothing at the top of the app looped back over that list to redraw the earlier ones. Since Streamlit reruns the whole script on every interaction, only the latest exchange stayed on screen — a chat that forgot everything before the second-to-last line, even though the data underneath was intact.

**The chat had no memory at all.** This one was worse: every question turned into an isolated call to `model.generate_content(prompt)`. Visually it looked like a conversation; to the model, every reply was born from zero, with no prior question in context.

The fix for the first bug is the kind that's easy to forget: at the top of `chat_interface`, loop over `st.session_state.messages` and redraw each one with `st.chat_message` before handling new input, then close with an explicit `st.rerun()` after any reply — the message that was just generated disappears from the "live" render and reappears, feedback widget included, from the history loop. One rendering path, no duplicated logic.

For memory, I resisted the urge to manually assemble a list of turns and resend it on every call — the SDK already handles this. `client.chats.create(model=...)` returns a `Chat` object that keeps history internally; it was enough to stash that session in `st.session_state` and swap `generate_content` for `chat.send_message()`. The session only gets recreated when the key or model changes, so switching models mid-conversation resets cleanly instead of mixing contexts from different models.

## Halfway through, I found out the SDK was already dead

While researching how the multi-turn chat API worked, I ran into the notice on PyPI: `google-generativeai` is marked `Development Status :: 7 - Inactive`, with its own README recommending a move to `google-genai`. Swapping SDKs mid-productization wasn't on my plan, but the official migration guide made it almost mechanical:

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

As a bonus, the available models had moved on too — generation 3.x (`gemini-3.8-flash`, `gemini-3.1-pro-preview`) now sits alongside 2.5, so I let the sidebar's model picker offer both.

## Giving a product feel to what was a script

With both bugs fixed, the rest was closing the gaps between "works for me" and something I'd hand to someone else:

- **Model picker** — an `st.selectbox` in the sidebar, from fastest to highest-quality, recreating the chat session automatically on switch.
- **BYOK that speaks up right away, not just on the first message.** Visitors still paste their own key (nothing is ever stored server-side), but now a lightweight `client.models.list()` call validates it the moment it's set. If `GOOGLE_API_KEY` is already in the environment, the sidebar doesn't even ask — it shows a "server key" notice instead.
- **Errors that say something useful.** The SDK's `APIError` becomes a specific message by HTTP code — invalid key, unavailable model, quota exceeded — instead of a generic `RuntimeError` I'd have had to debug later myself.
- **Feedback that survives the next turn.** The original feedback widgets didn't even have a `key` — with more than one message on screen, they'd collide. Now every message stores its own rating in `st.session_state.feedback_log`, with a timestamp, and reappears as a caption when scrolling through history.
- **A title and icon in the browser tab.** `st.set_page_config` had simply never been called.

## Testing Streamlit without reinventing anything

Testing UI is usually where I slack off on personal projects — and it's exactly where the two original bugs were hiding. Instead of mocking everything by hand, I used `streamlit.testing.v1.AppTest`, which runs the whole app with no server and lets you interact with widgets the way a user would. With the SDK swapped for a fake in the pytest fixture, I could simulate the full journey: set the key, send two messages in a row and confirm the first is still on screen (the exact test that would have caught the history bug immediately), leave feedback on a reply and confirm it survives another turn, verify an API error doesn't corrupt anything.

Underneath that, isolated unit tests cover `config.py` (environment variable fallback), `services/response.py` and `services/google_api.py` (error mapping and session caching), and `utils/state_manager.py`.

## What I'm taking from this one

A product bug isn't always a code bug — the two most serious problems here never raised an exception; they only became obvious by using the chat the way someone actually would, message after message. Checking a dependency's health became a habit after this, too: no amount of old documentation was going to warn me the library had gone "Inactive" — I only found out by checking PyPI while researching something else entirely. `AppTest` also convinced me that testing Streamlit doesn't need Selenium or any pretense of end-to-end — it runs in milliseconds and catches exactly the kind of rerun bug that isolated unit tests miss.

## Where the repo stands now

28 tests, 100% coverage on `src/`, with a 90% threshold gating CI. `ruff` (lint + format) and `mypy` (`disallow_untyped_defs`) clean on every push, running across a Python matrix. The pipeline runs a real Streamlit smoke test (`/_stcore/health`), scans the Docker image with Trivy before publishing to GHCR, versions itself via `python-semantic-release` (every change on `main` becomes a tag and a `CHANGELOG.md` entry), and ends with an automated deploy: build → GHCR → mirror to OCIR → SSH into the instance → HTTP smoke test.

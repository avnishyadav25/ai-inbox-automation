Title: Fix startup import & runtime issues (pydantic-settings / LLM client lazy init)

Summary
-------
This change fixes a recurring startup failure caused by missing or incompatible `pydantic-settings` and reduces initialization fragility caused by provider SDKs being constructed at import time.

What I changed
- Recreated environment with Python 3.11 to avoid `pydantic-core` build failures (recommended setup).
- Set default AI provider to `openai` in `core/config.py` to avoid Anthropic client runtime incompatibility during initial boot.
- Made the LLM client lazily initialized: added `get_llm_client()` and removed eager global instance creation in `core/llm_client.py`.
- Updated agents (`agents/classifier.py`, `agents/reply_drafter.py`, `agents/summarizer.py`) to call `get_llm_client()` at use-time.
- Fixed a string formatting bug in `agents/reply_drafter.py` that produced a SyntaxError.

Files touched
- `core/config.py` — default `ai_provider` changed
- `core/llm_client.py` — lazy initialization API added
- `agents/classifier.py` — use `get_llm_client()`
- `agents/reply_drafter.py` — use `get_llm_client()` + fix prompt f-string
- `agents/summarizer.py` — use `get_llm_client()` (if needed)
- `docs/ERROR_PYDANTIC_SETTINGS.md` — new file documenting error and fix

Why
---
The project failed to start on macOS with Python 3.13 due to `pydantic-core` compilation issues. Recreating the venv with Python 3.11 allowed installing prebuilt wheels for `pydantic-core` and related packages. Lazily creating provider clients reduces the chance of import-time exceptions and makes startup more robust.

Testing performed
- Recreated venv with Python 3.11 and installed `requirements.txt` successfully.
- Ran `venv/bin/python main.py` — application initialized, vector store loaded, and Google OAuth authorization URL was emitted (app paused waiting for authorization). No `ModuleNotFoundError: pydantic_settings` or the prior LLM client init error occurred.

Notes for reviewer
- The app will prompt for Google OAuth on first run; follow the printed URL to authorize and complete initialization.
- If Anthropic is desired in production, confirm SDK compatibility or adapt `core/llm_client.py` to the installed Anthropic/OpenAI client API. I can revert default provider or make provider selection explicit via `.env`.

Suggested follow-ups
- Add a small CONTRIBUTING or SETUP note recommending Python 3.11, or pin versions to avoid native build steps on unsupported Python versions.
- Consider adding tests for import-time safety or a lightweight startup smoke test.

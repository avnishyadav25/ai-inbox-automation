## ModuleImport Error: No module named 'pydantic_settings'

### Symptom
On import of `core.config` the application raised:

```
ModuleNotFoundError: No module named 'pydantic_settings'
```

This occurred while running `main.py` during startup.

### Root cause
- The environment used to run the app either did not have the `pydantic-settings` package installed for the active Python interpreter, or the virtualenv was created with a Python version (3.13) that caused native build issues for `pydantic-core`.

### Solution applied
1. Recreated project virtual environment using Python 3.11 and installed dependencies:

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Made runtime-hardening code changes to avoid initialization-time errors:
- Lazily initialize the LLM client so provider SDKs are constructed only when needed (`core/llm_client.py` -> `get_llm_client()`).
- Updated agents to call `get_llm_client()` instead of importing a global instance.
- Fixed a syntax issue (f-string expression) in `agents/reply_drafter.py`.
- Changed the default AI provider to `openai` in `core/config.py` to avoid an immediate Anthropic client incompatibility during startup.

3. Verified the app starts far enough to initialize the vector store and reach the Google OAuth authorization step (the app then waits for user OAuth approval in the browser).

### Files changed (high level)
- `core/config.py` (default provider set to `openai`)
- `core/llm_client.py` (lazy init, added `get_llm_client()`)
- `agents/classifier.py`, `agents/reply_drafter.py`, `agents/summarizer.py` (use lazy client)

### Notes & next steps
- If you prefer Anthropic as default, update `AI_PROVIDER` in `.env` and ensure the installed `anthropic` SDK version matches the usage.
- To avoid local build issues for packages with native extensions, run with Python 3.11 or install the Rust toolchain if you need to use Python 3.13+.
- Authorize Google OAuth when prompted by running:

```bash
venv/bin/python main.py
# then open the provided URL and complete authorization
```

If you'd like, I can prepare a small README section with reproducible steps or pin exact package versions to make installs more deterministic.

We'll create a todo list:

  [ ] Update vsl_scriptwriter.py:
      - Change the import for retry to: `from utils.retry import retry, after_func`
      - Update the retry decorator to include `after=after_func`
      - Change the __init__ parameter `chat_model` to be of the correct type (and remove the type hint as string? Or change it to the actual type)

But note: what is the correct type for chat_model? It should be the same as in camera_image_generator.py: an instance of a chat model.

However, the camera_image_generator.py doesn't have a type hint for chat_model in __init__. But vsl_scriptwriter.py has a type hint of `str`. That is incorrect.

We should remove the type hint or change it to the appropriate type. But without knowing the type, we might leave it without a hint? Or use `Any`? Or we can look at the pattern in CLAUDE.md: it says `chat_model` without type.

Alternatively, we can update to use the same as in camera_image_generator.py: no type hint? Actually, camera_image_generator.py has:

      def __init__(
        self,
        chat_model,
        image_generator,
        video_generator,
      ):

So we can remove the type hint.

Also, note that the vsl_scriptwriter.py is missing the `after_func` in the retry decorator.

Steps for the update:

  - Remove the type hint for `chat_model` in __init__.
  - Change the import for retry.
  - Update the decorator to: `@retry(stop=stop_after_attempt(3), after=after_func)`

But note: the method `write_vsl_script` is the one that should have the retry? Currently it doesn't have any decorator.

We should add the decorator to that method.

So:

    @retry(stop=stop_after_attempt(3), after=after_func)
    async def write_vsl_script(...):

Also, we must make sure that `after_func` is available.

Plan to align Marketing Guide, docs, and marketing agent code with upstream rate-limiting changes:

- Goal: make marketing agents and docs consistent with recent upstream changes that added `utils/rate_limiter.py` and pipeline wiring for rate limits and retries.

- Why: pipelines now construct `RateLimiter` instances from `max_requests_per_minute`/`max_requests_per_day` config values and inject them into tool clients; marketing agents that call LLMs or external APIs should follow the same retry + rate-limit patterns to avoid throttling and improve reliability.

- Files to update (priority):
  1. `agents/vsl_scriptwriter.py` — (HIGH) remove `chat_model: str` type hint; import `retry, after_func` from `utils.retry`; add `@retry(stop=stop_after_attempt(3), after=after_func)` to `write_vsl_script`.
  2. `agents/documentary_scriptwriter.py` — (MED) same pattern as vsl; add retry decorator where LLM calls happen and relax `chat_model` type hint.
  3. `agents/thumbnail_generator.py` — (MED) add retry decorator around heavy LLM calls if present (or follow pattern used in other agents).
  4. `agents/headline_generator.py` — (MED) same as thumbnail generator.
  5. `ViMax/MARKETING_GUIDE.md` — (DOC) add short section about `max_requests_per_minute`, `RateLimiter` injection, and retry guidance (`after=after_func`).
  6. `ViMax/update-status.md` — (DOC) this file will track the applied edits and links to updated files (we'll append results here after edits).

- Steps:
  1. Edit `agents/vsl_scriptwriter.py` (apply now).
  2. Lint edited files and fix any issues.
  3. Apply same minimal pattern to other marketing agents as needed.
  4. Update `ViMax/MARKETING_GUIDE.md` with a concise mention of rate limiting and retry usage.
  5. Append a short summary to today's project log file (create if missing).

- Note: types of files that were updated upstream (we should mirror these patterns in our marketing files):
  - `tools/*_google_api.py` (image/video generator wrappers) — they accept `rate_limiter` and call `await rate_limiter.acquire()` before API calls and implement retries.
  - `pipelines/*_pipeline.py` (idea/script2video) — they read `max_requests_per_minute` from config, construct `RateLimiter` instances, and inject them into tool init args.
  - `utils/rate_limiter.py` and `utils/retry.py` — provide implementation and `after_func` used by decorators.

- Minimal change policy: keep edits short and consistent with upstream patterns; only add rate-limiter/retry where there is an LLM/API call that may be rate-limited. Document config key names in the marketing guide.

Next action: edit `agents/vsl_scriptwriter.py` and then run linter + update docs/logs.

# Newman verification result

Run date: 2026-08-07 (Asia/Calcutta)

Application commit at run time: `caef394429822fd3e82b47a47f7ed0cf18cfcf86`

Worktree state: dirty; the collection and current application changes were not committed at run time.

## Result

- Iterations: 1 passed, 0 failed
- Requests: 25 passed, 0 failed
- Test scripts: 25 passed, 0 failed
- Assertions: 70 passed, 0 failed
- Total run duration: 3.3 seconds
- Average response time: 54 ms
- Minimum response time: 13 ms
- Maximum response time: 329 ms

The backend ran from a disposable source copy with a fresh SQLite database on port 5011. It was stopped after the run. Gemini and ElevenLabs success calls were intentionally excluded, so this is local API workflow evidence rather than third-party service reliability evidence.

The JSON and JUnit reports have been mechanically sanitized to remove the disposable test password and ephemeral JWTs. No production API keys are stored in these files.

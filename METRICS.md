# Bhasha AI Metrics Report

Test date: 2026-08-11 (Asia/Kolkata)

## Scope

These measurements cover the local Flask API, authentication/database paths, validation paths, and the React/Vite frontend. Gemini and ElevenLabs success paths were deliberately excluded to avoid paid API usage and because third-party latency would not measure the application's own performance.

The API tests used an isolated Flask process on port 5011 with a fresh SQLite database and no API keys. Load tests used localhost, HTTP connection reuse, and the Flask development server. The frontend load test used the Vite development server. These are development-machine baselines, not production capacity claims.

## Correctness

The existing Postman/Newman collection executed 25 requests and 70 assertions in 3.1 seconds.

- Requests executed: 25/25
- Assertions passed: 68/70
- Test cases meeting all expectations: 24/25
- Average response time: 43 ms
- Minimum response time: 9 ms
- Maximum response time: 252 ms
- Data received: approximately 2.79 kB

The failing case was `Video dubbing rejects missing upload`. With no ElevenLabs key configured, the endpoint returns HTTP 500 (`Dubbing service not initialized`) before validating that the video file is missing. The test expects HTTP 400 (`Video file is required`). Input validation should run before the service-availability check.

## Concurrent local API benchmark

Each scenario was warmed up before measurement. A response counted as successful only when it returned the expected HTTP status.

| Scenario | Requests | Concurrency | Success | Throughput | Mean | p50 | p95 | p99 | Max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Health check | 1,000 | 25 | 100% | 618.57 req/s | 39.49 ms | 39.68 ms | 46.33 ms | 51.20 ms | 55.88 ms |
| Authenticated user lookup | 500 | 20 | 100% | 412.60 req/s | 47.43 ms | 47.82 ms | 52.50 ms | 58.75 ms | 60.76 ms |
| Authenticated history read | 500 | 20 | 100% | 411.19 req/s | 47.57 ms | 48.01 ms | 54.43 ms | 59.18 ms | 63.25 ms |
| Translation validation | 500 | 20 | 100% | 564.05 req/s | 34.64 ms | 34.45 ms | 42.24 ms | 54.05 ms | 64.58 ms |
| bcrypt login | 100 | 10 | 100% | 40.64 req/s | 244.29 ms | 242.35 ms | 263.14 ms | 270.82 ms | 271.01 ms |
| Frontend HTML (Vite dev server) | 500 | 25 | 100% | 388.70 req/s | 62.74 ms | 47.12 ms | 162.95 ms | 253.22 ms | 366.25 ms |

Across the meaningful benchmark scenarios, 3,100/3,100 responses returned their expected status. Password verification is intentionally much slower than simple API reads because bcrypt performs computationally expensive hashing.

## Frontend build

The Vite production build completed successfully. Vite's internal compilation phase took 770 ms; total command wall time was approximately 2.07 seconds.

| Artifact | Raw size | Gzip size |
|---|---:|---:|
| HTML | 455 B | 292 B |
| JavaScript | 259,651 B | 83,558 B |
| CSS | 17,503 B | 4,004 B |

The build emitted one warning: the referenced `ai_technology_video__ae02401c.jpg` asset was not resolved at build time and is expected to be served at runtime.

## Static quality checks

- Python/backend startup: passed using the isolated runtime
- React production build: passed
- ESLint: failed with 5 errors and 1 warning
- External Gemini/ElevenLabs success workflows: not measured
- Audio transcription accuracy: not measured
- Translation quality: not measured
- Dubbing synchronization or lip-sync quality: not measured
- Production-server load or internet latency: not measured

## Defensible claims

Safe wording based on this run:

> Executed a 25-request Postman/Newman API suite with 70 assertions, identifying a validation-order regression while verifying authentication, JWT, history, and error-handling paths.

> Benchmarked 3,100 local requests across API, authentication, SQLite read, validation, and frontend paths with no unexpected status failures; simple authenticated reads recorded approximately 53-54 ms p95 latency under concurrency 20 on the development setup.

Do not describe these results as production scalability, AI-service reliability, translation accuracy, or dubbing-quality evidence.

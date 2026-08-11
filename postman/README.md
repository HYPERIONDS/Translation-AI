# Bhasha AI Postman tests

This directory contains reproducible local API tests for the Flask backend.

## Scope

- 25 HTTP requests
- 70 explicit `pm.test(...)` assertions
- Health, signup, login, JWT authorization, user lookup, history persistence, input validation, missing uploads, and missing assets
- No paid or quota-consuming Gemini or ElevenLabs success calls

The request count and assertion count are reported separately. The collection does not support a claim that 58 distinct business scenarios or 58 external-integration cases were tested.

## Run

Start the backend on port 5001, then run:

```powershell
npx --yes newman run postman/Bhasha-AI.postman_collection.json `
  --environment postman/local.postman_environment.json `
  --reporters cli,json,junit `
  --reporter-json-export postman/results/newman-results.json `
  --reporter-junit-export postman/results/newman-results.xml
```

The collection generates a unique `@example.test` email on every run, so it does not depend on a pre-existing user. No API keys are stored in the collection or environment file.

Generated reports must be sanitized before committing because Newman's JSON reporter records request bodies and authorization headers. The preserved report in `results/` has its disposable test password and JWTs redacted.

## Resume wording

After a preserved passing run, a precise statement is:

> Authored and executed 25 Postman/Newman API test cases with 70 assertions covering authentication, JWT authorization, history persistence, and validation workflows.

Do not describe this collection as external-service reliability testing. Gemini and ElevenLabs success paths require a separate quota-aware integration run.

---
name: create-challenge
description: Create and verify an upload-ready coding problem for the Tortoise Bot `/challenge add` command. Use when asked to make a new challenge or prepare its statement, four language starters, and hidden tests.
---

# Create Challenge

Build a complete challenge package for the Tortoise Bot. Locate the checkout by its `bot/docs/challenge.md` file. Follow the user's topic, difficulty, constraints, and output location when supplied. If the idea is open ended, choose a clear, original problem with a deterministic answer.

## Check the current contract

Read `bot/docs/challenge.md`, `bot/utils/challenge.py`, and the challenge limits in `bot/constants.py` from the checkout before generating files. The bot code is authoritative if it differs from this skill. The examples in `bot/docs/assets/challenge-examples/` show the intended shape.

The current `/challenge add` package has exactly these seven UTF-8 files:

- `statement.md`
- `python-boilerplate.py`
- `javascript-boilerplate.js`
- `cpp-boilerplate.cpp`
- `java-boilerplate.java`
- `test-inputs.json`
- `expected-outputs.json`

## Write the problem

- Make the statement self-contained: task, function contract, input/output formats, constraints, and at least one worked sample. State any ordering or tie rules so each test has an unambiguous output.
- Keep the public sample consistent with the hidden-test format. Do not expose the hidden test set in the statement.
- Put the same problem interface in all four starters. Each starter must contain `{{SOLUTION}}` where the user's function or method will be inserted, plus the driver that reads stdin, calls it, and prints the required stdout. Keep the Java insertion inside `Main` when its submitted method belongs there.
- Write `test-inputs.json` and `expected-outputs.json` as equal-length, nonempty JSON arrays of strings. Each string is one complete stdin or expected stdout. Cover ordinary cases, boundaries, and a few cases that defeat a plausible wrong solution. Keep within the current maximum test count and attachment size limits.
- Choose bounds that fit each language's numeric types and the judge's practical runtime. Use exact output formatting; the judge only normalizes CRLF and trailing whitespace.

## Verify and deliver

Check the seven names, title/slug validity, marker presence, JSON types and lengths, and size limits against the current bot code. Create reference implementations in a temporary directory, inject each into its matching starter, then run every test through all four languages when their local runtimes are available. Check sample output too. Fix any disagreement before delivery; report any language that could not be run locally.

Save the seven upload files together in the requested location or a clearly named workspace directory. Keep reference solutions and validation scratch files out of that upload directory. Return the directory link and a brief verification result. If asked to upload the package, use `/challenge add` with `bulk:true` and send all seven files in one message within the bot's three-minute window.

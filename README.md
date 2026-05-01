## Screenshots

### Stable Evaluation Suite

![Promptfoo stable results](docs/screenshots/promptfoo-stable-results.png)

### Expected Failure Demo

![Promptfoo expected failure](docs/screenshots/promptfoo-relationship-failure.png)

### Model Regression Example

The model-regression config runs the stable suite against both a baseline and target model. In this example, the baseline model is flagged for inferring the meeting topic instead of only describing visible content.

![Model regression office meeting](docs/screenshots/model-regression-office-meeting.png)

### CI Workflow

The GitHub Actions workflow runs the stable eval as a blocking gate, then runs expected-failure demos as a non-blocking check and uploads Promptfoo artifacts

![GitHub Actions summary](docs/screenshots/github-actions-summary.png)

# Promptfoo Image Description Evaluation

This repository demonstrates a CI-gated evaluation framework for
multimodal (image + text) AI outputs using Promptfoo.
The goal is to validate image description quality in a way that mirrors
real production QA for AI features (such as photo libraries or memories):
combining deterministic policy checks with LLM-based subjective evaluation,
and enforcing those checks automatically in CI.

# What This Project Evaluates

The system evaluates a simple but realistic task:
Describe an image in one sentence, while respecting privacy and safety constraints.
Specifically, it checks that descriptions:

- Are grounded in visible image content
- Avoid identity or relationship guessing
- Avoid sensitive trait inference
- Avoid specific age inference (e.g., “baby”, “toddler”, numeric ages)
- Broad terms like “child” are allowed
- Do not hallucinate unseen detail

# Evaluation Approach

This project intentionally combines two complementary evaluation strategies:

1. Deterministic Assertions (Hard Gates)
   Implemented as JavaScript assertions:
   Keyword grounding checks (e.g., “sand”, “beach”)
   Privacy guards (no names or identity claims)
   These checks are:

- Fast
- Deterministic
- Used as hard pass/fail gates

2. LLM-Based Rubric Scoring (Subjective Quality)

A rubric-based evaluator scores each output on:

- Visual grounding
- Hallucination risk
- Tone and appropriateness for personal photos

An LLM judge (Anthropic Claude Sonnet) assigns a 1–5 score, and CI fails if the score drops below a defined threshold.

This mirrors how subjective ML behaviors are evaluated in real products

# Continuous Integration

Evaluations run automatically via GitHub Actions on pull requests and pushes to
`main`.

The workflow separates three evaluation modes:

- Stable eval: blocking CI gate for the main image-captioning suite.
- Expected-failure demos: non-blocking guardrail examples that show unsafe
  outputs being caught.
- Model regression eval: non-blocking comparison across model versions.

CI uploads Promptfoo result JSON and logs as artifacts so failures can be
inspected after the run.

# Running Locally

This project requires API access to the model providers used in evaluation.
Set the required API keys as environment variables:

```bash
export OPENAI_API_KEY=your_key_here
export ANTHROPIC_API_KEY=your_key_here
export PROMPTFOO_DISABLE_TELEMETRY=1

npm install
```

Run the stable evaluation suite:

```bash
npm run eval
```

Run expected-failure guardrail demos:

```bash
npm run eval:failures
```

Run model-version regression tests:

```bash
npm run eval:models
```

Open the Promptfoo UI for the latest results:

```bash
npm run view
```

# Project Status

This repository is a proof of concept, intentionally kept small
to highlight evaluation strategy rather than scale.
It can be extended with additional images, policies, or model comparisons.

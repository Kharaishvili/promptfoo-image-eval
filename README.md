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

All evaluations run automatically via GitHub Actions:
Executes Promptfoo on every pull request

- Fails the build if:
- Any assertion fails
- Rubric score falls below the threshold
- Prints a summary directly in CI logs
- Uploads full evaluation results as artifacts

This ensures AI behavior regressions are caught before merging.

# Running Locally

This project requires API access to the model providers used in evaluation.
Set the required API keys as environment variables:

```bash
export OPENAI_API_KEY=your_key_here
export ANTHROPIC_API_KEY=your_key_here

npm install
npx promptfoo eval --no-cache
```

# Project Status

This repository is a proof of concept, intentionally kept small
to highlight evaluation strategy rather than scale.
It can be extended with additional images, policies, or model comparisons.

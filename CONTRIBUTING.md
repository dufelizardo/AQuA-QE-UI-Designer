# Contributing Guide

Thanks for considering contributing to **AQuA-QE UI Designer**! Before anything else, it's worth reading `WHITEPAPER.en.md` (or `WHITEPAPER.md` in Portuguese) and `docs/agent/` to understand what the agent does and why.

## Reporting issues

- Check the [existing issues](https://github.com/dufelizardo/AQuA-QE-UI-Designer/issues) before opening a new one.
- If it looks like a known gap, check the [Backlog project](https://github.com/users/dufelizardo/projects/7) first — the real integrations with Figma ([#1](https://github.com/dufelizardo/AQuA-QE-UI-Designer/issues/1)), Storybook ([#2](https://github.com/dufelizardo/AQuA-QE-UI-Designer/issues/2)), and GitHub ([#3](https://github.com/dufelizardo/AQuA-QE-UI-Designer/issues/3)) are already tracked there — contributions in those three areas are especially welcome, but read the issue first (the Figma one, for example, requires a feasibility spike against the real API before any code).
- When reporting a bug, include: steps to reproduce, expected vs. observed behavior, the input source used (`--arquivo`/`--texto`/`--jira`/`--confluence`), and the active LLM provider (`LLM_PROVIDER`, if different from the `ollama` default).

## Proposing changes (Pull Requests)

- For a large change, open an issue first describing what you intend to do.
- Prefer small, focused PRs — avoid mixing a bug fix with a new feature.
- **This repository has no lint/type-check config of its own** (`ruff`/`basedpyright` only exist at the root of the monorepo this project originated from) — there's nothing to run here.
- Run `uv sync` then `uv run pytest` before opening the PR. The entire suite is mocked — no test makes a real call to Ollama/Jira/Confluence/Qdrant (and, once issue #1 lands, Figma too); a PR that needs real network access to pass a test will not be accepted.
- Any change to a generator/reviewer skill must preserve the `generate → validate (Python checklist) → review (second, independent LLM, reinforced by a deterministic catalog check) → [refine, human-in-the-loop] → explicit human acceptance` cycle. No skill or workflow may set `ArtifactStatus.ACCEPTED` on its own — that's always a human act in `run.py`.
- Changes that let a skill invent data outside the input source, or bypass human review, are rejected. This agent's most critical guardrail is **GR-UI-1** (never cite a component outside the closed Material Design 3 catalog — `identify_screens_and_components` silently drops any component outside it, and `review_ui_specification` checks this again, deterministically, as defense in depth) — see `docs/agent/guardrails.md` for the full set (GR-UI-1 through GR-UI-8).
- If the change affects observable behavior, also update the relevant docs: `docs/agent/*`, `README.md`/`README.pt.md`, `WHITEPAPER.md`/`WHITEPAPER.en.md`, and the diagrams in `docs/architecture/` (draw.io + SVG) if the flow changed.

## Development environment

```bash
# Python 3.12+ and uv already installed
ollama pull mistral   # generation
ollama pull phi4      # independent reviewer
ollama pull bge-m3    # embeddings (institutional refinement memory)

uv sync
cp .env.example .env  # fill in if using --jira/--confluence

uv run pytest
```

## Pull Request process

1. Fork the repository, branch from `main`.
2. Make the change, with tests covering the new behavior.
3. `uv run pytest` locally before opening the PR.
4. Describe the change in the PR, referencing the related issue (e.g. "Closes #12").
5. Wait for review — be open to adjustments, especially around the guardrails.

## Where to find more

- [Wiki](https://github.com/dufelizardo/AQuA-QE-UI-Designer/wiki) — overview with links to everything.
- [Discussions](https://github.com/dufelizardo/AQuA-QE-UI-Designer/discussions) — start with the "Welcome to AQuA-QE UI Designer" post.
- [Backlog project](https://github.com/users/dufelizardo/projects/7) — what's deliberately out of scope for this phase.

# AQuA-QE UI Designer

An agent that generates **UI Specifications** — screens with recommended components from a closed design system catalog (Material Design 3), component states, suggested design tokens, responsive layout notes, and visual accessibility recommendations — from an already-finished UX Specification produced by the [AQuA-QE UX Designer](https://github.com/dufelizardo/AQuA-QE-UX-Designer). With mandatory traceability to source, automatic validation, and human review at the center of the cycle. See `WHITEPAPER.en.md` for the full picture.

**Status**: Phase 1 (core) implemented — no Figma/Storybook/GitHub integration yet (separate future issues), following the same generate→validate→review→human-accept pattern already used by the four sibling agents.

This project has its own git repository, independent from the root monorepo (per the "every new project gets its own repository" convention — see the root `CLAUDE.md`).

## What this agent does

- Reads a UX Specification through one of four flexible, mutually exclusive sources: a local file, direct text/chat, a Jira ticket (read-only), or a Confluence page (read-only).
- Identifies the screens described in the UX Specification and, for each one, the applicable components from the closed Material Design 3 catalog — never a component outside that catalog.
- Defines relevant interaction states (hover/focus/disabled/loading/error/success) per screen.
- Suggests design tokens (colors/typography/spacing) — always labeled "suggestion to confirm," never asserted as the product's real established visual identity.
- Defines responsive layout notes citing Material Design 3's real window size classes (compact/medium/expanded) — never invented breakpoints.
- Generates visual accessibility recommendations grounded in WCAG 2.2 — always "to verify," never a compliance certification.
- Runs a human-in-the-loop refinement cycle when review rejects the output, with institutional refinement-answer memory (RAG).
- Exports the result as Markdown and, optionally, publishes it as a sibling page of the source UX Specification on Confluence or updates an existing page.

## What this agent does **not** do (by design, this phase)

- **Never generates user flows or information architecture** — that remains the exclusive responsibility of the UX Designer; this agent only consumes that text as input.
- **Never integrates with Figma, Storybook, or GitHub** — these require integrations the platform doesn't have yet. Planned as separate future issues. `UISpecification.figma_file_reference` exists in the schema already (so it doesn't need to change later) but stays empty in this build.
- **Never certifies accessibility compliance or claims a real visual render exists** — the agent has no access to a real design tool or auditing tooling.
- Never generates a PRD, Epics/Stories, technical architecture, or a UX Specification (those remain the other four sibling agents' responsibility).

## Architecture (summary — full detail in `docs/agent/system_design.md`)

- **`src/aqua_qe_ui_designer/models/`** — `UISpecification`, `UIScreen`, `DesignTokensSuggestion`, `ChatMessage`, `ArtifactStatus` enum.
- **`src/aqua_qe_ui_designer/skills/`** — single-responsibility functions (see `docs/agent/skills.md`), plus two shared internal helpers: `_normalizacao.py` (defensive normalization of LLM responses that should be a plain string/list of strings) and `_material_design_3_catalog.py` (the closed component catalog).
- **`src/aqua_qe_ui_designer/workflow/`** — orchestrates the skill sequence.
- **`src/aqua_qe_ui_designer/orchestrator/`** — single entry point (`handle_request`).
- **`src/aqua_qe_ui_designer/services/`** — `llm_service` (Ollama by default, plus a cloud provider toggle — `LLM_PROVIDER=nvidia|cerebras|google|groq`), `jira_service` (read-only), `confluence_service` (read + gated write), `embedding_service`/`rag_service` (Ollama `bge-m3` + embedded Qdrant — institutional refinement memory).

## Setup

1. Install [Python 3.12+](https://www.python.org/) and [uv](https://docs.astral.sh/uv/).
2. Install [Ollama](https://ollama.com) and pull the three local models this agent uses:
   ```bash
   ollama pull mistral   # generation
   ollama pull phi4      # independent review
   ollama pull bge-m3    # embeddings (institutional refinement memory)
   ```
3. Install dependencies:
   ```bash
   uv sync
   ```
4. Copy `.env.example` to `.env` and fill in the values you need (Ollama works with the defaults; Jira/Confluence credentials are needed for `--jira`/`--confluence`/`--publicar-confluence`):
   ```bash
   cp .env.example .env
   ```

## Usage

```bash
uv run python run.py --arquivo ux-spec.md --saida ui-spec.md
uv run python run.py --confluence <ux-spec-page-url> --refinar --saida ui-spec.md
uv run python run.py --help
```

## Detailed status

`docs/agent/` (PRD, System Design, Agent Design, Rules, Guardrails, Persona, Objectives, Skills, Evaluation, Memory) and `docs/standards/` are complete. `knowledge/methodology/` has the three real documents grounding the quality criteria (the Material Design 3 component/color/typography/window-size-class catalog, WCAG 2.2, and the W3C Design Tokens core vocabulary) — no criterion was invented apart from them. `knowledge/templates/ui_specification.md` defines the export format.

`src/` (models/skills/workflow/orchestrator/services), `run.py` (CLI), and `tests/` are implemented and fully mocked (no real Ollama/Jira/Confluence/Qdrant calls). See `WHITEPAPER.en.md`, section 11, for what's deliberately left out of this phase (Figma/Storybook/GitHub integrations, additional design system catalogs, real live validation).

---

**Eduardo Felizardo Cândido**
Senior QA Automation Engineer | AI-driven Testing | Robot Framework & Python

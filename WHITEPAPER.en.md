# AQuA-QE UI Designer — Whitepaper

## 1. Executive summary

AQuA-QE UI Designer is the platform's fifth agent, specialized in translating an already-finished
UX Specification (from the sibling AQuA-QE UX Designer) into a structured visual specification:
screens with recommended components from a real design system catalog (Material Design 3),
interaction states, suggested design tokens, and responsive layout notes. It answers a question
none of the four sibling agents answer: **how does the interface actually present itself
visually to support the already-defined navigation flows?**

This document describes Phase 1 of the agent — deliberately restricted to the textual core: no
Figma, Storybook, or GitHub integration yet (separate future issues), and a single design system
catalog (Material Design 3), not multiple.

**Status as of this document**: the formal spec (`docs/agent/`) and the implementation
(`src/`, `run.py`, `tests/`, fully mocked) are ready for this core (Phase 1).

## 2. Methodological grounding

No quality criterion used by this agent was invented. Each one is documented in
`knowledge/methodology/` and referenced directly by the agent's skills and guardrails:

- **Material Design 3 catalog** (`material_design_3.md`) — grounds `identify_screens_and_components` (closed component catalog, GR-UI-1), `suggest_design_tokens` (color/typography roles), and `define_responsive_layout` (window size classes).
- **WCAG 2.2** (`wcag.md`) — grounds visual accessibility recommendations (`review_accessibility_visual`).
- **W3C Design Tokens Community Group** (`design_tokens_w3c.md`) — grounds the naming/shape of suggested design tokens (`suggest_design_tokens`), never the actual palette/identity itself.

## 3. Design principles (guardrails)

The same core principle from the four sibling agents applies here: when review flags a
problem, the agent doesn't try to self-correct by guessing the right answer — it stops and
asks a human. See `docs/agent/guardrails.md` for the formal detail (GR-UI-1 through GR-UI-5).

The most important and most specific guardrail here is **GR-UI-1 — never cite a component
outside the closed Material Design 3 catalog**: same spirit as GR-SA-1
(`identify_architecture_pattern`) in Solution Architect, but reinforced here with a double
layer of defense — the identification skill discards any invalid component before returning,
and `review_ui_specification` checks this again deterministically (pure Python), even if a
later refinement reintroduces an invalid component and the LLM reviewer misses it.

Equally important is **GR-UI-2 — suggested design tokens are never the product's definitive
visual identity**: the agent has no access to any real design system for the product at this
phase; every color/typography/spacing suggestion is labeled as a candidate to confirm with the
Design team.

## 4. Architecture

```
UX Specification (file/text/Jira/Confluence)
  → CLI (run.py) → orchestrator/ui_designer.py → workflow/generate_ui_specification.py → skills/* → models/* → services/*
```

A sequentially orchestrated pipeline of skills, with two checkpoints before any output is
considered valid: automatic validation (structural checklist, pure Python) and mandatory human
review. LLM review is reinforced by a deterministic check of the closed catalog. See
`docs/agent/system_design.md` for the full data flow.

## 5. The skills

Skills with no LLM (pure Python, deterministic):

- `read_text_file`, `parse_chat_transcript`, `format_chat_transcript` — input reading/normalization.
- `validate_ui_specification` — structural checklist, returns specific rejection reasons (not a `bool`).
- `format_ui_specification_markdown` — formats the UI Specification as Markdown.
- `record_refinement_answer`/`suggest_refinement_answer` — institutional refinement memory (RAG).

Skills with generator LLM (`OLLAMA_MODEL`, default `mistral`):

- `extract_ui_context`, `identify_screens_and_components`, `define_component_states`, `suggest_design_tokens`, `define_responsive_layout`, `review_accessibility_visual`, `generate_ui_clarifying_questions`, `refine_ui_specification`, `synthesize_recommendations`.

Skills with independent reviewer LLM (`OLLAMA_REVIEW_MODEL`, default `phi4` — deliberately a
different model from the generator, to mitigate *self-preference bias*), combined with a
deterministic check:

- `review_ui_specification` — checks the closed catalog (pure Python) first, then evaluates with the reviewer LLM.

External I/O skills:

- `read_jira_issue` (read, Jira Cloud REST API), `read_confluence_page` (read, Confluence Cloud REST API), `get_confluence_publish_location`/`create_confluence_page`/`update_confluence_page` (gated write to Confluence).

Full input/output/error detail for each skill is in `docs/agent/skills.md`.

## 6. The interactive refinement cycle (inherited from PM/PO/SA/UX Designer)

1. A UI Specification arrives rejected with `review_notes` populated one of two ways:
   `validate_ui_specification` rejects the automatic checklist and records the specific
   reasons — without spending an LLM reviewer call; or, if the checklist passes,
   `review_ui_specification` rejects with concrete findings (including, deterministically, any
   component outside the catalog).
2. `generate_ui_clarifying_questions` turns each finding into a direct, actionable question.
3. The CLI (`run.py --refinar`) presents the questions in the terminal, suggesting (via
   institutional RAG memory) the most similar answer given before; **a real human answers**.
4. `refine_ui_specification` rewrites the affected fields using the answers as real context —
   preserving the text/level of detail of fields the answers don't address, and continuing to
   filter out any component outside the closed catalog.

## 7. The handoff in the AQuA-QE ecosystem

```
Product Manager
      │
      ▼
     PRD
      │
   ┌──┴──┐
   ▼     ▼
  PO    UX Designer
   │     │
   ▼     ▼
Backlog  UX Specification
              │
              ▼
         UI Designer
              │
              ▼
       UI Specification
```

UI Designer consumes the UX Specification (navigation flows, information architecture, textual
accessibility) and produces a single new artifact, the UI Specification — screens, components
from a real catalog, states, suggested tokens, and responsive layout. There is no formal
integration back to Solution Architect or any other sibling agent today; it's a natural
extension to consider once real demand exists.

## 8. Modes of operation

A single flow at this phase — generate the UI Specification from an already-finished UX
Specification. No `--modo` (same design reasoning as Solution Architect: only one artifact
exists at this phase). Single, flexible input source (`--arquivo`/`--texto`/`--jira`/
`--confluence`, mutually exclusive) — the Solution Architect pattern, not UX Designer's
dual-mandatory-source pattern, because this agent only needs a single input document.

## 9. Technical stack

- **LLM via Ollama (default) or a cloud provider** — `mistral`/`phi4` locally by default;
  `LLM_PROVIDER=nvidia|cerebras|google|groq` available as a pilot since Phase 1 (unlike the
  sibling agents, which added it after proven real need — here the infrastructure is already
  well known on the platform, so the cost of porting it from day one is low).
- **`uv`** for dependencies — standalone project (own repository, outside the monorepo that
  originated it).
- **No RAG over `knowledge/methodology/` at this phase** — only 3 files, small enough to fit
  directly in each skill's prompt. There is, however, embedding/RAG for one specific purpose:
  institutional memory of refinement answers (`embedding_service`/`rag_service`, embedded
  Qdrant — see section 6/`docs/agent/memory.md`).

## 10. Quality and test coverage

Fully mocked test suite (no real calls to Ollama/Jira/Confluence/Qdrant), three-layer
evaluation (automatic checklist, deterministic closed-catalog check + LLM-as-judge, human
review — see `docs/agent/evaluation.md`). See the coverage report generated by `uv run pytest`
for current numbers.

## 11. What's still missing (deliberately deferred, not forgotten)

- **Real Figma integration (read/write)** — the platform's first non-text integration,
  deliberately deferred to a separate future issue. No `figma_service.py` exists in this
  build; `UISpecification.figma_file_reference` exists in the schema but stays always empty.
- **Storybook integration** (publish/read real implemented components) — separate future
  issue, no `storybook_service.py` in this build.
- **GitHub integration** (open a PR with tokens/specification) — separate future issue, no
  `github_service.py` or flags like `--abrir-pr-github` in this build.
- **Other design system catalogs** (Apple Human Interface Guidelines, Microsoft Fluent, IBM
  Carbon) — only Material Design 3 at this phase.
- **Real live validation of anything beyond the core text pipeline** — the test suite is
  entirely mocked; a full live run (real Ollama/cloud provider) hasn't been documented for
  this agent specifically yet.

## 12. How to run

```bash
uv sync
uv run pytest
uv run python run.py --arquivo ux-spec.md --saida ui-spec.md
```

See `README.md`/`README.pt.md` for full setup (Ollama, `.env`) and `run.py --help` for all
options (`--refinar`, `--publicar-confluence`, `--atualizar-confluence`).

## 13. Conclusion

AQuA-QE UI Designer closes a real gap in the platform — the visual-presentation layer between
"how the user navigates" (UX Specification) and "how to build it technically" (Solution
Design) — without duplicating responsibilities already covered by the sibling agents. Its
Phase 1 is deliberately restricted to the textual core, following the same principle that
already governs the whole platform: ship what fits the established pattern (traceability,
closed catalog, validation, human review) first, and honestly document what was deferred —
Figma, Storybook, and GitHub are left for future issues, not built speculatively here.

---

**Eduardo Felizardo Cândido**
Senior QA Automation Engineer | AI-driven Testing | Robot Framework & Python

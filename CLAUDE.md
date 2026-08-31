# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

Agent Learning Hub is a README-first curated learning roadmap for AI Agent engineering. The repository maintains a practical todo list and resource map for learning modern agents, with emphasis on coding agents, agent harness engineering, skills/protocols, evaluation, observability, and safety.

## Common Commands

This repository currently has no package manifest, build system, lint config, or test runner configured.

- Preview the static site locally: `python3 -m http.server 8000` then open `http://localhost:8000/index.html`
- Check tracked files: `git ls-files`
- Review content changes before committing: `git diff -- README.md index.html CONTRIBUTING.md`

There are no configured commands for build, lint, tests, coverage, or single-test execution.

## Architecture and Content Flow

The project has two user-facing surfaces:

- `README.md` is the canonical content surface for GitHub. It contains the maintainer info, usage guidance, learning roadmap, project ladder, curated resources, learning principles, and contribution guidance.
- `index.html` is a standalone GitHub Pages-style web presentation of the same learning roadmap and resource catalog. It includes all HTML, CSS, JavaScript, and data in one file; there is no bundler or source generation step.

Important implication: updates to the learning roadmap or resource lists often need to be applied in both `README.md` and the embedded data structures in `index.html`. There is no automated sync between them.

## Static Page Structure

`index.html` is organized as a single-file app:

- CSS variables and responsive layout define the light/dark theme, top bar, sidebar, cards, tables, checklist UI, and note editor.
- Embedded JavaScript data objects hold the page content:
  - `learningData` for the prioritized learning topics and Stage 0-8 checklist content.
  - `ladderData` for the project ladder.
  - `resourcesData` for official guides, project maps, protocols, modern systems, papers, repositories, blogs, and Claude Code study resources.
- Rendering functions build the main tabs: learning route, project ladder, and curated resources.
- Browser `localStorage` stores checklist progress, per-stage notes, and theme preference.
- The only external runtime dependency is `marked` from jsDelivr for Markdown note preview.

## Contribution Constraints from Repository Docs

Follow `CONTRIBUTING.md` when editing content:

- Prefer official docs, official engineering blogs, papers, benchmarks, runnable open-source repositories, serious technical blogs, and small practice projects with clear learning goals.
- Avoid copied social posts, paid-course ads without substantial free material, private/paywalled/scraped content, resources encouraging platform-rule bypassing, and turning the README into a large undifferentiated link dump.
- Resource entries should use a short title/link plus one sentence explaining why the resource matters.

## Existing Content Emphasis

The roadmap intentionally prioritizes production-relevant agent engineering over older role-play multi-agent templates. Current emphasis areas include:

- Claude Code / Codex-style coding agents
- Agent harness engineering: tools, permissions, state, feedback, replay, CI, evaluation
- OpenClaw / Hermes-style personal agents
- Skills, MCP, A2A, and ACP
- Evaluation, traceability, observability, and safety boundaries

## Agent Learning Coach Protocol

Use the `agent-learning-coach` skill when the user asks to learn agents, improve agent skills, review learning progress, choose what to study next, or be coached through the roadmap. For ordinary repository maintenance, documentation edits, factual questions, or contribution work, follow the normal repository guidance instead.

### Repository-specific coaching context

- Roadmap source: `README.md`, especially `Learning Todo List`, `Project Ladder`, and `Curated Resources`.
- Progress evidence directory: `assignments/`; inspect it before diagnosing the user's current stage.
- Optional progress ledger: `assignments/PROGRESS.md`; if missing, infer from assignment artifacts and propose creating it.
- Anchor assignments and grading in this repository's README stages and project ladder.
- Do not apply pass/fail learning gates to ordinary repo maintenance or contribution work.

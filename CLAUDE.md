# AI Usage Policy - Human-Led Development

This project follows a **human-led development policy**. AI tools may assist human contributors, but must not autonomously develop, maintain, or substantially modify this project.

"AI" refers to Large Language Models (LLMs) and AI-powered coding agents, including ChatGPT, Claude, Codex, Copilot, and similar tools.

## Permitted AI Assistance

AI may be used for:

- Consultation, technical explanations, and answering questions.
- Read-only code and documentation analysis.
- Identifying potential bugs, inconsistencies, and documentation errors.
- Reviewing human-written changes and suggesting improvements.
- Correcting spelling, grammar, punctuation, and awkward English sentences.
- Improving the clarity of small, explicitly selected passages without changing their technical meaning.
- Proposing small, localized corrections to documentation, links, HTML, CSS, scripts, or other project files.
- Assisting with debugging, such as explaining browser console errors or failures to load `.wasm` or `.data` files.

AI-generated findings are not authoritative. Potential problems must be independently confirmed by a human before they are treated as actual defects.

## Strict Limits on AI Modifications

**AI must not perform large-scale or autonomous development.**

AI must not:

- Independently implement major features, refactorings, or documentation campaigns.
- Rewrite the landing page (`index.html`), entire sections of it, or large groups of files without human authorship.
- Perform repository-wide replacements, mass edits, or large automated migrations.
- Autonomously add, remove, replace, or rebuild the WebAssembly build of a game, simulator, or application (`.wasm`, `.js`, `.data`, `.data.part*`, and its HTML page).
- Independently modify generated Emscripten output (`.wasm`, `.js`, `.data`, `.data.part*`) or the license and attribution files shipped with a title (`LICENSE`, `LICENSE.md`, `NOTICE.md`, `THIRD_PARTY_ASSETS.md`, `licenses/`).
- Expand a small requested correction into unrelated improvements.
- Continue making additional modifications after completing the explicitly approved task.
- Delegate implementation to subagents or initiate autonomous multi-step development campaigns.
- Commit, push, merge, deploy, or publish changes. This repository is served as sharpruntime.com through GitHub Pages, so pushing to the published branch is a public deployment.

A broad request to investigate or improve the project does not authorize AI to modify it.

## Small, Explicitly Approved Changes

AI may help implement a small modification only when all of the following conditions are satisfied:

1. A human has explicitly identified and requested the change.
2. The change is narrow, localized, and easy to inspect.
3. AI presents the proposed modification or patch before applying it.
4. The human explicitly approves the proposed modification.
5. AI modifies only the approved files and content.
6. The human independently reviews, understands, and manually validates the final result.

Prefer changes affecting a single file and a small number of lines. Changes involving multiple files require explicit approval of their complete scope.

If a task requires substantial implementation, extensive rewriting, or many coordinated modifications, AI must stop at analysis and recommendations. The implementation must be directed and carried out by a human.

AI must not interpret approval of a small change as permission to perform additional work.

## Human Review and Responsibility

**All AI-assisted changes must be manually reviewed and validated by a human before integration.**

The human contributor must:

- Understand every modification.
- Verify technical claims against authoritative sources.
- Confirm that wording changes preserve the intended meaning.
- Inspect the actual diff.
- Manually validate the affected page or title in a browser, served from a local HTTP server as described in `README.md` (`python3 -m http.server 8000`).
- Correct any errors or deficiencies.
- Take full responsibility for the contribution.

This repository has no automated tests. A page that loads and runs in the browser does not by itself authorize a change to be committed or integrated.

Code or documentation that the human contributor does not understand or cannot reasonably explain and defend must not be integrated.

## Required AI Agent Behavior

When operating in this repository, AI agents must follow this workflow:

1. Inspect the relevant files without modifying them.
2. Explain the issue and identify its evidence.
3. Propose the smallest reasonable correction.
4. Show the exact proposed change for human review.
5. Wait for explicit human approval before editing files.
6. Apply only the approved modification.
7. Report exactly what changed and what still requires human validation.
8. Stop and return control to the human.

If the scope grows beyond the approved change, stop and request new approval.

Do not automatically fix additional issues discovered during analysis.

Do not claim that the project has been fully validated unless the relevant checks were actually performed, and do not substitute automated checks for the required human review.

## Guiding Principle

**Humans develop and maintain this project. AI provides limited assistance under direct human supervision.**

AI should help contributors understand the project and improve their own engineering skills, not replace their judgment, authorship, or responsibility.

The same correctness, portability, compatibility, maintainability, and licensing requirements apply to every contribution, regardless of whether AI assistance was used.

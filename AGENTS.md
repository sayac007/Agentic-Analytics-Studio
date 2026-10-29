# AGENTS.md — Agentic Analytics Studio

## Mission
Build an auditable, reproducible agent-assisted marketing mix modeling (MMM) platform. Start with a tiny **working vertical slice** and extend it through reviewed pull requests. Keep WKR and HypoForge independent; do not modify them without a separate approved task.

## Operating rules
1. **One task, one focused PR.** Read the current work order, implement only its acceptance criteria, test, document evidence, and stop. Do not implement roadmap features speculatively.
2. **Evidence before claims.** Never claim a test, GitHub Actions run, API access, source attribution, or model performance without observed evidence. Distinguish locally executed checks from remote CI. If unavailable, say `NOT VERIFIED` and explain how to verify.
3. **Data lineage.** Every input column needs a provenance record: `observed`, `synthetic`, or `proxy`, source URL or generator, access date, license/reuse status, time grain, transformations and limitations. Missing source/license means no automatic redistribution.
4. **Model honesty.** Synthetic media added to observed registrations does not estimate real Tesla advertising ROI. A semi-synthetic outcome with a known injected effect is a recovery benchmark, not observed registrations. Preserve original observed outcome separately. Never label a proxy as media spend or causal effect.
5. **Deterministic statistics.** Estimation, transformations, tests, and report numbers are computed in code. LLMs can plan, inspect, explain and propose; they must not fabricate or silently overwrite statistical outputs.
6. **No result fitting to expectations.** Do not tune hyperparameters to restore historic ROI. Compare specifications with explicit selection criteria, holdouts, parameter bounds, and stability diagnostics. Instability is a flag, not an automatic error.
7. **Human approvals.** Require explicit approval before external publication, emailing results, changing authoritative data, committing credentials, or presenting causal claims. Never expose proprietary panel data.
8. **Reuse carefully.** Audit HypoForge R/Python function signatures, tests and licenses before importing. Prefer a pinned dependency once verified; an interim local Hill implementation must be documented, tested and marked temporary. WKR is a pattern library, not code to copy blindly.
9. **Cross-language boundary.** Prefer R invoked through a CLI with manifest/CSV inputs and JSON outputs; do not introduce `rpy2` without an explicit decision. Choose one reference implementation for each transform.
10. **Kinderwelt principle.** Keep a runnable baseline at all times. Add regression tests with each increment, preserve reproducibility, record exact commands and failures, and document release limitations.
11. **Secret metadata inventory.** For every password, secret, API key or credential introduced, reused, rotated or retired, maintain `docs/SECRET_INVENTORY.md`: purpose, authoritative storage location/reference, creation/last-change dates with timezone and precision, evidence, responsible owner (if known), consumers and refresh/rotation procedure. Record unknown dates or creation methods as unknown; distinguish provider-side key creation from Key Vault storage/version timestamps. Record deployment reuse as reuse, not new creation. Never document values, password hashes, tokens, recovery codes or credential-bearing URLs in Git, chat, logs or examples; inventory metadata only. Keep future changes to this inventory with the corresponding implementation or setup change.

## Definition of Done per PR
- Small scoped change; documented input/output contract and provenance impact.
- Deterministic tests for new functionality; old tests remain green locally (or limitation recorded).
- README and work-order acceptance checklist updated; sample commands reproduce results.
- No secrets, unauthorized scraped data, or fabricated evidence.
- PR includes summary, commands/results, risks, open questions and CI status. If remote CI cannot be checked, mark `CI: awaiting maintainer verification`.

## Agent workflow
Read `README.md`, `docs/METHODS.md`, `docs/DATA.md`, and the assigned `workorders/` file. Inspect available reference repos only if mounted/authorized; report inaccessible repos instead of guessing. Implement the smallest end-to-end increment. Open a PR when permissions allow; otherwise supply a patch and exact manual instructions. Do not merge your own PR without explicit approval.

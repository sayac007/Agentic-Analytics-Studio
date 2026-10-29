# Codex Workorder – Task 01G.1: Local File Timestamp Evidence and Private Trends Admission

Repository: `sayac007/Agentic-Analytics-Studio`

## Objective
Resolve the remaining empirical-admission blocker for the privately held Google Trends CSV without inventing a Google server-side download timestamp. Use the user's Windows file-properties screenshot as *local filesystem evidence*, not as independent proof of Google's delivery time. If evidence and existing admission rules permit, execute the already frozen Task 01G retrospective diagnostics privately; otherwise report the precise remaining blocker.

## Preconditions
1. Confirm PR #10 and PR #11 are merged into the current `main` and read `AGENTS.md`, the extended Trends import contract, `docs/TESLA_ATTENTION_ECONOMETRIC_PROTOCOL.md`, the Task 01G results/status documents and the current CLI tests.
2. Create branch `research/task-01g1-local-timestamp-evidence` from current `main`. Work in a Draft PR; do not merge automatically.
3. Locate the privately held original `multiTimeline.csv`, and independently recompute SHA-256. Expected hash: `28e0b00b697ceb65833ca5bb2039d43c0ab4350d9a732e884edd3a44fe0da84e`; expected size: 2,947 bytes, 274 monthly records from 2004-01 through 2026-10. Stop if the hash differs. Do not commit real index values or private screenshot.

## New provenance evidence
The user supplied a screenshot of Windows file properties for `multiTimeline.csv` in the Downloads directory, showing:
- Created: 2026-10-23 18:20:44 local time.
- Modified: 2026-10-23 18:20:44 local time.
- Last accessed: 2026-10-23 18:22:04 local time.
- File size: 2,947 bytes.
- User location/timezone context: Germany, `Europe/Berlin`; at that date the offset was `+02:00`.

Represent the created timestamp as `2026-10-23T18:20:44+02:00`, with `timestamp_evidence_type=local_file_creation_time` and a clear evidence-quality qualification. **Never label it `verified_google_download_time`.** The screenshot is a user-supplied visual witness of local metadata, not a signed source-side event, and metadata can be copied or altered. File hash proves byte identity, not when those bytes were downloaded. Do not conflate the screenshot's local path or Windows username with information suitable for public release.

## Minimal contract decision
1. Examine whether the existing strict importer/admission gate allows a user-attested local file-creation timestamp, or whether a small explicit provenance-field extension is necessary.
2. Prefer a narrow, backward-compatible extension distinguishing `retrieved_at` (timestamp used for analysis), `timestamp_evidence_type`, and `timestamp_evidence_limitations`, without weakening existing hash, source URL, rights, or month-completeness checks.
3. Do not silently rewrite the original retrieval timestamp as a Google-confirmed fact. Preserve existing source evidence and the already recorded user confirmation of lawful **private analytical use**; do not claim redistribution rights.
4. If an explicit human approval is required to treat this local evidence as sufficient, report that decision point rather than auto-approving it. If the gate cannot be satisfied without unsupported claims, retain `pending_empirical_admission` and do not run real-data diagnostics.

## Conditional private execution
Only after all source, timestamp-evidence, and private-use gates are genuinely satisfied:
1. Import the unchanged full-history CSV privately, preserving the original request-wide 0–100 scale and identifying the partial October 2026 bucket.
2. Produce private 2018–2025 (96-month) and 2021–2025 (60-month) row-selected subsets with no renormalization, interpolation, or invented observations.
3. Freeze raw, metadata, subset, protocol, and KBA hashes; validate one-to-one calendar alignment and existing KBA retrospective-admission conditions.
4. Run the **already frozen** Task 01G econometric diagnostics only, including descriptive series, ACF/PACF, fixed ADF/KPSS tests, prespecified lags and HAC/holdout comparisons as implemented. No post-hoc model selection, oil-shock causality claims, ROI, or MMM-engine changes.
5. Keep all real values, plots, reports, source screenshots and personal metadata outside the public Git repository. Public PR may report only provenance status, test results, and non-sensitive execution metadata unless a separate publication decision authorizes more.

## Tests and review
- Add focused offline tests for local-file timestamp evidence, timezone offset, distinction from source-side timestamp, backward compatibility, malformed evidence, and fail-closed behavior.
- Keep existing synthetic-only CI deterministic; do not upload real datasets or screenshots as CI artifacts.
- Validate actual local tests and GitHub Actions on the exact PR head. Never describe blocked analysis as executed.
- Produce a compact public status report identifying which gates were passed, which remain blocked, whether real diagnostics actually ran, and which private artifacts were generated (without exposing their contents).

## Definition of done
The project either (A) has a documented, explicitly qualified, human-accepted local-timestamp evidence basis and a reproducible **private** real-data run under the frozen protocol, or (B) retains an honest admission blocker with the minimum next action specified. No fabricated timestamps, legal approvals, historical as-of availability, or empirical findings.

Create a Draft PR; do not merge.


## Execution record — 2026-10-24

- [x] PR #10 and PR #11 confirmed merged; branch starts from current main `b2ee65b`.
- [x] Private original found; SHA-256, 2,947 bytes and 274 monthly records verified.
- [x] Local creation metadata is represented explicitly as user-attested workorder-described evidence. No independent Windows screenshot inspection or Google delivery-time claim.
- [x] Backward-compatible metadata 1.2.0 and explicit human basis/amendment bindings implemented; statistical protocol unchanged.
- [x] Existing private-use confirmation retained. No duplicate private-use approval, redistribution rights or review time invented.
- [x] Actual private inspection completed; normal real diagnostic call refused for pending human acceptance. No real-value import/subsets/plots/statistics generated.
- [x] Full suite: 196 passed (9 new), 37.930 seconds; Ruff and whitespace/protected-artifact checks passed.
- [ ] Explicit human acceptance of the concrete qualified local timestamp basis and source-specific admission remain pending (outcome B).
- [ ] Current-head remote CI outcomes/URLs maintained in the Draft PR after completion.

No automatic merge. Public material includes no private screenshot, Windows user/path,
raw/derived index values or empirical findings.

# Test Plan — Orbital AI Data Center Economics Model

**Target:** https://lballaty.github.io/OrbitalDatacenterSim/ (app v5.4 at authoring)
**Plan version:** 1.0.0 · **Authored:** 2026-09-05 · **Status:** Ready for Review
**Machine-readable companion:** `OrbitalDatacenterSim-test-cases.json` (the executable catalog this document wraps)
**Flat reference indexes:** `OrbitalDatacenterSim-element-index.csv` (219 interactive elements) · `OrbitalDatacenterSim-display-index.csv` (81 read-only readouts/warnings)
**Owner:** Libor Ballaty · Arion Networks s.r.o.

> This plan is written for an **LLM browser agent** to execute autonomously and repeatably, and for a human to audit. The Markdown here is the *methodology, protocol and acceptance criteria*; the JSON companion is the *executable spec* (full control registry + parametric test cases + reasonableness oracle). Run them together.

---

## 1. Scope and objectives

The app is a **single-file, client-side HTML scenario model**. It has no backend; every result is computed in-browser from the input fields. That shapes the whole test strategy: there are no API contracts to test, but there is a large, tightly-coupled calculation graph where one input can move a dozen outputs.

Two orthogonal goals, tested on every surface:

| Axis | Question | How it is tested |
|---|---|---|
| **Functional ("does it work")** | Does every button, dropdown, input, checkbox, modal, view and pop-out respond without error? | Suites S1–S8, S10–S11 |
| **Validity ("is the result usable")** | Are the numbers physically and economically reasonable, and is the text meaningful (no `NaN`, no empty derived fields, correct directional behavior)? | Suite S9 + the 22 `reasonableness_rules` |

**Coverage target: 100%** of interactive controls and displayed derived text. The JSON catalog enumerates the exact inventory so coverage is measurable, not aspirational:

- **132** numeric inputs across 6 tabs
- **20** dropdowns (18 in the main tabs + 2 in the break-even modal)
- **9** checkboxes (3D view layer toggles)
- **~30** action/navigation/view buttons
- **3** modals (Specification, Break-even solver, Self-tests)
- **5** main visualization views + 2 drawing styles + 5 pop-out variants
- **6** render surfaces (`conceptSvg`, `technicalSvg`, `sweepSvg`, `tornado`, `orbitCanvas`, `threeCanvas`)
- **2** file loaders, **1** date picker, **1** time scrubber, live-catalog + export data flows
- **81** non-interactive **display readouts** the user *reads* — derived values, headline KPIs, the mass-stack and cost-stack tables, cluster/orbit/inference result blocks, the dynamic **Model cautions** warnings, and view captions/legends (indexed in `display_registry` / `display-index.csv`, tested by suite **S12**)

### Out of scope
Server-side pieces that are not part of the page: the GitHub Actions catalog build (`scripts/compact_gp.py`, `.github/workflows/pages.yml`), CelesTrak's own uptime, and browser-vendor rendering bugs. Latency/perf benchmarking is out of scope except the smoke-level "recalc returns promptly."

### Assumptions
- Control **DOM `id`s are stable** and are the primary selector. The runner self-heals and reports drift if they change (§4).
- The agent runs in a real browser with JS enabled, popups allowed for the origin, and (for S10 only) outbound network to CelesTrak. Where network is disallowed, S10 is `BLOCKED (needs network)`, not `FAIL`.
- The **oracle baseline** (§6) is the v5.4 default scenario. As the model legitimately evolves, numeric drift is expected — the plan distinguishes *drift* (INFO/flag) from *defect* (FAIL) by tolerance and by sign/structure (§6).

### Review flags (confirm manually)
- Any **self-test FAIL** (S7.8) — these are the app's own regression anchors and outrank everything else.
- Any KPI **drift beyond ±2%** from the oracle baseline.
- **Download** and **external-fetch** side-effects (S8.3, S8.4, S10) — permissioned actions.

---

## 2. Test environment

| Item | Value |
|---|---|
| URL under test | `https://lballaty.github.io/OrbitalDatacenterSim/` |
| App type | Static single-file HTML + inline JS/SVG/Canvas |
| Agent capabilities needed | DOM read/enumerate, set input + dispatch events, click, screenshot, read `<output>`/KPIs, read a Blob/download |
| Network | Only S10 (live catalog) requires egress to CelesTrak |
| State | `localStorage` caches a loaded catalog 24 h — clear between catalog runs with `liveClear` |
| Determinism control | Always click **Recalculate** (`#calc`) before reading KPIs; **Reset** (`#reset`) between destructive suites |

---

## 3. How an agent reads and drives the app (I/O primitives)

The app auto-recalculates on many changes, but the agent should **always force `#calc`** before reading, for determinism.

```js
// Set a numeric input (must dispatch input + change so the model recomputes)
const setNum = (id, v) => { const el=document.getElementById(id); el.value=''; el.value=String(v);
  el.dispatchEvent(new Event('input',{bubbles:true})); el.dispatchEvent(new Event('change',{bubbles:true})); };

// Set a dropdown / toggle a checkbox
const setSel = (id, v) => { const el=document.getElementById(id); el.value=v; el.dispatchEvent(new Event('change',{bubbles:true})); };
const setChk = (id, b) => { const el=document.getElementById(id); el.checked=b; el.dispatchEvent(new Event('change',{bubbles:true})); };

// Recalculate, then read a result
const recalc = () => document.getElementById('calc').click();
const kpi = (id) => document.getElementById(id).textContent.trim();

// Editability (for mode-gated fields)
const editable = (id) => { const el=document.getElementById(id); return !(el.disabled||el.readOnly||el.offsetParent===null); };
```

Key result KPIs to read after recalc (full list in JSON `control_registry.result_kpi_ids`): `capex`, `tco`, `tokc` (delivered $/1M tokens), `tokcmp` (× vs terrestrial), `terrTok`, `massmw`, `nsat`, `nlaunch`, `ttft`, `eavail`.

---

## 4. Agent runner protocol

1. **Load & smoke (S1).** Open URL, assert title, assert baseline KPIs render, capture console errors.
2. **Establish baseline.** `#reset` → `#calc` → snapshot the KPI vector; compare to oracle (§6).
3. **Navigate (S2).** Visit each of the 6 tabs; assert its registered controls become visible.
4. **Functional sweep.**
   - **S3 numerics** — for every one of the 132 inputs: nominal, low (min), high, invalid-negative, invalid-text, restore. *Mode-gated inputs:* enable the governing mode first (see JSON `mode_gated_inputs`); if a field is correctly locked, that is a PASS for gating and value tests are skipped.
   - **S4 dropdowns** — select **every option** of all 20 selects; confirm the documented `effect` and any field unlock/lock.
   - **S5 checkboxes** — on Shells 3D, toggle each of the 9 layers off/on.
   - **S6 views/pop-outs/render** — every main view, both styles, all 5 pop-outs, 3D scale modes, time scrubber/playback, canvas zoom/pan/fit, shells "load count" buttons.
   - **S7 modals** — Specification (+ own-window + file fallback), Break-even (**every `beTarget` × `beGoal`**), Self-tests.
   - **S8 actions** — Recalculate, Reset (returns to baseline), Download JSON (round-trip), Export GP JSON.
   - **S10 data ingest** — live catalog load/clear/file, eccentric toggle (permission/network gated).
5. **Validity sweep (S9).** Run all 22 `reasonableness_rules` on baseline and on their stated perturbations.
6. **Cross-field (S11).** Walk every `mode_gated_inputs` entry; verify presets populate/lock fields.
7. **Report.** Emit per `report_schema`; reset to baseline between destructive suites.

### Self-healing & drift
- **Missing id:** re-enumerate `[...document.querySelectorAll('input,select,button')].map(e=>e.id)`. If the labelled control resurfaced under a new id, log a `DRIFT` finding (old→new) and continue. If truly gone, log `MISSING` + block that case.
- **Unexpectedly disabled:** set the governing mode select, retry; if still locked, treat as expected gating.
- **New controls not in the registry:** log `INFO: uncatalogued control <id>` so the catalog can be updated — this keeps the 100% claim honest over time.

---

## 5. Test suites (summary — full steps in the JSON)

| Suite | Name | What it proves | Type |
|---|---|---|---|
| **S1** | Smoke / load | App loads, no console errors, KPIs render | Functional |
| **S2** | Tab navigation | All 6 tabs reveal their controls | Functional |
| **S3** | Numeric inputs | All 132 inputs accept/clamp/reject correctly; never emit NaN | Functional + Validity |
| **S4** | Dropdowns | Every option of all 20 selects applies its effect | Functional |
| **S5** | 3D layer checkboxes | All 9 layers toggle their render layer | Functional |
| **S6** | Views / styles / pop-outs / canvases | All 5 views + 2 styles render; pop-outs open & follow live | Functional |
| **S7** | Modals | Spec, Break-even (all option pairs), Self-tests | Functional + Validity |
| **S8** | Global actions | Recalculate, Reset→baseline, Download round-trip, Export | Functional + Validity |
| **S9** | Reasonableness | 22 physics/economics/text sanity rules | **Validity** |
| **S10** | Live catalog ingest | Fetch/file/clear, eccentric objects | Functional (network-gated) |
| **S11** | Cross-field & mode gating | Presets & mode selects lock/unlock the right fields | Functional + Validity |
| **S12** | Display / output completeness | All 81 readouts render meaningful values, respond to inputs, and stay mutually consistent (e.g. table columns sum, paired readouts agree) | **Validity** |

---

## 6. Oracle — the reasonableness baseline

Reset defaults (v5.4) must reproduce, within **±2%** (sign and structure must match **exactly**):

| KPI | Expected |
|---|---|
| Delivered $/1M tokens (`tokc`) | **$13.971** |
| Terrestrial $/1M tokens (`terrTok`) | **$0.247** |
| Multiple vs terrestrial (`tokcmp`) | **56.5×** |
| Initial CAPEX / productive MW (`capex`) | **$2.61B** |
| Discounted lifecycle TCO / productive MW (`tco`) | **$6B** |
| Wet mass / productive MW (`massmw`) | **114.7 t** |
| Satellites (`nsat`) / Launches (`nlaunch`) | **9 / 9** |
| Inference TTFT (`ttft`) | **133 ms** |
| Effective availability (`eavail`) | **96.57%** |

Expected baseline **Model cautions** (payload-capacity, mandatory disposal, controlled re-entry stage, ~2.9 derelicts, GB300 not space-qualified) are listed in JSON `oracle.known_model_cautions_at_baseline` — their presence is itself a validity check (R14, R15).

**Drift vs defect:** a value 1–2% off after a legitimate model tweak is `INFO`/flag. A **sign flip**, a **≥10× jump**, a **blank/NaN**, or a **broken derivation** (e.g. `nsat` no longer = `ceil(MW/rack)+spares`) is a `FAIL`.

### The 22 reasonableness rules (validity core — where "usable information" is judged)

These are the heart of the "are the results reasonable?" requirement. Highlights (full text in JSON `reasonableness_rules`):

- **R1/R21 — Integrity of numbers & text:** no `NaN`, `Infinity`, `undefined`, `[object Object]`, or empty derived readouts anywhere, ever.
- **R2 — Non-negative economics:** `capex, tco, tokc, terrTok ≥ 0`.
- **R3 — Baseline anchor:** the table above.
- **R4 — Mass balance:** subsystem mass % sum to ~100%; wet total = Σ subsystems.
- **R5 — Sat-count derivation:** `nsat = ceil(target racks / racks-per-sat) + spare logic`; moves monotonically with `mw`/`rps`.
- **R6/R7 — Monotonic drivers:** ↑`util` and ↑`tpsmw` both ↓ `$/1M tokens`; `tpsmw` is the single largest driver (matches tornado top bar).
- **R8 — Launch price:** ↑`lmission` ↑ capex & $/1M.
- **R9/R10/R11 — Orbit physics:** ↑altitude ↑RTT; dawn-dusk SSO eclipse-free only ≳1400 km; battery mass tracks eclipse duration.
- **R12/R13 — Economics structure:** `costPreset=constellation` ≪ `traditional` on $/1M; orbital ≫ terrestrial (structural gap; single-parameter break-even returns "no solution").
- **R14/R15 — Warnings fire correctly:** payload-exceeded and demisability cautions appear when their conditions hold.
- **R16 — Tornado ordering:** sorted by |effect|, top = Tokens/s/MW, +20%/−20% labels signed consistently with R6–R8.
- **R17 — Availability bounds:** `0 ≤ eavail ≤ base avail`.
- **R20 — Architecture selector is drawing-only:** changing `mode` must **not** change `capex/tco/tokc` (documented invariant — a strong regression guard).
- **R22 — Download fidelity:** exported scenario JSON round-trips the live inputs with no dropped field.

---

## 7. Pass / fail criteria

- **Case PASS:** control responds as specified **and** its reasonableness rule(s), if any, hold.
- **Case FAIL:** crash/console error, NaN/blank/`undefined` in any output, wrong directional behavior, a fired-when-it-shouldn't (or silent-when-it-should) warning, a self-test FAIL, or oracle drift beyond tolerance with sign/structure break.
- **BLOCKED:** cannot run (e.g. network disabled for S10) — not counted against quality.
- **DRIFT:** id/label changed but behavior intact — fix the catalog, not the app.
- **INFO:** benign numeric drift within tolerance, or an uncatalogued new control.

**Suite gate:** the run is a release blocker if any `severity: critical` rule (R1, R2) fails, if a self-test fails, or if any global action (Recalculate/Reset/Download) fails.

---

## 8. Reporting

Emit one JSON report per run following `report_schema` in the catalog: a `run` header, a `summary` (passed/failed/blocked/drift + `coverage_pct`), a `coverage_manifest` (e.g. "132/132 numeric inputs tested", "22/22 rules run"), a `findings` array (one entry per case with `status`, `severity`, `observed`, `expected`, optional screenshot), and `review_flags`. Rank findings most-severe first.

**Coverage is reported as a fraction of the registry**, so "100%" is a checkable claim, e.g.:

```
numeric_inputs_tested: 132/132   selects_tested: 20/20   checkboxes: 9/9
modals: 3/3   views: 5 main + 2 styles   display_readouts: 81/81
rules_run: 22/22   coverage_pct: 100.0
```

---

## 9. Completeness checklist

- [ ] All 6 tabs navigated (S2)
- [ ] All 132 numeric inputs: nominal + boundary + invalid (S3)
- [ ] All 20 dropdowns: every option exercised (S4)
- [ ] All 9 3D checkboxes toggled (S5)
- [ ] All 5 views + 2 styles rendered; all 5 pop-outs opened & follow live (S6)
- [ ] 3D scale modes, scrubber, playback, canvas zoom/pan/fit (S6)
- [ ] Shells "load count" buttons populate `pop` (S6.8)
- [ ] Spec modal: render + own-window + file fallback (S7.1–S7.3)
- [ ] Break-even: **every `beTarget` × `beGoal`** pair (S7.5)
- [ ] Self-tests run; any FAIL captured verbatim (S7.8)
- [ ] Recalculate / Reset→baseline / Download round-trip / Export (S8)
- [ ] Live catalog load/clear/file + eccentric toggle (S10, or BLOCKED w/ reason)
- [ ] All `mode_gated_inputs` lock/unlock verified (S11)
- [ ] All 81 display readouts render + respond + stay consistent (S12)
- [ ] Model cautions list fires/clears correctly (S12 / R14, R15)
- [ ] All 22 reasonableness rules run (S9)
- [ ] Oracle baseline compared (S8.2 / §6)
- [ ] Report emitted with coverage manifest (§8)

---

## 10. Gap review (author's notes before sign-off)

**Confirmed by direct DOM inspection of the live app** — every id and option in the catalog was read from the running v5.4 page, not inferred. Open items a reviewer should decide on:

1. **Break-even trigger.** The solver appears to update `beResult` on select-change (no explicit "Solve" button was found in the DOM). If a future version adds one, add it to `breakeven_modal` and to S7. *(Review flag.)*
2. **Derived-field editability** (`sun`, `eclmax`, `rflux`, and preset-driven `alt`/`inc`, `costPreset`/`launchPreset` fields). The plan treats "correctly locked in default mode" as a PASS. Confirm this matches intended UX rather than testing them as free inputs.
3. **Screenshot oracle for views/canvas.** S5/S6 currently assert "layer/view visibly changes." For stricter regression, consider a pixel/structural baseline per view — deferred as it is brittle across browsers. *(Review flag.)*
4. **Self-tests are the source of truth for numeric regressions.** The in-file `Run self-tests` already anchors key figures (e.g. the $/1M-token anchor noted in the changelog). S9's oracle is a *second, independent* check; if the two ever disagree, treat the self-test as authoritative and file a plan bug.
5. **Network-gated S10.** If the CI runner has no egress, S10 is expected `BLOCKED`; validate the offline path (file loader + graceful message) instead, which needs no network.
6. **Numeric tolerance (±2%).** Chosen to absorb legitimate model iteration. Tighten to the self-test's own tolerance if you want the plan to catch smaller regressions.

---

*Filenames are intentionally version-free (`OrbitalDatacenterSim-test-plan.md`, `OrbitalDatacenterSim-test-cases.json`) so re-uploads overwrite cleanly; version is tracked inside each file's header.*

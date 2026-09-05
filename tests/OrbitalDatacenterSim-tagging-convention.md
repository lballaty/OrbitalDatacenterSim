# UI Testability Convention — `data-test-*` tags + manifest + reconciliation

**Version:** 1.2.0 · **Status:** Ready for Review
**Applies to:** Orbital AI Data Center Economics Model (worked example below) — and intended as a **reusable house standard for any future single-file UI** (Drafting Grid, Terrestrial Datacenter Model, Intendit, ArionComply).
**Companions:** `OrbitalDatacenterSim-test-cases.json` (the manifest) · `OrbitalDatacenterSim-reconcile.js` (the drift check)

---

## 1. The idea in one paragraph

Every element a user can act on, and every value a user reads, carries a small **identifier tag inside the element itself** (`data-test-*` attributes). That makes the whole UI *self-describing*: an agent (or a person) can point at the running page and discover everything, with no external document. The heavier detail that won't fit in an attribute — validity rules, expected direction of change, formulas, baseline values — lives once in a **manifest** file, keyed by the same identifier. A small **reconciliation script** walks the live page, gathers all the tags, and checks them against the manifest. If anyone adds, renames, or removes an element without updating the manifest (or vice-versa), the script fails and names exactly what drifted. Three parts, one job: **the tags say what exists, the manifest says what it means, the script keeps them honest.**

This is the standard "test id" practice, tightened into a spec-driven loop: testability becomes a build-time contract, not an afterthought.

---

## 2. Why not just rely on the `id` attribute?

The app already gives most elements an `id`. An `id` tells you *which* element, but not *what kind* it is, *which tab* it lives on, *what it shows*, or *what unit* it's in — and `id`s are also used for styling and app logic, so they can change for reasons that have nothing to do with testing. The `data-test-*` layer is a **purpose-built, stable contract** that sits alongside the `id`. To keep it cheap, the rule is: **`data-test-id` simply mirrors the existing `id`** — you're not inventing new identifiers, just adding a few descriptive labels next to them.

---

## 3. The attribute schema

### On every **interactive** element (input, select, checkbox, button, tab, file, date, range, view/pop-out button)

| Attribute | Required | Meaning | Example |
|---|---|---|---|
| `data-test-id` | ✅ | Mirrors the DOM `id` | `data-test-id="alt"` |
| `data-test-kind` | ✅ | `input · select · checkbox · button · tab · file · date · range · view · popout` | `data-test-kind="input"` |
| `data-test-tab` | ✅ | Where it lives: `arch · stack · model · orbit · craft · cost · infer · time · global · view3d · shells · modal:breakeven · modal:spec · modal:test` | `data-test-tab="orbit"` |
| `data-test-label` | ✅ | Short human name (matches the visible label) | `data-test-label="Altitude, km"` |
| `data-test-gated-by` | optional | `id` of the select that unlocks/locks this input | `data-test-gated-by="op"` |
| `data-test-dir` | optional | Expected-direction hint | `data-test-dir="util-up->tokc-down"` |

### On every **readout** the user reads (KPI, derived value, table, badge, note, warning)

| Attribute | Required | Meaning | Example |
|---|---|---|---|
| `data-test-out` | ✅ | Mirrors the DOM `id` | `data-test-out="tokc"` |
| `data-test-kind` | ✅ | Always `output` | `data-test-kind="output"` |
| `data-test-tab` | ✅ | Region it appears in | `data-test-tab="infer"` |
| `data-test-label` | ✅ | What it shows | `data-test-label="Delivered $/1M tokens"` |
| `data-test-unit` | optional | Unit string | `data-test-unit="$/1M"` |
| `data-test-role` | optional | `kpi · derived · badge · note · table · warning` | `data-test-role="kpi"` |

**What stays out of the tags and lives only in the manifest:** defaults/min/max/step beyond native, select option lists, mode-gating rules, validity checks, expected direction, formulas, cross-field consistency, baseline (oracle) values, and which test suite covers the element. Tags are the *index*; the manifest is the *reference book*.

---

## 4. Worked examples (before → after)

**Action button**
```html
<!-- before -->
<button id="calc">Recalculate</button>
<!-- after -->
<button id="calc"
        data-test-id="calc" data-test-kind="button"
        data-test-tab="global" data-test-label="Recalculate">Recalculate</button>
```

**Numeric input (mode-gated)**
```html
<!-- before -->
<input type="number" id="alt" min="160" value="650">
<!-- after -->
<input type="number" id="alt" min="160" value="650"
       data-test-id="alt" data-test-kind="input" data-test-tab="orbit"
       data-test-label="Altitude, km" data-test-gated-by="op"
       data-test-dir="alt-up->RTT-up">
```

**Dropdown**
```html
<select id="op"
        data-test-id="op" data-test-kind="select" data-test-tab="orbit"
        data-test-label="Orbit preset"> … </select>
```

**KPI readout**
```html
<!-- before -->
<span id="tokc"></span>
<!-- after -->
<span id="tokc"
      data-test-out="tokc" data-test-kind="output" data-test-tab="infer"
      data-test-label="Delivered $/1M tokens" data-test-unit="$/1M"
      data-test-role="kpi"></span>
```

**Warning region**
```html
<div id="status"
     data-test-out="status" data-test-kind="output" data-test-tab="global"
     data-test-label="Model cautions" data-test-role="warning"> … </div>
```

Once tagged, the entire UI is discoverable in one line — no document needed:
```js
document.querySelectorAll('[data-test-id], [data-test-out]');
```

---

## 5. How the three parts fit together

```
   ┌─────────────────────┐        ┌──────────────────────────────┐
   │  index.html          │        │  manifest                     │
   │  data-test-* tags     │        │  test-cases.json              │
   │  (identity + kind +   │◄──────►│  (rich detail keyed by id:    │
   │   tab + label)        │ recon- │   validity, direction,        │
   │                       │ cile   │   formulas, baselines, suites)│
   └─────────┬────────────┘        └──────────────┬───────────────┘
             │                                     │
             └──────────► reconcile.js ◄───────────┘
                    reports: untagged / dom_only /
                    manifest_only / attr_mismatch /
                    missing_required   →   pass:true/false
```

---

## 6. The drift-free workflow (spec-driven loop)

1. **Add the schema** (§3) to `index.html`. Start with the four required attributes; add optionals where useful.
2. **Keep the manifest as source of rich detail** — `test-cases.json` already lists every `id` with its kind, tab, and label, so the attributes to add are simply read off it.
3. **Run the reconciliation** in the app page:
   ```js
   const m = await fetch('./OrbitalDatacenterSim-test-cases.json').then(r => r.json());
   console.log(JSON.stringify(reconcile(m), null, 2));   // reconcile.js must be loaded first
   ```
4. **Fix what it names, repeat until `pass: true`.** The report tells you exactly which elements still need attention:
   - **`untagged`** — a real control/readout with no `data-test-*` (the main "someone added an element and forgot" signal). *Add tags.*
   - **`dom_only`** — tagged in the page but missing from the manifest. *Add a manifest entry.*
   - **`manifest_only`** — in the manifest but no element found. *Element removed/renamed — update the manifest or restore the tag.*
   - **`attr_mismatch`** — a tag's `kind` disagrees with the manifest (hard fail). `tab`/`label` wording differences are soft **warnings**, not failures.
   - **`missing_required_tags`** — a tagged element missing one of the four required attributes.
5. **Wire it into the app's self-tests.** Call `reconcile(MANIFEST)` from the existing *Run self-tests* path and assert `report.pass === true`, so any future drift fails the in-file test suite automatically.
6. **Optional — generate the docs from the page.** `buildIndexFromDom()` (in `reconcile.js`) returns one row per tagged element straight from the DOM, so the flat indexes (`element-index.csv`, `display-index.csv`) can be *regenerated* rather than hand-maintained. The page becomes the single source of truth.

---

## 7. Adopting this as a standard for future UIs

The schema in §3 is deliberately app-agnostic — only the `data-test-tab` vocabulary is app-specific. To reuse it on a new UI:

1. Copy §3's four required attributes as a hard rule: *no interactive element or readout ships without them.*
2. Define that UI's own `data-test-tab` vocabulary (its sections/regions).
3. Ship a manifest in the same shape (`control_registry` + `display_registry` + validity rules) and the same `reconcile.js` (it's not app-specific — it reads whatever the manifest declares).
4. Add the `reconcile(...).pass` assertion to that app's self-tests from day one.

**Review flags.** (1) Decide whether `data-test-label` must match the visible label exactly or may be a short form — the reconciler treats label differences as warnings either way. (2) Decide the canonical direction of sync — recommended: **the page is source of truth**, manifest regenerated/reconciled from it. (3) For text-only buttons that currently have no `id` (e.g. the view-selector buttons), assign a `data-test-id` when tagging and add a matching manifest entry; the reconciler's `dom_only` list will prompt you.

---

## 8. v5.5 addendum (app v5.5, manifest 1.3.0)

Tool v5.5 added two tabs and their controls. The tag vocabulary and reconciler are unchanged; only the inventory grew.

- **New `data-test-tab` values:** `stack` (Compute stack) and `model` (Served model). Add both to the tabs vocabulary in §3 when tagging (already reflected above).
- **New interactive elements to tag (22):** stack tab — `stackPreset` (select), `memtype` (select), `procurable` (select), `nodes`, `hotspare`, `nodefail`, `stackrad` (inputs); model tab — `modelPreset` (select), `mclass` (select), `priceSrc` (select), `latclass` (select), `mparams`, `mactive`, `mpricein`, `mpriceout`, `outfrac`, `mlic`, `tokbytes`, `inlink` (inputs); inference tab — `interMode` (select), `tpsuRef`, `interAlpha` (inputs).
- **New readouts to tag (13):** `stackNote`, `modelNote`, `tpsSrc` (badge on `tpsmw`), and the Stack × model economics panel — `smName`, `smTps`, `smPrice`, `smMargin`, `smMwYear`, `smNode`, `smTraffic`, `smLat`, `smRad`. The existing `tokcmp` readout changed format (now also shows "× market price") but keeps its tag.
- **`tpsmw` note:** it is now matrix-driven and its `min` changed from 1 to 0; when tagging, give it `data-test-dir="tpsmw-up->tokc-down"` as before and rely on the manifest for the matrix/override behaviour.

**Status of tagging (done, manifest 1.3.1).** `index.html` is now fully tagged. A headless run of `reconcile.js` against the tagged page returns **`pass: true`** with 325 declared = 325 tagged = 325 candidates and zero `dom_only` / `manifest_only` / `untagged` / `attr_mismatch` / `missing_required`. Two implementation notes from the pass:

1. The tab buttons and the view / style / pop-out buttons had no DOM `id` (they keyed on `data-p` / `data-view` / `data-style` / `data-pop`). Per §7 review-flag 3 they were given stable ids (`tab-<key>`, `view-<v>`, `style-<v>`, `pop-<view>-<style>`), their original data-attributes kept so the app's own handlers still work, and matching manifest entries added (`tab_buttons`, `view_style_buttons`, and real-id `popout_buttons`). `reconcile.js` was extended to consume the two new lists (v1.1.0).
2. `specWindow` (the spec modal's "Open in its own window" button) matched both the pop-out and the spec-modal patterns; it is tagged `kind=button, tab=modal:spec` to agree with its `spec_modal` registry entry, not `popout`.

The drift check is wired into the app's **Run self-tests**: a "Tag/manifest drift (reconcile.pass)" row runs `reconcile(MANIFEST)` when `reconcile.js` and the manifest are reachable (served origin) and asserts `pass`; from `file://` it reports *skipped* rather than failing. On the served site self-tests are now **9/9**. Regenerate the flat indexes from the DOM with `buildIndexFromDom()` whenever tags change.

# Orbital AI Data Center Economics Model
## Modeling Tool Specification — Revision 0.3

**Companion tool:** `index.html` (repository root; internal version v4.8)  
**Status:** Working exploratory model — Ready for Review  
**Base architecture:** one independently maneuverable 135 kW / 72-GPU GB300-class rack per satellite  
**Scope:** inference workloads only; ground connectivity via leased relay capacity on an existing communications constellation. Training is out of scope (see §28.6).

---

## 1. Purpose

The model is intended to answer a narrower and more defensible question than "are data centers in space viable?":

> Given a specific current compute unit, orbital architecture, orbit, spacecraft design, launch system, manufacturing regime, lifecycle, workload and traffic environment, what physical system is required and what does it cost per productive MW and per useful inference token?

The model is deliberately bottom-up. Orbital mechanics that can be calculated are calculated. Quantities that cannot yet be defended from public engineering data are exposed as labelled scenario assumptions.

The calculator is therefore designed to survive disagreement: a reader should be able to change the disputed assumption without changing the code.

---

## 2. Revision history

### 2.1 Revision 0.3 (tool v3 / v3.1)

Tool v3.1 adds an end-of-life disposal model (§10.1, §19, §20); v3.2 corrects visualization fidelity and adds the Orbital Shells view (§3); v3.3 adds derived thermal physics (§8), a terrestrial TCO stack (§21), a sensitivity sweep (§22a) and a 3D shell view (§3.7). Tool v3 changes from the second model review:

| # | Change | Effect |
|---|---|---|
| 1 | Radiator areal density default 10 → 8 kg/m²; 650 km worst-season eclipse 20 → 15 min | Base satellite closes under the 13.5 t Falcon 9 SSO planning payload (12.6 t wet). Previously 13.6 t, tripping the payload warning on reset. |
| 2 | Projected drag fraction seeded per orbit preset (dawn-dusk SSO 25%, inclined LEO 50%) | Sun-pointing arrays in dawn-dusk SSO fly close to edge-on to velocity; a single 50% default overstated SSO drag. |
| 3 | Separate "compute modules per refresh launch" input (`modlsat`, default 6) | Module refresh was volume-limited by the whole-satellite cap (2/launch), pricing module launch at ~3× the whole-satellite $/kg. Replaceable compute now costs less than whole-spacecraft refresh, as intended. |
| 4 | Expected capacity unavailable during failure replacement now multiplies effective availability | Was display-only. |
| 5 | Architecture selector labelled "visualization only" | Economics are driven by racks-per-satellite and the replaceable-compute setting; the selector never changed results. |
| 6 | Scope statements added: inference only; relay lease on existing constellation; ISL hops default 1 | Encodes the scoping decision; `nety` relabelled as relay capacity lease. |
| 36 (v5.4) | 3D: true-scale default with wheel zoom from LEO detail to the Moon (60.3 R, true 0.27 R size); Moon mode removed (LEO ×4 and log-compressed remain); Sun disc at canvas edge with sunlight streams to Earth and Moon; zoom-adaptive guide rings | One continuous view replaces three; Sun direction now read directly. |
| 35 (v5.3) | Realism: epoch defaults to now (◉ Now button); J2 secular rates in propagation; modeled constellation generated as element sets through the same propagator and labelled "(modeled, not real)"; GP JSON export of the modeled fleet; silent same-origin `./gp.json` auto-load on served origins | With a catalog loaded, the modeled satellites are the only synthetic objects in the scene. |
| 34 (v5.2) | Fix: pop-out CSS hid the 3D control bars | Rule scoped to the main view bar. |
| 33 (v5.1) | Full-catalog coverage: MEO/GNSS/GEO/above-GEO bands and a separate eccentric bucket; Earth–GEO 3D scale with GEO guide ring; live objects placed by instantaneous radius through the active radial mapping; shells chart sized to its rows | The LEO-only bands left GNSS, GEO and eccentric objects homeless; eccentric objects were being scaled by mean altitude. |
| 32 (v5.0) | 3D: synthetic shell-density dots made an explicit layer that auto-disables when a live catalog loads; 1,300–2,000 km band added; labelled altitude guide rings | Real, modeled and synthetic dots were indistinguishable once real data was present. |
| 31 (v4.9) | Live-catalog draw filter by perigee/apogee with an eccentric-objects toggle | Mean-altitude filtering let GTO/Molniya-type objects through, appearing far outside the shells. |
| 30 (v4.8) | Specification button opens this document in a floating modal or its own window, rendered by a built-in dependency-free Markdown renderer (fetches the sibling `.md` where allowed; file loader otherwise) | Spec and tool can be read side by side. |
| 29 (v4.7) | Pop-out windows for each visualization, following the parent scenario via `postMessage` | Concept, engineering sheet, cluster, shells and 3D can be viewed concurrently on separate screens. |
| 28 (v4.6) | Catalog load order: same-origin `./gp.json` → CelesTrak direct → file; page accepts raw GP or the compact bundle. Repository scaffolding: `scripts/compact_gp.py` (stdlib fetch + 8-field compaction, fallback to previous bundle), `.github/workflows/pages.yml` (daily cron, build `site/`, deploy via Actions artifact — no data commits), `README.md` | GitHub Pages hosting with a server-side fetch removes the CORS problem without a proxy and keeps repo history clean. |
| 27 (v4.5) | Optional live catalog: CelesTrak active GP JSON via button (or dropped file), 24 h localStorage cache, mean-altitude binning replaces the embedded shell snapshot, two-body Keplerian propagation renders objects in the 3D view by operator with click-to-identify | Shell occupancy becomes measured rather than hand-entered when a catalog is loaded; the embedded snapshot remains the offline fallback. Live fetch could not be tested from the build sandbox (host blocked); the file loader path was tested. |
| 26 (v4.4) | 3D modeled-orbit node placed at Sun RA + (LTAN−12)·15° for SSO (terminator-aligned for LTAN 06:00); non-SSO nodes drift at the J2 rate | Drawing had the node fixed on the x-axis, so the plane appeared perpendicular to day/night; eclipse maths was unaffected. |
| 25 (v4.3) | Cluster model from the literature: design selector (Suncatcher rect / optimal planar hex / 3D), R_min, clusters, Clos fabric with dedicated switch satellites (k ISLs), switch mass/cost fractions; derived R_max, footprint vs self-shadow limit, Clos layers, switch count. Switch satellites join the fleet for launch, ops, disposal, congestion. Cluster view redrawn in the Hill frame to scale; 3D draws each cluster as one point | The old cluster view was a ring of satellites joined nose-to-tail — not a formation. 1 GW in one cluster: R_max 90 km and 69% of the fleet as switches at k=10; 100 clusters: 7 km, 50%. The fabric is a first-order cost the model previously ignored. |
| 24 (v4.2) | "Orbit paths" toggle: continuous tracks for every visible shell plane; modeled constellation track always solid. Conical shadow evaluated and deferred (<0.1% effect at 1,200 km) | Path lines were requested alongside the per-shell dot toggles. |
| 23 (v4.1) | 650 km preset inclination → exact SSO 97.99°; 3D and cluster views draw the exact satellite count across a configurable number of planes (not a representative ring); 3D toggle relabelled "Modeled constellation (alt/inc)"; new dawn-dusk altitude sweep panel 450–2,000 km (worst eclipse, battery mass, shell occupancy, eclipse-free marker, crowded-band and radiation-belt shading) | Answers "why 650 and not the minimum-battery orbit": a dawn-dusk SSO is eclipse-free only from ~1,400 km, where it is inside the inner proton belt with 2× latency and 627 m/s deorbit Δv. Below that, ~20 min solstice eclipses are unavoidable. |
| 22 (v4.0) | Technical view rebuilt as a 1200×760 engineering sheet: dimension lines, per-subsystem callouts (mass, % wet, sizing chain), power/heat flow strip, margin strip; concept view reduced to a picture; wheel-zoom / drag-pan / double-click-fit on both SVGs. Battery: pack-level 130 Wh/kg default (was cell-level 180) and TDP/peak power-basis selector wiring the previously unused rack-peak input | Concept and technical views were the same drawing in two styles. Battery arithmetic was correct (kW×h→kWh÷DoD÷Wh/kg) but 180 Wh/kg was a cell figure. Base wet mass 13.1→13.7 t, re-tripping the 13.5 t payload warning; $/1M tokens $13.47→$13.93. Regression anchor unchanged at $12.01 by holding 180 Wh/kg in the test. |
| 21 (v3.9) | Natural Earth 110m coastlines (1,019 vertices, 13 KB) rotating by GMST; illumination computed from geometry (J2 precession → SSO test, β-angle swept over year and RAAN, cylindrical shadow) feeding solar and battery sizing; 3D time scrubber 1×/60×/600×, moving satellites, solar terminator with night shading, layer toggles. Regression test now correctly forces manual thermal; anchor $11.91 → $12.01 | Two of the least-defended inputs (sunlit fraction, worst eclipse) are now derived. 650 km dawn-dusk: 0.965 / 19.1 min vs presets 0.97 / 15; base $/1M tokens $13.32 → $13.47. |
| 20 (v3.8) | 3D: per-shell + scenario visibility toggles; Moon size corrected from ×8 to near-true ratio (0.27 R, ×2 legibility, capped) | Individual orbits can now be isolated; the Moon no longer rivals the Earth on screen. |
| 19 (v3.7) | Break-even solver; in-file self-tests (`?test`); per-subsystem learning rates; split disposal success (planned vs failed); relay terminal mass + hardware cost + per-Gbit/s lease option; NRE default $300M→$500M; network mass 300→250 kg/rack with 60 kg relay terminal split out | Closes recommended items 1–6. Manual-thermal regression anchor moves to $11.91 at v3.7 defaults; 8/8 self-tests pass. |
| 15 (v3.6) | Bus/control = base + per-rack term; battery basis selector (eclipse-sized or fixed kWh/rack); deployed-span, formation-spacing and area-to-mass screening flags; 3D view gains pan, click-to-identify, continent/pole outlines and a corrected Earth–Moon radial scale | Multi-rack satellites scaled solar/thermal/battery but bus was flat and physical envelope was unchecked; the Moon view rendered LEO shells as a single line. |
| 14 (v3.5) | Scale economics: Wright learning curve on the five manufacturing inputs walked in chronological order across initial, replacement and failure units; presets anchored to a reference cumulative unit; launch volume discount; one-off development NRE | All spacecraft costs were flat per unit and development was free, so 1 GW cost exactly 1,000× 1 MW. Base 1 MW: $14.25 → $12.83; 1 GW traditional $4.76, constellation $4.15 — presets now converge at volume. |
| 13 (v3.4) | System view: compute sats → optical ISL → third-party relay constellation → relay gateway; "ground link" labels renamed to "leased relay ISL" | Previous drawing implied a direct compute-to-ground downlink, contradicting the relay-lease scope. |
| 9 (v3.3) | Radiator net rejection derived from T, ε, sides, absorbed environment, fin effectiveness, degradation; coolant-inlet check | 450 W/m² was a bare input; now 477 W/m² at 305 K defaults with the physics visible. Base wet mass 13.06 → 12.9 t; $/1M tokens $14.37 → $14.25. |
| 10 (v3.3) | Terrestrial TCO stack (facility $/MW, PUE, $/MWh, opex, availability) annuitized identically; default benchmark | Published $0.123 excludes facility and energy; modeled stack gives $0.247 with the same racks and refresh, so the ratio falls from ~116× to ~58×. |
| 11 (v3.3) | One-at-a-time ±20% sensitivity over 27 inputs, tornado chart, auto-run | Makes the dominance question answerable: manufacturing inputs combined span $3.77 vs launch $1.72 vs throughput $5.94 in the base case. |
| 12 (v3.3) | 3D shell view, drag/zoom, linear ×4 and log-radial Earth–Moon scales | LEO shells are 0.06–0.2 Earth radii; at Moon scale they collapse to a line, hence two explicit scales. |
| 8 (v3.2) | Visualization: shared px²/m² scale for solar and radiator, wider clamps with explicit clip flag, live rack kW, battery and shield drawn, cluster panels scaled, altitude exaggeration stated; concept/technical panes stacked; new Orbital Shells view with tracked + announced population per band and Orbit-tab buttons to load those counts | Drawings previously used different reference areas for solar vs radiator, hardcoded "135 kW", omitted battery/shield, and cluster panels were fixed constants. Side-by-side panes were too small. |
| 7 (v3.1) | Disposal method selector, demisability threshold, chemical targeted-re-entry stage, disposal success probability, derelict handling (ADR price or shell population), disposal ops cost | Deorbit was Δv-only. Multi-tonne satellites will not demise, so casualty-risk rules force a controlled re-entry the spacecraft could not previously perform; failed disposals now have a cost or a population consequence. Base wet mass 12.6 → 13.1 t (still closes under 13.5 t). |

### 2.2 Revision 0.2 (tool v2)

Corrections from the first review, all present in the current tool:

- Manufacturing cost regime presets (traditional / mid / constellation / custom) — §15.
- Solar sizing includes eclipse-energy recharge — §6.
- Battery depth of discharge explicit; battery sized on worst-season eclipse — §7.
- Heat-transport mass (kg/kW) added to thermal subsystem — §8.
- Drag Δv derived from density, velocity, Cd, projected area and dry mass — §10.
- Shell capacity materially affects avoidance rate (occupancy-pressure function) — §12.
- Spare racks excluded from token throughput — §5, §17.
- Low-thrust spiral deorbit Δv by default; impulsive option retained — §10.
- Refresh launches use the selected launch pricing model — §14.
- Launch payload is "usable payload to selected orbit" with performance presets — §14.
- Radiation affects failure rate, availability and warns on qualification life — §13.
- Straight-line residual (salvage) credit for replacements that outlive the analysis horizon — §19.
- Dynamic visualization — §3.

---

## 3. Dynamic visual subsystem

The graphic is driven by current model state and never feeds back into the calculation.

### 3.1 Rendering architecture

**Canvas layer:** Earth limb, selected orbital path, altitude/inclination label, congestion field (log-compressed occupancy), configured shell occupancy.

**SVG layer:** spacecraft or platform structure, compute modules, bus/control body, solar arrays, radiators, propulsion/tank indication, inter-satellite links, ground/relay links, subsystem labels.

### 3.2 Visual styles

Semi-realistic concept, technical schematic, or both. Neither view is dimensionally to scale.

### 3.3 View modes

Single satellite (solar/radiator/bus/compute/propellant scale), cluster (formation spacing, ISLs), system overview (constellation scale, shell occupancy, orbital mass, relay link).

### 3.3a Technical engineering sheet (v4.0)

A 1200×760 SVG replacing the former "technical schematic" (which was the concept drawing in flat colours). It carries: dimension lines for solar and radiator tip-to-tip (from area at a 3.6:1 wing aspect) and a schematic stack height; a header line comparing characteristic span with the fairing envelope and formation spacing; six callouts (solar, radiator + heat transport, battery, compute + network + shield, bus/GNC/propulsion, structure + totals) each giving mass, share of wet mass and the sizing chain that produced it; a power/heat flow strip solar → PCU → IT load → heat transport → radiator with the battery charge/discharge branch; and a margin strip with pass/warn/fail chips for mass margin to payload, span vs envelope, span vs spacing, radiator temperature vs coolant limit. Wheel zooms about the cursor, drag pans, double-click fits. The concept view is a picture with a one-line caption pointing to the sheet.

Note the two span figures deliberately differ: characteristic span (44 m base) is the square-equivalent used by the screening flags; wing-based tip-to-tip (≈96 m base) is what a deployed 3.6:1 array would actually measure. The flags are therefore conservative-low; tighten the envelope input if tip-to-tip is the binding constraint.

### 3.3b Pop-out windows (v4.7)

Buttons above the visualization open concept, engineering sheet, cluster, orbital shells or 3D in a separate window (`?popout=<view>&style=<style>`). A pop-out hides all controls and panels except the chosen view, announces itself to the opener, and thereafter mirrors every recalculation of the parent through `window.postMessage` (all input and select values are sent; file inputs and 3D time controls are excluded). Children are followers only — edits are made in the parent. Works from `file://`, a local server and GitHub Pages; the live catalog is loaded per window (a child is told when the parent has one).

### 3.4 Architecture selector

The **Architecture** dropdown (independent satellites / multi-rack modules / persistent platform) changes the drawing only. It is labelled "visualization only" in the tool. Economic architecture is set by:

- racks per independently maneuverable satellite (`rps`),
- replaceable compute modules yes/no (`replace`).

### 3.5 Dynamic visual inputs and fidelity

Satellite count, racks per spacecraft, rack kW, architecture mode, solar area, radiator area, battery mass and nameplate, shielding mass, bus mass, EP and chemical propellant, controlled re-entry stage, altitude, inclination, shell occupancy, formation spacing, ISL hops, ground-link capacity.

Fidelity rules (v3.2): solar and radiator panels are drawn at one shared 12 px²/m², so their relative area is true; panel linear size is clamped at 50–300 px and a "clipped at scale limit" flag appears in the caption when the clamp binds. Bus width ∝ √bus mass, battery block ∝ √battery mass, shield outline thickness ∝ shield mass, tank radius ∝ √propellant. Everything else is schematic. The orbit canvas prints its altitude exaggeration factor relative to Earth radius.

### 3.7 Shells 3D view (v3.6)

Hand-rolled canvas projection (no external library). Each band is six RAAN planes at a representative inclination (43°, 43°, 53°, 52°, 89°, 88°), point density ∝ tracked + announced. The modeled constellation is drawn as the exact number of satellites (v4.1), evenly phased across a configurable number of orbital planes at the configured altitude and inclination and moving at mean motion, over a faint orbit track; above 2,000 satellites every k-th is shown and labelled so. The cluster view (v4.3) is drawn in the Hill frame to scale: lattice per design, satellite footprints at R_sat, R_max circle and the inscribed 2:1 ellipse for the rectangular design, the outermost satellite's relative orbit, and compute→switch / switch↔switch ISLs; above 400 satellites an inner region is drawn at the same R_min, and ISLs are omitted above 150. Each cluster appears in the 3D view as a single point since R_max is ≪ 1% of the orbit radius. The Earth sphere carries Natural Earth 110m land outlines (Douglas-Peucker simplified to 1,019 vertices, public domain) rotating with Earth by GMST, a graticule and N/S pole labels; a UTC time scrubber (1×/60×/600× playback) moves satellites at their mean motion and drives a solar terminator with night-side shading and a Sun marker; coastline/graticule/terminator layers toggle independently (v3.9). Interaction: per-shell and scenario visibility checkboxes (v3.8), an "Orbit paths" toggle drawing continuous tracks per plane (v4.2), drag to rotate, Shift-drag or right/middle-drag to pan, wheel to zoom, click any dot to identify its shell/scenario/moon label. Radial scales: linear with altitude ×4 (Moon off-screen), and log-radial $r=1+1.15\log_{10}(1+h/300\,\text{km})$ placing LEO at ≈1.35–1.7 R and the Moon at ≈4.6 R (Moon drawn at ≈0.27 R true ratio ×2 for legibility, capped so it never rivals the Earth). The earlier 0.55-coefficient map collapsed LEO onto the surface at Moon scale and is replaced.

### 3.6a Live catalog (v4.5)

Opt-in only. "Load live catalog" fetches `https://celestrak.org/NORAD/ELEMENTS/gp.php?GROUP=active&FORMAT=json`; if the browser blocks it (CORS from a `file://` origin, or offline), the status line says so and a file input accepts a manually downloaded copy of the same JSON. Records are compacted to name, epoch, mean motion, eccentricity, inclination, RAAN, argument of perigee and mean anomaly (~80 bytes each; ~1 MB for the active catalog) and cached in `localStorage` for 24 h. Each object's mean altitude is $a-R_E$ with $a=(\mu/n^2)^{1/3}$; objects are binned into the six shells, overwriting `SHELLS[].now` (announced figures are untouched) and re-dating the shells view and Orbit-tab hint. In the 3D view objects are propagated two-body (Newton–Raphson Kepler solve) to the epoch-date + UTC-scrubber time and drawn by operator class (Starlink, OneWeb, Amazon Leo, Guowang/Qianfan, other); click identifies name, altitude, inclination. Propagation is two-body plus J2 secular rates for Ω, ω and M (v5.3); drag and short-period terms are omitted — fine for a same-day picture, not for conjunction work. The modeled constellation is generated as GP-style element sets (RAAN from LTAN and Sun for SSO, small dithers within the cluster arc) and propagated by the same code; it is labelled "(modeled, not real)" and can be exported as GP JSON with NORAD IDs 900000+ and a COMMENT marking the objects synthetic. In LEO mode only near-circular objects (e ≤ 0.05) with apogee below 3,000 km are drawn unless the eccentric toggle is on (v4.9). Objects are placed by instantaneous radius through the active radial mapping (v5.1), so eccentric orbits appear at the correct guide-ring distance rather than scaled by their mean altitude. The live fetch path could not be exercised from the build environment; the file path was tested with synthetic records.

### 3.6 Orbital Shells view

Thirteen bands — seven LEO (300–400, 400–500, 500–600, 600–700, 700–900, 900–1,300, 1,300–2,000 km), then 2,000–8,000, 8,000–15,000 (O3b), 15,000–25,000 (GNSS), 25,000–35,000, GEO belt 35,000–36,500, above GEO — plus an eccentric bucket (e > 0.05) filled only from the live catalog, since mean altitude is meaningless for GTO/Molniya/HEO objects. Non-LEO `now` values are approximate operator totals and carry no announced figures. The Earth-quadrant inset shows LEO bands only, each with tracked active count, announced/authorized additions, and this scenario's satellites overlaid; a ×4-exaggerated Earth quadrant shades each band by tracked + announced. Data live in the `SHELLS` constant with a snapshot date (2026-09-04) and per-row source. Where operator filings are not shell-resolved (Guowang, Qianfan, Amazon Leo Gen2, Starlink Gen2 remainder), the band allocation is an author assumption and labelled so. Announced figures are ceilings, not launch schedules. The Orbit tab shows the band's counts and offers two buttons to load tracked, or tracked + announced, into the population input; presets are not auto-changed.

Snapshot values: 400–500 km ≈ 3,620 tracked (Starlink 43°/480) + 8,300 announced; 500–600 km ≈ 7,570 tracked (Starlink 540–570 + Guowang) + 7,280 announced; 600–700 km ≈ 390 tracked (Amazon Leo; sources conflict, 231 reported July 2026) + 6,950 announced; 700–900 km ≈ 130 (Qianfan) + 7,000; 900–1,300 km ≈ 740 (OneWeb, Guowang) + 13,500. Starlink is lowering ~4,400 satellites from 550 to 480 km during 2026, so the 500–600 and 400–500 bands are in transition.

---

## 4. Base compute reference

| Parameter | Base value | Type |
|---|---:|---|
| Rack TDP | 135 kW | anchor (Lenovo GB300 NVL72) |
| Peak rack power | 155 kW | anchor |
| GPUs | 72 | anchor |
| Rack hardware mass | 1,580 kg | anchor (terrestrial chassis, not space-packaged) |
| Compute cost / rack | $4M | assumption |
| IT overhead beyond TDP | 10% | assumption |
| Network/storage + relay terminal mass / rack | 300 kg | assumption |
| Racks / satellite | 1 | scenario |
| Productive target | 1 MW | scenario |
| Spare installed capacity | 10% | scenario |

---

## 5. Architecture model

$$N_{productive}=\left\lceil\frac{1000\,P_{target}}{P_{rack}}\right\rceil,\qquad
N_{spare}=\left\lceil N_{productive}\,S\right\rceil,\qquad
N_{installed}=N_{productive}+N_{spare}$$

$$N_{sat}=\left\lceil\frac{N_{installed}}{N_{rack/sat}}\right\rceil,\qquad
P_{productive}=\frac{N_{productive}P_{rack}}{1000}$$

Mass and CAPEX use installed racks. Throughput uses productive racks only.

---

## 6. Power model

Per maneuverable unit:

$$P_{load}=N_{rack/sat}\,P_{rack}\,(1+O_{IT})$$

Daylight array requirement, including eclipse-energy recharge:

$$P_{solar}=P_{load}\left[1+\frac{1-F_{sun}}{F_{sun}\,\eta_{charge}}\right]\frac{1}{\eta_{power}}(1+M_{solar})$$

$$M_{solar}=\frac{1000\,P_{solar}}{SP_{solar}},\qquad A_{solar}=\frac{1000\,P_{solar}}{AP_{solar}}$$

$F_{sun}$ is the annual-average sunlight fraction from the orbit preset. For dawn-dusk SSO ($F_{sun}\approx0.97$) the recharge term is ~3%; at 400 km / 51.6° ($F_{sun}\approx0.62$) it is ~68%.

Defaults: $SP_{solar}$ = 85 W/kg, $AP_{solar}$ = 300 W/m², $\eta_{power}$ = 0.92, $\eta_{charge}$ = 0.90, $M_{solar}$ = 20%. Solar area also feeds the drag model (§10).

---

## 7. Battery model

$$T_{orbit}=2\pi\sqrt{\frac{(R_E+h)^3}{GM_E}}$$

$$T_{eclipse,design}=\max\big(T_{orbit}(1-F_{sun}),\ T_{eclipse,worst}\big)$$

where $T_{eclipse,worst}$ is the per-orbit worst-season eclipse. Default basis (v3.9) is computed from geometry; a preset mode retains the old scenario values.

### 7.0 Why 650 km dawn-dusk, and the eclipse-free question (v4.1)

The base orbit is the terminator-riding (LTAN 06:00) sun-synchronous orbit — the minimum-battery family. It is not eclipse-free: at 650 km the shadow half-angle is 65° and the dawn-dusk β falls to ~57–60° around the December solstice, giving ~20 min of eclipse per orbit for a few weeks a year. The sweep panel shows that eclipse-free operation requires the shadow half-angle to drop below the solstice β, which happens at **~1,400 km**: battery falls to reserve-only (~800 kg vs ~1,900 kg), but the orbit sits inside the inner proton belt on polar passes, propagation RTT more than doubles, deorbit Δv rises to ~630 m/s, and launch payload to that altitude is lower. 650 km is therefore a deliberate compromise between battery mass and radiation/latency/disposal, not the battery optimum. The sweep recomputes at each altitude with exact SSO inclination and the current rack load, DoD, reserve and Wh/kg.

### 7.1 Illumination from orbit geometry (v3.9)

Nodal precession from J2: $\dot\Omega=-\tfrac32 J_2 (R_E/a)^2 n\cos i$. The orbit is treated as sun-synchronous when $\dot\Omega$ is within 0.15°/day of 360°/365.24 d; then RAAN relative to the Sun is fixed by LTAN, $\Omega-\alpha_\odot=(LTAN-12)\cdot15°$. Otherwise RAAN is swept uniformly. For each of 73 days across the year, the β-angle is

$$\sin\beta=\cos\delta_\odot\sin i\sin(\Omega-\alpha_\odot)+\sin\delta_\odot\cos i$$

with a ~1° low-precision solar ephemeris. Cylindrical-shadow eclipse fraction for a circular orbit:

$$f_{ecl}=\frac{1}{\pi}\arccos\frac{\sqrt{h^2+2R_Eh}}{(R_E+h)\cos\beta}\quad\text{for }|\beta|<\arcsin\frac{R_E}{R_E+h},\ \text{else }0$$

Annual sunlit fraction $F_{sun}=1-\overline{f_{ecl}}$ and worst-season eclipse $=\max f_{ecl}\cdot T_{orbit}$ replace the preset values and are written back to the inputs. Validation against presets: 400 km/51.6° 0.657/36.0 min (preset 0.62/36); 550/53° 0.687/35.6 (0.63/35); 650 dawn-dusk 0.965/19.1 (0.97/15); 800 SSO LTAN 10.5 0.664/34.3 (0.66/35); 1,200/87° 0.821/34.8 (preset 0.65 was too low). Limits: circular orbits, cylindrical not conical shadow (umbra correction is h·tan 0.264° ≈ 5.5 km at 1,200 km, <0.1% of eclipse duration — deliberately deferred), no penumbra, ~1° solar ephemeris, precession tolerance heuristic for SSO.

$$E_{battery,nameplate}=\frac{P_{load}\,(T_{eclipse,design}+T_{reserve})}{DoD},\qquad
M_{battery}=\frac{1000\,E_{battery}}{SE_{battery}}$$

Defaults: DoD 35%, reserve 15 min, 180 Wh/kg.

A future version should compute illumination from beta angle and season rather than presets (§28).

---

## 8. Thermal model

Net rejection (default, derived):

$$q_{rad}=N_{sides}\,\eta_{fin}\,\big(\varepsilon\sigma T_{rad}^4-q_{env}\big)(1-d)$$

Defaults: $T_{rad}$ = 305 K, $\varepsilon$ = 0.88, $N_{sides}$ = 2, $q_{env}$ = 120 W/m² per side (orbit-average absorbed Earth IR + albedo + solar, scenario), $\eta_{fin}$ = 0.85, $d$ = 10% → $q_{rad}$ ≈ 477 W/m². A manual W/m² mode is retained. The tool warns when $T_{rad}$ exceeds the GPU coolant inlet limit (318 K) minus a 10 K loop approach.

$$A_{rad}=\frac{1000\,P_{load}}{q_{rad}},\qquad
M_{rad}=A_{rad}\,\rho_{rad},\qquad
M_{heat\,transport}=P_{load}\,k_{HT}$$

$\rho_{rad}$ = 8 kg/m² (light end of deployable-radiator studies, range ~5–12), $k_{HT}$ = 3 kg/kW. Because $q\propto T^4$ the radiator temperature is the strongest thermal lever, and it is bounded above by the GPU loop, not by radiator technology. $q_{env}$ is the least-defended thermal input; a view-factor model is future work.

Reference: ISS EATCS rejects ~150 W/m² at ~14 kg/m² with a cold ammonia loop.

---

## 9. Spacecraft mass stack

Per satellite:

$$M_{bus}=M_{bus,base}+M_{bus,rack}(N_{rack/sat}-1)$$

$$M_{pre}=M_{compute}+M_{net}+M_{shield}+M_{bus}+M_{prop\,hw}+M_{solar}+M_{battery}+M_{rad}+M_{HT}+M_{CR}$$

$$M_{struct}=M_{pre}\,f_{struct},\qquad M_{dry}=M_{pre}+M_{struct},\qquad M_{wet}=M_{dry}+M_{propellant}$$

Defaults: bus base 1,500 kg + 250 kg per rack beyond the first (v3.6), propulsion hardware 250 kg, shielding 500 kg/rack, structure/deployment 15%. Solar, radiator, heat transport, battery, compute, network and shield scale with racks-per-satellite; core avionics do not, so bus growth is sub-linear (set the per-rack term to 0 for fully fixed control).

### 9.1 Physical envelope and agility (v3.6)

Characteristic deployed span is the square-equivalent size of combined solar + radiator area as two wings: $L_{char}=2\sqrt{(A_{solar}+A_{rad})/2}$. Area-to-mass $A_{tot}/M_{dry}$ is a slew/flexibility proxy. Screening flags fire when span exceeds the stowed/fairing envelope (default 60 m), span exceeds formation spacing (collision-avoidance envelope violated), or area-to-mass exceeds an agility limit (default 0.25 m²/kg). Flags, not a flexible-body dynamics model. At 4 racks the base design reaches ~89 m span and trips the envelope and spacing flags.

---

## 10. Propulsion

Annual Δv:

$$\Delta v_{year}=\Delta v_{sk}+\Delta v_{drag}+N_{avoid}\,\Delta v_{avoid}$$

Drag from first principles, against dry mass:

$$\Delta v_{drag}=\frac{\tfrac12\,\rho\,v_{circ}^2\,C_d\,A_{drag}}{M_{dry}}\,T_{year},\qquad
A_{drag}=(A_{solar}+A_{rad})\,f_{drag}$$

$f_{drag}$ is seeded by orbit preset: 25% for dawn-dusk SSO (arrays near edge-on to velocity), 50% for inclined LEO. Density is a mean-solar-activity value; solar maximum raises it 3–10× at 400–650 km.

Lifetime:

$$\Delta v_{life}=T_{life}\,\Delta v_{year}+\Delta v_{contingency}+\Delta v_{deorbit}$$

Deorbit to ~200 km perigee, user-selectable:

- low-thrust spiral (default, electric propulsion): $\Delta v=|v_{circ}(200\,\text{km})-v_{circ}(h)|$
- impulsive: $\Delta v=v_{circ}(h)-\sqrt{\mu\left(\tfrac{2}{r_1}-\tfrac{1}{a}\right)}$, $a=(r_1+r_{200})/2$

Propellant:

$$M_{prop}=M_{dry}\left[e^{\Delta v_{life}/(g_0 I_{sp})}-1\right]$$

Default $I_{sp}$ 1,900 s, contingency 100 m/s. Known simplification: drag is computed against dry mass, slightly understating propellant.

### 10.1 End-of-life disposal (v3.1)

Disposal method: **auto** (default), controlled, or uncontrolled. Auto selects controlled re-entry when preliminary dry mass exceeds the demisability threshold (default 800 kg; usual rule of thumb 500–1,000 kg).

Controlled re-entry adds a chemical stage: hardware $M_{CR}$ (150 kg, inside the structure-fraction base) and an impulsive burn from the 200 km circular parking orbit reached by the EP spiral to a target perigee $h_p$ (50 km):

$$\Delta v_{CR}=v_{circ}(200)-\sqrt{\mu\left(\frac{2}{r_{200}}-\frac{1}{a}\right)},\qquad a=\frac{r_{200}+r_{p}}{2}\quad(\approx45\ \text{m/s})$$

$$M_{chem}=M_{dry}\left[e^{\Delta v_{CR}/(g_0 I_{sp,chem})}-1\right],\qquad
M_{EP}=(M_{dry}+M_{chem})\left[e^{\Delta v_{life}/(g_0 I_{sp,EP})}-1\right]$$

The chemical propellant is carried through the EP spiral, so it sits in the EP rocket-equation mass. Default chemical $I_{sp}$ 230 s (monopropellant class).

Disposal events per year:

$$N_{disp/yr}=N_{retire/yr}+N_{fail/yr},\qquad
N_{retire/yr}=\frac{N_{sat}}{\min(T_{refresh},T_{life})}\ \text{(non-serviceable)}\ \text{or}\ \frac{N_{sat}}{T_{life}}\ \text{(serviceable)}$$

$$N_{derelict/yr}=N_{disp/yr}\,(1-p_{disp})$$

Default success is split (v3.7): 95% for planned retirements, 60% for already-failed satellites (a dead bus may lack the propulsion or attitude control to deorbit). Derelicts are handled one of two ways (selector): priced at an ADR cost per object (default $20M, scenario), or accumulated over the analysis horizon and added to shell population before the congestion calculation (§12). Disposal operations are charged per event (default $0.3M).

Warnings: uncontrolled disposal with dry mass above threshold; auto having selected a controlled stage; ≥ 1 expected derelict over the horizon. The 5-year post-mission disposal clock is noted as starting at failure, not design end of life.

---

## 11. Orbit model

Presets: 400 km / 51.6°, 550 km / 53°, 650 km dawn-dusk SSO / 97.5° (base), 800 km SSO / 98.6°, 1,200 km / 87°, custom.

Each preset seeds: altitude, inclination, sunlight fraction, worst-season eclipse, mean atmospheric density, projected drag fraction, non-drag stationkeeping Δv, shell population, shell capacity, baseline avoidance rate.

Only altitude and inclination are direct orbit descriptors; the rest are scenario values. The 650 km preset population of 2,500 predates the Shells data (tracked ≈ 390 in 600–700 km as of 2026-09-04) and is retained until the user loads the tracked value.

---

## 11a. Cluster geometry and ISL fabric (v4.3)

Sources: Google Suncatcher preprint (Nov 2025) — 81 satellites, R_min 100–200 m, R_max 1 km, planar rectangular lattice in the cluster Hill frame, each satellite tracing a 2:1 relative ellipse; Penot & Balakrishnan, "Designing Dense Satellite Clusters for Distributed Space-based Datacenters", AAS 26-754 (May 2026) — optimal planar hexagonal design on a 60°-inclined plane with circular relative orbits and rigid rotation, a 3D stacked-plane design, self-shadowing limits, and a VL2 Clos fabric mapping.

Deployable satellites per cluster: $N\approx a\,(R_{max}/R_{min})^{b}$ with $(a,b)$ = (0.80, 2) rectangular, (3.63, 2) hexagonal, (0.27, 3) 3D. The tool inverts this: $R_{max}=R_{min}(N_{cluster}/a)^{1/b}$. Self-shadowing begins when footprint radius $R_{sat}$ (half the wing tip-to-tip, ≈40 m base) exceeds ≈0.50, 0.19 or 0.03·$R_{min}$ respectively; the base design fits the rectangular lattice at $R_{min}$ ≥ ~100 m and shades itself in the hex and 3D designs at Suncatcher-scale spacing.

ISL fabric: with the Clos option, per cluster of $N_c$ compute satellites and $k$ ISLs per switch, L = 1 (full mesh) if $N_c \le k+1$, L = 2 if $N_c \le k$, else the smallest L with $(k/2)^{L-1} \ge N_c$; switch satellites $=\lceil (2L-3)(k/2)^{L-2}\, N_c/(k/2)^{L-1}\rceil$. Switch satellites carry no racks, a configurable fraction of a compute satellite's wet mass (0.35) and non-compute cost (0.40), and $k/2$ relay terminals; they enter launch mass, ops, disposal events and shell occupancy. Consequences at 1 GW (8,149 compute satellites): one cluster → R_max 90 km, L = 7, 17,928 switches (69% of fleet), $/1M tokens $19.58; 100 clusters → R_max 7 km, L = 4, 50% switches, $13.41. The base 9-satellite case is a full mesh with no switches. Raising $k$ is the main lever; the paper's compute fraction is $k/(k+4L-6)$.

Limitations: switch satellites are scaled copies, not designed; ISL range and pointing budgets are not modelled; multi-cluster fleets are assumed to be independent formations.

## 12. Congestion model

$$O_0=\min\!\left(\frac{N_{existing}}{C_{shell}},0.98\right),\qquad
O_1=\min\!\left(\frac{N_{existing}+N_{sat}}{C_{shell}},0.98\right)$$

$$N_{avoid}=N_{avoid,base}\left[\max\!\left(1,\frac{1-O_0}{1-O_1}\right)\right]^{\alpha}M_{debris}$$

The 0.98 clamp bounds the function at $50^{\alpha}$. Practical capacity is an operational stress threshold, not a count of orbital slots. Warnings fire when avoidance demand exceeds autonomous maneuver capacity or when post-deployment occupancy ≥ 100%. Occupancy bar thresholds: 60% high, 80% severe, 100% exceeded.

---

## 13. Radiation model

Inputs: shielding mass/rack, radiation failure multiplier (1.25), radiation availability loss (0.2%), assumed COTS qualified life (5 yr).

$$P_{fail,eff}=P_{fail,base}\,M_{radiation}$$

Availability is reduced by the configured radiation downtime. The tool warns when mission life exceeds qualification life, and always warns that GB300/HBM is not space-qualified. Google's Suncatcher proton testing of Trillium TPU/HBM to a five-year SSO dose target is a reference, not a qualification of GB300.

---

## 14. Launch model

Presets: Falcon 9 reusable polar/SSO planning case (13.5 t, $74M, ≤2 sats/launch — base), Falcon 9 published max LEO envelope (22.8 t, expendable, ≤3), future reusable heavy (100 t, $100M, ≤10), custom.

**Dedicated mission:**

$$u=\max\!\left(1,\min\!\left(U_{max},\left\lfloor\frac{M_{cap}}{M_{unit}}\right\rfloor\right)\right),\qquad
N_{launch}=\left\lceil\frac{N_{units}}{u}\right\rceil,\qquad
C=N_{launch}\,C_{mission}$$

$U_{max}$ is `lsat` for whole satellites and `modlsat` for compute-module refresh payloads. Warns when $M_{unit}>M_{cap}$.

**Bulk $/kg:** $C=M_{total}\,C_{kg}$, launches $=\lceil M_{total}/M_{cap}\rceil$.

**Rideshare:** $C=M_{total}\,C_{ride}$, one launch per unit; warns when unit mass exceeds port limit.

Refresh payloads use the same selected pricing model. Replacement launches/year are reported as replacement mass ÷ usable payload.

---

## 15. Manufacturing cost model

$$C_{CAPEX}=C_{compute}+C_{bus}+C_{solar}+C_{thermal}+C_{other}+C_{integration}+C_{launch}$$

| Term | Basis |
|---|---|
| $C_{compute}$ | installed racks × $/rack |
| $C_{bus}$ | satellites × $M/sat |
| $C_{solar}$ | solar mass × $/kg |
| $C_{thermal}$ | (radiator + heat transport) mass × $/kg |
| $C_{other}$ | (network + shielding + propulsion hw + battery + structure + propellant) mass × $/kg |
| $C_{integration}$ | satellites × $M/sat |

Cost regime presets:

| Preset | Bus $M | Solar $/kg | Thermal $/kg | Other $/kg | Integration $M |
|---|---:|---:|---:|---:|---:|
| Traditional aerospace (base) | 15 | 20,000 | 10,000 | 15,000 | 5 |
| Industrialized / mid | 5 | 8,000 | 6,000 | 6,000 | 2 |
| Constellation-class | 1.5 | 2,500 | 3,000 | 2,000 | 0.6 |

The constellation preset is illustrative, not a published Starlink unit cost. The tool reports effective non-compute spacecraft manufacturing $/kg and prints active assumptions in the footer.

### 15.1 Learning curve, launch volume and NRE (v3.5)

Each preset's prices refer to a stated cumulative unit $N_{ref}$ (traditional 5, mid 100, constellation 2,000). Unit $k$ of the spacecraft manufacturing stack costs

$$C_{mfg}(k)=C_{mfg,ref}\left(\frac{k}{N_{ref}}\right)^{b},\qquad b=\log_2(LR),\quad LR=0.85\ \text{default}$$

Split-rate mode (v3.7) walks separate curves for structure/mechanical (default 82%), avionics/bus (90%) and integration (88%) against the same cumulative count; single-rate mode applies the default to all. A batch of $q$ units starting at cumulative unit $k_0$ is priced at the continuous mean $\frac{1}{q}\int_{k_0-\tfrac12}^{k_0+q-\tfrac12}(k/N_{ref})^{b}\,dk$. The counter runs through initial deployment, then every whole-spacecraft event (failure replacements each year, scheduled full replacements) in chronological order, so later units are cheaper. Compute hardware and compute-module refresh are not on the curve.

Launches in mission-price mode follow the same form with $b_L=\log_2(1-d)$, $d$ = 5% per doubling of cumulative launches, floored at 60% of list. Bulk and rideshare $/kg modes are unaffected.

Development/qualification NRE (default $300M, scenario) is added once at $t=0$, excluded from the insurance base, and reported per spacecraft built over the horizon. The initial-CAPEX metric includes it; the cost table lists it separately.

Consequence: at 1 MW the curve barely moves (units 1–9 average 1.06× reference) while NRE adds ~$7.6M/sat; at 1 GW traditional prices fall to 0.23× and the two presets land within 15% of each other.

---

## 16. Availability

$$A_{eff}=\left[A_{base}-\frac{N_{avoid}\,T_{maneuver}}{8760}-A_{rad\,loss}\right]\left(1-\frac{N_{fail/yr}\,T_{repl}}{N_{sat}\cdot365.25}\right)$$

The second factor is the expected fraction of capacity awaiting failure replacement (default logistics 120 days). Spares are installed reserve only; hot-spare failover is not modeled.

---

## 17. Inference throughput

$$TPS=TPS_{MW}\,P_{productive}\,U\,A_{eff}\,L$$

$L=\min(1,B_{available}/B_{required})$ is the relay-link throughput factor. Defaults: 2.8M tokens/s/MW, 75% utilization.

---

## 18. Communications and latency

**Scope:** compute satellites have no direct ground link. Connectivity is by optical ISL to a third-party communications constellation whose gateways carry the downlink, under an assumed commercial agreement. No ground-station build is modeled. The optical relay terminal is separate hardware — 60 kg and $0.8M/sat (v3.7) — not folded into the rack. The lease is either flat $M/sat/yr or derived from provisioned Gbit/s at a monthly rate (default $500/Gbit/s/month — third-party optical-terminal access is proprietary and priced).

$$B_{available}=N_{sat}\,B_{sat}\,D_{link},\qquad
B_{required}=\frac{TB_{day/MW}\times8\times10^{12}}{86400\times10^{9}}\,P_{productive}$$

$$T_{space,RTT}=\frac{2\,h\,F_{route}}{c},\qquad
T_{ISL,RTT}=2\,N_{hops}\left(\frac{d_{ISL}}{c}+T_{switch}\right)$$

$$TTFT=T_{proc}+T_{ground}+T_{routing}+T_{space,RTT}+T_{ISL,RTT}$$

Default $N_{hops}=1$ (compute sat → relay sat → gateway).

---

## 19. Lifecycle cost

$$PV=C_{CAPEX,0}+C_{NRE}+C_{ops,yr}\,AF(r,Y)+\sum_{events}\left[\frac{C_{ev}}{(1+r)^{t_{ev}}}-Salvage_{repl}(C_{ev},t_{ev},\Delta)\right]$$

Events are the yearly expected failure replacements ($N_{sat}P_{fail,eff}$ units) and scheduled full replacements ($N_{sat}$ units), each priced by §15.1 at its position on the learning and launch curves; salvage applies to scheduled replacements only.

$$C_{ops,yr}=N_{sat}(C_{ops}+C_{relay})+C_{CAPEX}\,i_{ins}+N_{disp/yr}C_{disp\,ops}+N_{derelict/yr}C_{ADR},\qquad
AF(r,Y)=\frac{1-(1+r)^{-Y}}{r}$$

$$Salvage(C,t,\Delta)=C\,\frac{\max(0,\,t+\Delta-Y)}{\Delta}\,(1+r)^{-Y}$$

**Non-serviceable:** full CAPEX at $t=k\cdot\min(T_{refresh},T_{life})$, $t<Y$.

**Replaceable compute:** module refresh at $t=k\,T_{refresh}$ costing installed racks × $/rack + service $M/sat + module launch (via §14 with `modlsat`); full CAPEX at $t=k\,T_{life}$. A module refresh coinciding with a platform replacement is skipped.

$$C_{annualized}=\frac{PV}{AF(r,Y)},\qquad
C_{1M\,tok}=\frac{C_{annualized}}{Tokens_{year}}10^6,\qquad
C_{GPUh}=\frac{C_{annualized}}{N_{productive}\,N_{GPU/rack}\,8760\,U\,A_{eff}}$$

Defaults: horizon 10 yr, discount 8%, refresh 3 yr, life 5 yr, ops $1M/sat/yr, insurance 2% CAPEX/yr. $C_{ADR}$ applies only in the ADR handling mode (§10.1).

Known quirk: propellant mass is priced at the "other hardware" $/kg (§15). Small in the base case (~2% of dry mass) but wrong in kind; flagged for a later revision.

---

## 20. Failure replacement and logistics

$$N_{fail/yr}=N_{sat}P_{fail,eff}$$

Scheduled replacement mass/year: non-serviceable $=M_{wet,total}/\min(T_{refresh},T_{life})$; serviceable $=M_{infra}/T_{life}+M_{modules}/T_{refresh}$. Expected failed-satellite wet mass is added. Disposal events, derelicts and disposal cost per year are reported alongside (§10.1). Expected-value model, not Monte Carlo.

---

## 21. Terrestrial TCO stack (v3.3)

Same racks, rack cost, IT overhead, spares, utilization, throughput, refresh, salvage rule, horizon and discount rate as §19:

$$C_{fac}=P_{IT,installed}\,c_{fac},\qquad
C_{energy,yr}=P_{IT,installed}\,PUE\cdot8760\,U\,c_{MWh},\qquad
C_{ops,yr}=C_{fac}\,o_{fac}+C_{energy,yr}$$

$$PV_{terr}=C_{compute}+C_{fac}+C_{ops,yr}AF+\sum_{t=k T_{refresh}<Y}\left[\frac{C_{compute}}{(1+r)^t}-Salvage\right]-Salvage(C_{fac},0,T_{fac})$$

$$C_{1M\,tok,terr}=\frac{PV_{terr}/AF}{TPS_{MW}P_{productive}U A_{terr}T_{year}}10^6$$

Defaults: $c_{fac}$ = $12M/MW of IT, $T_{fac}$ = 15 yr, PUE 1.3, $c_{MWh}$ = $80, $o_{fac}$ = 4%/yr, $A_{terr}$ = 99.5% → $0.247/1M tokens. The benchmark selector chooses this or the published $0.123. Excluded: land, grid-connection queue cost, carbon.

## 22a. Sensitivity sweep (v3.3)

One-at-a-time, ±20% of each of 27 numeric inputs (radiator temperature ±10 K because $T^4$ makes a 20% temperature change unphysical), recomputing $/1M tokens with selects fixed. Top 16 by span drawn as a tornado; the note reports combined manufacturing span vs launch span. Runs on every recalculation. Not a variance-based or interaction-aware analysis.

## 21b. Deployment timeline

$$T_{deploy}=T_{dev}+T_{prod}+T_{queue}+\frac{N_{launch}}{Cadence}+\frac{T_{commission}}{30.44}$$

Compared against configurable terrestrial time-to-power (36 months default). Tests the hypothesis that orbital compute may win on time-to-power before it wins on $/MW.

---

## 22. Base scenario reference results (regression)

Tool v3.5 defaults, traditional cost regime (N_ref 5), learning 85%, NRE $300M, launch discount 5%/floor 60%, F9 SSO preset, non-serviceable, 650 km dawn-dusk, auto disposal, derived thermal (477 W/m²), modeled terrestrial benchmark:

| Output | Value |
|---|---:|
| Wet mass / satellite | 12.9 t (9 sats, 115.9 t); bus 1,500 kg at 1 rack/sat |
| Deployed span / area-to-mass | ~44 m / 0.079 m²/kg (within envelope) |
| Break-even (throughput) | ~146M tok/s/MW (52×) for terrestrial parity; no cost input alone reaches it |
| Manual-thermal regression | $12.01 (learning off, NRE 0, disc 0, manual 450 W/m², preset illumination, 180 Wh/kg) |
| Base $/1M tokens (v4.0, geometry illumination, 130 Wh/kg) | $13.93; wet 13.7 t (exceeds 13.5 t preset — warning fires by design); battery 241 kWh / 1,853 kg |
| Radiator area | 311 m² |
| Initial launches | 9 |
| Initial CAPEX incl. NRE / MW | $2.30B |
| Delivered cost / 1M tokens | $12.83 (39 spacecraft over horizon; last unit 0.616×; NRE $7.6M/sat) |
| Scale check | 100 MW $5.98; 1 GW traditional $4.76 (0.23× avg); 1 GW constellation $4.15; 1 MW constellation $9.95 (4.3× avg — preset misapplied below its reference) |
| Learning off, NRE 0, discount 0 | $14.253 (reproduces v3.4) |
| Modeled terrestrial cost / 1M tokens | $0.247; published $0.123 |
| Sensitivity top three (span $) | tokens/s/MW 5.94; utilization; refresh interval |
| Manufacturing (5 inputs) vs launch span | $3.77 vs $1.72 |
| Effective availability | 96.57% |
| TTFT | 133 ms |
| Drag Δv | ~9 m/s/yr |
| Controlled re-entry burn | 45 m/s; ~250 kg chemical propellant |
| Disposal events / derelicts per year | 3.34 / 0.27 |
| Disposal ops + ADR cost / year | $6.3M |

Variants (v3.1 thermal, 450 W/m² manual): base $14.37, 13.06 t; uncontrolled disposal → 12.6 t, $14.12, demisability warning fires; derelicts-to-population mode → $14.29, occupancy 2,512; disposal success 80% → $14.48; 1 GW → 3,022 disposal events/yr, 242 derelicts/yr, $5.7B/yr disposal + ADR, occupancy 88.7%. Pre-disposal v3 values were 12.6 t, $1.98B, $14.03.

Any code change that moves these without an intended model change is a regression.

---

## 23. Output categories

**Financial:** CAPEX/MW, lifecycle TCO/MW, $/1M tokens, $/GPU-hour, spacecraft manufacturing $/kg.  
**Physical:** subsystem mass stack, wet mass, orbital mass, t/MW, solar area and nameplate, radiator area, battery nameplate and design eclipse.  
**Orbit:** period, end-of-life Δv (EP method plus chemical targeted burn when selected), lifetime Δv, drag Δv and projected area, avoidance rate, shell occupancy.  
**Compute:** productive/installed racks, tokens/s, tokens/year.  
**Communications:** link utilization, propagation RTT, TTFT, inter-token time.  
**Lifecycle:** deployment months vs terrestrial, replacement mass/yr, replacement launches/yr, failures/yr, capacity unavailable (applied), disposal events/yr, derelicts/yr, disposal + ADR cost/yr.

---

## 24. Empirical anchors and assumptions

**Anchors:** Lenovo GB300 NVL72 rack power/GPU count; tracked constellation counts (orbitalradar/CelesTrak-derived, McDowell, KeepTrack, Sept 2026) and SpaceX/FCC shell statements for the Shells view; NVIDIA inference benchmark; SpaceX published Falcon 9 max LEO (expendable); observed ~14.4 t Starlink polar payloads; Starlink production statements; ESA population data; NASA deorbit/low-thrust references; Google Suncatcher.

**Scenario assumptions (all editable):** rack cost; shell population and capacity; avoidance baseline/exponent/Δv; solar W/kg and W/m²; radiator W/m² and kg/m²; heat-transport kg/kW; bus/control and propulsion masses; shielding; atmospheric density; worst-season eclipse; drag fraction; all manufacturing $; failure probability; radiation multipliers; usable payload to orbit; units and modules per launch; bulk/rideshare $/kg; relay lease; development schedule; service cost; demisability threshold; controlled re-entry stage mass and Isp; disposal success probability; ADR cost per object; disposal ops cost.

---

## 25. Known limitations

No ephemeris/TLE conjunction analysis, collision probability, debris-flux integration, plane/phasing optimization, flexible-body dynamics, attitude-control sizing, optical pointing simulation, radiation transport, HBM upset-rate modeling, fairing-volume packing, launch loads, re-entry casualty-risk computation (demisability is a mass threshold, not a fragmentation/ablation analysis), robotic-servicing design, or distributed-training simulation. Relay access is assumed available and priced as a flat lease.

---

## 26. Recommended next technical phase

1. ~~Sensitivity view~~ — done v3.3 (§22a). Next: interaction-aware (two-at-a-time) or Monte Carlo.
2. ~~Terrestrial TCO stack~~ — done v3.3 (§21). Next: grid-queue cost and carbon.
3. ~~Break-even solver~~ — done v3.7. Bisection on a chosen input (launch price, $/kg, bus, compute, utilization, throughput) to a terrestrial-parity goal (1×/2×/5×); reports the required value or that the gap is structural. In the base case no single input reaches parity — throughput must rise ~52× — which is itself the finding.
4. ~~Thermal physics~~ — partly done v3.3 (§8). Next: view-factor and beta-angle model for $q_{env}$; GPU throughput derating vs coolant temperature.
5. **Radiation → throughput** — SEU rate by orbit, checkpoint/restart cost, so shielding trades against availability.
6. ~~Fleet learning curve~~ — done v3.5 (§15.1). Next: separate curves per subsystem; launch curve tied to a vehicle roadmap rather than a flat % per doubling.
7. ~~Illumination from geometry~~ — done v3.9 (§7.1). Next: conical shadow with penumbra, eccentric orbits.
8. **Orbital traffic cells** — altitude × inclination × plane × phase with debris flux and conjunction rates.
9. **Launch vehicle curves** — payload vs altitude/inclination/recovery mode, fairing volume.
10. **Stochastic reliability** — Monte Carlo on launch, satellite and propulsion failures, replacement queues.
11. ~~In-file unit tests~~ — done v3.7. `?test` or a button runs 8 checks (ISS period, circular velocity, impulsive and spiral deorbit Δv, rocket equation, annuity factor, learning multiplier, base-case regression); 8/8 pass.
12. **Training mode (separate model)** — collective-communication topology, Tbit/s east-west bandwidth, synchronization, checkpointing, straggler cost, utilization loss vs terrestrial fabrics.

---

## 27. Primary questions the model should ultimately answer

1. Which orbital architecture minimizes lifecycle cost/productive MW?
2. At what launch price does inference reach terrestrial parity?
3. How strongly does manufacturing regime dominate launch economics?
4. At what scale does shell congestion materially reduce utilization?
5. Which orbit gives the best combined power, drag, disposal, congestion and latency result?
6. Does serviceable compute change the answer enough to justify robotic infrastructure?
7. What annual launch cadence sustains 1 MW, 100 MW and 1 GW?
8. How much does the battery cycle requirement penalize non-dawn-dusk LEO?
9. What radiation reliability is required for COTS HBM to be economically viable?
10. Can orbital compute win on deployment time while losing on direct $/MW?
11. What manufacturing $/kg must be achieved before launch becomes the dominant spacecraft cost?
12. How does orbital capacity change when spacecraft cross-section grows to multi-thousand-m² structures?

---

## 28. Source anchors

- Lenovo GB300 NVL72: https://lenovopress.lenovo.com/lp2357-lenovo-nvidia-gb300-nvl72-rack-scale-ai
- NVIDIA inference performance: https://developer.nvidia.com/deep-learning-performance-training-inference/ai-inference
- SpaceX Falcon capabilities/pricing: https://www.spacex.com/media/Capabilities%26Services.pdf
- Starlink production report: https://www.starlink.com/public-files/starlinkProgressReport_2025.pdf
- ESA orbital statistics: https://sdup.esoc.esa.int/discosweb/statistics/
- NASA deorbit systems: https://www.nasa.gov/smallsat-institute/sst-soa/deorbit-systems/
- NASA low-thrust reference: https://history.arc.nasa.gov/hist_pdfs/nasa_sp428.pdf
- Google Suncatcher: https://research.google/blog/exploring-a-space-based-scalable-ai-infrastructure-system-design/
- Google Suncatcher paper: https://goo.gle/project-suncatcher-paper

---

## 28a. Hosting and data pipeline (v4.6)

The tool is a single static file and runs from disk. For live catalog data it needs a same-origin `gp.json` or a CORS-permissive source. The repository provides:

- `scripts/compact_gp.py` — fetches CelesTrak `GROUP=active` GP JSON, compacts each object to `[name, epoch_ms, n_rad_s, e, i, Ω, ω, M0, class]` (~80 B; ~1 MB total), writes `{fetched, source, count, recs}`; if the fetch fails and a previous bundle path is given, it republishes that bundle and exits 0.
- `.github/workflows/pages.yml` — on push, daily cron (03:17 UTC) and manual dispatch: recovers the previously published `gp.json` from the live site as fallback, runs the script, assembles `site/` (`index.html`, spec, README, `gp.json`, `.nojekyll`) and deploys with `actions/deploy-pages`. No data is committed to the repository.
- Load order in the page: `./gp.json` → CelesTrak direct → file loader → embedded snapshot; the status line reports which source is in force.

## 29. Interpretation rule

The model should never be quoted as producing one universal number for "the cost of a data center in space."

> Under these visible assumptions, this architecture in this orbit requires this mass, this launch and replacement burden, this lifecycle cost, and produces this amount of useful compute.

The value of the tool is not eliminating uncertainty but making it inspectable and debatable.

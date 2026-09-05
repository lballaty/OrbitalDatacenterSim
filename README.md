# Orbital AI Data Center Economics Model

A single-file, zero-dependency browser tool that asks a narrow question: **given a specific compute rack, orbit, spacecraft design, launch system, manufacturing regime, lifecycle and traffic environment, what physical system is required and what does it cost per productive MW and per delivered inference token?**

It is deliberately bottom-up. Orbital mechanics that can be calculated are calculated (period, eclipse from β-angle geometry, drag, J2 precession, deorbit Δv, propellant). Everything that cannot yet be defended from public engineering data is an explicit, labelled input. The point is not to produce one number for "data centers in space" but to make every assumption inspectable and changeable without touching code.

**Live tool:** `https://<owner>.github.io/<repo>/`
**Specification:** [`orbital_ai_datacenter_model_specification.md`](orbital_ai_datacenter_model_specification.md) — every formula, default, source and known limitation.

---

## What it models

| Area | What is derived | What you set |
|---|---|---|
| Architecture | racks → satellites, spares, Clos switch satellites | target MW, rack TDP/mass/cost, racks per satellite |
| Orbit | period, sunlit fraction, worst eclipse, nodal precession, drag Δv, deorbit Δv | altitude, inclination, LTAN, density, presets 400–1,200 km |
| Power & thermal | solar kW/area/mass incl. eclipse recharge; radiator area from εσT⁴; battery from eclipse or kWh/rack | efficiencies, W/kg, radiator T, ε, DoD, Wh/kg |
| Spacecraft | full mass stack, structure fraction, EP + chemical propellant, characteristic span, area-to-mass | bus base + per-rack, shielding, Isp, disposal method |
| Cluster | R_max from Suncatcher / hex / 3D packing, self-shadow check, Clos layers & switch count | design, R_min, clusters, k ISLs per switch |
| Congestion | avoidance rate vs shell occupancy, tracked + announced per band | population, capacity, exponent |
| Launch | launches, cost with volume discount, payload warning | vehicle preset, price, payload, units per launch |
| Cost | learning curve by cumulative unit, NRE, refresh & failure replacement, salvage, disposal & ADR | cost regime preset, learning rate, $/kg, discount, horizon |
| Output | CAPEX/MW, TCO/MW, $/1M tokens vs a like-for-like terrestrial TCO stack, $/GPU-hour, TTFT | throughput, utilization, availability, terrestrial facility $/MW, PUE, $/MWh |

Plus: a ±20% sensitivity tornado, a dawn-dusk altitude sweep, a break-even solver, an engineering-sheet drawing with dimensions and margins, a to-scale Hill-frame cluster view, a shells occupancy view, and a rotatable 3D Earth with terminator, time scrubber and (optionally) the live satellite catalog.

## Quick start

1. Open `index.html` in any modern browser. No install, no network required.
2. The default scenario is one 135 kW GB300-class rack per satellite, 1 MW productive, 650 km dawn-dusk sun-synchronous orbit, traditional-aerospace cost regime. Change anything; everything recalculates.
3. Read the **Model cautions** box first — it tells you which constraints the current design violates.
4. **Run self-tests** (button, or append `?test` to the URL) checks the physics functions and a regression anchor. All 8 should pass.
5. Use the **⧉ Open in its own window** buttons above the visualization to put the concept drawing, engineering sheet, cluster view, shells view or 3D globe on separate screens; they follow the main window's scenario live. The **Specification** button in the top bar opens the full spec in a modal or its own window (on GitHub Pages it loads automatically; from disk, pick the `.md` file when prompted).

## Live satellite catalog

The shells and 3D views ship with an embedded population snapshot (dated). To use real tracked objects:

- **On the GitHub Pages site** the daily workflow fetches CelesTrak's active-object catalog server-side, compacts it to ~1 MB, and publishes it as `gp.json` beside the HTML. Click **Load live catalog** — same origin, no CORS.
- **Locally** the button tries `./gp.json`, then CelesTrak directly (works from `http://localhost`, usually not from `file://`), then offers a file loader: download `https://celestrak.org/NORAD/ELEMENTS/gp.php?GROUP=active&FORMAT=json` and drop it in.
- Loaded catalogs are cached in the browser for 24 h. **Clear cache** resets to the embedded snapshot.

Objects are propagated two-body (Keplerian). That is fine for a same-day picture and for binning by altitude; it is not a conjunction tool.

## Hosting your own copy

The repo is set up for GitHub Pages via Actions — no committed data, no server:

1. Fork or push this repo. In **Settings → Pages**, set *Source* to **GitHub Actions**.
2. Push to `main` (or run the workflow manually). `.github/workflows/pages.yml` fetches CelesTrak with `scripts/compact_gp.py`, assembles `site/` (tool + spec + `gp.json`) and deploys it.
3. The schedule refreshes the catalog daily at 03:17 UTC. If CelesTrak is unreachable the previously published `gp.json` is kept, so the site never regresses to no data.

Nothing about the tool itself needs GitHub: the HTML runs from any static host or from disk.

## Reading the results honestly

- The headline $/1M tokens is dominated by three unanchored inputs: spacecraft manufacturing $/kg, launch price and NRE. The cost-regime badge and the sensitivity tornado exist so nobody mistakes a preset for a measurement.
- The **break-even solver** will usually report "no parity in range" for any single cost input. That is the finding, not a bug: the gap is structural.
- The base 650 km dawn-dusk orbit is *not* eclipse-free (≈20 min around the December solstice). Eclipse-free needs ~1,400 km, inside the proton belt. The altitude sweep shows the trade.
- Clos switch satellites can be a large fraction of a GW-scale fleet; cluster count and ISLs-per-switch are the levers.
- Announced/authorized constellation figures are ceilings, not launch schedules. Chinese totals are allocated to altitude bands by assumption and labelled so.

## Repository layout

```
index.html                                   the tool (single file)
orbital_ai_datacenter_model_specification.md formulas, defaults, sources, limitations, revision history
scripts/compact_gp.py                        CelesTrak fetch + compaction (stdlib only)
.github/workflows/pages.yml                  build + deploy to Pages, daily catalog refresh
```

## Versioning

The tool's version is in its `<title>` and in the *Model integrity notes* panel; the specification carries a matching revision table. File names never change between versions so links and re-uploads stay stable.

## Sources

Lenovo GB300 NVL72 · NVIDIA inference benchmarks · SpaceX Falcon 9 capabilities · Starlink progress report · ESA DISCOS statistics · NASA deorbit references · Google Project Suncatcher preprint · Penot & Balakrishnan, *Designing Dense Satellite Clusters for Distributed Space-based Datacenters*, AAS 26-754 (2026) · Natural Earth 110m land (public domain) · CelesTrak GP data. Full list with URLs in the specification.

## Licence

Choose one before publishing (MIT is the usual fit for a single-file tool). Natural Earth data is public domain; CelesTrak data is subject to their terms.


## Contributing

Issues, comments, and pull requests are all welcome, but `main` stays controlled: only the maintainer ([@lballaty](https://github.com/lballaty)) merges to it, so the published tool and its history stay clean.

**To report or discuss:** open an [issue](../../issues) or comment on an existing one. No fork needed to flag a bug, a wrong assumption, a missing source, or a feature idea.

**To propose a change:**

1. Fork the repo to your own account.
2. Branch in your fork (`git checkout -b my-change`).
3. Keep it single-file and dependency-free, and keep file names stable (see Versioning).
4. Run the self-tests (**Run self-tests** button, or append `?test` to the URL). All 8 should pass.
5. Open a pull request against `main`. Every PR gets read; expect questions on any input that changes a default or a labelled assumption.


## AI assistance

Claude, ChatGPT, and Gemini were used during development and testing of this project.

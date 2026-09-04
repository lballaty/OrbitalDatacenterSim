# Orbital Datacenter Sim

A standalone, dependency-free browser simulation exploring the economics and physics
of orbital AI data centers — one independently maneuverable 135 kW / 72-GPU
GB300-class rack per satellite, inference workloads only, ground connectivity via
leased relay capacity on an existing communications constellation.

> Fun project looking at orbital datacenters — the moon is next.

## Contents

| File | Description |
|------|-------------|
| [`index.html`](index.html) | The interactive modeling tool. A single self-contained HTML file with no external dependencies — open it in any modern browser. |
| [`orbital_ai_datacenter_model_specification.md`](orbital_ai_datacenter_model_specification.md) | The full model specification: purpose, orbital mechanics, thermal physics, TCO stack, sensitivity sweeps, and revision history. |

## Running it

No build step, no server, no dependencies. Either:

- Open `index.html` directly in a browser (double-click, or `File → Open`), or
- Visit the GitHub Pages URL once Pages is enabled for this repository.

## About the model

The model is deliberately bottom-up. Orbital mechanics that can be calculated are
calculated; quantities that cannot yet be defended from public engineering data are
exposed as labelled scenario assumptions. It is designed to survive disagreement —
a reader should be able to change a disputed assumption without changing the code.

See the [specification](orbital_ai_datacenter_model_specification.md) for the full
detail.

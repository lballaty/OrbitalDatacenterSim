#!/usr/bin/env python3
"""Fetch CelesTrak's active-object GP catalog and write a compact bundle for the tool.

Output format (read by Space-Datacenter-Modeling-Tool.html):
{
  "fetched": ISO-8601 UTC timestamp,
  "source":  "CelesTrak GP GROUP=active",
  "count":   N,
  "recs":    [[name, epoch_ms, n_rad_s, e, i_rad, raan_rad, argp_rad, M0_rad, cls], ...]
}
About 80 bytes per object (~1 MB for the full active catalog) versus ~5 MB raw.
Stdlib only. Exit code 0 on success; 1 if the fetch fails and no fallback file exists.
"""
import json, math, sys, time, urllib.request, pathlib, datetime as dt

URL = "https://celestrak.org/NORAD/ELEMENTS/gp.php?GROUP=active&FORMAT=json"
OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "site/gp.json")
FALLBACK = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else None
RAD = math.pi / 180.0

def classify(name: str) -> str:
    u = (name or "").upper()
    if u.startswith("STARLINK"): return "starlink"
    if u.startswith("ONEWEB"): return "oneweb"
    if u.startswith(("KUIPER", "AMAZON", "LEO-")): return "kuiper"
    if u.startswith(("QIANFAN", "HULIANWANG", "SATNET", "GUOWANG")): return "china"
    return "other"

def compact(records):
    out = []
    for o in records:
        try:
            n = float(o["MEAN_MOTION"])
            if n <= 0: continue
            ep = dt.datetime.fromisoformat(o["EPOCH"].replace("Z", "")).replace(tzinfo=dt.timezone.utc)
            out.append([
                o.get("OBJECT_NAME", ""),
                int(ep.timestamp() * 1000),
                n * 2 * math.pi / 86400.0,
                float(o.get("ECCENTRICITY", 0) or 0),
                float(o.get("INCLINATION", 0) or 0) * RAD,
                float(o.get("RA_OF_ASC_NODE", 0) or 0) * RAD,
                float(o.get("ARG_OF_PERICENTER", 0) or 0) * RAD,
                float(o.get("MEAN_ANOMALY", 0) or 0) * RAD,
                classify(o.get("OBJECT_NAME", "")),
            ])
        except (KeyError, ValueError, TypeError):
            continue
    return out

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(URL, headers={"User-Agent": "orbital-ai-dc-model/1.0 (github actions)"})
        with urllib.request.urlopen(req, timeout=120) as r:
            raw = json.load(r)
        recs = compact(raw)
        if len(recs) < 1000:
            raise RuntimeError(f"suspiciously small catalog: {len(recs)} records")
        bundle = {
            "fetched": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "source": "CelesTrak GP GROUP=active",
            "count": len(recs),
            "recs": recs,
        }
        OUT.write_text(json.dumps(bundle, separators=(",", ":")))
        print(f"wrote {OUT} with {len(recs)} objects ({OUT.stat().st_size/1e6:.2f} MB)")
        return 0
    except Exception as e:  # noqa: BLE001
        print(f"fetch failed: {e}", file=sys.stderr)
        if FALLBACK and FALLBACK.exists():
            OUT.write_text(FALLBACK.read_text())
            print(f"kept previous bundle from {FALLBACK}")
            return 0
        return 1

if __name__ == "__main__":
    sys.exit(main())

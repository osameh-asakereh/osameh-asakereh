#!/usr/bin/env python3
"""
Generate a sleek animated SVG "Mission Control" HUD for your GitHub profile README.

Outputs:
  - assets/hud.svg

No extra secrets needed:
  - uses the built-in GitHub Actions GITHUB_TOKEN
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from collections import Counter

import requests


def gh_get(url: str, headers: dict, timeout: int = 30):
    r = requests.get(url, headers=headers, timeout=timeout)
    if r.status_code >= 400:
        raise RuntimeError(f"GitHub API error {r.status_code} for {url}: {r.text[:200]}")
    return r.json()


def clamp(n: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, n))


def pct(x: float) -> str:
    return f"{x:.0f}%"


def main() -> None:
    user = (os.environ.get("GH_USER", "") or "osameh-asakereh").strip()
    token = (os.environ.get("GITHUB_TOKEN", "") or "").strip()

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    # --- Theme knobs (tweak freely) ---
    title = f"{user} // Mission Control"
    subtitle = "Telemetry + Repo Signals"
    bg_opacity = 0.92
    panel_radius = 22

    u = gh_get(f"https://api.github.com/users/{user}", headers)
    repos = gh_get(f"https://api.github.com/users/{user}/repos?per_page=100&sort=pushed", headers)

    followers = int(u.get("followers", 0))
    public_repos = int(u.get("public_repos", 0))

    total_stars = 0
    langs = Counter()

    repos_list = repos if isinstance(repos, list) else []
    top_for_langs = repos_list[:12]

    for r in repos_list:
        total_stars += int(r.get("stargazers_count", 0))

    for r in top_for_langs:
        lang_url = r.get("languages_url")
        if not lang_url:
            continue
        try:
            d = gh_get(lang_url, headers)
        except Exception:
            continue
        for k, v in (d or {}).items():
            langs[k] += int(v)

    top_langs = langs.most_common(5)
    total_lang_bytes = sum(langs.values()) or 1
    lang_lines = [(name, bytes_ / total_lang_bytes) for name, bytes_ in top_langs]

    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Spark bars: stars on most recently pushed repos
    latest = repos_list[:16]
    stars = [int(r.get("stargazers_count", 0)) for r in latest]
    max_star = max(stars) if stars else 1
    bars = []
    for s in stars[:16]:
        h = 6 + int(28 * (s / max_star if max_star else 0))
        bars.append(h)

    # Layout
    W, H = 1100, 260
    pad = 18
    radar_cx, radar_cy = 150, 130
    radar_r = 72

    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{title}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0b0f14"/>
      <stop offset="100%" stop-color="#05070a"/>
    </linearGradient>

    <linearGradient id="sheen" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.00"/>
      <stop offset="50%" stop-color="#ffffff" stop-opacity="0.06"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0.00"/>
    </linearGradient>

    <filter id="softGlow">
      <feGaussianBlur stdDeviation="2.6" result="b"/>
      <feMerge>
        <feMergeNode in="b"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <clipPath id="clip">
      <rect x="{pad}" y="{pad}" width="{W-2*pad}" height="{H-2*pad}" rx="{panel_radius}" />
    </clipPath>
  </defs>

  <rect x="{pad}" y="{pad}" width="{W-2*pad}" height="{H-2*pad}" rx="{panel_radius}" fill="url(#bg)" opacity="{bg_opacity}"/>

  <!-- subtle moving sheen -->
  <g clip-path="url(#clip)" opacity="0.55">
    <rect x="-250" y="{pad}" width="240" height="{H-2*pad}" fill="url(#sheen)">
      <animate attributeName="x" values="-250;{W};-250" dur="6.5s" repeatCount="indefinite"/>
    </rect>
  </g>

  <!-- Radar -->
  <g transform="translate({radar_cx} {radar_cy})" filter="url(#softGlow)">
    <circle r="{radar_r}" fill="none" stroke="#ffffff" stroke-opacity="0.16" stroke-width="2"/>
    <circle r="{int(radar_r*0.66)}" fill="none" stroke="#ffffff" stroke-opacity="0.10" stroke-width="2"/>
    <circle r="{int(radar_r*0.33)}" fill="none" stroke="#ffffff" stroke-opacity="0.08" stroke-width="2"/>
    <line x1="-{radar_r}" y1="0" x2="{radar_r}" y2="0" stroke="#ffffff" stroke-opacity="0.07" stroke-width="2"/>
    <line x1="0" y1="-{radar_r}" x2="0" y2="{radar_r}" stroke="#ffffff" stroke-opacity="0.07" stroke-width="2"/>

    <!-- sweep wedge -->
    <path d="M0,0 L0,-{radar_r} A{radar_r},{radar_r} 0 0 1 {int(radar_r*0.86)},{int(-radar_r*0.50)} Z" fill="#ffffff" fill-opacity="0.11">
      <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="4.0s" repeatCount="indefinite"/>
    </path>

    <!-- blip -->
    <circle cx="{int(radar_r*0.45)}" cy="{int(-radar_r*0.15)}" r="3" fill="#ffffff" fill-opacity="0.65">
      <animate attributeName="r" values="2.5;4.2;2.5" dur="1.4s" repeatCount="indefinite"/>
      <animate attributeName="fill-opacity" values="0.35;0.85;0.35" dur="1.4s" repeatCount="indefinite"/>
    </circle>
  </g>

  <!-- Title / subtitle -->
  <text x="260" y="74" fill="#ffffff" fill-opacity="0.92"
        font-family="ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto"
        font-size="28" font-weight="700">{title}</text>

  <text x="260" y="104" fill="#ffffff" fill-opacity="0.60"
        font-family="ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto"
        font-size="15">{subtitle}</text>

  <!-- Stats row -->
  <g font-family="ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto" font-size="15" fill="#ffffff" fill-opacity="0.78">
    <text x="260" y="142">Followers: <tspan font-weight="700">{followers}</tspan></text>
    <text x="430" y="142">Public repos: <tspan font-weight="700">{public_repos}</tspan></text>
    <text x="610" y="142">Stars: <tspan font-weight="700">{total_stars}</tspan></text>
  </g>

  <!-- Spark bars (latest repo stars) -->
  <g transform="translate(260 160)">
    <text x="0" y="0" fill="#ffffff" fill-opacity="0.45"
          font-family="ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto"
          font-size="12">Signal (stars on recently pushed repos)</text>
    <g transform="translate(0 10)" opacity="0.75">
"""

    x = 0
    for h in bars:
        svg += f'      <rect x="{x}" y="{40-h}" width="10" height="{h}" rx="3" fill="#ffffff" fill-opacity="0.30"/>
'
        x += 14

    svg += f"""    </g>
    <!-- scanning line -->
    <rect x="0" y="52" width="580" height="2" fill="#ffffff" fill-opacity="0.10">
      <animate attributeName="x" values="0;520;0" dur="3.2s" repeatCount="indefinite"/>
    </rect>
  </g>

  <!-- Language mix -->
  <g transform="translate(860 70)">
    <text x="0" y="0" fill="#ffffff" fill-opacity="0.55"
          font-family="ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto"
          font-size="12" text-anchor="end">Languages (recent repos)</text>
"""

    y = 16
    for name, share in lang_lines:
        w = int(clamp(120 * share, 20, 120))
        svg += f"""    <g transform="translate(0 {y})">
      <rect x="{-w}" y="0" width="{w}" height="12" rx="6" fill="#ffffff" fill-opacity="0.22"/>
      <text x="-130" y="10" fill="#ffffff" fill-opacity="0.72"
            font-family="ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto"
            font-size="12" text-anchor="end">{name}</text>
      <text x="0" y="10" fill="#ffffff" fill-opacity="0.62"
            font-family="ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto"
            font-size="12" text-anchor="end">{pct(share*100)}</text>
    </g>
"""
        y += 18

    if not lang_lines:
        svg += """    <text x="0" y="22" fill="#ffffff" fill-opacity="0.55"
          font-family="ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto"
          font-size="12" text-anchor="end">(no language data)</text>
"""

    svg += f"""  </g>

  <!-- Footer -->
  <text x="{W-pad}" y="{H-pad-10}" fill="#ffffff" fill-opacity="0.35"
        font-family="ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto"
        font-size="12" text-anchor="end">Updated: {updated}</text>
</svg>
"""

    os.makedirs("assets", exist_ok=True)
    with open("assets/hud.svg", "w", encoding="utf-8") as f:
        f.write(svg)


if __name__ == "__main__":
    main()

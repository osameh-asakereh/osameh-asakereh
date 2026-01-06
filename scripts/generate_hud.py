# scripts/generate_hud.py
import os, requests
from datetime import datetime, timezone

USER = os.environ.get("GH_USER")
TOKEN = os.environ.get("GITHUB_TOKEN")

headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28",
}

u = requests.get(f"https://api.github.com/users/{USER}", headers=headers, timeout=30).json()
repos = requests.get(f"https://api.github.com/users/{USER}/repos?per_page=100&sort=pushed", headers=headers, timeout=30).json()

followers = u.get("followers", 0)
public_repos = u.get("public_repos", 0)

# quick-and-dirty “total stars”
total_stars = 0
for r in repos if isinstance(repos, list) else []:
    total_stars += int(r.get("stargazers_count", 0))

stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="900" height="220" viewBox="0 0 900 220" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%"/>
      <stop offset="100%"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="3" result="b"/>
      <feMerge>
        <feMergeNode in="b"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <rect x="12" y="12" width="876" height="196" rx="18" fill="url(#g)" opacity="0.9"/>

  <!-- Radar ring -->
  <g transform="translate(140 110)" filter="url(#glow)">
    <circle r="62" fill="none" stroke="white" opacity="0.18" stroke-width="2"/>
    <circle r="44" fill="none" stroke="white" opacity="0.12" stroke-width="2"/>
    <circle r="26" fill="none" stroke="white" opacity="0.10" stroke-width="2"/>

    <path d="M0,0 L0,-62 A62,62 0 0 1 54,-31 Z" fill="white" opacity="0.10">
      <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="4s" repeatCount="indefinite"/>
    </path>
    <circle r="2.5" fill="white" opacity="0.7"/>
  </g>

  <!-- Text -->
  <text x="250" y="70" font-size="26" fill="white" opacity="0.92" font-family="ui-sans-serif, system-ui">
    {USER} // Mission Control
  </text>

  <text x="250" y="110" font-size="16" fill="white" opacity="0.75" font-family="ui-sans-serif, system-ui">
    Followers: {followers}   •   Public repos: {public_repos}   •   Stars: {total_stars}
  </text>

  <text x="250" y="145" font-size="13" fill="white" opacity="0.55" font-family="ui-sans-serif, system-ui">
    Updated: {stamp}
  </text>

  <!-- tiny scanning line -->
  <rect x="250" y="160" width="600" height="2" fill="white" opacity="0.18">
    <animate attributeName="x" values="250;820;250" dur="3.2s" repeatCount="indefinite"/>
  </rect>
</svg>
"""

os.makedirs("assets", exist_ok=True)
with open("assets/hud.svg", "w", encoding="utf-8") as f:
    f.write(svg)

## How to use this template

1) Create a **public** repo named exactly:
   `osameh-asakereh/osameh-asakereh`

2) Copy everything from this folder into that repo.

3) Put your GIF into:
   `assets/shabah-gif3.gif`

4) Enable GitHub Actions (repo → Actions tab → enable workflows if prompted).

5) Wait for the scheduled run or trigger it:
   Actions → Generate HUD → Run workflow

### Customize
Open `scripts/generate_hud.py` and change:
- title/subtitle text
- layout constants
- gradients and opacities

### Notes
- GitHub READMEs can't run JavaScript. This is why it's a generated animated SVG.
- The workflow uses `secrets.GITHUB_TOKEN` (built-in). No extra secrets needed.

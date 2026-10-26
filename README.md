# evoremake

An HTML/browser remake of **E.V.O.: Search for Eden** (SNES, 1992): a side-scrolling action game where you
eat, earn EVO points and evolve your creature part by part through five eras of life.
Art direction: chibi and cutesy, with original assets only (no ripped sprites or music).

**Status:** planning + art pipeline prototype. First milestone is a vertical slice: one sea level (era 1, fish).

| Where | What |
|---|---|
| `STATUS.md` | the truth about the current state: what runs, what was verified, next steps |
| `docs/PLAN.md` | design decisions (decided vs proposed), slice scope, risks |
| `docs/TASKS.md` | task checklists with effort levels (slice first, then full game) |
| `docs/ART_STYLE.md` | style bible, Gemini prompt templates, QA checklist, lessons learned |
| `docs/RESEARCH.md` | notes on the original game, with sources to verify |
| `docs/WORKFLOW.md` | how we work with Claude here (zip -> commit -> Sync now) |
| `art/` | raw generator output, style references, extracted rig parts |
| `tools/` | Python scripts that turn raw art into rig parts |

## Build the game assets from the art
```
pip install -r requirements.txt
python tools/build_assets.py     # art/parts.json + art/raw/*  ->  assets/fish/ (atlas, tint atlas, rig.json); exits 1 on a contract failure
python tools/preview_skins.py    # renders docs/skin_preview.png from the built atlas (heads x skins x tail swing)
python tools/selftest.py         # 22 checks, including mutation checks
```

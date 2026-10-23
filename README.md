# evoremake

An HTML/browser remake of **E.V.O.: Search for Eden** (SNES, 1992): a side-scrolling action game where you
eat, earn EVO points and evolve your creature part by part through five eras of life.
Art direction: chibi and cutesy, with original assets only (no ripped sprites or music).

**Status:** planning + art pipeline prototype. First milestone is a vertical slice: one sea level (era 1, fish).

| Where | What |
|---|---|
| `docs/PLAN.md` | design decisions (decided vs proposed), slice scope, risks |
| `docs/TASKS.md` | task checklists with effort levels (slice first, then full game) |
| `docs/ART_STYLE.md` | style bible, Gemini prompt templates, QA checklist, lessons learned |
| `docs/RESEARCH.md` | notes on the original game, with sources to verify |
| `docs/WORKFLOW.md` | how we work with Claude here (zip -> commit -> Sync now) |
| `art/` | raw generator output, style references, extracted rig parts |
| `tools/` | Python scripts that turn raw art into rig parts |

## Rebuild the rig parts
```
pip install -r requirements.txt
python tools/extract_parts.py   # art/raw/*  ->  art/rig/parts/*.png + art/rig/rig.json
python tools/preview_rig.py     # art/rig/rig_preview.png
```

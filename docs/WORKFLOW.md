# How we work with Claude on this repo (free tier, no Claude Code)

Claude reads this repo through the **GitHub integration of the Claude Project** and cannot push to it.
1. In the Project: knowledge **+** -> **GitHub** -> pick this repo (grant the Claude GitHub App access to *only this repo*).
2. Claude builds files in chat and hands over a zip.
3. Unzip into the repo, commit and push.
4. In the Project, click **Sync now**. Start a new chat in the Project if the new files do not show up.

Keep Project knowledge lean (it has to fit in Claude's context window): use **Configure files** to exclude
`art/raw/`, `art/style/` and big PNGs; keep code, `docs/`, `art/rig/rig.json`.
If the integration misbehaves, a public repo also works with Claude's web tools.

## Session routine
- **Start:** read `STATUS.md` (then `docs/PLAN.md` and `docs/TASKS.md` if needed); run the tools/tests if the last session touched them.
- **During:** deliver a zip early after the first real progress, then refresh it at the end (chat sessions can be cut off).
- **End:** rewrite `STATUS.md` so it is true; list any files the human must overwrite or delete.
- **Honesty rule:** never mark something as working unless it was run; keep "verified" and "not verified" separate.

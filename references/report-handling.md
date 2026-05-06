# Paperyy and AIGC Report Handling

## User Hand-Off

Tell the user:

1. Open `https://www.paperyy.com/`.
2. Run the free AIGC/plagiarism check for the current thesis version.
3. Download the report.
4. Leave it in Downloads or place it in `reports/`.

The agent should not upload the user's thesis to third-party services unless the user explicitly asks and confirms the privacy risk.

## Local Report Discovery

Search likely locations:

- user's Downloads directory
- workspace `reports/`
- workspace root

Likely file patterns:

- names containing `Paperyy`, `paper`, `AIGC`, `AI`, `查重`, `检测`, `报告`, `相似`, `重复`
- `.zip`, `.rar`, `.7z`, `.pdf`, `.html`, `.htm`, `.xlsx`, `.xls`, `.docx`, `.txt`

Use `scripts/find_aigc_reports.ps1` on Windows when available.

## Optimization Scope

Only revise:

- high-risk report hits
- medium-risk report hits
- immediately adjacent transition sentences needed for coherence

Do not change:

- figures
- tables
- code blocks
- formulas
- reference list
- verified data and statistics

## Round Report

After each optimization round, write:

- source report path
- thesis version analyzed
- hit paragraphs handled
- paragraphs intentionally left unchanged
- new output DOCX path
- recommendation for whether another Paperyy round is needed

---
name: thesis-workflow-agent
description: "Use when the user needs end-to-end thesis or dissertation assistance: workspace setup, material audit, outline design, chapter-by-chapter writing, revision, expansion, shortening, translation/paraphrase, academic polishing, plagiarism reduction, AIGC/Paperyy report handling, references, figures, template-based DOCX creation, DOCX editing, or final formatting."
---

# Thesis Workflow Agent

## Overview

Act as the thesis process controller. Coordinate evidence collection, chapter writing, `thesis-optimizer` content optimization, `minimax-docx` Word output, AIGC report feedback loops, and final checks without hard-coding any school, discipline, or project.

## Required Sub-Skills

- **REQUIRED SUB-SKILL:** Use bundled `skills/minimax-docx` for every `.docx` creation, editing, template application, layout repair, table/image placement, TOC, page header/footer, section, or final Word output task. If the bundled copy is unavailable, fall back to the globally installed `minimax-docx`.
- **REQUIRED SUB-SKILL:** Use bundled `skills/thesis-optimizer` for thesis diagnosis, polishing, expansion, shortening, paraphrase, plagiarism reduction, AIGC reduction, and chapter-level academic expression optimization. If the bundled copy is unavailable, fall back to the globally installed `thesis-optimizer`.
- Use image generation/editing tools only when the user asks for bitmap figures. For diagrams, prefer Mermaid/draw.io/structured diagram drafts before image generation.
- **OPTIONAL BUNDLED MCP:** Use `mcp/suxi-image/suxi_image_mcp.py` only when the user needs GPT-image bitmap generation. If the user does not need image generation, skip Suxi setup completely and do not ask for its API key.

Do not copy the internals of sub-skills into this skill. Load and follow each sub-skill when its stage triggers.

## Bundled Sub-Skill Layout

This skill is self-contained for core thesis workflows:

```text
thesis-workflow-agent/
  SKILL.md
  skills/
    minimax-docx/
      SKILL.md
    thesis-optimizer/
      SKILL.md
  mcp/
    suxi-image/
      suxi_image_mcp.py
  template/
    simple.docx
```

When using a sub-skill, prefer the bundled path first:

- `skills/minimax-docx/SKILL.md`
- `skills/thesis-optimizer/SKILL.md`

## Hard Rules

1. Work from verified materials first; never fabricate references, experiments, parameters, statistics, results, or conclusions.
2. Do not change factual data unless the user explicitly asks. If materials conflict, report the risk and ask before correcting.
3. Keep thesis prose independent from local file paths, current directories, or tool execution details.
4. Write content first, then format. Avoid repeated DOCX layout work while the text is still unstable.
5. Before formal DOCX writes, keep or create a backup of the source document.
6. For AIGC reduction, prefer targeted sentence-level and paragraph-local revision. Do not rewrite the whole thesis unless the user explicitly requests it.
7. Never store a Metaso API key in this skill, examples, logs, or committed files. Ask the user for the key only during environment setup, then inject it only into the active agent's local configuration after confirming the target config file.

## Quick Start

1. Load this skill and inspect the workspace.
2. Run `scripts/check_thesis_environment.ps1 -Workspace "<workspace>" -CreateDirs` when PowerShell is available.
3. If the task may need academic search, check whether Metaso MCP is configured. If not, tell the user to get an API key from `https://metaso.cn/search-api/api-keys` and send it in the current session; do not include the key in any example.
4. Ask the user to choose the task type only if it is not already clear: create, edit, optimize, reduce AIGC, format DOCX, search references, generate figures, or full workflow.
5. Produce a thesis workspace report and the next executable action.

## Workspace Standard

Create or use these directories in the current thesis workspace:

| Directory | Purpose |
|---|---|
| `chapters/` | Chapter TXT/Markdown drafts, confirmed chapter text, revision records |
| `images/` | Figures, screenshots, generated images, diagram exports |
| `templates/` | User-provided school templates and formatting references |
| `references/` | Literature, reports, project materials, notes, source evidence |
| `reports/` | AIGC/plagiarism reports and extracted report files |
| `outputs/` | Generated DOCX/PDF/TXT deliverables |
| `logs/` | Process notes, material audit, risk list, change summaries |

This skill also has its own default template path: `template/simple.docx`. If the user does not provide a template and this file exists, use it as the default template through `minimax-docx`.

## Workflow Decision Table

| User intent | Action |
|---|---|
| "帮我开始写论文", "从零生成", "完整流程" | Audit materials, create workspace dirs, propose thesis structure tree, wait for confirmation or YOLO approval, then write chapters |
| "根据模板创建" | Locate user template first; otherwise use `template/simple.docx`; then invoke `minimax-docx` create/apply-template pipeline |
| "修改/扩写/删减/润色/改写/翻译/转义" | Identify target chapter/section, preserve facts, use `thesis-optimizer`, save TXT draft, then write confirmed text to DOCX via `minimax-docx` if needed |
| "降低AIGC率/查重/降重" | Ask user to run Paperyy and download report; locate/extract report; map hits to thesis; use `thesis-optimizer`; output revised text and DOCX |
| "补参考文献/研究现状" | Configure/use Metaso MCP if available; collect candidate sources with relevance notes; mark items needing manual bibliographic verification |
| "生成论文插图/流程图/架构图" | Draft figure plan first: title, purpose, placement, required elements, caption. Prefer Mermaid/draw.io for diagrams; use bundled Suxi `gpt-image-2-vip` MCP only for bitmap generation |
| "整理成正式Word/套模板/修格式" | Invoke `minimax-docx`; analyze source and template, apply formatting, validate, preview, and diff |

## Full Workflow

### Phase 0: Dependency and Material Check

1. Check bundled `skills/minimax-docx` first, then global `minimax-docx`; run the selected sub-skill's environment check. If dependencies are missing, report the exact missing item and the command needed. Ask before high-risk installs or global package operations.
2. Check bundled `skills/thesis-optimizer` first, then global `thesis-optimizer`; verify that its templates/references are readable.
3. Check Metaso MCP status when literature search may be needed. If missing, ask the user to visit `https://metaso.cn/search-api/api-keys`, send the API key, then configure only the active local agent. Read `references/metaso-setup.md` before configuring.
4. If bitmap image generation is needed, check bundled Suxi MCP status. If missing API key, tell the user to register/top up at `https://new.suxi.ai/console/topup` (`1 CNY = 1 USD credit`; each generation consumes `0.12 USD credit`, about `0.12 CNY`), create an API key at `https://new.suxi.ai/console/token`, then send the key for local MCP configuration. If the user does not need image generation, skip this step.
5. Scan the workspace for templates, existing DOCX drafts, TXT/Markdown chapter drafts, reports, references, images, data, source code, and project documents.
6. If any thesis template or reference file is legacy Word `.doc`, tell the user to convert it to `.docx` at `https://www.freeconvert.com/zh/docx-converter` before DOCX processing. Explain that this conversion is intended to preserve document content for editing, and the file can be converted back to `.doc` later if the user needs that final format.
7. Report found materials, missing materials, usable chapters, risky gaps, and a recommended next action.

### Phase 1: Workspace Setup

Create the standard directories if they do not exist. Ask the user to place materials according to the workspace standard. Continue if the user confirms all available materials are already present.

### Phase 2: Requirement Confirmation

Classify the task as one of:

- create new thesis
- edit existing thesis
- optimize/polish
- expand/shorten
- translate/paraphrase
- reduce plagiarism or AIGC
- format/apply template
- literature/reference work
- figure planning/generation
- full workflow

If mode is unclear, ask one concise question. Otherwise proceed.

### Phase 3: Structure Tree

For creation or major rewrite tasks, output a thesis structure tree before writing body text. Each node should include:

- chapter/section title
- purpose
- evidence/material source
- missing evidence
- recommended figures/tables
- whether it is ready to write

Default mode requires user confirmation after the structure tree. In YOLO mode, after the user confirms the tree once, write all chapters and generate the DOCX without per-chapter confirmation.

### Phase 4: Chapter Drafting

For each chapter:

1. Read only relevant materials first.
2. Draft content into `chapters/` as TXT or Markdown for user review.
3. Mark unsupported claims as "待确认" instead of inventing evidence.
4. Provide missing evidence, suggested figures, and citation needs.
5. In default mode, wait for user confirmation before writing that chapter into DOCX.
6. In YOLO mode, continue chapter by chapter and write all confirmed generated content to DOCX at the end.

### Phase 5: Content Optimization

Use `thesis-optimizer` for:

- academic polishing
- expansion without adding unsupported facts
- shortening while preserving argument and evidence
- sentence-level paraphrase
- plagiarism reduction
- AIGC risk reduction

Save optimized chapter text in `chapters/` and summarize which paragraphs changed and why.

### Phase 6: DOCX Writing and Formatting

Use `minimax-docx`:

- New document: template if available, otherwise `template/simple.docx`, otherwise create a minimal academic DOCX.
- Existing document: preview/analyze first, edit minimally, validate after write.
- Template application: preserve template sections, headers/footers, TOC-recognizable heading styles, image/table counts, and page numbering.

Always report output path, validation result, and remaining formatting risks.

### Phase 7: Paperyy AIGC Loop

When reducing AIGC based on reports:

1. Tell the user to run free AIGC checking at `https://www.paperyy.com/` and download the report.
2. Search `Downloads`, `reports/`, and the workspace for likely Paperyy/AIGC/plagiarism reports. Use `scripts/find_aigc_reports.ps1` when available.
3. Extract archives into `reports/extracted/`.
4. Read report files and identify high/medium risk text spans.
5. Map hits to thesis chapters and revise only hit paragraphs plus adjacent transition sentences.
6. Use `thesis-optimizer` with minimal-intervention rules.
7. Write a new DOCX version with `minimax-docx` and ask the user to recheck if another round is needed.

## References

Load only what is needed:

- `references/workflow-details.md`: detailed execution checklists and deliverable naming.
- `references/metaso-setup.md`: safe Metaso MCP API key setup rules.
- `references/suxi-image-mcp.md`: optional Suxi `gpt-image-2-vip` MCP setup, exact image generation API, and image upload API.
- `references/report-handling.md`: Paperyy/AIGC report handling and mapping rules.

## Common Mistakes

| Mistake | Correct action |
|---|---|
| Starting body text before material audit | Audit first, then write |
| Treating search results as final references | Keep them as candidates until bibliographic verification |
| Rewriting whole thesis for AIGC | Target report-hit paragraphs only |
| Formatting repeatedly during drafting | Keep TXT drafts until content stabilizes |
| Processing legacy `.doc` directly as a thesis template/reference | Ask the user to convert it to `.docx` at `https://www.freeconvert.com/zh/docx-converter`; content is expected to remain intact for editing and can be converted back later |
| Using visual bold text as headings | Use DOCX heading styles with TOC outline levels through `minimax-docx` |
| Exposing API keys in examples | Never echo, store, or commit secrets |

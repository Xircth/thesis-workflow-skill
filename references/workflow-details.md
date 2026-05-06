# Thesis Workflow Details

## Material Audit Checklist

Look for:

- school template or formatting guide
- task book, proposal, mid-term report, defense requirements
- existing thesis drafts in DOCX/TXT/Markdown/PDF
- chapter fragments, outlines, notes, reference lists
- source data, experiment records, screenshots, tables, logs
- project documents, code, deployment notes, API docs, diagrams
- literature PDFs, DOI links, web notes, citation exports

Report three lists: usable now, missing but important, optional enhancement material.

## Deliverable Naming

Prefer stable names:

- `logs/material-audit.md`
- `logs/thesis-structure.md`
- `chapters/chapter-01-title.txt`
- `chapters/chapter-01-title.optimized.txt`
- `references/reference-candidates.md`
- `reports/aigc-round-01-analysis.md`
- `outputs/thesis-draft-v01.docx`
- `outputs/thesis-aigc-optimized-v02.docx`
- `outputs/thesis-final-candidate.docx`

## Chapter Writing Contract

Each chapter draft should include:

1. chapter text
2. evidence used
3. unsupported or pending facts
4. suggested figures/tables
5. citation needs
6. AIGC/plagiarism risk notes

When a chapter is approved, write it to DOCX with `minimax-docx`. If the user asks for YOLO mode, record that the user approved one-pass generation and continue without per-chapter stops.

## Final Review Checklist

Check:

- title hierarchy and TOC recognition
- page numbering and section breaks
- headers/footers
- figure/table numbering and captions
- reference numbering and in-text citation consistency
- duplicated or incomplete references
- unsupported claims, invented facts, and unverified statistics
- residual local path/file-perspective wording
- obvious AI-style templated paragraphs

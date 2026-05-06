param(
    [string]$Workspace = (Get-Location).Path,
    [switch]$CreateDirs
)

$ErrorActionPreference = "Stop"

function Test-PathState {
    param([string]$Path)
    [pscustomobject]@{
        Path = $Path
        Exists = Test-Path -LiteralPath $Path
    }
}

$workspacePath = (Resolve-Path -LiteralPath $Workspace).Path
$skillRoot = Split-Path -Parent $PSScriptRoot
$agentsSkills = Split-Path -Parent $skillRoot
$bundledSkills = Join-Path $skillRoot "skills"
$bundledMinimax = Join-Path $bundledSkills "minimax-docx"
$bundledOptimizer = Join-Path $bundledSkills "thesis-optimizer"
$suxiMcp = Join-Path $skillRoot "mcp/suxi-image/suxi_image_mcp.py"
$globalMinimax = Join-Path $agentsSkills "minimax-docx"
$globalOptimizer = Join-Path $agentsSkills "thesis-optimizer"
$preferredMinimax = if (Test-Path -LiteralPath $bundledMinimax) { $bundledMinimax } else { $globalMinimax }
$preferredOptimizer = if (Test-Path -LiteralPath $bundledOptimizer) { $bundledOptimizer } else { $globalOptimizer }

$dirs = @("chapters", "images", "templates", "references", "reports", "outputs", "logs")
if ($CreateDirs) {
    foreach ($dir in $dirs) {
        $target = Join-Path $workspacePath $dir
        if (-not (Test-Path -LiteralPath $target)) {
            New-Item -ItemType Directory -Path $target | Out-Null
        }
    }
}

$patterns = @{
    Templates = @("*.docx", "*.dotx", "*.doc", "*模板*")
    Drafts = @("*.docx", "*.md", "*.txt", "*.pdf")
    Reports = @("*AIGC*", "*查重*", "*检测*", "*报告*", "*Paperyy*", "*paper*")
    Diagrams = @("*.drawio", "*.mmd", "*.mermaid", "*.png", "*.jpg", "*.jpeg")
}

$scan = @{}
foreach ($key in $patterns.Keys) {
    $items = @()
    foreach ($pattern in $patterns[$key]) {
        $items += Get-ChildItem -LiteralPath $workspacePath -Recurse -File -Filter $pattern -ErrorAction SilentlyContinue |
            Select-Object -ExpandProperty FullName
    }
    $scan[$key] = $items | Sort-Object -Unique
}

$legacyDocFiles = Get-ChildItem -LiteralPath $workspacePath -Recurse -File -Filter "*.doc" -ErrorAction SilentlyContinue |
    Where-Object { $_.Extension -ieq ".doc" } |
    Select-Object -ExpandProperty FullName |
    Sort-Object -Unique

$defaultTemplate = Join-Path $skillRoot "template/simple.docx"

[pscustomobject]@{
    Workspace = $workspacePath
    CreatedDirectories = [bool]$CreateDirs
    Skill = Test-PathState $skillRoot
    BundledSkills = Test-PathState $bundledSkills
    BundledMiniMaxDocx = Test-PathState $bundledMinimax
    BundledThesisOptimizer = Test-PathState $bundledOptimizer
    SuxiImageMcp = Test-PathState $suxiMcp
    SuxiImageConfigured = [bool]$env:SUXI_API_KEY
    GlobalMiniMaxDocx = Test-PathState $globalMinimax
    GlobalThesisOptimizer = Test-PathState $globalOptimizer
    PreferredMiniMaxDocx = Test-PathState $preferredMinimax
    PreferredThesisOptimizer = Test-PathState $preferredOptimizer
    DefaultTemplate = Test-PathState $defaultTemplate
    WorkspaceDirectories = $dirs | ForEach-Object { Test-PathState (Join-Path $workspacePath $_) }
    Found = $scan
    LegacyDocFiles = $legacyDocFiles
    LegacyDocInstruction = if ($legacyDocFiles.Count -gt 0) { "Legacy .doc files detected. Ask the user to convert them to .docx at https://www.freeconvert.com/zh/docx-converter before DOCX processing; explain that content is intended to be preserved and can be converted back later if needed." } else { "" }
    Next = "If PreferredMiniMaxDocx exists, load that sub-skill and run its env_check. If academic search is needed, check Metaso MCP configuration without exposing secrets."
} | ConvertTo-Json -Depth 6

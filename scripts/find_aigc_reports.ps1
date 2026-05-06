param(
    [string]$Workspace = (Get-Location).Path,
    [string]$Downloads = (Join-Path $HOME "Downloads"),
    [switch]$Extract
)

$ErrorActionPreference = "Stop"

$workspacePath = (Resolve-Path -LiteralPath $Workspace).Path
$locations = @($Downloads, (Join-Path $workspacePath "reports"), $workspacePath) |
    Where-Object { $_ -and (Test-Path -LiteralPath $_) } |
    Sort-Object -Unique

$nameRegex = "(?i)(paperyy|aigc|plagiarism|similarity|查重|检测|报告|相似|重复|ai[\s_\-]*(检测|查重|审查|率|report))"
$extensions = @(".zip", ".pdf", ".html", ".htm", ".xlsx", ".xls", ".docx", ".txt", ".rar", ".7z")

$matches = foreach ($location in $locations) {
    Get-ChildItem -LiteralPath $location -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object {
            ($_.Name -match $nameRegex) -and ($extensions -contains $_.Extension.ToLowerInvariant())
        } |
        Select-Object FullName, Name, Extension, Length, LastWriteTime
}

$extractRoot = Join-Path $workspacePath "reports/extracted"
$extracted = @()

if ($Extract) {
    if (-not (Test-Path -LiteralPath $extractRoot)) {
        New-Item -ItemType Directory -Path $extractRoot | Out-Null
    }

    foreach ($item in $matches | Where-Object { $_.Extension.ToLowerInvariant() -eq ".zip" }) {
        $safeName = [IO.Path]::GetFileNameWithoutExtension($item.Name) -replace '[^\p{L}\p{Nd}\-_]+', '_'
        $target = Join-Path $extractRoot $safeName
        if (-not (Test-Path -LiteralPath $target)) {
            New-Item -ItemType Directory -Path $target | Out-Null
        }
        Expand-Archive -LiteralPath $item.FullName -DestinationPath $target -Force
        $extracted += $target
    }
}

[pscustomobject]@{
    SearchLocations = $locations
    ReportCandidates = $matches | Sort-Object LastWriteTime -Descending
    ExtractedDirectories = $extracted
    Note = "Read candidates manually before optimizing. For non-zip archives such as rar/7z, use an installed archive tool only after confirming availability."
} | ConvertTo-Json -Depth 5

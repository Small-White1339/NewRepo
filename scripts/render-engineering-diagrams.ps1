param(
    [Parameter(Mandatory = $true)][string]$PlantUmlJar,
    [string]$JavaExecutable = 'java',
    [string]$DotExecutable = 'dot'
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$diagramRoot = Join-Path $repoRoot 'docs/software-engineering/diagrams'
$sourceRoot = Join-Path $diagramRoot 'src'
$svgRoot = Join-Path $diagramRoot 'svg'
$pngRoot = Join-Path $diagramRoot 'png'
$jarPath = (Resolve-Path -LiteralPath $PlantUmlJar).Path
New-Item -ItemType Directory -Path $svgRoot, $pngRoot -Force | Out-Null

# 文本按 UTF-8 与 LF 归一，避免 Git 在 Windows 转换换行后误报图片过期。
function Get-CanonicalTextHash([string]$Path) {
    $text = [IO.File]::ReadAllText($Path).Replace("`r`n", "`n").Replace("`r", "`n")
    $bytes = [Text.UTF8Encoding]::new($false).GetBytes($text)
    $hashProvider = [Security.Cryptography.SHA256]::Create()
    try {
        return [BitConverter]::ToString($hashProvider.ComputeHash($bytes)).Replace('-', '').ToLowerInvariant()
    } finally { $hashProvider.Dispose() }
}

# 图源由本仓库维护；在本机渲染，不向在线图床发送业务资料。
foreach ($format in @('svg', 'png')) {
    $outputRoot = if ($format -eq 'svg') { $svgRoot } else { $pngRoot }
    $pumlFiles = @(Get-ChildItem -LiteralPath $sourceRoot -Filter 'F*.puml' -File)
    $pumlArgs = @('-Djava.awt.headless=true', '-jar', $jarPath, '-charset', 'UTF-8', '-failfast2', '-nometadata', "-t$format", '-o', $outputRoot) + @($pumlFiles.FullName)
    & $JavaExecutable @pumlArgs
    if ($LASTEXITCODE -ne 0) { throw "PlantUML $format rendering failed." }
    foreach ($source in Get-ChildItem -LiteralPath $sourceRoot -Filter 'F*.dot' -File) {
        $target = Join-Path $outputRoot ($source.BaseName + '.' + $format)
        & $DotExecutable "-T$format" $source.FullName '-o' $target
        if ($LASTEXITCODE -ne 0) { throw "Graphviz rendering failed: $($source.Name)" }
    }
}
$figureEntries = @()
foreach ($source in Get-ChildItem -LiteralPath $sourceRoot -Filter 'F*' -File | Sort-Object Name) {
    $figureEntries += [ordered]@{
        id = $source.BaseName.Substring(0, 3)
        source = $source.Name
        sourceSha256 = Get-CanonicalTextHash $source.FullName
        svgSha256 = Get-CanonicalTextHash (Join-Path $svgRoot ($source.BaseName + '.svg'))
        pngSha256 = (Get-FileHash -LiteralPath (Join-Path $pngRoot ($source.BaseName + '.png')) -Algorithm SHA256).Hash.ToLowerInvariant()
    }
}
$renderManifest = [ordered]@{
    schema = 2
    textNormalization = 'UTF-8 without BOM; LF'
    sharedStyleSha256 = Get-CanonicalTextHash (Join-Path $sourceRoot '_style.puml')
    figures = $figureEntries
}
$manifestText = $renderManifest | ConvertTo-Json -Depth 5
[IO.File]::WriteAllText((Join-Path $diagramRoot 'render-manifest.json'), $manifestText + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
Write-Output 'Engineering diagrams exported as SVG and PNG.'

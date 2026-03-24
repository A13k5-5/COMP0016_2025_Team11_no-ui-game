param(
    [string]$ProjectRoot = $PSScriptRoot,
    [string]$VenvName = ".venv_gameEngine_build"
)

$ErrorActionPreference = "Stop"

function Assert-PathExists {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Label
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        throw "$Label not found: $Path"
    }
}

function Invoke-CheckedCommand {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string[]]$Arguments
    )

    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed ($LASTEXITCODE): $FilePath $($Arguments -join ' ')"
    }
}

function Resolve-PythonCommand {
    $candidates = @("python3.12")
    foreach ($candidate in $candidates) {
        $command = Get-Command $candidate -ErrorAction SilentlyContinue
        if ($null -ne $command) {
            return $candidate
        }
    }
    throw "Python launcher not found. Install Python and ensure 'py' or 'python' is available in PATH."
}

$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
$runScript = Join-Path $ProjectRoot "NO_GUI_engine.py"
$modelSource = Join-Path $ProjectRoot "src\game_engine\game_generation_local_llm\models\model_path"
$distDir = Join-Path $ProjectRoot "NO_GUI_engine.dist"
$venvDir = Join-Path $ProjectRoot $VenvName
$venvPython = Join-Path $venvDir "Scripts\python.exe"

Assert-PathExists -Path $runScript -Label "Entry script"
Assert-PathExists -Path $modelSource -Label "AI model folder"

Write-Host "[1/4] Checking virtual environment exists: $venvDir"
Assert-PathExists -Path $venvPython -Label "Virtual environment python"

Write-Host "[2/4] Copying AI model folder"
$intelDest = Join-Path $distDir "src\game_engine\game_generation_local_llm\models\model_path"
if (Test-Path -LiteralPath $intelDest) {
    Remove-Item -LiteralPath $intelDest -Recurse -Force
}
New-Item -ItemType Directory -Path (Split-Path -Path $intelDest -Parent) -Force | Out-Null
Copy-Item -LiteralPath $modelSource -Destination $intelDest -Recurse -Force

Write-Host "[3/4] Copying OpenVINO and NLP runtime libs into dist"
$sitePackagesDir = Join-Path $venvDir "Lib\site-packages"
$packagesToCopy = @(
    "openvino",
    "spacy_curated_transformers",
    "curated_transformers",
    "curated_tokenizers",
    "openvino_tokenizers"
)

foreach ($packageName in $packagesToCopy) {
    $packageSource = Join-Path $sitePackagesDir $packageName
    Assert-PathExists -Path $packageSource -Label "$packageName libs in venv"

    $packageDest = Join-Path $distDir $packageName
    New-Item -ItemType Directory -Path $packageDest -Force | Out-Null
    Copy-Item -Path (Join-Path $packageSource "*") -Destination $packageDest -Recurse -Force
}

$openvinoSource = Join-Path $sitePackagesDir "openvino"
Write-Host "[4/4] Copying OpenVINO DLLs and required packages into dist root"
$dllNames = @("libs/openvino_intel_cpu_plugin.dll", "libs/openvino_intel_gpu_plugin.dll", "libs/openvino_ir_frontend.dll")
foreach ($dllName in $dllNames) {
    $dllSource = Join-Path $openvinoSource $dllName
    $dllFileName = Split-Path -Path $dllName -Leaf
    Write-Host "Copying $dllSource"
    Assert-PathExists -Path $dllSource -Label "Required DLL"
    Copy-Item -LiteralPath $dllSource -Destination (Join-Path $distDir $dllFileName) -Force
}

Write-Host "Build automation complete. Output folder: $distDir"

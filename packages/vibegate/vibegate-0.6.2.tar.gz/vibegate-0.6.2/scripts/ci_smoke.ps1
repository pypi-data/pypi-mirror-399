$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..")
$TempRoot = if ($env:RUNNER_TEMP) { $env:RUNNER_TEMP } else { [System.IO.Path]::GetTempPath() }
$VenvRoot = Join-Path $TempRoot ("vibegate-smoke-" + [System.Guid]::NewGuid().ToString("N"))
$VenvDir = Join-Path $VenvRoot "venv"

try {
    New-Item -ItemType Directory -Path $VenvRoot | Out-Null

    Set-Location $RepoRoot
    if (Test-Path "$RepoRoot/dist") { Remove-Item -Recurse -Force "$RepoRoot/dist" }

    python -m venv $VenvDir
    $VenvBin = Join-Path $VenvDir "Scripts"

    & "$VenvBin/python" -m pip install -U pip
    & "$VenvBin/python" -m pip install build
    & "$VenvBin/python" "$RepoRoot/scripts/sync_schemas.py" --check
    & "$VenvBin/python" "$RepoRoot/scripts/sync_schemas.py"
    & "$VenvBin/python" -m build

    $Wheel = Get-ChildItem -Path "$RepoRoot/dist" -Filter "*.whl" | Select-Object -First 1
    if (-not $Wheel) {
        throw "No wheel found in dist/"
    }

    & "$VenvBin/python" -m pip install $Wheel.FullName

    & "$VenvBin/vibegate" --version
    & "$VenvBin/python" -m vibegate --version
    & "$VenvBin/vibegate" doctor .
    & "$VenvBin/vibegate" check .
} finally {
    if (Test-Path $VenvRoot) { Remove-Item -Recurse -Force $VenvRoot }
}

param(
  [Parameter(Mandatory = $true, Position = 0)]
  [string]$Executable,
  [string[]]$Arguments = @(),
  [string]$ReportDir = 'reports',
  [ValidateSet('basic', 'full')]
  [string]$NcuSet = 'basic'
)

$ErrorActionPreference = 'Stop'
$ReportDir = [IO.Path]::GetFullPath($ReportDir)
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$Executable = (Resolve-Path $Executable).Path

$systems = Join-Path $ReportDir 'systems'
$compute = Join-Path $ReportDir 'compute.csv'
$trace = if ($env:OS -eq 'Windows_NT') { 'cuda,nvtx' } else { 'cuda,nvtx,osrt' }
$platformOptions = @()
if ($env:OS -eq 'Windows_NT') {
  $platformOptions = @('--sample=none', '--cpuctxsw=none')
}
if ($env:CUDA_PATH -and (Test-Path (Join-Path $env:CUDA_PATH 'bin'))) {
  $env:Path = (Join-Path $env:CUDA_PATH 'bin') + ';' + $env:Path
}
Push-Location (Split-Path $Executable -Parent)
try {
  nsys profile --force-overwrite=true --trace=$trace --stats=true `
    @platformOptions -o $systems $Executable @Arguments
  if ($LASTEXITCODE -ne 0) { throw "nsys failed: $LASTEXITCODE" }
  ncu --force-overwrite --set $NcuSet --page raw --kernel-name-base demangled --csv --log-file $compute $Executable @Arguments
  if ($LASTEXITCODE -ne 0) { throw "ncu failed: $LASTEXITCODE" }
} finally {
  Pop-Location
}

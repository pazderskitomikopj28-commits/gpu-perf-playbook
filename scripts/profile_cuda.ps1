param(
  [Parameter(Mandatory = $true, Position = 0)]
  [string]$Executable,
  [string[]]$Arguments = @(),
  [string]$ReportDir = 'reports',
  [ValidateSet('basic', 'full')]
  [string]$NcuSet = 'basic'
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null

$systems = Join-Path $ReportDir 'systems'
$compute = Join-Path $ReportDir 'compute.csv'
nsys profile --force-overwrite=true --trace=cuda,nvtx,osrt --stats=true -o $systems $Executable @Arguments
ncu --force-overwrite --set $NcuSet --page raw --kernel-name-base demangled --csv --log-file $compute $Executable @Arguments

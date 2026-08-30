param(
  [Parameter(Mandatory = $true, Position = 0)]
  [string]$Executable,
  [string[]]$Arguments = @(),
  [string]$ReportDir = 'reports'
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null

$systems = Join-Path $ReportDir 'systems'
$compute = Join-Path $ReportDir 'compute.csv'
nsys profile --trace=cuda,nvtx,osrt --stats=true -o $systems $Executable @Arguments
ncu --set full --kernel-name-base demangled --csv --log-file $compute $Executable @Arguments

$ErrorActionPreference = "Stop"

$root = "D:\marginplus_mvp"
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$zip = Join-Path $root ("marginplus_mvp_pack_" + $stamp + ".zip")

$include = @("app.py","run.bat","README.txt","pack.ps1")

foreach ($f in $include) {
  $p = Join-Path $root $f
  if (-not (Test-Path $p)) { Write-Host "Missing: $p"; exit 1 }
}

if (Test-Path $zip) { Remove-Item $zip -Force }
Compress-Archive -Path ($include | ForEach-Object { Join-Path $root $_ }) -DestinationPath $zip

Write-Host ("PACK OK: " + $zip)

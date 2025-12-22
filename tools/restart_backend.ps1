# Restart backend: stop processes on port 8000, then start uvicorn
try {
    $conns = Get-NetTCPConnection -LocalPort 8000 -ErrorAction Stop
}
catch {
    $conns = @()
}
$pids = @()
foreach ($c in $conns) { $pids += $c.OwningProcess }
if ($pids.Count -gt 0) {
    foreach ($pitem in $pids) {
        try { Stop-Process -Id $pitem -Force -ErrorAction SilentlyContinue } catch {}
    }
}
# Start uvicorn in background using venv/python if available, fallback to python on PATH
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$candidateWin = Join-Path $repoRoot ".venv\Scripts\python.exe"
$candidateNix = Join-Path $repoRoot ".venv/bin/python"
if (Test-Path $candidateWin) { $pythonExe = $candidateWin }
elseif (Test-Path $candidateNix) { $pythonExe = $candidateNix }
else { $pythonExe = 'python' }

Write-Host "Using Python executable: $pythonExe"

# Use Start-Process with separate args to avoid quoting issues
# Avoid assigning to the automatic `$args` variable (PSScriptAnalyzer warning)
$uvicornArgs = @('-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000', '--reload')
Start-Process -FilePath $pythonExe -ArgumentList $uvicornArgs -WindowStyle Hidden
Write-Host "Issued backend start using: $pythonExe $($uvicornArgs -join ' ')"

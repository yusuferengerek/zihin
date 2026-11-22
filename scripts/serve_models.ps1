# Starts the Ollama server with the project's settings.
#
# Why PowerShell: the model server runs on the Windows side, the experiment inside
# WSL. The architecture takes this split from K-01.
#
# Why from a script: OLLAMA_KV_CACHE_TYPE and OLLAMA_FLASH_ATTENTION have to reach
# the server process, not the client. Starting it from a script lets the manifest
# prove the settings (K-22).
#
# Why independent of the session: started as a background process tied to the
# session, the server fell twice. Losing the server in the middle of a long run
# means silent data loss (K-22).
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File scripts/serve_models.ps1
#
# To stop it: Stop-Process -Name ollama

param(
    [int]$NumCtx = 32768,
    [string]$KvCacheType = "q8_0",
    [string]$KeepAlive = "30m",
    [string]$BindAddress = "127.0.0.1:11434"
)

$ErrorActionPreference = "Stop"

# 127.0.0.1 is enough: in mirrored networking mode WSL shares the host's network
# namespace, so binding to 0.0.0.0 is not needed and the server does not listen
# on the LAN interface (K-34).
$env:OLLAMA_HOST = $BindAddress
$env:OLLAMA_CONTEXT_LENGTH = "$NumCtx"
$env:OLLAMA_KV_CACHE_TYPE = $KvCacheType
$env:OLLAMA_FLASH_ATTENTION = "1"
$env:OLLAMA_KEEP_ALIVE = $KeepAlive

$exe = (Get-Command ollama).Source
$log = Join-Path $env:TEMP "zihin-ollama.log"

$mevcut = Get-Process ollama -ErrorAction SilentlyContinue
if ($mevcut) {
    Write-Output "Stopping the running ollama process (PID $($mevcut.Id))."
    Stop-Process -Name ollama -Force
    Start-Sleep -Seconds 3
}

Start-Process -FilePath $exe -ArgumentList "serve" -WindowStyle Hidden -RedirectStandardError $log

# Polling instead of a fixed wait. GPU discovery takes up to 23 seconds on this
# machine, and a fixed eight-second wait reported failure even with the server up.
# A measurement taken before the GPU is ready would also mislead.
$hazir = $false
for ($i = 1; $i -le 30; $i++) {
    Start-Sleep -Seconds 2
    try {
        $yanit = Invoke-WebRequest -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 5 -UseBasicParsing
        if ($yanit.StatusCode -eq 200) { $hazir = $true; break }
    } catch { }
}
if (-not $hazir) {
    Write-Error "The server did not come up. Log: $log"
    exit 1
}
Write-Output "Server up: HTTP 200 (after $($i * 2) seconds)"

# The inference compute line does not reach the log until GPU discovery ends. We
# wait for that line before measuring.
$gpu = $false
for ($i = 1; $i -le 30; $i++) {
    if (Select-String -Path $log -Pattern "inference compute" -Quiet) { $gpu = $true; break }
    Start-Sleep -Seconds 2
}
Write-Output "GPU discovery finished: $gpu"

$satir = (Select-String -Path $log -Pattern "server config" | Select-Object -First 1).Line
foreach ($ad in @("OLLAMA_CONTEXT_LENGTH", "OLLAMA_KV_CACHE_TYPE", "OLLAMA_FLASH_ATTENTION", "OLLAMA_KEEP_ALIVE")) {
    if ($satir -match "$ad`:(\S*)") {
        Write-Output "$ad = $($matches[1])"
    }
}
Write-Output "PID = $((Get-Process ollama | Select-Object -First 1).Id)"
Write-Output "Log = $log"

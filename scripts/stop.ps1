$ErrorActionPreference = "Stop"
$containerName = "pm-mvp"

Write-Host "Stopping Project Management MVP container..."
podman rm -f $containerName 2>$null | Out-Null

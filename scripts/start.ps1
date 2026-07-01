$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$containerName = "pm-mvp"
$envFile = Join-Path $repoRoot ".env"

Write-Host "Starting Project Management MVP with Podman..."
podman build -f "$repoRoot/backend/Containerfile" -t $containerName "$repoRoot"
podman run --rm -d --name $containerName --env-file $envFile -p 8000:8000 $containerName

Write-Host "Application is running at http://localhost:8000"

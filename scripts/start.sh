#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "$0")/.." && pwd)"
container_name="pm-mvp"

printf 'Starting Project Management MVP with Podman...\n'
podman build -f "$repo_root/backend/Containerfile" -t "$container_name" "$repo_root"
podman run --rm -d --name "$container_name" -p 8000:8000 "$container_name"

printf 'Application is running at http://localhost:8000\n'

#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "$0")/.." && pwd)"
container_name="pm-mvp"
env_file="$repo_root/.env"

printf 'Starting Project Management MVP with Podman...\n'
podman build -f "$repo_root/backend/Containerfile" -t "$container_name" "$repo_root"
podman run --rm -d --name "$container_name" --env-file "$env_file" -p 8000:8000 "$container_name"

printf 'Application is running at http://localhost:8000\n'

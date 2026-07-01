#!/usr/bin/env bash
set -euo pipefail
container_name="pm-mvp"

printf 'Stopping Project Management MVP container...\n'
podman rm -f "$container_name" >/dev/null 2>&1 || true

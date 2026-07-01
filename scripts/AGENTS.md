# Scripts guidance

This folder contains local Podman start and stop scripts.

## Scripts

- `start.ps1`: Windows PowerShell start script.
- `start.sh`: macOS/Linux shell start script.
- `stop.ps1`: Windows PowerShell stop script.
- `stop.sh`: macOS/Linux shell stop script.

## Behavior

The start scripts:
- Build the `pm-mvp` image from `backend/Containerfile`.
- Pass the root `.env` file into the container with `--env-file`.
- Run the container as `pm-mvp`.
- Publish the app on `http://localhost:8000`.

The stop scripts remove the running `pm-mvp` container if present.

## Notes

- The scripts assume Podman is installed and available on `PATH`.
- `.env` must contain `OPENROUTER_API_KEY` for AI features.
- If port `8000` is already in use, stop the existing service or change the port mapping manually.

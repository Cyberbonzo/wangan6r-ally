#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PKG="$ROOT/runtime/WanganLauncher-0.1.0-linux-x86_64"
export WANGAN_DATA="$ROOT/userdata"
export LD_LIBRARY_PATH="$PKG/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS=1
export SDL_GAMECONTROLLER_ALLOW_STEAM_VIRTUAL_GAMEPAD=0
unset SDL_GAMECONTROLLER_IGNORE_DEVICES LD_PRELOAD
export MESA_SHADER_CACHE_DIR="$ROOT/userdata/mesa-cache"
mkdir -p "$ROOT/logs" "$WANGAN_DATA"
export PATH="$ROOT/source/bin:$PATH"
if [[ "${XDG_CURRENT_DESKTOP:-}" == *gamescope* || -n "${GAMESCOPE_WAYLAND_DISPLAY:-}" ]]; then
    export WANGAN_USE_EXISTING_GAMESCOPE=1
fi
python3 "$ROOT/source/controls.py" >>"$ROOT/logs/controls.log" 2>&1 &
CONTROL_PID=$!
cleanup() {
    kill "$CONTROL_PID" 2>/dev/null || true
    wait "$CONTROL_PID" 2>/dev/null || true
    WINEPREFIX="$WANGAN_DATA/prefix" "$PKG/components/wine/bin/wineserver" -k 2>/dev/null || true
}
trap cleanup EXIT
trap 'exit 0' TERM INT
"$PKG/wangan-launcher" --library "$ROOT/game" --play mt6r --output 1920x1080 --upscaler linear --fullscreen on --deadzone 0.12 --no-input "$@" >>"$ROOT/logs/launcher.log" 2>&1

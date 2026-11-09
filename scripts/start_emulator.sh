#!/usr/bin/env bash
# Start the AndroidWorld emulator. Extra arguments go to the emulator, for
# example:  bash scripts/start_emulator.sh -no-window
set -euo pipefail

SDK="${ANDROID_SDK_ROOT:-$HOME/Android/Sdk}"
AVD_NAME="${AVD_NAME:-AndroidWorldAvd}"
GRPC_PORT="${GRPC_PORT:-8554}"

exec "$SDK/emulator/emulator" -avd "$AVD_NAME" -no-snapshot \
  -grpc "$GRPC_PORT" -gpu swiftshader_indirect "$@"

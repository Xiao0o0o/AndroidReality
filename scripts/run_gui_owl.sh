#!/usr/bin/env bash
# Run a GUI-Owl model on AndroidReality.
#
#   bash scripts/run_gui_owl.sh <served-model-name> <clean|perturbed>
#   TTIR=1 bash scripts/run_gui_owl.sh gui_owl_7b perturbed
#   TASKS=AudioRecorderRecordAudio bash scripts/run_gui_owl.sh gui_owl_7b perturbed
set -euo pipefail

if [ "$#" -ne 2 ]; then
  sed -n '2,6p' "$0" >&2
  exit 2
fi
MODEL="$1"
SETTING="$2"

source "$(dirname -- "${BASH_SOURCE[0]}")/common.sh"
resolve_setting "$SETTING"

TTIR="${TTIR:-0}"
if [ "$TTIR" = "1" ]; then
  DOWNSTREAM_PRE_ACTION_ENABLE=True
  TTIR_SUFFIX="_ttir"
else
  DOWNSTREAM_PRE_ACTION_ENABLE=False
  TTIR_SUFFIX=""
fi

SESSION_DIR="${SESSION_DIR:-$ROOT_DIR/random_perturb_runs/session_$(date +%Y-%m-%d_%H-%M-%S)_${MODEL}_${SETTING}${TTIR_SUFFIX}}"

# GUI-Owl-1.5 uses Qwen-VL coordinates. The earlier GUI-Owl models use resized
# absolute coordinates.
case "$MODEL" in
  *1.5*|*1_5*) GUIOWL_COORDINATE_FORMAT="${GUIOWL_COORDINATE_FORMAT:-qwen-vl}" ;;
  *)           GUIOWL_COORDINATE_FORMAT="${GUIOWL_COORDINATE_FORMAT:-abs_resized}" ;;
esac

export GUIOWL_MIN_PIXELS="${GUIOWL_MIN_PIXELS:-3136}"
export GUIOWL_MAX_PIXELS="${GUIOWL_MAX_PIXELS:-2592000}"

build_shared_args

python run_random_perturb_batch.py \
  "${SHARED_ARGS[@]}" \
  "${CLEAN_ARGS[@]}" \
  --agent=gui_owl \
  --model="$MODEL" \
  --guiowl-coordinate-format="$GUIOWL_COORDINATE_FORMAT" \
  --guiowl-temperature="${GUIOWL_TEMPERATURE:-0.1}" \
  --downstream-pre-action-enable="$DOWNSTREAM_PRE_ACTION_ENABLE" \
  --downstream-pre-action-log-enable=True \
  --downstream-pre-action-use-recovery-prompt=True \
  --downstream-pre-action-wait-seconds=2.0 \
  --downstream-recovery-max-steps=3 \
  --downstream-hard-stuck-window=3

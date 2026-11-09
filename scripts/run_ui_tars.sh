#!/usr/bin/env bash
# Run a UI-TARS model on AndroidReality.
#
#   bash scripts/run_ui_tars.sh <ui_tars_7b_sft|ui_tars_1.5_7b> <clean|perturbed>
#
# Both models are served under the name "ui_tars" by scripts/serve_model.sh. The
# first argument selects the matching response parser.
set -euo pipefail

if [ "$#" -ne 2 ]; then
  sed -n '2,7p' "$0" >&2
  exit 2
fi
VARIANT="$1"
SETTING="$2"

case "$VARIANT" in
  ui_tars_7b_sft) PARSER=qwen2vl ;;
  ui_tars_1.5_7b) PARSER=qwen25vl ;;
  *)
    echo "Unknown UI-TARS variant '$VARIANT'." >&2
    exit 2
    ;;
esac

source "$(dirname -- "${BASH_SOURCE[0]}")/common.sh"
resolve_setting "$SETTING"

SESSION_DIR="${SESSION_DIR:-$ROOT_DIR/random_perturb_runs/session_$(date +%Y-%m-%d_%H-%M-%S)_${VARIANT}_${SETTING}}"

build_shared_args

python ui_tars_runner/run_ui_tars_random_perturb_batch.py \
  "${SHARED_ARGS[@]}" \
  "${CLEAN_ARGS[@]}" \
  --agent=ui_tars \
  --model=ui_tars \
  --ui-tars-parser-model-type="$PARSER" \
  --ui-tars-language=English \
  --ui-tars-temperature="${UI_TARS_TEMPERATURE:-0.0}" \
  --ui-tars-max-tokens=400 \
  --ui-tars-max-retry=10 \
  --ui-tars-history-window=8

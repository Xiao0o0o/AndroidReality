# Shared defaults for the benchmark runners. Sourced by run_gui_owl.sh and
# run_ui_tars.sh. Values match the paper; override any of them through the
# environment.

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

API_KEY="${API_KEY:-sk-local}"
BASE_URL="${BASE_URL:-http://127.0.0.1:4243/v1}"
TASKS="${TASKS:-}"
TASKS_FILE="${TASKS_FILE:-}"
REPEATS_PER_TASK="${REPEATS_PER_TASK:-1}"
GRPC_PORT="${GRPC_PORT:-8554}"
CONSOLE_PORT="${CONSOLE_PORT:-5554}"
EPISODE_STEP_BUDGET_MULTIPLIER="${EPISODE_STEP_BUDGET_MULTIPLIER:-20.0}"

# SAMPLING_SEED decides which perturbation each task receives. 20260427 is the
# assignment used in the paper. Changing it gives a different benchmark.
SAMPLING_SEED="${SAMPLING_SEED:-20260427}"
# Seeds for the probabilistic action perturbations.
ACTION_DELAY_SEED="${ACTION_DELAY_SEED:-0}"
ACTION_DROP_SEED="${ACTION_DROP_SEED:-0}"

ALL_PROFILES="font_size_large,font_size_small,ui_theme_dark,display_size_dpi_compact,display_size_dpi_zoomed_out,orientation_landscape,execution_delay_loading,execution_delay_frozen,partial_loading_skeleton,app_hang_restart_required,state_reset_home,bottom_sheet_consent,popup_permission,popup_security,interstitial_ad,ad_trial_offer,rate_dialog,update_system,update_app_sheet,notification_message,notification_delivery,locale_date_format_us12,locale_date_format_eu24,action_delay_realistic,action_drop_random"

FONT_SIZE_LARGE_SCALE="${FONT_SIZE_LARGE_SCALE:-1.35}"
FONT_SIZE_SMALL_SCALE="${FONT_SIZE_SMALL_SCALE:-0.82}"
DISPLAY_COMPACT_DENSITY_SCALE="${DISPLAY_COMPACT_DENSITY_SCALE:-0.85}"
DISPLAY_COMPACT_SIZE_SCALE="${DISPLAY_COMPACT_SIZE_SCALE:-0.94}"
DISPLAY_ZOOMED_OUT_DENSITY_SCALE="${DISPLAY_ZOOMED_OUT_DENSITY_SCALE:-0.76}"
DISPLAY_ZOOMED_OUT_SIZE_SCALE="${DISPLAY_ZOOMED_OUT_SIZE_SCALE:-0.88}"
ORIENTATION_PROFILE_SEQUENCE="${ORIENTATION_PROFILE_SEQUENCE:-landscape}"
APP_HANG_TRIGGER_STEPS="${APP_HANG_TRIGGER_STEPS:-2}"
ACTION_DELAY_PROBABILITY="${ACTION_DELAY_PROBABILITY:-0.15}"
ACTION_DELAY_SECONDS="${ACTION_DELAY_SECONDS:-1.5}"
ACTION_DROP_PROBABILITY="${ACTION_DROP_PROBABILITY:-0.08}"

# resolve_setting <clean|perturbed>
# Sets PROFILE_NAMES and CLEAN_ARGS for the requested setting. PROFILE_NAMES can
# still be narrowed from the environment in the perturbed setting.
resolve_setting() {
  case "$1" in
    clean)
      PROFILE_NAMES="clean"
      CLEAN_ARGS=()
      ;;
    perturbed)
      PROFILE_NAMES="${PROFILE_NAMES:-$ALL_PROFILES}"
      CLEAN_ARGS=(--disable-clean)
      ;;
    *)
      echo "Unknown setting '$1'. Use 'clean' or 'perturbed'." >&2
      exit 2
      ;;
  esac
}

# Fills SHARED_ARGS with the flags both batch runners accept.
build_shared_args() {
  SHARED_ARGS=(
    --suite-family=android_world
    --repeats-per-task="$REPEATS_PER_TASK"
    --sampling-seed="$SAMPLING_SEED"
    --session-dir="$SESSION_DIR"
    --api-key="$API_KEY"
    --base-url="$BASE_URL"
    --grpc-port="$GRPC_PORT"
    --console-port="$CONSOLE_PORT"
    --profiles="$PROFILE_NAMES"
    --font-size-large-scale="$FONT_SIZE_LARGE_SCALE"
    --font-size-small-scale="$FONT_SIZE_SMALL_SCALE"
    --display-compact-density-scale="$DISPLAY_COMPACT_DENSITY_SCALE"
    --display-compact-size-scale="$DISPLAY_COMPACT_SIZE_SCALE"
    --display-zoomed-out-density-scale="$DISPLAY_ZOOMED_OUT_DENSITY_SCALE"
    --display-zoomed-out-size-scale="$DISPLAY_ZOOMED_OUT_SIZE_SCALE"
    --orientation-profile-sequence="$ORIENTATION_PROFILE_SEQUENCE"
    --app-hang-trigger-steps="$APP_HANG_TRIGGER_STEPS"
    --action-delay-probability="$ACTION_DELAY_PROBABILITY"
    --action-delay-seconds="$ACTION_DELAY_SECONDS"
    --action-delay-seed="$ACTION_DELAY_SEED"
    --action-drop-probability="$ACTION_DROP_PROBABILITY"
    --action-drop-seed="$ACTION_DROP_SEED"
    --episode-step-budget-multiplier="$EPISODE_STEP_BUDGET_MULTIPLIER"
  )
  [ -n "$TASKS_FILE" ] && SHARED_ARGS+=(--tasks-file="$TASKS_FILE")
  [ -n "$TASKS" ] && SHARED_ARGS+=(--tasks="$TASKS")
  return 0
}

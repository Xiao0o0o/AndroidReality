"""Shared runner-side MDP perturbation flags and env wrapping helpers."""

from __future__ import annotations

from absl import flags

from android_world.env import interface

from .action_delay import ActionDelayPerturbationConfig
from .action_delay import ActionDelayPerturbationEnv
from .action_drop import ActionDropPerturbationConfig
from .action_drop import ActionDropPerturbationEnv
from .app_hang import AppHangPerturbationConfig
from .app_hang import AppHangPerturbationEnv
from .display_size_dpi import DisplaySizeDpiPerturbationConfig
from .display_size_dpi import DisplaySizeDpiPerturbationEnv
from .execution_delay import ExecutionDelayPerturbationConfig
from .execution_delay import ExecutionDelayPerturbationEnv
from .font_size import FontSizePerturbationConfig
from .font_size import FontSizePerturbationEnv
from .helper_interruption import HelperInterruptionPerturbationConfig
from .helper_interruption import HelperInterruptionPerturbationEnv
from .locale_date_format import LocaleDateFormatPerturbationConfig
from .locale_date_format import LocaleDateFormatPerturbationEnv
from .orientation import OrientationPerturbationConfig
from .orientation import OrientationPerturbationEnv
from .state_reset import StateResetPerturbationConfig
from .state_reset import StateResetPerturbationEnv
from .ui_theme import UIThemePerturbationConfig
from .ui_theme import UIThemePerturbationEnv

_MDP_ACTION_DROP_ENABLE = flags.DEFINE_boolean(
    'mdp_action_drop_enable',
    False,
    'Whether to randomly drop some agent actions before they reach the device.',
)
_MDP_ACTION_DROP_PROBABILITY = flags.DEFINE_float(
    'mdp_action_drop_probability',
    0.1,
    'Probability that a non-answer action is skipped entirely.',
)
_MDP_ACTION_DROP_SEED = flags.DEFINE_integer(
    'mdp_action_drop_seed',
    0,
    'Random seed used for action dropping.',
)
_MDP_ACTION_DELAY_ENABLE = flags.DEFINE_boolean(
    'mdp_action_delay_enable',
    False,
    'Whether to add real wall-clock latency before some actions execute.',
)
_MDP_ACTION_DELAY_PROBABILITY = flags.DEFINE_float(
    'mdp_action_delay_probability',
    0.15,
    'Probability that a non-answer action is delayed before execution.',
)
_MDP_ACTION_DELAY_SECONDS = flags.DEFINE_float(
    'mdp_action_delay_seconds',
    1.5,
    'How many seconds to sleep before executing a delayed action.',
)
_MDP_ACTION_DELAY_SEED = flags.DEFINE_integer(
    'mdp_action_delay_seed',
    0,
    'Random seed used for action-delay sampling.',
)
_MDP_EXECUTION_DELAY_ENABLE = flags.DEFINE_boolean(
    'mdp_execution_delay_enable',
    False,
    'Whether to enable execution-delay perturbation.',
)
_MDP_EXECUTION_DELAY_TRIGGER_STEPS = flags.DEFINE_string(
    'mdp_execution_delay_trigger_steps',
    '3',
    'Comma-separated action steps at which execution delay should trigger.',
)
_MDP_EXECUTION_DELAY_STEPS = flags.DEFINE_integer(
    'mdp_execution_delay_steps',
    2,
    'How many observations should stay delayed before the new state appears.',
)
_MDP_EXECUTION_DELAY_MODE = flags.DEFINE_string(
    'mdp_execution_delay_mode',
    'loading',
    "Execution-delay style: 'loading', 'frozen', or 'skeleton'.",
)
_MDP_EXECUTION_DELAY_BLOCK_ACTIONS = flags.DEFINE_boolean(
    'mdp_execution_delay_block_actions',
    True,
    'Whether subsequent actions should be ignored while the delayed transition is pending.',
)
_MDP_EXECUTION_DELAY_LOADING_TEXT = flags.DEFINE_string(
    'mdp_execution_delay_loading_text',
    'Loading...',
    'Text shown in loading-mode delayed transitions.',
)
_MDP_EXECUTION_DELAY_FROZEN_TITLE = flags.DEFINE_string(
    'mdp_execution_delay_frozen_title',
    "App isn't responding",
    'Title shown in frozen-mode delayed transitions.',
)
_MDP_EXECUTION_DELAY_FROZEN_MESSAGE = flags.DEFINE_string(
    'mdp_execution_delay_frozen_message',
    'The app is taking longer than usual to respond.',
    'Message shown in frozen-mode delayed transitions.',
)
_MDP_FONT_SIZE_ENABLE = flags.DEFINE_boolean(
    'mdp_font_size_enable',
    False,
    'Whether to enable real emulator font scaling perturbation.',
)
_MDP_FONT_SIZE_ACTIVATION_MODE = flags.DEFINE_string(
    'mdp_font_size_activation_mode',
    'on_reset',
    "When to apply font scaling: 'on_reset' for a task-long device condition or"
    " 'on_steps' for a mid-episode perturbation.",
)
_MDP_FONT_SIZE_TRIGGER_STEPS = flags.DEFINE_string(
    'mdp_font_size_trigger_steps',
    '3',
    'Comma-separated action steps at which the font scale should change when'
    ' activation mode is on_steps.',
)
_MDP_FONT_SIZE_SCALE = flags.DEFINE_float(
    'mdp_font_size_scale',
    1.3,
    'Target Android system font scale.',
)
_MDP_FONT_SIZE_SETTLE_TIME_SEC = flags.DEFINE_float(
    'mdp_font_size_settle_time_sec',
    1.0,
    'Seconds to wait after changing the system font scale.',
)
_MDP_FONT_SIZE_RESTORE_ON_CLOSE = flags.DEFINE_boolean(
    'mdp_font_size_restore_on_close',
    True,
    'Whether to restore the original system font scale when the env closes.',
)
_MDP_DISPLAY_SIZE_DPI_ENABLE = flags.DEFINE_boolean(
    'mdp_display_size_dpi_enable',
    False,
    'Whether to enable real emulator display size / density perturbation.',
)
_MDP_DISPLAY_SIZE_DPI_ACTIVATION_MODE = flags.DEFINE_string(
    'mdp_display_size_dpi_activation_mode',
    'on_reset',
    "When to apply display size / density changes: 'on_reset' for a task-long"
    " device profile or 'on_steps' for a mid-episode perturbation.",
)
_MDP_DISPLAY_SIZE_DPI_TRIGGER_STEPS = flags.DEFINE_string(
    'mdp_display_size_dpi_trigger_steps',
    '3',
    'Comma-separated action steps at which display size / density should change'
    ' when activation mode is on_steps.',
)
_MDP_DISPLAY_SIZE_DPI_DENSITY_SCALE = flags.DEFINE_float(
    'mdp_display_size_dpi_density_scale',
    0.85,
    'Multiplier applied to wm density.',
)
_MDP_DISPLAY_SIZE_DPI_SIZE_SCALE = flags.DEFINE_float(
    'mdp_display_size_dpi_size_scale',
    0.94,
    'Multiplier applied to wm size.',
)
_MDP_DISPLAY_SIZE_DPI_SETTLE_TIME_SEC = flags.DEFINE_float(
    'mdp_display_size_dpi_settle_time_sec',
    1.2,
    'Seconds to wait after changing wm size / density.',
)
_MDP_DISPLAY_SIZE_DPI_RESTORE_ON_CLOSE = flags.DEFINE_boolean(
    'mdp_display_size_dpi_restore_on_close',
    True,
    'Whether to restore the original wm size / density when the env closes.',
)
_MDP_ORIENTATION_ENABLE = flags.DEFINE_boolean(
    'mdp_orientation_enable',
    False,
    'Whether to enable orientation switching perturbation.',
)
_MDP_ORIENTATION_ACTIVATION_MODE = flags.DEFINE_string(
    'mdp_orientation_activation_mode',
    'on_reset',
    "When to apply the orientation perturbation: 'on_reset' keeps a device"
    " orientation for the whole episode, while 'on_steps' can rotate during the"
    ' task.',
)
_MDP_ORIENTATION_TRIGGER_STEPS = flags.DEFINE_string(
    'mdp_orientation_trigger_steps',
    '3',
    'Comma-separated action steps at which orientation should change when'
    ' activation mode is on_steps.',
)
_MDP_ORIENTATION_SEQUENCE = flags.DEFINE_string(
    'mdp_orientation_sequence',
    'landscape',
    'Comma-separated orientation sequence, e.g. landscape or landscape,portrait.',
)
_MDP_ORIENTATION_SETTLE_TIME_SEC = flags.DEFINE_float(
    'mdp_orientation_settle_time_sec',
    1.0,
    'Seconds to wait after forcing a new orientation.',
)
_MDP_ORIENTATION_RESTORE_ON_CLOSE = flags.DEFINE_boolean(
    'mdp_orientation_restore_on_close',
    True,
    'Whether to restore the original orientation settings when the env closes.',
)
_MDP_LOCALE_DATE_FORMAT_ENABLE = flags.DEFINE_boolean(
    'mdp_locale_date_format_enable',
    False,
    'Whether to enable system date/time format perturbation.',
)
_MDP_LOCALE_DATE_FORMAT_ACTIVATION_MODE = flags.DEFINE_string(
    'mdp_locale_date_format_activation_mode',
    'on_reset',
    "When to apply date/time formatting changes: 'on_reset' for a task-long"
    " device profile or 'on_steps' for a mid-episode perturbation.",
)
_MDP_LOCALE_DATE_FORMAT_TRIGGER_STEPS = flags.DEFINE_string(
    'mdp_locale_date_format_trigger_steps',
    '3',
    'Comma-separated action steps at which the date/time format should change'
    ' when activation mode is on_steps.',
)
_MDP_LOCALE_DATE_FORMAT_TIME_FORMAT = flags.DEFINE_string(
    'mdp_locale_date_format_time_format',
    '24',
    "Target time format: '12' or '24'.",
)
_MDP_LOCALE_DATE_FORMAT_DATE_FORMAT = flags.DEFINE_string(
    'mdp_locale_date_format_date_format',
    'dd-MM-yyyy',
    'Target Android system date format string.',
)
_MDP_LOCALE_DATE_FORMAT_SETTLE_TIME_SEC = flags.DEFINE_float(
    'mdp_locale_date_format_settle_time_sec',
    1.0,
    'Seconds to wait after changing the system date/time format.',
)
_MDP_LOCALE_DATE_FORMAT_RESTORE_ON_CLOSE = flags.DEFINE_boolean(
    'mdp_locale_date_format_restore_on_close',
    True,
    'Whether to restore the original date/time format when the env closes.',
)
_MDP_STATE_RESET_ENABLE = flags.DEFINE_boolean(
    'mdp_state_reset_enable',
    False,
    'Whether to enable foreground app reset perturbation.',
)
_MDP_STATE_RESET_TRIGGER_STEPS = flags.DEFINE_string(
    'mdp_state_reset_trigger_steps',
    '3',
    'Comma-separated action steps at which the foreground app should be force-stopped.',
)
_MDP_STATE_RESET_RETURN_HOME = flags.DEFINE_boolean(
    'mdp_state_reset_return_home',
    True,
    'Whether to press Home after resetting the foreground app.',
)
_MDP_STATE_RESET_SETTLE_TIME_SEC = flags.DEFINE_float(
    'mdp_state_reset_settle_time_sec',
    1.0,
    'Seconds to wait after resetting the foreground app.',
)
_MDP_UI_THEME_ENABLE = flags.DEFINE_boolean(
    'mdp_ui_theme_enable',
    False,
    'Whether to enable real emulator UI theme switching.',
)
_MDP_UI_THEME_ACTIVATION_MODE = flags.DEFINE_string(
    'mdp_ui_theme_activation_mode',
    'on_reset',
    "When to apply theme switching: 'on_reset' for a task-long device"
    " condition or 'on_steps' for a mid-episode perturbation.",
)
_MDP_UI_THEME_TRIGGER_STEPS = flags.DEFINE_string(
    'mdp_ui_theme_trigger_steps',
    '3',
    'Comma-separated action steps at which the theme should switch when'
    ' activation mode is on_steps.',
)
_MDP_UI_THEME_MODE = flags.DEFINE_string(
    'mdp_ui_theme_mode',
    'dark',
    "Target theme to apply: 'light' or 'dark'.",
)
_MDP_UI_THEME_SETTLE_TIME_SEC = flags.DEFINE_float(
    'mdp_ui_theme_settle_time_sec',
    1.0,
    'Seconds to wait after changing the system theme.',
)
_MDP_UI_THEME_RESTORE_ON_CLOSE = flags.DEFINE_boolean(
    'mdp_ui_theme_restore_on_close',
    True,
    'Whether to restore the original theme when the env closes.',
)
_MDP_HELPER_INTERRUPTION_ENABLE = flags.DEFINE_boolean(
    'mdp_helper_interruption_enable',
    False,
    'Whether to trigger the standalone helper-app interruption.',
)
_MDP_HELPER_INTERRUPTION_TRIGGER_STEPS = flags.DEFINE_string(
    'mdp_helper_interruption_trigger_steps',
    '3',
    'Comma-separated action steps at which the helper interruption should launch.',
)
_MDP_HELPER_INTERRUPTION_KIND = flags.DEFINE_string(
    'mdp_helper_interruption_kind',
    'popup',
    "Helper interruption content type: 'popup', 'ad', 'update', or 'notification'.",
)
_MDP_HELPER_INTERRUPTION_SURFACE_STYLE = flags.DEFINE_string(
    'mdp_helper_interruption_surface_style',
    '',
    "Helper interruption surface style: 'dialog', 'bottom_sheet', 'interstitial', or 'banner'. Leave empty to infer by kind.",
)
_MDP_HELPER_INTERRUPTION_APP_NAME = flags.DEFINE_string(
    'mdp_helper_interruption_app_name',
    'Android System',
    'App name shown by the standalone helper interruption.',
)
_MDP_HELPER_INTERRUPTION_TITLE = flags.DEFINE_string(
    'mdp_helper_interruption_title',
    'Allow notifications?',
    'Title shown by the standalone helper interruption.',
)
_MDP_HELPER_INTERRUPTION_MESSAGE = flags.DEFINE_string(
    'mdp_helper_interruption_message',
    'Android System wants to send alerts while you use this app.',
    'Message shown by the standalone helper interruption.',
)
_MDP_HELPER_INTERRUPTION_PRIMARY_BUTTON = flags.DEFINE_string(
    'mdp_helper_interruption_primary_button',
    'Allow',
    'Primary button text for the standalone helper interruption.',
)
_MDP_HELPER_INTERRUPTION_SECONDARY_BUTTON = flags.DEFINE_string(
    'mdp_helper_interruption_secondary_button',
    'Not now',
    'Secondary button text for the standalone helper interruption.',
)
_MDP_HELPER_INTERRUPTION_BLOCKING = flags.DEFINE_boolean(
    'mdp_helper_interruption_blocking',
    True,
    'Whether the standalone helper interruption should block background interaction.',
)
_MDP_HELPER_INTERRUPTION_AUTO_DISMISS_MS = flags.DEFINE_integer(
    'mdp_helper_interruption_auto_dismiss_ms',
    0,
    'Auto-dismiss timeout for the standalone helper interruption in milliseconds.',
)
_MDP_HELPER_INTERRUPTION_PRIMARY_ACTION = flags.DEFINE_string(
    'mdp_helper_interruption_primary_action',
    '',
    "Primary button behavior: 'dismiss' or 'open_destination'. Leave empty to infer from the interruption copy.",
)
_MDP_HELPER_INTERRUPTION_SECONDARY_ACTION = flags.DEFINE_string(
    'mdp_helper_interruption_secondary_action',
    '',
    "Secondary button behavior: 'dismiss' or 'open_destination'. Leave empty to infer from the interruption copy.",
)
_MDP_HELPER_INTERRUPTION_PRIMARY_DESTINATION = flags.DEFINE_string(
    'mdp_helper_interruption_primary_destination',
    '',
    'Destination template to open when the primary button is configured to open a destination.',
)
_MDP_HELPER_INTERRUPTION_SECONDARY_DESTINATION = flags.DEFINE_string(
    'mdp_helper_interruption_secondary_destination',
    '',
    'Destination template to open when the secondary button is configured to open a destination.',
)
_MDP_HELPER_INTERRUPTION_PROFILE_POOL = flags.DEFINE_string(
    'mdp_helper_interruption_profile_pool',
    '',
    'Optional comma-separated helper interruption presets to sample from at each trigger step.',
)
_MDP_HELPER_INTERRUPTION_PROFILE_SEED = flags.DEFINE_integer(
    'mdp_helper_interruption_profile_seed',
    0,
    'Random seed used when choosing helper interruption presets.',
)
_MDP_HELPER_INTERRUPTION_PROFILE_STRATEGY = flags.DEFINE_string(
    'mdp_helper_interruption_profile_strategy',
    'cycle',
    "How to choose helper interruption presets: 'cycle' or 'random'.",
)
_MDP_HELPER_INTERRUPTION_WAIT_AFTER_LAUNCH_SEC = flags.DEFINE_float(
    'mdp_helper_interruption_wait_after_launch_sec',
    1.0,
    'Seconds to wait after launching the standalone helper interruption.',
)
_MDP_APP_HANG_ENABLE = flags.DEFINE_boolean(
    'mdp_app_hang_enable',
    False,
    'Whether to enable the app-hang / restart-required perturbation.',
)
_MDP_APP_HANG_TRIGGER_STEPS = flags.DEFINE_string(
    'mdp_app_hang_trigger_steps',
    '3',
    'Comma-separated action steps at which the app hang should trigger.',
)
_MDP_APP_HANG_TITLE = flags.DEFINE_string(
    'mdp_app_hang_title',
    "App isn't responding",
    'Title shown in the app-hang overlay.',
)
_MDP_APP_HANG_MESSAGE = flags.DEFINE_string(
    'mdp_app_hang_message',
    'This app stopped responding. Restart it to continue.',
    'Message shown in the app-hang overlay.',
)
_MDP_APP_HANG_RESTART_BUTTON = flags.DEFINE_string(
    'mdp_app_hang_restart_button',
    'Restart app',
    'Restart button text for the app-hang overlay.',
)
_MDP_APP_HANG_CLOSE_BUTTON = flags.DEFINE_string(
    'mdp_app_hang_close_button',
    'Close app',
    'Close button text for the app-hang overlay.',
)
_MDP_APP_HANG_SETTLE_TIME_SEC = flags.DEFINE_float(
    'mdp_app_hang_settle_time_sec',
    1.0,
    'Seconds to wait after restarting or closing the hung app.',
)
_MDP_APP_HANG_ALLOW_HOME_RECOVERY = flags.DEFINE_boolean(
    'mdp_app_hang_allow_home_recovery',
    True,
    'Whether navigate_home should clear the hang state.',
)
_MDP_APP_HANG_ALLOW_OPEN_APP_RECOVERY = flags.DEFINE_boolean(
    'mdp_app_hang_allow_open_app_recovery',
    True,
    'Whether open_app should clear the hang state.',
)
_MDP_APP_HANG_CLOSE_GOES_HOME = flags.DEFINE_boolean(
    'mdp_app_hang_close_goes_home',
    True,
    'Whether the Close app button should return the device to Home.',
)


def apply_mdp_perturbations(
    env: interface.AsyncEnv,
) -> interface.AsyncEnv:
  """Wraps an AndroidWorld env with the configured perturbation layers."""
  font_size_config = FontSizePerturbationConfig.from_flag_string(
      enabled=_MDP_FONT_SIZE_ENABLE.value,
      activation_mode=_MDP_FONT_SIZE_ACTIVATION_MODE.value,
      trigger_steps=_MDP_FONT_SIZE_TRIGGER_STEPS.value,
      font_scale=_MDP_FONT_SIZE_SCALE.value,
      settle_time_sec=_MDP_FONT_SIZE_SETTLE_TIME_SEC.value,
      restore_on_close=_MDP_FONT_SIZE_RESTORE_ON_CLOSE.value,
  )
  if font_size_config.enabled:
    env = FontSizePerturbationEnv(env, font_size_config)

  display_size_dpi_config = DisplaySizeDpiPerturbationConfig.from_flag_string(
      enabled=_MDP_DISPLAY_SIZE_DPI_ENABLE.value,
      activation_mode=_MDP_DISPLAY_SIZE_DPI_ACTIVATION_MODE.value,
      trigger_steps=_MDP_DISPLAY_SIZE_DPI_TRIGGER_STEPS.value,
      density_scale=_MDP_DISPLAY_SIZE_DPI_DENSITY_SCALE.value,
      size_scale=_MDP_DISPLAY_SIZE_DPI_SIZE_SCALE.value,
      settle_time_sec=_MDP_DISPLAY_SIZE_DPI_SETTLE_TIME_SEC.value,
      restore_on_close=_MDP_DISPLAY_SIZE_DPI_RESTORE_ON_CLOSE.value,
  )
  if display_size_dpi_config.enabled:
    env = DisplaySizeDpiPerturbationEnv(env, display_size_dpi_config)

  orientation_config = OrientationPerturbationConfig.from_flag_string(
      enabled=_MDP_ORIENTATION_ENABLE.value,
      activation_mode=_MDP_ORIENTATION_ACTIVATION_MODE.value,
      trigger_steps=_MDP_ORIENTATION_TRIGGER_STEPS.value,
      orientation_sequence=_MDP_ORIENTATION_SEQUENCE.value,
      settle_time_sec=_MDP_ORIENTATION_SETTLE_TIME_SEC.value,
      restore_on_close=_MDP_ORIENTATION_RESTORE_ON_CLOSE.value,
  )
  if orientation_config.enabled:
    env = OrientationPerturbationEnv(env, orientation_config)

  locale_date_format_config = LocaleDateFormatPerturbationConfig.from_flag_string(
      enabled=_MDP_LOCALE_DATE_FORMAT_ENABLE.value,
      activation_mode=_MDP_LOCALE_DATE_FORMAT_ACTIVATION_MODE.value,
      trigger_steps=_MDP_LOCALE_DATE_FORMAT_TRIGGER_STEPS.value,
      time_format=_MDP_LOCALE_DATE_FORMAT_TIME_FORMAT.value,
      date_format=_MDP_LOCALE_DATE_FORMAT_DATE_FORMAT.value,
      settle_time_sec=_MDP_LOCALE_DATE_FORMAT_SETTLE_TIME_SEC.value,
      restore_on_close=_MDP_LOCALE_DATE_FORMAT_RESTORE_ON_CLOSE.value,
  )
  if locale_date_format_config.enabled:
    env = LocaleDateFormatPerturbationEnv(env, locale_date_format_config)

  helper_interruption_config = HelperInterruptionPerturbationConfig.from_flag_string(
      enabled=_MDP_HELPER_INTERRUPTION_ENABLE.value,
      trigger_steps=_MDP_HELPER_INTERRUPTION_TRIGGER_STEPS.value,
      kind=_MDP_HELPER_INTERRUPTION_KIND.value,
      surface_style=_MDP_HELPER_INTERRUPTION_SURFACE_STYLE.value,
      app_name=_MDP_HELPER_INTERRUPTION_APP_NAME.value,
      title=_MDP_HELPER_INTERRUPTION_TITLE.value,
      message=_MDP_HELPER_INTERRUPTION_MESSAGE.value,
      primary_button=_MDP_HELPER_INTERRUPTION_PRIMARY_BUTTON.value,
      secondary_button=_MDP_HELPER_INTERRUPTION_SECONDARY_BUTTON.value,
      blocking=_MDP_HELPER_INTERRUPTION_BLOCKING.value,
      auto_dismiss_ms=_MDP_HELPER_INTERRUPTION_AUTO_DISMISS_MS.value,
      primary_action=_MDP_HELPER_INTERRUPTION_PRIMARY_ACTION.value,
      secondary_action=_MDP_HELPER_INTERRUPTION_SECONDARY_ACTION.value,
      primary_destination=_MDP_HELPER_INTERRUPTION_PRIMARY_DESTINATION.value,
      secondary_destination=_MDP_HELPER_INTERRUPTION_SECONDARY_DESTINATION.value,
      profile_pool=_MDP_HELPER_INTERRUPTION_PROFILE_POOL.value,
      profile_seed=_MDP_HELPER_INTERRUPTION_PROFILE_SEED.value,
      profile_strategy=_MDP_HELPER_INTERRUPTION_PROFILE_STRATEGY.value,
      wait_after_launch_sec=_MDP_HELPER_INTERRUPTION_WAIT_AFTER_LAUNCH_SEC.value,
  )
  if helper_interruption_config.enabled:
    env = HelperInterruptionPerturbationEnv(env, helper_interruption_config)

  app_hang_config = AppHangPerturbationConfig.from_flag_string(
      enabled=_MDP_APP_HANG_ENABLE.value,
      trigger_steps=_MDP_APP_HANG_TRIGGER_STEPS.value,
      title=_MDP_APP_HANG_TITLE.value,
      message=_MDP_APP_HANG_MESSAGE.value,
      restart_button=_MDP_APP_HANG_RESTART_BUTTON.value,
      close_button=_MDP_APP_HANG_CLOSE_BUTTON.value,
      settle_time_sec=_MDP_APP_HANG_SETTLE_TIME_SEC.value,
      allow_home_recovery=_MDP_APP_HANG_ALLOW_HOME_RECOVERY.value,
      allow_open_app_recovery=_MDP_APP_HANG_ALLOW_OPEN_APP_RECOVERY.value,
      close_goes_home=_MDP_APP_HANG_CLOSE_GOES_HOME.value,
  )
  if app_hang_config.enabled:
    env = AppHangPerturbationEnv(env, app_hang_config)

  execution_delay_config = ExecutionDelayPerturbationConfig.from_flag_string(
      enabled=_MDP_EXECUTION_DELAY_ENABLE.value,
      trigger_steps=_MDP_EXECUTION_DELAY_TRIGGER_STEPS.value,
      delay_steps=_MDP_EXECUTION_DELAY_STEPS.value,
      mode=_MDP_EXECUTION_DELAY_MODE.value,
      block_actions_while_pending=_MDP_EXECUTION_DELAY_BLOCK_ACTIONS.value,
      loading_text=_MDP_EXECUTION_DELAY_LOADING_TEXT.value,
      frozen_title=_MDP_EXECUTION_DELAY_FROZEN_TITLE.value,
      frozen_message=_MDP_EXECUTION_DELAY_FROZEN_MESSAGE.value,
  )
  if execution_delay_config.enabled:
    env = ExecutionDelayPerturbationEnv(env, execution_delay_config)

  state_reset_config = StateResetPerturbationConfig.from_flag_string(
      enabled=_MDP_STATE_RESET_ENABLE.value,
      trigger_steps=_MDP_STATE_RESET_TRIGGER_STEPS.value,
      return_home=_MDP_STATE_RESET_RETURN_HOME.value,
      settle_time_sec=_MDP_STATE_RESET_SETTLE_TIME_SEC.value,
  )
  if state_reset_config.enabled:
    env = StateResetPerturbationEnv(env, state_reset_config)

  ui_theme_config = UIThemePerturbationConfig.from_flag_string(
      enabled=_MDP_UI_THEME_ENABLE.value,
      activation_mode=_MDP_UI_THEME_ACTIVATION_MODE.value,
      trigger_steps=_MDP_UI_THEME_TRIGGER_STEPS.value,
      theme_mode=_MDP_UI_THEME_MODE.value,
      settle_time_sec=_MDP_UI_THEME_SETTLE_TIME_SEC.value,
      restore_on_close=_MDP_UI_THEME_RESTORE_ON_CLOSE.value,
  )
  if ui_theme_config.enabled:
    env = UIThemePerturbationEnv(env, ui_theme_config)

  action_delay_config = ActionDelayPerturbationConfig.from_values(
      enabled=_MDP_ACTION_DELAY_ENABLE.value,
      delay_probability=_MDP_ACTION_DELAY_PROBABILITY.value,
      delay_seconds=_MDP_ACTION_DELAY_SECONDS.value,
      seed=_MDP_ACTION_DELAY_SEED.value,
  )
  if action_delay_config.enabled:
    env = ActionDelayPerturbationEnv(env, action_delay_config)

  action_drop_config = ActionDropPerturbationConfig.from_values(
      enabled=_MDP_ACTION_DROP_ENABLE.value,
      drop_probability=_MDP_ACTION_DROP_PROBABILITY.value,
      seed=_MDP_ACTION_DROP_SEED.value,
  )
  if action_drop_config.enabled:
    env = ActionDropPerturbationEnv(env, action_drop_config)

  return env

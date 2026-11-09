"""Run AndroidWorld with a dedicated UI-TARS agent.

This runner intentionally lives beside, not inside, the existing GUI-Owl path.
It reuses the AndroidWorld environment and suite logic, but model prompting and
action parsing follow the official UI-TARS prompt template and the official
`ui_tars.action_parser` package.
"""

from __future__ import annotations

from collections.abc import Sequence
import os
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_ANDROID_WORLD_V3_ROOT = os.path.dirname(_THIS_DIR)
if _ANDROID_WORLD_V3_ROOT not in sys.path:
  sys.path.insert(0, _ANDROID_WORLD_V3_ROOT)

from absl import app
from absl import flags
from absl import logging
from android_world import checkpointer as checkpointer_lib
from android_world import episode_runner
from android_world import registry
from android_world import suite_utils
from android_world.agents import base_agent
from android_world.env import env_launcher
from android_world.env import interface
from android_world.task_evals import task_eval
from android_world.task_evals.miniwob import miniwob_base
from mdp_perturbation.runner_support import apply_mdp_perturbations
from ui_tars_runner.agent import UITarsAgent
from ui_tars_runner.client import UITarsOpenAIClient

logging.set_verbosity(logging.WARNING)

os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GRPC_TRACE'] = 'none'


def _find_adb_directory() -> str:
  potential_paths = [
      os.path.expanduser('~/Library/Android/sdk/platform-tools/adb'),
      os.path.expanduser('~/Android/Sdk/platform-tools/adb'),
      '/root/android/android_sdk/platform-tools/adb',
  ]
  for path in potential_paths:
    if os.path.isfile(path):
      return path
  raise EnvironmentError(
      'adb not found in the common Android SDK paths. Please install Android '
      'SDK and ensure adb is reachable.'
  )


_ADB_PATH = flags.DEFINE_string(
    'adb_path',
    _find_adb_directory(),
    'Path to adb.',
)
_EMULATOR_SETUP = flags.DEFINE_boolean(
    'perform_emulator_setup',
    False,
    'Whether to perform one-time emulator setup before evaluation.',
)
_DEVICE_CONSOLE_PORT = flags.DEFINE_integer(
    'console_port',
    5554,
    'Console port of the running Android device.',
)
_GRPC_PORT = flags.DEFINE_integer('grpc_port', 8554, 'gRPC port.')
_MODEL = flags.DEFINE_string('model', '', 'Served model name.')
_SUITE_FAMILY = flags.DEFINE_enum(
    'suite_family',
    registry.TaskRegistry.ANDROID_WORLD_FAMILY,
    [
        registry.TaskRegistry.ANDROID_WORLD_FAMILY,
        registry.TaskRegistry.MINIWOB_FAMILY_SUBSET,
        registry.TaskRegistry.MINIWOB_FAMILY,
        registry.TaskRegistry.ANDROID_FAMILY,
        registry.TaskRegistry.INFORMATION_RETRIEVAL_FAMILY,
    ],
    'Suite family to run.',
)
_TASK_RANDOM_SEED = flags.DEFINE_integer(
    'task_random_seed', 30, 'Random seed for task randomness.'
)
_TASKS = flags.DEFINE_list(
    'tasks',
    None,
    'Specific tasks to run. If unset, runs the whole suite family.',
)
_N_TASK_COMBINATIONS = flags.DEFINE_integer(
    'n_task_combinations',
    1,
    'Number of task instances to run for each task template.',
)
_CHECKPOINT_DIR = flags.DEFINE_string(
    'checkpoint_dir',
    '',
    'Optional checkpoint directory.',
)
_OUTPUT_PATH = flags.DEFINE_string(
    'output_path',
    os.path.expanduser('~/android_world/runs'),
    'Run output directory when no checkpoint dir is provided.',
)
_TRAJ_OUTPUT_PATH = flags.DEFINE_string(
    'traj_output_path',
    '',
    'Directory used to save per-task screenshots and actions.',
)
_API_KEY = flags.DEFINE_string('api_key', '', 'API key for the model service.')
_BASE_URL = flags.DEFINE_string(
    'base_url',
    '',
    'OpenAI-compatible base URL for the model service.',
)
_AGENT_NAME = flags.DEFINE_string(
    'agent_name',
    'ui_tars',
    'Agent label used in logs.',
)
_FIXED_TASK_SEED = flags.DEFINE_boolean(
    'fixed_task_seed',
    False,
    'Whether to reuse the same task seed across task combinations.',
)
_UI_TARS_PARSER_MODEL_TYPE = flags.DEFINE_string(
    'ui_tars_parser_model_type',
    'qwen2vl',
    'Model type passed to the official ui-tars action parser. '
    'Use qwen2vl for UI-TARS-7B-DPO; if your installed parser expects a '
    'different variant, switch to qwen25vl.',
)
_UI_TARS_LANGUAGE = flags.DEFINE_string(
    'ui_tars_language',
    'English',
    'Language placeholder inserted into the official UI-TARS prompt.',
)
_UI_TARS_TEMPERATURE = flags.DEFINE_float(
    'ui_tars_temperature',
    0.0,
    'Sampling temperature used for UI-TARS inference.',
)
_UI_TARS_MAX_TOKENS = flags.DEFINE_integer(
    'ui_tars_max_tokens',
    400,
    'Maximum number of tokens requested from the model service.',
)
_UI_TARS_MAX_RETRY = flags.DEFINE_integer(
    'ui_tars_max_retry',
    10,
    'Maximum number of retry attempts for model calls.',
)
_UI_TARS_HISTORY_WINDOW = flags.DEFINE_integer(
    'ui_tars_history_window',
    8,
    'How many previous action lines to keep in the prompt history.',
)
_EPISODE_STEP_BUDGET_MULTIPLIER = flags.DEFINE_float(
    'episode_step_budget_multiplier',
    15.0,
    'Multiplier applied to task complexity when allocating the episode max step budget.',
)

_MINIWOB_TRANSITION_PAUSE = 0.2
_MINIWOB_ADDITIONAL_GUIDELINES = [
    (
        'This task is running in a mock app, you must stay in this app and '
        'DO NOT use the `navigate_home` action.'
    ),
]


def _get_agent(
    env: interface.AsyncEnv,
    family: str | None = None,
) -> base_agent.EnvironmentInteractingAgent:
  del family
  agent = UITarsAgent(
      env=env,
      client=UITarsOpenAIClient(
          api_key=_API_KEY.value,
          base_url=_BASE_URL.value,
          model_name=_MODEL.value,
          max_retry=_UI_TARS_MAX_RETRY.value,
          temperature=_UI_TARS_TEMPERATURE.value,
          max_tokens=_UI_TARS_MAX_TOKENS.value,
      ),
      parser_model_type=_UI_TARS_PARSER_MODEL_TYPE.value,
      prompt_language=_UI_TARS_LANGUAGE.value,
      history_window=_UI_TARS_HISTORY_WINDOW.value,
      name=_AGENT_NAME.value,
      output_path=_TRAJ_OUTPUT_PATH.value,
  )
  agent.name = _AGENT_NAME.value
  return agent


def _build_termination_fn(
    task: task_eval.TaskEval,
):
  if task.name.lower().startswith('miniwob'):
    return miniwob_base.is_episode_terminated

  def _termination_fn(env: interface.AsyncEnv) -> bool:
    try:
      return task.is_successful(env) >= 1.0
    except Exception as exc:  # pylint: disable=broad-exception-caught
      logging.warning(
          'Task success check failed during episode for %s: %s',
          task.name,
          exc,
      )
      return False

  return _termination_fn


def _run_suite_with_task_success_termination(
    suite: suite_utils.Suite,
    agent: base_agent.EnvironmentInteractingAgent,
    checkpointer: checkpointer_lib.Checkpointer,
):
  def run_episode(task: task_eval.TaskEval) -> episode_runner.EpisodeResult:
    return episode_runner.run_episode(
        goal=task.goal,
        agent=agent,
        max_n_steps=suite_utils._allocate_step_budget(task.complexity),
        start_on_home_screen=task.start_on_home_screen,
        termination_fn=_build_termination_fn(task),
    )

  return suite_utils._run_task_suite(
      suite,
      run_episode,
      agent.env,
      checkpointer=checkpointer,
      demo_mode=False,
      agent_name=agent.name,
      return_full_episode_data=False,
      process_episodes_fn=None,
      check_episode_fn=None,
  )


def _main() -> None:
  env = env_launcher.load_and_setup_env(
      console_port=_DEVICE_CONSOLE_PORT.value,
      emulator_setup=_EMULATOR_SETUP.value,
      adb_path=_ADB_PATH.value,
      grpc_port=_GRPC_PORT.value,
  )
  env = apply_mdp_perturbations(env)

  suite_utils.set_step_budget_multiplier(_EPISODE_STEP_BUDGET_MULTIPLIER.value)
  task_registry = registry.TaskRegistry()
  suite = suite_utils.create_suite(
      task_registry.get_registry(family=_SUITE_FAMILY.value),
      n_task_combinations=_N_TASK_COMBINATIONS.value,
      seed=_TASK_RANDOM_SEED.value,
      tasks=_TASKS.value,
      use_identical_params=_FIXED_TASK_SEED.value,
  )
  suite.suite_family = _SUITE_FAMILY.value

  agent = _get_agent(env, _SUITE_FAMILY.value)
  agent.get_task_name(suite)
  if _SUITE_FAMILY.value.startswith('miniwob'):
    agent.transition_pause = _MINIWOB_TRANSITION_PAUSE
  else:
    agent.transition_pause = None

  if _CHECKPOINT_DIR.value:
    checkpoint_dir = _CHECKPOINT_DIR.value
  else:
    checkpoint_dir = checkpointer_lib.create_run_directory(_OUTPUT_PATH.value)

  print(
      f'Starting eval with agent {_AGENT_NAME.value} and writing to'
      f' {checkpoint_dir}'
  )
  _run_suite_with_task_success_termination(
      suite,
      agent,
      checkpointer=checkpointer_lib.IncrementalCheckpointer(checkpoint_dir),
  )
  print(
      f'Finished running agent {_AGENT_NAME.value} on {_SUITE_FAMILY.value}'
      f' family. Wrote to {checkpoint_dir}.'
  )
  env.close()


def main(argv: Sequence[str]) -> None:
  del argv
  _main()


if __name__ == '__main__':
  app.run(main)

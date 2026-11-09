"""UI-TARS agent for AndroidWorld."""

from __future__ import annotations

import json
import os
import pprint
from typing import Any

from PIL import Image

from android_world.agents import base_agent
from android_world.agents import new_json_action as json_action
from android_world.env import interface
from ui_tars_runner.action_adapter import convert_ui_tars_action_to_androidworld
from ui_tars_runner.client import UITarsOpenAIClient
from ui_tars_runner.official_prompt import MOBILE_USE_DOUBAO
from ui_tars_runner.parser import extract_action_line
from ui_tars_runner.parser import extract_thought
from ui_tars_runner.parser import parse_response_with_official_ui_tars


def _non_null_action_dict(action: json_action.JSONAction) -> dict[str, Any]:
  return {
      key: value
      for key, value in action.__dict__.items()
      if value is not None
  }


class UITarsAgent(base_agent.EnvironmentInteractingAgent):
  """Environment-interacting Android agent backed by the official UI-TARS parser."""

  def __init__(
      self,
      env: interface.AsyncEnv,
      client: UITarsOpenAIClient,
      parser_model_type: str,
      prompt_language: str = 'English',
      history_window: int = 8,
      name: str = 'UI-TARS',
      output_path: str = '',
  ):
    super().__init__(env, name)
    self._client = client
    self._parser_model_type = parser_model_type
    self._prompt_language = prompt_language
    self._history_window = max(1, history_window)
    self.output_path = output_path
    self.task_name: dict[str, str] = {}
    self._records: list[dict[str, Any]] = []
    self._history_lines: list[str] = []

    if self.output_path:
      os.makedirs(self.output_path, exist_ok=True)

  def get_task_name(self, suite) -> None:
    for name, instances in suite.items():
      self.task_name[instances[0].goal] = name

  def reset(self, go_home: bool = False) -> None:
    super().reset(go_home)
    self.env.hide_automation_ui()
    self._records.clear()
    self._history_lines.clear()

  def _task_output_dir(self, goal: str) -> str | None:
    if not self.output_path:
      return None
    task_dir_name = self.task_name.get(goal, goal.replace(' ', '_')[:50])
    task_output_dir = os.path.join(self.output_path, task_dir_name)
    os.makedirs(task_output_dir, exist_ok=True)
    return task_output_dir

  def _build_prompt_text(self, goal: str) -> str:
    if self._history_lines:
      history_lines = self._history_lines[-self._history_window :]
      instruction = (
          f'{goal}\n\nPrevious Actions:\n'
          + '\n'.join(
              f'Step {idx + 1}: {line}'
              for idx, line in enumerate(history_lines)
          )
      )
    else:
      instruction = f'{goal}\n\nPrevious Actions:\nNone'
    return MOBILE_USE_DOUBAO.format(
        language=self._prompt_language,
        instruction=instruction,
    )

  def _flush_records(self, task_output_dir: str) -> None:
    action_file = os.path.join(task_output_dir, 'action.jsonl')
    with open(action_file, 'w', encoding='utf-8') as f:
      for record in self._records:
        f.write(json.dumps(record, ensure_ascii=False) + '\n')

  def _print_debug_block(self, title: str, payload: Any) -> None:
    print(f'========== {title} ==========', flush=True)
    if payload is None:
      print('None', flush=True)
      return
    if isinstance(payload, (dict, list, tuple)):
      pprint.pprint(payload, width=120, compact=False, sort_dicts=False)
      return
    print(payload, flush=True)

  def step(self, goal: str) -> base_agent.AgentInteractionResult:
    result: dict[str, Any] = {}
    step_idx = len(self._records)
    state = self.get_post_transition_state()
    result['ui_elements'] = state.ui_elements
    result['screenshot'] = state.pixels

    screenshot = Image.fromarray(state.pixels)
    task_output_dir = self._task_output_dir(goal)
    screenshot_file = f'screenshot_{step_idx}.png'
    if task_output_dir:
      screenshot_file = os.path.join(task_output_dir, screenshot_file)
    screenshot.save(screenshot_file)

    prompt_text = self._build_prompt_text(goal)
    max_steps = getattr(self, '_max_steps', None)
    task_label = self.task_name.get(goal, goal.replace(' ', '_')[:50])
    step_header = f'UI-TARS STEP {step_idx + 1}'
    if max_steps is not None:
      step_header += f'/{max_steps}'
    step_header += f' | {task_label}'
    self._print_debug_block(step_header, '')
    self._print_debug_block('UI-TARS GOAL', goal)
    self._print_debug_block('UI-TARS SCREENSHOT', screenshot_file)
    self._print_debug_block('UI-TARS PROMPT', prompt_text)

    response, messages, raw_response = self._client.predict(
        prompt_text=prompt_text,
        screenshot_file=screenshot_file,
    )
    result['prompt_text'] = prompt_text
    result['messages'] = messages
    result['raw_response'] = response

    thought = extract_thought(response)
    action_line = extract_action_line(response) or 'unparsed_action'
    result['thought'] = thought
    result['action_line'] = action_line
    self._print_debug_block('UI-TARS RAW RESPONSE', response)
    self._print_debug_block('UI-TARS THOUGHT', thought)
    self._print_debug_block('UI-TARS ACTION LINE', action_line)

    parsed_action = None
    used_model_type = None
    conversion = None
    action = json_action.JSONAction(action_type=json_action.UNKNOWN)

    try:
      parsed_actions, used_model_type = parse_response_with_official_ui_tars(
          response=response,
          image_width=state.pixels.shape[1],
          image_height=state.pixels.shape[0],
          model_type=self._parser_model_type,
      )
      parsed_action = parsed_actions[0]
      conversion = convert_ui_tars_action_to_androidworld(
          parsed_action,
          screen_size=(state.pixels.shape[1], state.pixels.shape[0]),
      )
      action = conversion.action
      if conversion.terminal_text:
        self.env.interaction_cache = conversion.terminal_text
      self.env.execute_action(action)
    except Exception as exc:
      result['parse_error'] = str(exc)
      self._print_debug_block('UI-TARS PARSE ERROR', str(exc))

    record = {
        'step': step_idx,
        'goal': goal,
        'thought': thought,
        'action_line': action_line,
        'response': response,
        'parsed_action': parsed_action,
        'parser_model_type': used_model_type,
        'executed_action': _non_null_action_dict(action),
    }
    self._records.append(record)
    self._history_lines.append(
        conversion.action_summary if conversion is not None else action_line
    )

    result['parsed_action'] = parsed_action
    result['parser_model_type'] = used_model_type
    result['action'] = action
    result['raw_completion'] = raw_response
    self._print_debug_block(
        'UI-TARS PARSED ACTION',
        {
            'parser_model_type': used_model_type,
            'parsed_action': parsed_action,
        },
    )
    self._print_debug_block('UI-TARS EXECUTED ACTION', _non_null_action_dict(action))

    if task_output_dir:
      self._flush_records(task_output_dir)

    return base_agent.AgentInteractionResult(
        done=action.action_type == json_action.STATUS,
        data=result,
    )

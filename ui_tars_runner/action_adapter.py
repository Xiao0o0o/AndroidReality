"""Maps official UI-TARS parsed actions to AndroidWorld JSONAction."""

from __future__ import annotations

import ast
import dataclasses
import re
from typing import Any

from android_world.agents import new_json_action as json_action


@dataclasses.dataclass(frozen=True)
class UITarsActionConversion:
  action: json_action.JSONAction
  action_summary: str
  terminal_text: str | None = None


_OPEN_APP_NAME_ALIASES = {
    'file manager': 'files',
    'filemanager': 'files',
    'simpledrawpro': 'simple draw pro',
}


def _extract_action_type(parsed_action: dict[str, Any]) -> str:
  action_type = parsed_action.get('action_type') or parsed_action.get('action')
  if not action_type:
    raise ValueError(f'Parsed UI-TARS action missing action_type: {parsed_action}')
  return str(action_type)


def _extract_inputs(parsed_action: dict[str, Any]) -> dict[str, Any]:
  action_inputs = parsed_action.get('action_inputs')
  if isinstance(action_inputs, dict):
    return action_inputs
  if action_inputs is None:
    return {}
  raise ValueError(f'Unexpected UI-TARS action_inputs payload: {action_inputs!r}')


def _parse_numeric_sequence(value: Any) -> list[float]:
  if isinstance(value, (list, tuple)):
    return [float(v) for v in value]
  if isinstance(value, str):
    cleaned = (
        value.replace('<|box_start|>', '')
        .replace('<|box_end|>', '')
        .replace('<point>', '')
        .replace('</point>', '')
        .strip()
    )
    point_match = re.fullmatch(r'\(?\s*(-?\d+(?:\.\d+)?)\s*,?\s+(-?\d+(?:\.\d+)?)\s*\)?', cleaned)
    if point_match:
      return [float(point_match.group(1)), float(point_match.group(2))]
    literal = ast.literal_eval(cleaned)
    if isinstance(literal, (list, tuple)):
      return [float(v) for v in literal]
  raise ValueError(f'Could not parse numeric UI-TARS coordinates from: {value!r}')


def _point_from_box(box_like: Any, width: int, height: int) -> tuple[int, int]:
  values = _parse_numeric_sequence(box_like)
  if len(values) == 2:
    x_val, y_val = values
    if max(abs(x_val), abs(y_val)) <= 1.0:
      return int(round(x_val * width)), int(round(y_val * height))
    return int(round(x_val)), int(round(y_val))
  if len(values) != 4:
    raise ValueError(f'Expected 2 or 4 coordinates, got: {values!r}')
  x1, y1, x2, y2 = values
  if max(abs(x1), abs(y1), abs(x2), abs(y2)) <= 1.0:
    return (
        int(round(((x1 + x2) / 2.0) * width)),
        int(round(((y1 + y2) / 2.0) * height)),
    )
  return int(round((x1 + x2) / 2.0)), int(round((y1 + y2) / 2.0))


def _first_present(inputs: dict[str, Any], *keys: str) -> Any:
  for key in keys:
    if key in inputs and inputs[key] is not None:
      return inputs[key]
  return None


def _normalize_open_app_name(app_name: str) -> str:
  normalized = re.sub(r'\s+', ' ', app_name).strip()
  collapsed = re.sub(r'[\s_-]+', '', normalized).lower()
  return _OPEN_APP_NAME_ALIASES.get(collapsed, normalized)


def convert_ui_tars_action_to_androidworld(
    parsed_action: dict[str, Any],
    screen_size: tuple[int, int],
) -> UITarsActionConversion:
  width, height = screen_size
  action_type = _extract_action_type(parsed_action)
  inputs = _extract_inputs(parsed_action)

  if action_type == 'click':
    point = _first_present(inputs, 'start_box', 'point', 'start_point')
    x, y = _point_from_box(point, width, height)
    return UITarsActionConversion(
        action=json_action.JSONAction(action_type=json_action.CLICK, x=x, y=y),
        action_summary=f'click({x}, {y})',
    )

  if action_type == 'long_press':
    point = _first_present(inputs, 'start_box', 'point', 'start_point')
    x, y = _point_from_box(point, width, height)
    return UITarsActionConversion(
        action=json_action.JSONAction(
            action_type=json_action.LONG_PRESS, x=x, y=y
        ),
        action_summary=f'long_press({x}, {y})',
    )

  if action_type == 'type':
    text = str(_first_present(inputs, 'content', 'text') or '')
    return UITarsActionConversion(
        action=json_action.JSONAction(
            action_type=json_action.INPUT_TEXT, text=text
        ),
        action_summary=f"type({text!r})",
    )

  if action_type == 'scroll':
    direction = str(_first_present(inputs, 'direction') or '').strip().lower()
    return UITarsActionConversion(
        action=json_action.JSONAction(
            action_type=json_action.SCROLL, direction=direction
        ),
        action_summary=f"scroll(direction={direction!r})",
    )

  if action_type == 'drag':
    start = _first_present(inputs, 'start_box', 'start_point')
    end = _first_present(inputs, 'end_box', 'end_point')
    start_x, start_y = _point_from_box(start, width, height)
    end_x, end_y = _point_from_box(end, width, height)
    return UITarsActionConversion(
        action=json_action.JSONAction(
            action_type=json_action.SWIPE,
            direction=[start_x, start_y, end_x, end_y],
        ),
        action_summary=f'drag({start_x}, {start_y}) -> ({end_x}, {end_y})',
    )

  if action_type == 'open_app':
    app_name = str(_first_present(inputs, 'app_name', 'text', 'content') or '')
    app_name = _normalize_open_app_name(app_name)
    return UITarsActionConversion(
        action=json_action.JSONAction(
            action_type=json_action.OPEN_APP, app_name=app_name
        ),
        action_summary=f"open_app({app_name!r})",
    )

  if action_type == 'press_home':
    return UITarsActionConversion(
        action=json_action.JSONAction(action_type=json_action.NAVIGATE_HOME),
        action_summary='press_home()',
    )

  if action_type == 'press_back':
    return UITarsActionConversion(
        action=json_action.JSONAction(action_type=json_action.NAVIGATE_BACK),
        action_summary='press_back()',
    )

  if action_type == 'wait':
    return UITarsActionConversion(
        action=json_action.JSONAction(action_type=json_action.WAIT),
        action_summary='wait()',
    )

  if action_type == 'finished':
    terminal_text = _first_present(inputs, 'content', 'text')
    terminal_text = str(terminal_text) if terminal_text is not None else None
    return UITarsActionConversion(
        action=json_action.JSONAction(
            action_type=json_action.STATUS, goal_status='task_complete'
        ),
        action_summary=f'finished({terminal_text!r})',
        terminal_text=terminal_text,
    )

  return UITarsActionConversion(
      action=json_action.JSONAction(action_type=json_action.UNKNOWN),
      action_summary=f'unknown({action_type})',
  )

"""Official UI-TARS parser bridge."""

from __future__ import annotations

import importlib
import re
from typing import Any


class UITarsDependencyError(RuntimeError):
  """Raised when the official ui-tars package is unavailable."""


class UITarsParseError(RuntimeError):
  """Raised when the official parser cannot decode a model response."""


def extract_thought(response: str) -> str | None:
  match = re.search(r'Thought:\s*(.*?)(?:\nAction:|\Z)', response, re.DOTALL)
  if not match:
    return None
  return match.group(1).strip() or None


def extract_action_line(response: str) -> str | None:
  match = re.search(r'Action:\s*(.*)', response, re.DOTALL)
  if not match:
    return None
  return match.group(1).strip() or None


def _load_official_parser():
  try:
    module = importlib.import_module('ui_tars.action_parser')
  except ImportError as exc:
    raise UITarsDependencyError(
        'The official `ui-tars` package is required. Install it in the active '
        'environment with `pip install ui-tars` before running this runner.'
    ) from exc

  parser = getattr(module, 'parse_action_to_structure_output', None)
  if parser is None:
    raise UITarsDependencyError(
        'The installed `ui-tars` package does not export '
        '`parse_action_to_structure_output`.'
    )
  return parser


def parse_response_with_official_ui_tars(
    response: str,
    image_width: int,
    image_height: int,
    model_type: str,
) -> tuple[list[dict[str, Any]], str]:
  """Parses a UI-TARS response using the official parser package."""
  parser = _load_official_parser()
  errors: list[str] = []
  candidates: list[str | None] = []
  for candidate in (model_type, 'qwen2vl', 'qwen25vl', None):
    if candidate not in candidates:
      candidates.append(candidate)

  for candidate in candidates:
    try:
      kwargs = {
          'factor': 1000,
          'origin_resized_height': image_height,
          'origin_resized_width': image_width,
      }
      if candidate is not None:
        kwargs['model_type'] = candidate
      parsed = parser(response, **kwargs)
      if not parsed:
        raise UITarsParseError('Official parser returned no actions.')
      if isinstance(parsed, dict):
        return [parsed], candidate or 'default'
      return list(parsed), candidate or 'default'
    except Exception as exc:
      errors.append(f'{candidate or "default"}: {exc}')

  raise UITarsParseError(
      'Official UI-TARS parser could not decode the response. '
      + ' | '.join(errors)
  )


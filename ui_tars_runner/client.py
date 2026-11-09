"""OpenAI-compatible client for UI-TARS serving endpoints."""

from __future__ import annotations

import base64
import time
from pathlib import Path
from typing import Any

from openai import OpenAI


def _image_file_to_data_url(image_path: str) -> str:
  image_bytes = Path(image_path).read_bytes()
  encoded = base64.b64encode(image_bytes).decode('utf-8')
  return f'data:image/png;base64,{encoded}'


class UITarsOpenAIClient:
  """Thin OpenAI-compatible client following the official UI-TARS usage."""

  RETRY_WAITING_SECONDS = 20

  def __init__(
      self,
      api_key: str,
      base_url: str,
      model_name: str,
      max_retry: int = 10,
      temperature: float = 0.0,
      max_tokens: int = 400,
  ):
    self.max_retry = max(1, min(max_retry, 10))
    self.temperature = temperature
    self.max_tokens = max_tokens
    self.model = model_name
    self._client = OpenAI(api_key=api_key, base_url=base_url, timeout=30)

  def build_messages(
      self,
      prompt_text: str,
      screenshot_file: str,
  ) -> list[dict[str, Any]]:
    return [
        {
            'role': 'system',
            'content': [{'type': 'text', 'text': 'You are a helpful assistant.'}],
        },
        {
            'role': 'user',
            'content': [
                {'type': 'text', 'text': prompt_text},
                {
                    'type': 'image_url',
                    'image_url': {'url': _image_file_to_data_url(screenshot_file)},
                },
            ],
        },
    ]

  def predict(
      self,
      prompt_text: str,
      screenshot_file: str,
  ) -> tuple[str, list[dict[str, Any]], Any]:
    payload = self.build_messages(prompt_text, screenshot_file)
    counter = self.max_retry
    wait_seconds = self.RETRY_WAITING_SECONDS

    while counter > 0:
      try:
        request_kwargs = {
            'model': self.model,
            'messages': payload,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
        }
        if self.temperature > 0:
          request_kwargs['top_p'] = 0.95
        chat_completion = self._client.chat.completions.create(**request_kwargs)
        return chat_completion.choices[0].message.content or '', payload, chat_completion
      except Exception:
        counter -= 1
        if counter <= 0:
          raise
        time.sleep(wait_seconds)

    raise RuntimeError('Unreachable UI-TARS client retry state.')


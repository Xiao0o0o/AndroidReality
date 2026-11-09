# Copyright 2024 The android_world Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Some LLM inference interface."""

import abc
import time
from typing import Any, Optional
import numpy as np
from PIL import Image
from openai import OpenAI
from qwen_vl_utils import smart_resize
from io import BytesIO
import base64
import os
import json
import re

ERROR_CALLING_LLM = 'Error calling LLM'
_DEFAULT_MIN_PIXELS = 3136
_DEFAULT_MAX_PIXELS = 10035200


def _get_mm_pixel_limits() -> tuple[int, int]:
  min_pixels = int(os.environ.get("GUIOWL_MIN_PIXELS", _DEFAULT_MIN_PIXELS))
  max_pixels = int(os.environ.get("GUIOWL_MAX_PIXELS", _DEFAULT_MAX_PIXELS))
  if min_pixels <= 0:
    min_pixels = _DEFAULT_MIN_PIXELS
  if max_pixels < min_pixels:
    max_pixels = max(min_pixels, _DEFAULT_MAX_PIXELS)
  return min_pixels, max_pixels

def pil_to_base64(image):
    buffer = BytesIO()
    image.save(buffer, format="PNG") 
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def image_to_base64(image_path):
  dummy_image = Image.open(image_path)
  min_pixels, max_pixels = _get_mm_pixel_limits()
  resized_height, resized_width  = smart_resize(dummy_image.height,
      dummy_image.width,
      factor=28,
      min_pixels=min_pixels,
      max_pixels=max_pixels,)
  dummy_image = dummy_image.resize((resized_width, resized_height))
  return f"data:image/png;base64,{pil_to_base64(dummy_image)}"

class LlmWrapper(abc.ABC):
  """Abstract interface for (text only) LLM."""

  @abc.abstractmethod
  def predict(
      self,
      text_prompt: str,
  ) -> tuple[str, Optional[bool], Any]:
    """Calling multimodal LLM with a prompt and a list of images.

    Args:
      text_prompt: Text prompt.

    Returns:
      Text output, is_safe, and raw output.
    """

class MultimodalLlmWrapper(abc.ABC):
  """Abstract interface for Multimodal LLM."""

  @abc.abstractmethod
  def predict_mm(
      self, text_prompt: str, images: list[np.ndarray], messages = None
  ) -> tuple[str, Optional[bool], Any]:
    """Calling multimodal LLM with a prompt and a list of images.

    Args:
      text_prompt: Text prompt.
      images: List of images as numpy ndarray.

    Returns:
      Text output and raw output.
    """

class GUIOwlWrapper(LlmWrapper, MultimodalLlmWrapper):

    RETRY_WAITING_SECONDS = 20

    def __init__(
            self,
            api_key: str,
            base_url: str,
            model_name: str,
            max_retry: int = 10,
            temperature: float = 0.0,
    ):
        if max_retry <= 0:
            max_retry = 10
            print('Max_retry must be positive. Reset it to 3')
        self.max_retry = min(max_retry, 10)
        self.temperature = temperature
        self.model = model_name
        self.bot = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=30
        )

    def convert_messages_format_to_openaiurl(self, messages):
      converted_messages = []
      for message in messages:
          new_content = []
          for item in message['content']:
              if list(item.keys())[0] == 'text':
                  new_content.append({'type': 'text', 'text': item['text']})
              elif list(item.keys())[0] == 'image':
                new_content.append({'type': 'image_url', 'image_url': {'url': image_to_base64(item['image'])}})
          converted_messages.append({'role': message['role'], 'content': new_content})

      return converted_messages
    
    def predict(
            self,
            text_prompt: str,
    ) -> tuple[str, Optional[bool], Any]:
        return self.predict_mm(text_prompt, [])

    # def predict_mm(
    #         self, text_prompt: str, images: list[np.ndarray], messages = None
    # ) -> tuple[str, Optional[bool], Any]:
        
    #     if messages is None:
    #       payload = [
    #           {
    #               "role": "user",
    #               "content": [
    #                   {"text": text_prompt},
    #               ]
    #           }
    #       ]
          
    #       for image in images:
    #         payload[0]['content'].append({
    #             'image': image
    #         })
    #     else:
    #       payload = messages
            
    #     payload = self.convert_messages_format_to_openaiurl(payload)

    #     counter = self.max_retry
    #     wait_seconds = self.RETRY_WAITING_SECONDS
    #     while counter > 0:
    #         try:
    #           chat_completion_from_url = self.bot.chat.completions.create(model=self.model, messages=payload, **{})
    #           return (chat_completion_from_url.choices[0].message.content, payload, chat_completion_from_url)
    #         except Exception as e:
    #             time.sleep(wait_seconds)
    #             wait_seconds *= 1
    #             counter -= 1
    #             print('Error calling LLM, will retry soon...')
    #             print(e)
    #     return ERROR_CALLING_LLM, None, None
    def predict_mm(
        self, text_prompt: str, images: list[np.ndarray], messages = None ) -> tuple[str, Optional[bool], Any]:
        # 简单的调用计数器，方便 log 里区分第几次 LLM 调用
        if not hasattr(self, "seq_id"):
            self.seq_id = 0
        if messages is None:
            payload = [
                {
                    "role": "user",
                    "content": [
                        {"text": text_prompt},
                        ]
                    }
                ]
            for image in images:
                payload[0]['content'].append({
                    'image': image
                })
        else:
            payload = messages
          
        # 转成 OpenAI/vLLM 兼容的 messages 格式
        payload = self.convert_messages_format_to_openaiurl(payload)
        counter = self.max_retry
        wait_seconds = self.RETRY_WAITING_SECONDS
        while counter > 0:
            try:
                user_text = ""
                self.seq_id += 1
                chat_completion_from_url = self.bot.chat.completions.create(
                    model=self.model,
                    messages=payload,
                    temperature=self.temperature,
                    top_p=1.0 if self.temperature == 0 else 0.95,
                    logprobs=True,    # 开启 token logprob
                    top_logprobs=1,   # vLLM 一般要求同时设置
                )
                
                choice = chat_completion_from_url.choices[0]
                prediction = choice.message.content
                
                token_logprobs = []
                lp = getattr(choice, "logprobs", None)
                if lp is not None:
                  
                    if hasattr(lp, "content"):
                        for tok in lp.content:
                            try:
                                token_logprobs.append({
                                    "token": tok.token,
                                    "logprob": float(tok.logprob),
                                })
                            except Exception:
                                continue
                
                    elif isinstance(lp, dict):
                        toks = lp.get("tokens") or []
                        lps = lp.get("token_logprobs") or []
                        for t, v in zip(toks, lps):
                            try:
                                token_logprobs.append({
                                    "token": t,
                                    "logprob": float(v),
                                })
                            except Exception:
                                continue

                if not token_logprobs:
                    token_logprobs = None

                try:
                    base_dir = os.environ.get("VLM_TOKEN_LOG_DIR", "vlm_token_logs_android")
                    os.makedirs(base_dir, exist_ok=True)

                    # user_text = ""
                    # for m in payload:
                    #     if m.get("role") == "user":
                    #         content = m.get("content", [])
                    #         if isinstance(content, list):
                    #             for part in content:
                    #                 if isinstance(part, dict) and part.get("type") in (None, "text"):
                    #                     user_text = part.get("text", "")
                    #                     if user_text:
                    #                         break
                    #         elif isinstance(content, str):
                    #             user_text = content
                    #         if user_text:
                    #             break

                    #safe_name = re.sub(r"[^\w\-]+", "_", user_text)[:50] or "default"
                    #log_path = os.path.join(base_dir, f"{safe_name}_token_logprobs.jsonl")
                    task_name = os.environ.get("ANDROIDWORLD_TASK_NAME") or os.environ.get("TASK_NAME") or ""
                    if task_name:
                        safe_name = re.sub(r"[^\w\-]+", "_", task_name)[:80]
                    else:
                        safe_name = re.sub(r"[^\w\-]+", "_", user_text)[:50] or "default"

                    log_path = os.path.join(base_dir, f"{safe_name}_token_logprobs.jsonl")

                    record = {
                        "seq_id": self.seq_id,
                        "prompt_user": user_text,
                        "prediction": prediction, 
                    }
                    if token_logprobs is not None:
                        record["tokens"] = token_logprobs

                    with open(log_path, "a", encoding="utf-8") as f:
                        f.write(json.dumps(record, ensure_ascii=False) + "\n")
                except Exception as e:
                    print(f"[WARN] failed to write VLM token logprobs: {e}")

                # ===== 保持原来的返回值格式不变 =====
                return prediction, payload, chat_completion_from_url

            except Exception as e:
                time.sleep(wait_seconds)
                wait_seconds *= 1
                counter -= 1
                print('Error calling LLM, will retry soon...')
                print(e)

        return ERROR_CALLING_LLM, None, None

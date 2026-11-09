# UI-TARS Runner For AndroidWorld

This folder is a separate runner for using UI-TARS models with the
`android_world_v3` benchmark setup. It does not replace or modify the existing
GUI-Owl path.

## What It Reuses

- AndroidWorld environment loading
- suite/task execution
- AndroidWorld `JSONAction` actuation
- existing emulator workflow

## What It Keeps Separate

- UI-TARS prompt formatting
- UI-TARS response parsing
- UI-TARS-specific shell entrypoint

## Official References

- UI-TARS prompt template:
  https://github.com/bytedance/UI-TARS/blob/main/codes/ui_tars/prompt.py
- UI-TARS deployment guide:
  https://github.com/bytedance/UI-TARS/blob/main/README_deploy.md
- UI-TARS model card:
  https://huggingface.co/ByteDance-Seed/UI-TARS-7B-DPO

This runner intentionally follows the official mobile-use prompt template and
the official parser package:

```bash
pip install ui-tars
```

Without that package, the runner will stop with a clear dependency error.

## Recommended Start

1. Serve your UI-TARS model behind an OpenAI-compatible endpoint.
2. Set `MODEL` in `run_ui_tars.sh` to the endpoint's `--served-model-name`.
3. Install the official parser package in the same Python environment:

```bash
pip install ui-tars
```

4. Run:

```bash
cd .
sh ui_tars_runner/run_ui_tars.sh
```

## Parser Model Type

The official parser examples currently show `model_type="qwen25vl"`, while
`UI-TARS-7B-DPO` itself is a `qwen2_vl` model on Hugging Face. This runner
therefore exposes `--ui_tars_parser_model_type` and starts with `qwen2vl` by
default, then falls back across official variants when parsing.

## Current Scope

This first version focuses on clean-environment execution with an isolated
UI-TARS agent. The existing GUI-Owl runner remains unchanged.

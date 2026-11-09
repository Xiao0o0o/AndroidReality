#!/usr/bin/env python3
"""Batch runner that evaluates UI-TARS on random MDP perturbation profiles."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import random
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_ANDROID_WORLD_V3_ROOT = os.path.dirname(_THIS_DIR)
if _ANDROID_WORLD_V3_ROOT not in sys.path:
  sys.path.insert(0, _ANDROID_WORLD_V3_ROOT)

from run_random_perturb_batch import _aggregate_success_by_key
from run_random_perturb_batch import _build_profiles
from run_random_perturb_batch import _extract_success_from_log
from run_random_perturb_batch import _make_names
from run_random_perturb_batch import _perturbation_flags
from run_random_perturb_batch import _prepare_session_directories
from run_random_perturb_batch import _resolve_tasks
from run_random_perturb_batch import _sample_profiles_for_task
from run_random_perturb_batch import _select_profiles
from run_random_perturb_batch import _stream_subprocess
from run_random_perturb_batch import _write_text


PY_CMD = sys.executable
RUN_SCRIPT = str(Path(_THIS_DIR) / "run_ui_tars.py")


def main() -> None:
  parser = argparse.ArgumentParser()
  parser.add_argument("--suite-family", default="android_world")
  parser.add_argument("--tasks", default="")
  parser.add_argument("--tasks-file", default="")
  parser.add_argument("--repeats-per-task", type=int, default=3)
  parser.add_argument("--agent", default="ui_tars")
  parser.add_argument("--model", default="ui_tars")
  parser.add_argument("--api-key", dest="api_key", default="sk-local")
  parser.add_argument("--base-url", dest="base_url", default="http://127.0.0.1:4243/v1")
  parser.add_argument("--ui-tars-parser-model-type", default="qwen2vl")
  parser.add_argument("--ui-tars-language", default="English")
  parser.add_argument("--ui-tars-temperature", type=float, default=0.0)
  parser.add_argument("--ui-tars-max-tokens", type=int, default=400)
  parser.add_argument("--ui-tars-max-retry", type=int, default=10)
  parser.add_argument("--ui-tars-history-window", type=int, default=8)
  parser.add_argument("--grpc-port", type=int, default=8554)
  parser.add_argument("--console-port", type=int, default=5554)
  parser.add_argument("--adb-path", default="")
  parser.add_argument("--perform-emulator-setup", default="False")
  parser.add_argument("--sampling-seed", type=int, default=20260427)
  parser.add_argument(
      "--profiles",
      default="",
      help=(
          "Optional comma-separated subset of perturbation profiles to sample "
          "from. If clean is enabled, it remains eligible unless disabled."
      ),
  )
  parser.add_argument("--font-size-large-scale", type=float, default=1.35)
  parser.add_argument("--font-size-small-scale", type=float, default=0.82)
  parser.add_argument("--display-compact-density-scale", type=float, default=0.85)
  parser.add_argument("--display-compact-size-scale", type=float, default=0.94)
  parser.add_argument("--display-zoomed-out-density-scale", type=float, default=0.76)
  parser.add_argument("--display-zoomed-out-size-scale", type=float, default=0.88)
  parser.add_argument("--orientation-profile-trigger-steps", default="1,3")
  parser.add_argument("--orientation-profile-sequence", default="landscape")
  parser.add_argument("--app-hang-trigger-steps", default="2")
  parser.add_argument("--action-delay-probability", type=float, default=0.15)
  parser.add_argument("--action-delay-seconds", type=float, default=1.5)
  parser.add_argument("--action-delay-seed", type=int, default=0)
  parser.add_argument("--action-drop-probability", type=float, default=0.08)
  parser.add_argument("--action-drop-seed", type=int, default=0)
  parser.add_argument("--episode-step-budget-multiplier", type=float, default=20.0)
  parser.add_argument("--disable-clean", action="store_true")
  parser.add_argument("--session-dir", default="")
  args = parser.parse_args()

  tasks = _resolve_tasks(args)
  if not tasks:
    print("No tasks resolved for the UI-TARS random perturbation runner.")
    return

  profiles = _select_profiles(
      _build_profiles(include_clean=not args.disable_clean),
      args.profiles,
  )
  session_paths = _prepare_session_directories(args.session_dir)
  session_dir = session_paths["session_dir"]
  logs_dir = session_paths["logs_dir"]
  trajs_dir = session_paths["trajs_dir"]
  android_world_runs_dir = session_paths["android_world_runs_dir"]
  session_timestamp = session_dir.name
  combined_log_path = str(session_dir / "combined.log")
  manifest_path = str(session_dir / "manifest.jsonl")
  summary_path = str(session_dir / "summary.json")

  results: list[dict[str, object]] = []
  base_rng = random.Random(args.sampling_seed)

  with open(combined_log_path, "wb") as combined_log, open(
      manifest_path,
      "w",
      encoding="utf-8",
  ) as manifest_file:
    header = (
        f"UI-TARS random perturbation batch start: {session_timestamp}\n"
        f"Suite family: {args.suite_family}\n"
        f"Tasks: {len(tasks)}\n"
        f"Repeats per task: {args.repeats_per_task}\n"
        f"Profiles: {[profile.name for profile in profiles]}\n\n"
    )
    _write_text(combined_log, header)
    try:
      sys.stdout.write(header)
      sys.stdout.flush()
    except Exception:
      pass

    for task_index, task in enumerate(tasks, start=1):
      task_rng = random.Random(f"{args.sampling_seed}:{task}:{task_index}:{base_rng.random()}")
      sampled_profiles = _sample_profiles_for_task(
          task_rng, profiles, args.repeats_per_task
      )
      for repeat_index, profile in enumerate(sampled_profiles, start=1):
        traj_path, per_run_log_path = _make_names(
            task, repeat_index, trajs_dir, logs_dir
        )
        cmd = [
            PY_CMD,
            RUN_SCRIPT,
            f"--suite_family={args.suite_family}",
            f"--tasks={task}",
            "--n_task_combinations=1",
            f"--agent_name={args.agent}",
            f"--model={args.model}",
            f"--api_key={args.api_key}",
            f"--base_url={args.base_url}",
            f"--ui_tars_parser_model_type={args.ui_tars_parser_model_type}",
            f"--ui_tars_language={args.ui_tars_language}",
            f"--ui_tars_temperature={args.ui_tars_temperature}",
            f"--ui_tars_max_tokens={args.ui_tars_max_tokens}",
            f"--ui_tars_max_retry={args.ui_tars_max_retry}",
            f"--ui_tars_history_window={args.ui_tars_history_window}",
            f"--episode_step_budget_multiplier={args.episode_step_budget_multiplier}",
            f"--output_path={android_world_runs_dir}",
            f"--traj_output_path={traj_path}",
            f"--grpc_port={args.grpc_port}",
            f"--console_port={args.console_port}",
        ]
        if args.adb_path:
          cmd.append(f"--adb_path={args.adb_path}")
        if args.perform_emulator_setup:
          cmd.append(f"--perform_emulator_setup={args.perform_emulator_setup}")

        cmd.extend(_perturbation_flags(profile.name, args))

        manifest_record = {
            "task": task,
            "repeat_index": repeat_index,
            "profile_name": profile.name,
            "profile_description": profile.description,
            "traj_output_path": traj_path,
            "per_run_log_path": per_run_log_path,
            "command": cmd,
        }
        manifest_file.write(json.dumps(manifest_record, ensure_ascii=False) + "\n")
        manifest_file.flush()

        run_header = (
            f"\n[RUN] task={task} repeat={repeat_index}/{args.repeats_per_task} "
            f"profile={profile.name} traj={traj_path} log={per_run_log_path}\n"
        )
        _write_text(combined_log, run_header)
        try:
          sys.stdout.write(run_header)
          sys.stdout.flush()
        except Exception:
          pass

        return_code = _stream_subprocess(cmd, combined_log, per_run_log_path)
        success, success_source = _extract_success_from_log(
            task=task,
            log_path=per_run_log_path,
            return_code=return_code,
        )
        results.append(
            {
                "task": task,
                "repeat_index": repeat_index,
                "profile_name": profile.name,
                "return_code": return_code,
                "success": success,
                "success_source": success_source,
                "traj_output_path": traj_path,
                "per_run_log_path": per_run_log_path,
            }
        )

  repeat_summary = _aggregate_success_by_key(results, "repeat_index")
  profile_summary = _aggregate_success_by_key(results, "profile_name")

  with open(summary_path, "w", encoding="utf-8") as summary_file:
    json.dump(
        {
            "suite_family": args.suite_family,
            "agent_name": args.agent,
            "model": args.model,
            "repeats_per_task": args.repeats_per_task,
            "profiles": [profile.name for profile in profiles],
            "results": results,
            "repeat_summary": repeat_summary,
            "profile_summary": profile_summary,
            "combined_log_path": combined_log_path,
            "manifest_path": manifest_path,
        },
        summary_file,
        indent=2,
        ensure_ascii=False,
    )

  print("Success rate by repeat:")
  for repeat_index, stats in repeat_summary.items():
    print(
        f"  repeat {repeat_index}: "
        f"{stats['num_successes']}/{stats['num_runs']} "
        f"({stats['success_rate']:.3f})"
    )
  print(f"Session dir: {session_dir}")
  print(f"Combined log: {combined_log_path}")
  print(f"Manifest: {manifest_path}")
  print(f"Summary: {summary_path}")


if __name__ == "__main__":
  main()

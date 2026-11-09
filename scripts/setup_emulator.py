#!/usr/bin/env python3
"""One-time emulator setup: AndroidWorld apps plus the perturbation helper app.

Run this once after creating the AVD, with the emulator already started.
"""

import argparse
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from android_world.env import env_launcher  # pylint: disable=wrong-import-position

HELPER_APK = (
    ROOT / "perturbation_helper_android_studio" / "prebuilt" / "app-debug.apk"
)


def find_adb() -> str:
  candidates = [
      Path(os.environ[name]) / "platform-tools" / "adb"
      for name in ("ANDROID_SDK_ROOT", "ANDROID_HOME")
      if name in os.environ
  ]
  candidates += [
      Path.home() / "Android" / "Sdk" / "platform-tools" / "adb",
      Path.home() / "Library" / "Android" / "sdk" / "platform-tools" / "adb",
  ]
  for candidate in candidates:
    if candidate.exists():
      return str(candidate)
  on_path = shutil.which("adb")
  if on_path:
    return on_path
  raise SystemExit("adb not found. Pass --adb-path or set ANDROID_SDK_ROOT.")


def check_sqlite_fts4() -> None:
  try:
    sqlite3.connect(":memory:").execute("CREATE VIRTUAL TABLE t USING fts4(x)")
  except sqlite3.OperationalError as error:
    raise SystemExit(
        f"This Python's SQLite ({sqlite3.sqlite_version}) has no FTS4 support, "
        "which AndroidWorld needs. Run:\n"
        "  conda install -c conda-forge sqlite=3.50.4 -y"
    ) from error


def main() -> None:
  check_sqlite_fts4()
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--adb-path", default=None)
  parser.add_argument("--console-port", type=int, default=5554)
  parser.add_argument("--grpc-port", type=int, default=8554)
  args = parser.parse_args()
  adb = args.adb_path or find_adb()

  print("Installing AndroidWorld apps. This takes several minutes.", flush=True)
  env = env_launcher.load_and_setup_env(
      console_port=args.console_port,
      emulator_setup=True,
      adb_path=adb,
      grpc_port=args.grpc_port,
  )
  env.close()

  print("Installing the perturbation helper app.", flush=True)
  serial = f"emulator-{args.console_port}"
  subprocess.run(
      [adb, "-s", serial, "install", "-r", str(HELPER_APK)], check=True
  )
  print("Emulator setup finished.", flush=True)


if __name__ == "__main__":
  main()

# Changes from upstream

`android_world/` comes from the `Mobile-Agent-v3/android_world_v3` directory of [X-PLUG/MobileAgent](https://github.com/X-PLUG/MobileAgent), commit `c4cd0a8`. That directory is a fork of [google-research/android_world](https://github.com/google-research/android_world) with the GUI-Owl agent added.

Only these files differ from that source:

| File | Change |
| --- | --- |
| `android_world/agents/gui_owl.py` | Adds the TTIR hook, makes response parsing more tolerant, and sends actions through `env.execute_action` so that the perturbation wrappers can intercept them. |
| `android_world/agents/infer_ma3.py` | Reads the image pixel limits from `GUIOWL_MIN_PIXELS` and `GUIOWL_MAX_PIXELS`. |
| `android_world/agents/seeact.py` | Sends actions through `env.execute_action`, as above. |
| `android_world/suite_utils.py` | Adds a configurable step budget multiplier, with a default of 20. |

To keep the repository small, the Docker setup, the FastAPI server, and the source of the Android apps were not copied. The benchmark does not use them. The AndroidWorld apps are downloaded during `scripts/setup_emulator.py`.

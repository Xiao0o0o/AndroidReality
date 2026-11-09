#!/usr/bin/env bash
# Serve one of the paper's models with vLLM on port 4243.
#
#   bash scripts/serve_model.sh <model>
#
# Models: gui_owl_7b, gui_owl_32b, gui_owl_1.5_2b, gui_owl_1.5_4b,
#         gui_owl_1.5_8b, gui_owl_1.5_32b, ui_tars_7b_sft, ui_tars_1.5_7b
#
# The 32B models need two GPUs. Set PORT to serve on another port.
set -euo pipefail

if [ "$#" -ne 1 ]; then
  sed -n '2,8p' "$0" >&2
  exit 2
fi
MODEL="$1"
PORT="${PORT:-4243}"

SMALL_IMAGE_KWARGS='{"min_pixels":3136,"max_pixels":2592000}'
ONE_IMAGE='{"image":1,"video":0}'
FIVE_IMAGES='{"image":5,"video":0}'

case "$MODEL" in
  gui_owl_7b)
    exec vllm serve mPLUG/GUI-Owl-7B --trust-remote-code \
      --served-model-name gui_owl_7b --port "$PORT" \
      --max-model-len 32768 --gpu-memory-utilization 0.85 --max-num-seqs 1 \
      --tensor-parallel-size 1 --allowed-local-media-path / \
      --limit-mm-per-prompt '{"image":5}' \
      --mm-processor-kwargs '{"size":{"longest_edge":3072000,"shortest_edge":65536}}'
    ;;
  gui_owl_32b)
    exec vllm serve mPLUG/GUI-Owl-32B --trust-remote-code \
      --served-model-name gui_owl_32b --tensor-parallel-size 2 \
      --host 0.0.0.0 --port "$PORT" --enforce-eager \
      --max-model-len 8192 --gpu-memory-utilization 0.92 --max-num-seqs 1 \
      --limit-mm-per-prompt "$ONE_IMAGE" \
      --mm-processor-kwargs "$SMALL_IMAGE_KWARGS"
    ;;
  gui_owl_1.5_2b|gui_owl_1.5_4b)
    SIZE="${MODEL##*_}"
    SIZE="${SIZE^^}"
    exec vllm serve "mPLUG/GUI-Owl-1.5-${SIZE}-Instruct" --trust-remote-code \
      --served-model-name "$MODEL" --port "$PORT" \
      --max-model-len 32768 --gpu-memory-utilization 0.92 --max-num-seqs 1 \
      --limit-mm-per-prompt "$FIVE_IMAGES" \
      --mm-processor-kwargs "$SMALL_IMAGE_KWARGS"
    ;;
  gui_owl_1.5_8b)
    exec vllm serve mPLUG/GUI-Owl-1.5-8B-Instruct --trust-remote-code \
      --served-model-name gui_owl_1.5_8b --port "$PORT" \
      --max-model-len 8192 --gpu-memory-utilization 0.92 --max-num-seqs 1 \
      --limit-mm-per-prompt "$ONE_IMAGE" \
      --mm-processor-kwargs "$SMALL_IMAGE_KWARGS"
    ;;
  gui_owl_1.5_32b)
    exec vllm serve mPLUG/GUI-Owl-1.5-32B-Instruct --trust-remote-code \
      --served-model-name gui_owl_1.5_32b --tensor-parallel-size 2 \
      --host 0.0.0.0 --port "$PORT" --enforce-eager \
      --max-model-len 8192 --gpu-memory-utilization 0.92 --max-num-seqs 1 \
      --limit-mm-per-prompt "$ONE_IMAGE" \
      --mm-processor-kwargs "$SMALL_IMAGE_KWARGS"
    ;;
  ui_tars_7b_sft|ui_tars_1.5_7b)
    if [ "$MODEL" = ui_tars_7b_sft ]; then
      REPO=ByteDance-Seed/UI-TARS-7B-SFT
    else
      REPO=ByteDance-Seed/UI-TARS-1.5-7B
    fi
    exec vllm serve "$REPO" --trust-remote-code \
      --served-model-name ui_tars --port "$PORT" \
      --max-model-len 8192 --gpu-memory-utilization 0.85 --max-num-seqs 1 \
      --limit-mm-per-prompt "$FIVE_IMAGES" \
      --mm-processor-kwargs "$SMALL_IMAGE_KWARGS"
    ;;
  *)
    echo "Unknown model '$MODEL'." >&2
    sed -n '6,7p' "$0" >&2
    exit 2
    ;;
esac

#!/usr/bin/env bash
#SBATCH --job-name=glossaryrag-qwen3
#SBATCH --partition=batch
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=12:00:00
#SBATCH --output=logs/glossaryrag-qwen3-%j.log

set -euo pipefail

: "${VLLM_BIN:?Set VLLM_BIN to the vllm executable}"
MODEL_ID="${MODEL_ID:-Qwen/Qwen3-8B}"
PORT="${PORT:-8000}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-16384}"

if [[ -z "${CUDA_VISIBLE_DEVICES:-}" ]]; then
  echo "Slurm did not allocate a GPU" >&2
  exit 2
fi

exec "$VLLM_BIN" serve "$MODEL_ID" \
  --host 127.0.0.1 \
  --port "$PORT" \
  --dtype bfloat16 \
  --max-model-len "$MAX_MODEL_LEN" \
  --gpu-memory-utilization 0.90


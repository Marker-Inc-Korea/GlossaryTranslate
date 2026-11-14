#!/usr/bin/env bash
#SBATCH --job-name=glossaryrag-one
#SBATCH --partition=batch
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=12
#SBATCH --mem=96G
#SBATCH --time=04:00:00
#SBATCH --output=logs/glossaryrag-one-%j.log

set -euo pipefail

: "${PROJECT_DIR:?Set PROJECT_DIR to the repository root}"
: "${MODEL_PATH:?Set MODEL_PATH to the downloaded open model snapshot}"
: "${DATASET:?Set DATASET to a prepared benchmark JSONL}"
: "${OUTPUT:?Set OUTPUT to the prediction JSONL path}"
VLLM_BIN="${VLLM_BIN:-vllm}"
PYTHON="${PYTHON:-$PROJECT_DIR/.venv/bin/python}"
MODEL_NAME="${MODEL_NAME:-Qwen/Qwen3-8B}"
MODES="${MODES:-no_term,proper}"
MAX_TOKENS="${MAX_TOKENS:-1024}"
WORKERS="${WORKERS:-8}"
PORT="${PORT:-$((26000 + SLURM_JOB_ID % 1000))}"
BASE_URL="http://127.0.0.1:$PORT"

export VLLM_USE_FLASHINFER_SAMPLER=0
export VLLM_WORKER_MULTIPROC_METHOD=spawn
export VLLM_BATCH_INVARIANT=1

cd "$PROJECT_DIR"
mkdir -p logs results
if [[ -z "${CUDA_VISIBLE_DEVICES:-}" ]]; then
  echo "Slurm did not allocate a GPU" >&2
  exit 2
fi

"$VLLM_BIN" serve "$MODEL_PATH" \
  --served-model-name "$MODEL_NAME" \
  --host 127.0.0.1 --port "$PORT" \
  --dtype bfloat16 --max-model-len 32768 --gpu-memory-utilization 0.90 \
  >"logs/vllm-one-$SLURM_JOB_ID.log" 2>&1 &
SERVER_PID=$!
cleanup() {
  kill "$SERVER_PID" 2>/dev/null || true
  wait "$SERVER_PID" 2>/dev/null || true
}
trap cleanup EXIT

for _ in $(seq 1 180); do
  if curl -fsS "$BASE_URL/health" >/dev/null; then
    break
  fi
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    cat "logs/vllm-one-$SLURM_JOB_ID.log" >&2
    exit 3
  fi
  sleep 5
done
curl -fsS "$BASE_URL/health" >/dev/null

"$PYTHON" -m glossaryrag.cli benchmark \
  --dataset "$DATASET" --output "$OUTPUT" \
  --base-url "$BASE_URL" --model "$MODEL_NAME" \
  --modes "$MODES" --disable-thinking \
  --workers "$WORKERS" --max-tokens "$MAX_TOKENS"

echo "SINGLE_BENCHMARK=PASS"

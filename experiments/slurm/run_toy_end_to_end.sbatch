#!/usr/bin/env bash
#SBATCH --job-name=glossaryrag-toy
#SBATCH --partition=batch
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=12
#SBATCH --mem=96G
#SBATCH --time=12:00:00
#SBATCH --output=logs/glossaryrag-toy-%j.log

set -euo pipefail

: "${PROJECT_DIR:?Set PROJECT_DIR to the repository root}"
: "${MODEL_PATH:?Set MODEL_PATH to the downloaded open model snapshot}"
VLLM_BIN="${VLLM_BIN:-/data/home/mk01/.venvs/focus_tempnew/bin/vllm}"
PYTHON="${PYTHON:-$PROJECT_DIR/.venv/bin/python}"
MODEL_NAME="${MODEL_NAME:-Qwen/Qwen3-8B}"
PORT="${PORT:-$((24000 + SLURM_JOB_ID % 1000))}"
BASE_URL="http://127.0.0.1:$PORT"

cd "$PROJECT_DIR"
mkdir -p logs results

if [[ -z "${CUDA_VISIBLE_DEVICES:-}" ]]; then
  echo "Slurm did not allocate a GPU" >&2
  exit 2
fi

"$VLLM_BIN" serve "$MODEL_PATH" \
  --served-model-name "$MODEL_NAME" \
  --host 127.0.0.1 \
  --port "$PORT" \
  --dtype bfloat16 \
  --max-model-len 16384 \
  --gpu-memory-utilization 0.90 \
  >"logs/vllm-$SLURM_JOB_ID.log" 2>&1 &
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
    cat "logs/vllm-$SLURM_JOB_ID.log" >&2
    exit 3
  fi
  sleep 5
done
curl -fsS "$BASE_URL/health" >/dev/null

run_one() {
  local name="$1"
  local dataset="$2"
  local modes="$3"
  "$PYTHON" -m glossaryrag.cli benchmark \
    --dataset "$dataset" \
    --output "results/${name}.predictions.jsonl" \
    --base-url "$BASE_URL" \
    --model "$MODEL_NAME" \
    --modes "$modes" \
    --disable-thinking \
    --workers 4 \
    --max-tokens 2048
}

run_one "tico19-medical-en-fr-toy" "data/processed/tico19-en-fr-toy.jsonl" "no_term,proper"
run_one "wmt25-it-en-es-toy" "data/processed/wmt25-it-en-es-toy.jsonl" "no_term,proper,random"
run_one "wmt25-finance-en-zh-toy" "data/processed/wmt25-finance-toy.jsonl" "no_term,proper,random"

echo "TOY_EXPERIMENT=PASS"

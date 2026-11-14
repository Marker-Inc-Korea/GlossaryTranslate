#!/usr/bin/env bash
#SBATCH --job-name=glossaryrag-study
#SBATCH --partition=batch
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=96G
#SBATCH --time=12:00:00
#SBATCH --output=logs/glossaryrag-study-%j.log

set -euo pipefail

: "${PROJECT_DIR:?Set PROJECT_DIR to the repository root}"
: "${MODEL_PATH:?Set MODEL_PATH to the downloaded open model snapshot}"
VLLM_BIN="${VLLM_BIN:-/data/home/mk01/.venvs/focus_tempnew/bin/vllm}"
PYTHON="${PYTHON:-$PROJECT_DIR/.venv/bin/python}"
MODEL_NAME="${MODEL_NAME:-Qwen/Qwen3-8B}"
MODEL_REVISION="${MODEL_REVISION:-unknown}"
RUN_TAG="${RUN_TAG:-public-v1}"
PORT="${PORT:-$((25000 + SLURM_JOB_ID % 1000))}"
BASE_URL="http://127.0.0.1:$PORT"
VLLM_VERSION="$($VLLM_BIN --version 2>/dev/null | awk '{print $2}' || true)"
GPU_NAME="$(nvidia-smi --query-gpu=name --format=csv,noheader | head -n 1)"

export VLLM_USE_FLASHINFER_SAMPLER=0
export VLLM_WORKER_MULTIPROC_METHOD=spawn
export VLLM_BATCH_INVARIANT=1

cd "$PROJECT_DIR"
mkdir -p data/processed logs reports results

if [[ -z "${CUDA_VISIBLE_DEVICES:-}" ]]; then
  echo "Slurm did not allocate a GPU" >&2
  exit 2
fi

prepare_data() {
  "$PYTHON" -m glossaryrag.cli prepare tico19 \
    --input data/raw/tico19 \
    --terminology data/raw/tico19/terminologies/f_en-fr_XX.csv \
    --target-lang fr --limit 500 \
    --output data/processed/tico19-en-fr-500.jsonl
  "$PYTHON" -m glossaryrag.cli prepare tico19 \
    --input data/raw/tico19 \
    --terminology data/raw/tico19/terminologies/f_en-es_XX.csv \
    --target-lang es-LA --limit 500 \
    --output data/processed/tico19-en-es-la-500.jsonl
  "$PYTHON" -m glossaryrag.cli prepare tico19 \
    --input data/raw/tico19 \
    --terminology data/raw/tico19/terminologies/f_en-zh_CN.csv \
    --target-lang zh --limit 500 \
    --output data/processed/tico19-en-zh-500.jsonl
  for lang in de es ru; do
    "$PYTHON" -m glossaryrag.cli prepare wmt25-track1 \
      --input data/raw/wmt25 --target-lang "$lang" \
      --output "data/processed/wmt25-it-en-$lang-500.jsonl"
  done
  "$PYTHON" -m glossaryrag.cli prepare wmt25-track2 \
    --input data/raw/wmt25 --per-year-limit 2 \
    --output data/processed/wmt25-finance-balanced-20.jsonl
}

prepare_data

"$VLLM_BIN" serve "$MODEL_PATH" \
  --served-model-name "$MODEL_NAME" \
  --host 127.0.0.1 \
  --port "$PORT" \
  --dtype bfloat16 \
  --max-model-len 32768 \
  --gpu-memory-utilization 0.90 \
  >"logs/vllm-study-$SLURM_JOB_ID.log" 2>&1 &
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
    cat "logs/vllm-study-$SLURM_JOB_ID.log" >&2
    exit 3
  fi
  sleep 5
done
curl -fsS "$BASE_URL/health" >/dev/null

run_one() {
  local name="$1"
  local dataset="$2"
  local modes="$3"
  local max_tokens="$4"
  "$PYTHON" -m glossaryrag.cli benchmark \
    --dataset "$dataset" \
    --output "results/${name}-${RUN_TAG}.predictions.jsonl" \
    --base-url "$BASE_URL" \
    --model "$MODEL_NAME" \
    --modes "$modes" \
    --disable-thinking \
    --workers 8 \
    --max-tokens "$max_tokens"
}

run_one tico19-medical-en-fr data/processed/tico19-en-fr-500.jsonl no_term,proper 512
run_one tico19-medical-en-es-la data/processed/tico19-en-es-la-500.jsonl no_term,proper 512
run_one tico19-medical-en-zh data/processed/tico19-en-zh-500.jsonl no_term,proper 512
run_one wmt25-it-en-de data/processed/wmt25-it-en-de-500.jsonl no_term,proper,random 512
run_one wmt25-it-en-es data/processed/wmt25-it-en-es-500.jsonl no_term,proper,random 512
run_one wmt25-it-en-ru data/processed/wmt25-it-en-ru-500.jsonl no_term,proper,random 512
run_one wmt25-finance-balanced data/processed/wmt25-finance-balanced-20.jsonl no_term,proper,random 4096

"$PYTHON" experiments/build_public_report.py \
  --input "Medical en-fr=results/tico19-medical-en-fr-${RUN_TAG}.predictions.jsonl" \
  --input "Medical en-es-LA=results/tico19-medical-en-es-la-${RUN_TAG}.predictions.jsonl" \
  --input "Medical en-zh=results/tico19-medical-en-zh-${RUN_TAG}.predictions.jsonl" \
  --input "IT en-de=results/wmt25-it-en-de-${RUN_TAG}.predictions.jsonl" \
  --input "IT en-es=results/wmt25-it-en-es-${RUN_TAG}.predictions.jsonl" \
  --input "IT en-ru=results/wmt25-it-en-ru-${RUN_TAG}.predictions.jsonl" \
  --input "Finance en-zh and zh-en=results/wmt25-finance-balanced-${RUN_TAG}.predictions.jsonl" \
  --output "reports/public-benchmark-${RUN_TAG}.md" \
  --json-output "reports/public-benchmark-${RUN_TAG}.json" \
  --model "$MODEL_NAME" \
  --model-revision "$MODEL_REVISION" \
  --runtime "vLLM ${VLLM_VERSION:-unknown}" \
  --hardware "$(hostname), one Slurm-allocated $GPU_NAME" \
  --bootstrap-samples 1000

echo "PUBLIC_STUDY=PASS"

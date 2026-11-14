#!/usr/bin/env bash
#SBATCH --job-name=glossaryrag-eval
#SBATCH --partition=batch
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=12:00:00
#SBATCH --output=logs/glossaryrag-eval-%j.log

set -euo pipefail

: "${PROJECT_DIR:?Set PROJECT_DIR to the repository root}"
: "${BASE_URL:?Set BASE_URL to the local model endpoint}"
MODEL_ID="${MODEL_ID:-Qwen/Qwen3-8B}"
PYTHON="${PYTHON:-$PROJECT_DIR/.venv/bin/python}"

cd "$PROJECT_DIR"
mkdir -p results logs

for dataset in \
  data/processed/tico19-en-fr.jsonl \
  data/processed/wmt25-it-en-es.jsonl \
  data/processed/wmt25-finance.jsonl; do
  name="$(basename "$dataset" .jsonl)"
  "$PYTHON" -m glossaryrag.cli benchmark \
    --dataset "$dataset" \
    --output "results/$name.predictions.jsonl" \
    --base-url "$BASE_URL" \
    --model "$MODEL_ID" \
    --modes no_term,proper,random \
    --disable-thinking \
    --workers 4
done


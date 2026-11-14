from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from .client import OpenAICompatibleClient
from .datasets import prepare_tico19, prepare_wmt25_track1, prepare_wmt25_track2
from .downloads import download_tico19, download_wmt25
from .loaders import load_glossary
from .pipeline import GlossaryRAGTranslator
from .retriever import TrieGlossaryRetriever
from .runner import run_benchmark, score_predictions


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="glossaryrag")
    subparsers = parser.add_subparsers(dest="command", required=True)

    match = subparsers.add_parser("match", help="match glossary terms in source text")
    match.add_argument("--glossary", type=Path, required=True)
    match.add_argument("--text", required=True)
    match.add_argument("--source-lang", default="")
    match.add_argument("--target-lang", default="")
    match.add_argument("--max-terms", type=int)

    translate = subparsers.add_parser(
        "translate",
        help="translate through an OpenAI-compatible endpoint",
    )
    translate.add_argument("--glossary", type=Path, required=True)
    translate.add_argument("--text", required=True)
    translate.add_argument("--source-lang", required=True)
    translate.add_argument("--target-lang", required=True)
    translate.add_argument("--domain", default="general")
    translate.add_argument("--base-url", required=True)
    translate.add_argument("--model", required=True)
    translate.add_argument("--api-key", default=os.getenv("OPENAI_API_KEY", ""))
    translate.add_argument("--max-terms", type=int)

    download = subparsers.add_parser("download", help="download public benchmark source files")
    download.add_argument("dataset", choices=("wmt25", "tico19"))
    download.add_argument("--output", type=Path, required=True)
    download.add_argument("--languages", default="fr,es-LA,zh")

    prepare = subparsers.add_parser("prepare", help="convert an upstream benchmark to common JSONL")
    prepare.add_argument("dataset", choices=("wmt25-track1", "wmt25-track2", "tico19"))
    prepare.add_argument("--input", type=Path, required=True)
    prepare.add_argument("--output", type=Path, required=True)
    prepare.add_argument("--target-lang", default="es")
    prepare.add_argument("--terminology", type=Path)
    prepare.add_argument("--limit", type=int)

    benchmark = subparsers.add_parser(
        "benchmark",
        help="run no-term/proper/random translation modes",
    )
    benchmark.add_argument("--dataset", type=Path, required=True)
    benchmark.add_argument("--output", type=Path, required=True)
    benchmark.add_argument("--base-url", required=True)
    benchmark.add_argument("--model", required=True)
    benchmark.add_argument("--api-key", default=os.getenv("OPENAI_API_KEY", ""))
    benchmark.add_argument("--modes", default="no_term,proper,random")
    benchmark.add_argument("--workers", type=int, default=1)
    benchmark.add_argument("--max-tokens", type=int, default=1024)
    benchmark.add_argument("--limit", type=int)
    benchmark.add_argument("--disable-thinking", action="store_true")

    score = subparsers.add_parser("score", help="score an existing predictions JSONL")
    score.add_argument("--predictions", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.command == "match":
        entries = load_glossary(
            args.glossary,
            source_lang=args.source_lang,
            target_lang=args.target_lang,
        )
        matches = TrieGlossaryRetriever(entries).match(args.text, max_terms=args.max_terms)
        print(json.dumps([match.to_dict() for match in matches], ensure_ascii=False, indent=2))
        return 0
    if args.command == "translate":
        entries = load_glossary(
            args.glossary,
            source_lang=args.source_lang,
            target_lang=args.target_lang,
        )
        client = OpenAICompatibleClient(
            base_url=args.base_url,
            model=args.model,
            api_key=args.api_key,
        )
        translator = GlossaryRAGTranslator.from_entries(entries, client=client)
        result = translator.translate(
            args.text,
            source_language=args.source_lang,
            target_language=args.target_lang,
            domain=args.domain,
            max_terms=args.max_terms,
        )
        print(result.text)
        return 0
    if args.command == "download":
        if args.dataset == "wmt25":
            destination = download_wmt25(args.output)
        else:
            destination = download_tico19(
                args.output,
                languages=(item.strip() for item in args.languages.split(",") if item.strip()),
            )
        print(destination)
        return 0
    if args.command == "prepare":
        if args.dataset == "wmt25-track1":
            count = prepare_wmt25_track1(
                args.input / "ranking/references/track1",
                args.output,
                target_lang=args.target_lang,
                limit=args.limit,
            )
        elif args.dataset == "wmt25-track2":
            count = prepare_wmt25_track2(
                args.input / "ranking/references/track2",
                args.output,
                limit=args.limit,
            )
        else:
            if args.terminology is None:
                raise SystemExit("--terminology is required for TICO-19")
            count = prepare_tico19(
                args.input / "tico19-testset.zip",
                args.terminology,
                args.output,
                target_lang=args.target_lang,
                limit=args.limit,
            )
        print(json.dumps({"status": "PASS", "records": count, "output": str(args.output)}))
        return 0
    if args.command == "benchmark":
        report = run_benchmark(
            args.dataset,
            args.output,
            base_url=args.base_url,
            model=args.model,
            modes=(mode.strip() for mode in args.modes.split(",") if mode.strip()),
            api_key=args.api_key,
            workers=args.workers,
            max_tokens=args.max_tokens,
            limit=args.limit,
            disable_thinking=args.disable_thinking,
        )
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    if args.command == "score":
        print(json.dumps(score_predictions(args.predictions), ensure_ascii=False, indent=2))
        return 0
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())

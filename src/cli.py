#!/usr/bin/env python3
"""CLI: ingest knowledge base and ask nutrition questions."""

import argparse
import sys

from src.assistant import ask
from src.i18n import resolve_locale
from src.ingest.pipeline import run_ingest
from src.models import PatientContext
from src.retrieval.index_build import build_vector_index
from src.retrieval.store import resolve_retrieval_mode


def _build_patient_context(args: argparse.Namespace) -> PatientContext:
    return PatientContext(
        treatment_types=args.treatment or [],
        cycle_day=args.cycle_day,
        on_corticosteroids_today=args.corticosteroids,
        comorbidities=args.comorbidity or [],
        weight_trend=args.weight_trend,
        glucose=args.glucose,
        symptoms_today=args.symptoms or [],
        dietary_restrictions=args.dietary_restrictions or [],
        country=args.country,
        city=args.city,
    )


def cmd_ingest(args: argparse.Namespace) -> None:
    run_ingest()
    if args.index:
        stats = build_vector_index()
        print(f"  Indexed: {stats['total']} chunks (clinical {stats['clinical']}, peer {stats['peer']})")


def cmd_index(args: argparse.Namespace) -> None:
    stats = build_vector_index(reset=not args.no_reset)
    print(f"Indexed {stats['total']} chunks (clinical {stats['clinical']}, peer {stats['peer']})")
    print(f"Retrieval mode: {resolve_retrieval_mode()}")


def cmd_ask(args: argparse.Namespace) -> None:
    query = args.question
    locale = resolve_locale(query, args.lang)
    patient = _build_patient_context(args)
    response = ask(query, locale=locale, patient=patient)
    print(response.render_markdown())


def main() -> None:
    parser = argparse.ArgumentParser(description="Onco Nutrition Assistant")
    sub = parser.add_subparsers(dest="command", required=True)

    p_ingest = sub.add_parser("ingest", help="Build chunks.jsonl from docs/references")
    p_ingest.add_argument(
        "--index",
        action="store_true",
        help="Also build Chroma vector index after ingest (downloads embedding model on first run)",
    )
    p_ingest.set_defaults(func=cmd_ingest)

    p_index = sub.add_parser("index", help="Build Chroma vector index from chunks.jsonl")
    p_index.add_argument(
        "--no-reset",
        action="store_true",
        help="Append to existing index instead of rebuilding (default: full rebuild)",
    )
    p_index.set_defaults(func=cmd_index)

    p_ask = sub.add_parser("ask", help="Ask a nutrition question (requires ingest + API key)")
    p_ask.add_argument("question", help="Question in Bulgarian or English")
    p_ask.add_argument(
        "--lang",
        choices=["auto", "bg", "en"],
        default="auto",
        help="Response language: auto-detect from question, or force bg/en",
    )
    p_ask.add_argument(
        "--symptoms",
        nargs="+",
        help="Symptom tags, e.g. nausea no_appetite",
    )
    p_ask.add_argument(
        "--cycle-day",
        type=int,
        dest="cycle_day",
        help="Day of treatment cycle (0=pre-chemo, 1=chemo day, 2-3=early post, etc.)",
    )
    p_ask.add_argument(
        "--corticosteroids",
        action="store_true",
        help="On corticosteroids today (e.g. dexamethasone)",
    )
    p_ask.add_argument(
        "--weight-trend",
        choices=["stable", "losing", "gaining", "unknown"],
        default="unknown",
        dest="weight_trend",
        help="Recent weight trend",
    )
    p_ask.add_argument(
        "--glucose",
        choices=["normal", "high_recently", "unknown"],
        default="unknown",
        help="Self-reported blood sugar",
    )
    p_ask.add_argument(
        "--treatment",
        nargs="+",
        help="Treatment types, e.g. chemotherapy radiation",
    )
    p_ask.add_argument(
        "--comorbidity",
        nargs="+",
        help="Comorbidities, e.g. diabetes",
    )
    p_ask.add_argument(
        "--dietary-restrictions",
        nargs="+",
        dest="dietary_restrictions",
        help="Allergies or diet restrictions",
    )
    p_ask.add_argument(
        "--country",
        help="Country for seasonal/local produce, e.g. BG",
    )
    p_ask.add_argument(
        "--city",
        help="City for seasonal/local produce, e.g. Sofia",
    )
    p_ask.set_defaults(func=cmd_ask)

    args = parser.parse_args()
    try:
        args.func(args)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

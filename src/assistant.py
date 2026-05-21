import sys
import time

from src.i18n import DEFAULT_DISCLAIMER, Locale, resolve_locale
from src.llm import complete_json
from src.models import NutritionResponse, PatientContext, SourceRef
from src.prompts.nutrition import build_user_message, get_system_prompt
from src.retrieval.store import ChunkStore
from src.terminology import (
    flatten_food_items,
    normalize_display_text,
    normalize_optional,
    normalize_strings,
)


def _print_verbose_timing(
    *,
    store: ChunkStore,
    locale: Locale,
    clinical: list,
    peer: list,
    prompt_chars: int,
    seconds: dict[str, float],
) -> None:
    lines = [
        "--- timing ---",
        f"  retrieval mode: {store.retrieval_mode}",
        f"  locale:         {locale}",
        f"  load store:     {seconds['init']:.2f}s",
        f"  retrieve:       {seconds['retrieve']:.2f}s  "
        f"(clinical={len(clinical)}, peer={len(peer)})",
        f"  build prompt:   {seconds['prompt']:.2f}s  ({prompt_chars:,} chars)",
        f"  LLM (API):      {seconds['llm']:.2f}s",
        f"  total:          {seconds['total']:.2f}s",
        "--------------",
    ]
    print("\n".join(lines), file=sys.stderr)


def ask(
    query: str,
    store: ChunkStore | None = None,
    locale: Locale | None = None,
    patient: PatientContext | None = None,
    *,
    verbose: bool = False,
) -> NutritionResponse:
    t0 = time.perf_counter()
    store = store or ChunkStore()
    t_init = time.perf_counter()
    if not store.chunks:
        raise FileNotFoundError(
            "No chunks found. Run: python -m src.cli ingest"
        )

    loc = resolve_locale(query, locale)
    ctx = patient or PatientContext()
    clinical, peer = store.retrieve(query, locale=loc)
    t_retrieve = time.perf_counter()
    user_message = build_user_message(query, clinical, peer, loc, patient=ctx)
    t_prompt = time.perf_counter()
    data = complete_json(get_system_prompt(loc), user_message)
    t_llm = time.perf_counter()

    clinical_data = data.get("clinical", {})
    peer_data = data.get("peer") or {}
    app_data = data.get("app_suggestion", {})

    sources = [
        SourceRef(
            title=normalize_display_text(s.get("title", ""), loc),
            ref=s.get("ref", ""),
        )
        for s in clinical_data.get("sources", [])
    ]

    if verbose:
        _print_verbose_timing(
            store=store,
            locale=loc,
            clinical=clinical,
            peer=peer,
            prompt_chars=len(user_message),
            seconds={
                "init": t_init - t0,
                "retrieve": t_retrieve - t_init,
                "prompt": t_prompt - t_retrieve,
                "llm": t_llm - t_prompt,
                "total": t_llm - t0,
            },
        )

    return NutritionResponse(
        clinical_summary=normalize_display_text(clinical_data.get("summary", ""), loc),
        clinical_foods_to_eat=flatten_food_items(clinical_data.get("foods_to_eat", []), loc),
        clinical_foods_to_avoid=flatten_food_items(clinical_data.get("foods_to_avoid", []), loc),
        clinical_sources=sources,
        peer_summary=normalize_optional(peer_data.get("summary"), loc),
        peer_examples=normalize_strings(peer_data.get("examples", []), loc),
        app_meals=normalize_strings(app_data.get("meals", []), loc),
        app_hydration=normalize_display_text(app_data.get("hydration", ""), loc),
        disclaimer=normalize_display_text(
            data.get("disclaimer") or DEFAULT_DISCLAIMER[loc], loc
        ),
        locale=loc,
    )

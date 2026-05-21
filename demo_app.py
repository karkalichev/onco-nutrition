#!/usr/bin/env python3
"""Streamlit demo — open on phone via http://<laptop-ip>:8081 (same Wi‑Fi)."""

from __future__ import annotations

import os
import socket

import streamlit as st
from dotenv import load_dotenv

from src.assistant import ask
from src.config import CHROMA_DIR, CHUNKS_FILE
from src.retrieval.index_build import chroma_ready
from src.retrieval.store import resolve_retrieval_mode
from src.i18n import Locale, resolve_locale
from src.llm import resolve_anthropic_model
from src.models import PatientContext

load_dotenv()

DEMO_PORT = "8081"

SYMPTOM_OPTIONS = [
    "nausea",
    "no_appetite",
    "diarrhea",
    "constipation",
    "metal_taste",
    "mouth_sores",
    "fatigue",
]

TREATMENT_OPTIONS = ["chemotherapy", "radiation", "hormone_therapy", "surgery_recovery"]
COMORBIDITY_OPTIONS = ["diabetes", "kidney", "celiac"]

OPTION_LABELS: dict[str, dict[str, dict[str, str]]] = {
    "symptom": {
        "bg": {
            "nausea": "Гадене",
            "no_appetite": "Няма апетит",
            "diarrhea": "Диария",
            "constipation": "Запек",
            "metal_taste": "Метален вкус",
            "mouth_sores": "Язви / сухота в устата",
            "fatigue": "Умора",
        },
        "en": {
            "nausea": "Nausea",
            "no_appetite": "No appetite",
            "diarrhea": "Diarrhea",
            "constipation": "Constipation",
            "metal_taste": "Metallic taste",
            "mouth_sores": "Mouth sores / dry mouth",
            "fatigue": "Fatigue",
        },
    },
    "treatment": {
        "bg": {
            "chemotherapy": "Химиотерапия",
            "radiation": "Лъчево лечение",
            "hormone_therapy": "Хормонална терапия",
            "surgery_recovery": "Възстановяване след операция",
        },
        "en": {
            "chemotherapy": "Chemotherapy",
            "radiation": "Radiation",
            "hormone_therapy": "Hormone therapy",
            "surgery_recovery": "Surgery recovery",
        },
    },
    "comorbidity": {
        "bg": {
            "diabetes": "Диабет",
            "kidney": "Бъбречни проблеми",
            "celiac": "Целиакия",
        },
        "en": {
            "diabetes": "Diabetes",
            "kidney": "Kidney disease",
            "celiac": "Celiac disease",
        },
    },
    "response_lang": {
        "bg": {"auto": "Автоматично", "bg": "Български", "en": "Английски"},
        "en": {"auto": "Auto", "bg": "Bulgarian", "en": "English"},
    },
    "priority": {
        "bg": {
            "CALORIES_FIRST": "Калории първо",
            "BLOOD_SUGAR_AWARE": "Внимание към захарта",
            "BALANCED": "Балансирано",
        },
        "en": {
            "CALORIES_FIRST": "Calories first",
            "BLOOD_SUGAR_AWARE": "Blood sugar aware",
            "BALANCED": "Balanced",
        },
    },
    "phase": {
        "bg": {
            "pre_chemo": "Преди химио",
            "chemo_day": "Ден на химио",
            "post_chemo_early": "Ранно след химио (дни 1–3)",
            "post_chemo_late": "След химио (дни 4–10)",
            "recovery": "Възстановяване между циклите",
        },
        "en": {
            "pre_chemo": "Pre-chemo",
            "chemo_day": "Chemo day",
            "post_chemo_early": "Early post-chemo (days 1–3)",
            "post_chemo_late": "Post-chemo (days 4–10)",
            "recovery": "Recovery between cycles",
        },
    },
}

LABELS = {
    "bg": {
        "title": "Onco Nutrition — демо",
        "subtitle": "Обща информация, не медицински съвет. Съгласувайте с екипа си.",
        "question": "Въпрос",
        "question_ph": "Напр. Какво да ям при гадене след химио?",
        "lang": "Език на отговора",
        "symptoms": "Симптоми днес",
        "cycle_day": "Ден от цикъл (празно = неизвестно)",
        "corticosteroids": "Кортикостероиди днес (напр. дексаметазон)",
        "weight_trend": "Тегло напоследък",
        "glucose": "Кръвна захар (самоотчет)",
        "treatment": "Лечение",
        "comorbidity": "Съпътстващи",
        "submit": "Питай асистента",
        "priority": "Приоритет",
        "phase": "Фаза на цикъл",
        "phone_hint": "На телефона отвори:",
        "missing_chunks": "Липсва knowledge base. На лаптопа пусни: `python -m src.cli ingest`",
        "missing_key": "Липсва ANTHROPIC_API_KEY в .env на лаптопа.",
        "weight_opts": {"unknown": "не знам", "stable": "стабилно", "losing": "губя", "gaining": "качвам"},
        "glucose_opts": {"unknown": "не знам", "normal": "нормална", "high_recently": "висока напоследък"},
        "ui_lang": "Език на менюто",
        "wifi": "Телефонът и лаптопът трябва да са на **същия Wi‑Fi**.",
        "country": "Държава (сезонни продукти)",
        "city": "Град",
        "country_ph": "BG",
        "city_ph": "София",
    },
    "en": {
        "title": "Onco Nutrition — demo",
        "subtitle": "General information, not medical advice. Discuss with your care team.",
        "question": "Question",
        "question_ph": "e.g. What should I eat when nauseous after chemo?",
        "lang": "Response language",
        "symptoms": "Symptoms today",
        "cycle_day": "Cycle day (empty = unknown)",
        "corticosteroids": "Corticosteroids today (e.g. dexamethasone)",
        "weight_trend": "Weight trend",
        "glucose": "Blood sugar (self-report)",
        "treatment": "Treatment",
        "comorbidity": "Comorbidities",
        "submit": "Ask assistant",
        "priority": "Priority",
        "phase": "Cycle phase",
        "phone_hint": "On your phone open:",
        "missing_chunks": "Knowledge base missing. On laptop run: `python -m src.cli ingest`",
        "missing_key": "ANTHROPIC_API_KEY missing in laptop .env",
        "weight_opts": {"unknown": "unknown", "stable": "stable", "losing": "losing", "gaining": "gaining"},
        "glucose_opts": {"unknown": "unknown", "normal": "normal", "high_recently": "high recently"},
        "ui_lang": "Menu language",
        "wifi": "Phone and laptop must be on the **same Wi‑Fi**.",
        "country": "Country (seasonal produce)",
        "city": "City",
        "country_ph": "BG",
        "city_ph": "Sofia",
    },
}


def _lan_ip() -> str:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        sock.close()
        return ip
    except OSError:
        return "127.0.0.1"


def _ui_lang() -> str:
    return st.session_state.get("ui_lang", "bg")


def _L(key: str) -> str:
    return LABELS[_ui_lang()][key]


def _opt_label(group: str, value: str) -> str:
    return OPTION_LABELS[group][_ui_lang()][value]


st.set_page_config(
    page_title="Onco Nutrition",
    page_icon="🥗",
    layout="centered",
    initial_sidebar_state="expanded",
)

with st.sidebar:
    st.session_state.setdefault("ui_lang", "bg")
    ui_choice = st.radio(
        _L("ui_lang"),
        ["bg", "en"],
        format_func=lambda x: "Български" if x == "bg" else "English",
        horizontal=True,
    )
    st.session_state["ui_lang"] = ui_choice

    port = os.getenv("STREAMLIT_SERVER_PORT", DEMO_PORT)
    ip = _lan_ip()
    st.markdown(f"**{_L('phone_hint')}**")
    st.code(f"http://{ip}:{port}", language=None)
    st.caption(_L("wifi"))

    st.divider()
    st.caption(f"Model: `{resolve_anthropic_model()}`")
    if CHUNKS_FILE.exists():
        st.success("Knowledge base OK")
    else:
        st.error(_L("missing_chunks"))
    mode = resolve_retrieval_mode()
    if mode == "vector":
        st.success(f"Retrieval: vector ({CHROMA_DIR.name}/)")
    else:
        st.warning("Retrieval: keyword — run `python -m src.cli index` for vector search")
    if CHUNKS_FILE.exists() and not chroma_ready():
        st.caption("`python -m src.cli index`")
    if os.getenv("ANTHROPIC_API_KEY"):
        st.success("API key OK")
    else:
        st.error(_L("missing_key"))

st.title(_L("title"))
st.caption(_L("subtitle"))

lang_response = st.selectbox(
    _L("lang"),
    options=["auto", "bg", "en"],
    format_func=lambda x: _opt_label("response_lang", x),
)

question = st.text_area(
    _L("question"),
    placeholder=_L("question_ph"),
    height=100,
)

col1, col2 = st.columns(2)
with col1:
    symptoms = st.multiselect(
        _L("symptoms"),
        SYMPTOM_OPTIONS,
        format_func=lambda k: _opt_label("symptom", k),
    )
    cycle_raw = st.text_input(_L("cycle_day"), value="", placeholder="0–14")
    corticosteroids = st.checkbox(_L("corticosteroids"))
with col2:
    weight_keys = list(LABELS[_ui_lang()]["weight_opts"].keys())
    weight_trend = st.selectbox(
        _L("weight_trend"),
        weight_keys,
        format_func=lambda k: LABELS[_ui_lang()]["weight_opts"][k],
    )
    glucose_keys = list(LABELS[_ui_lang()]["glucose_opts"].keys())
    glucose = st.selectbox(
        _L("glucose"),
        glucose_keys,
        format_func=lambda k: LABELS[_ui_lang()]["glucose_opts"][k],
    )

treatment = st.multiselect(
    _L("treatment"),
    TREATMENT_OPTIONS,
    format_func=lambda k: _opt_label("treatment", k),
)
comorbidity = st.multiselect(
    _L("comorbidity"),
    COMORBIDITY_OPTIONS,
    format_func=lambda k: _opt_label("comorbidity", k),
)

loc_col1, loc_col2 = st.columns(2)
with loc_col1:
    country = st.text_input(_L("country"), placeholder=_L("country_ph"))
with loc_col2:
    city = st.text_input(_L("city"), placeholder=_L("city_ph"))

cycle_day: int | None = None
if cycle_raw.strip():
    try:
        cycle_day = int(cycle_raw.strip())
    except ValueError:
        st.warning("Ден от цикъл: въведи число." if _ui_lang() == "bg" else "Cycle day: enter a number.")

patient = PatientContext(
    treatment_types=treatment,
    cycle_day=cycle_day,
    on_corticosteroids_today=corticosteroids,
    comorbidities=comorbidity,
    weight_trend=weight_trend,  # type: ignore[arg-type]
    glucose=glucose,  # type: ignore[arg-type]
    symptoms_today=symptoms,
    country=country.strip() or None,
    city=city.strip() or None,
)

priority_key = patient.derive_priority()
phase_key = patient.derive_phase_hint()
priority_display = _opt_label("priority", priority_key)
phase_display = _opt_label("phase", phase_key) if phase_key else "—"

st.info(f"**{_L('priority')}:** {priority_display} · **{_L('phase')}:** {phase_display}")

if st.button(_L("submit"), type="primary", use_container_width=True):
    if not question.strip():
        st.warning("Въведи въпрос." if _ui_lang() == "bg" else "Enter a question.")
    elif not CHUNKS_FILE.exists():
        st.error(_L("missing_chunks"))
    elif not os.getenv("ANTHROPIC_API_KEY"):
        st.error(_L("missing_key"))
    else:
        locale: Locale | None = None if lang_response == "auto" else lang_response  # type: ignore[assignment]
        with st.spinner("Мисля…" if _ui_lang() == "bg" else "Thinking…"):
            try:
                response = ask(question.strip(), locale=locale, patient=patient)
                st.markdown(response.render_markdown())
            except Exception as exc:
                st.error(str(exc))

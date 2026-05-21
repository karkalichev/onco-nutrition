from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal

from src.i18n import DEFAULT_DISCLAIMER, Locale, ui


class Tier(str, Enum):
    CLINICAL = "clinical"
    PEER = "peer"


NutritionPriority = Literal["CALORIES_FIRST", "BALANCED", "BLOOD_SUGAR_AWARE"]
WeightTrend = Literal["stable", "losing", "gaining", "unknown"]
GlucoseSelfReport = Literal["normal", "high_recently", "unknown"]


@dataclass
class PatientContext:
    """Minimal patient state for menu + advice (self-reported, not EHR)."""

    treatment_types: list[str] = field(default_factory=list)  # chemotherapy, radiation, ...
    cycle_day: int | None = None
    cycle_length_days: int | None = None
    on_corticosteroids_today: bool = False
    diagnosis_site: str | None = None  # breast, head_neck, colorectal, ...
    comorbidities: list[str] = field(default_factory=list)
    weight_kg: float | None = None
    weight_trend: WeightTrend = "unknown"
    glucose: GlucoseSelfReport = "unknown"
    neutropenia_risk: bool | None = None
    symptoms_today: list[str] = field(default_factory=list)
    dietary_restrictions: list[str] = field(default_factory=list)
    country: str | None = None  # ISO or name, e.g. BG — for seasonal/local produce
    city: str | None = None  # e.g. Sofia, Plovdiv

    _CALORIES_FIRST_SYMPTOMS = frozenset({
        "nausea",
        "no_appetite",
        "diarrhea",
        "metal_taste",
        "mouth_sores",
        "fatigue",
    })

    def derive_priority(self) -> NutritionPriority:
        if self.glucose == "high_recently" or "diabetes" in self.comorbidities or self.on_corticosteroids_today:
            return "BLOOD_SUGAR_AWARE"
        if self.weight_trend == "losing" or any(
            s in self._CALORIES_FIRST_SYMPTOMS for s in self.symptoms_today
        ):
            return "CALORIES_FIRST"
        return "BALANCED"

    def derive_phase_hint(self) -> str | None:
        if self.cycle_day is None:
            return None
        if self.cycle_day <= 0:
            return "pre_chemo"
        if self.cycle_day == 1:
            return "chemo_day"
        if self.cycle_day <= 3:
            return "post_chemo_early"
        if self.cycle_day <= 10:
            return "post_chemo_late"
        return "recovery"

    def has_context(self) -> bool:
        return bool(
            self.treatment_types
            or self.cycle_day is not None
            or self.on_corticosteroids_today
            or self.diagnosis_site
            or self.comorbidities
            or self.weight_kg is not None
            or self.weight_trend != "unknown"
            or self.glucose != "unknown"
            or self.neutropenia_risk is not None
            or self.symptoms_today
            or self.dietary_restrictions
            or self.country
            or self.city
        )

    def to_prompt_block(self, locale: Locale) -> str:
        if not self.has_context():
            if locale == "en":
                return "[PATIENT_CONTEXT]\n(no patient context provided)\n"
            return "[PATIENT_CONTEXT]\n(няма подаден пациентски контекст)\n"

        priority = self.derive_priority()
        phase = self.derive_phase_hint()

        if locale == "en":
            lines = ["[PATIENT_CONTEXT]", f"nutrition_priority: {priority}"]
            if phase:
                lines.append(f"treatment_phase_hint: {phase}")
            if self.treatment_types:
                lines.append(f"treatment_types: {', '.join(self.treatment_types)}")
            if self.cycle_day is not None:
                lines.append(f"cycle_day: {self.cycle_day}")
            if self.on_corticosteroids_today:
                lines.append("on_corticosteroids_today: yes")
            if self.diagnosis_site:
                lines.append(f"diagnosis_site: {self.diagnosis_site}")
            if self.comorbidities:
                lines.append(f"comorbidities: {', '.join(self.comorbidities)}")
            if self.weight_trend != "unknown":
                lines.append(f"weight_trend: {self.weight_trend}")
            if self.weight_kg is not None:
                lines.append(f"weight_kg: {self.weight_kg}")
            if self.glucose != "unknown":
                lines.append(f"glucose_self_report: {self.glucose}")
            if self.neutropenia_risk is not None:
                lines.append(f"neutropenia_risk: {self.neutropenia_risk}")
            if self.symptoms_today:
                lines.append(f"symptoms_today: {', '.join(self.symptoms_today)}")
            if self.dietary_restrictions:
                lines.append(f"dietary_restrictions: {', '.join(self.dietary_restrictions)}")
            if self.country:
                lines.append(f"country: {self.country}")
            if self.city:
                lines.append(f"city: {self.city}")
            return "\n".join(lines) + "\n"

        lines = ["[PATIENT_CONTEXT]", f"nutrition_priority: {priority}"]
        if phase:
            lines.append(f"treatment_phase_hint: {phase}")
        if self.treatment_types:
            lines.append(f"тип_лечение: {', '.join(self.treatment_types)}")
        if self.cycle_day is not None:
            lines.append(f"ден_от_цикъл: {self.cycle_day}")
        if self.on_corticosteroids_today:
            lines.append("кортикостероиди_днес: да")
        if self.diagnosis_site:
            lines.append(f"локализация: {self.diagnosis_site}")
        if self.comorbidities:
            lines.append(f"съпътстващи: {', '.join(self.comorbidities)}")
        if self.weight_trend != "unknown":
            lines.append(f"тенденция_тегло: {self.weight_trend}")
        if self.weight_kg is not None:
            lines.append(f"тегло_kg: {self.weight_kg}")
        if self.glucose != "unknown":
            lines.append(f"захар_самоотчет: {self.glucose}")
        if self.neutropenia_risk is not None:
            lines.append(f"неутропения_риск: {self.neutropenia_risk}")
        if self.symptoms_today:
            lines.append(f"симптоми_днес: {', '.join(self.symptoms_today)}")
        if self.dietary_restrictions:
            lines.append(f"диетични_ограничения: {', '.join(self.dietary_restrictions)}")
        if self.country:
            lines.append(f"държава: {self.country}")
        if self.city:
            lines.append(f"град: {self.city}")
        return "\n".join(lines) + "\n"


@dataclass
class Chunk:
    id: str
    tier: Tier
    source_path: str
    source_title: str
    language: str
    text: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "tier": self.tier.value,
            "source_path": self.source_path,
            "source_title": self.source_title,
            "language": self.language,
            "text": self.text,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Chunk":
        return cls(
            id=data["id"],
            tier=Tier(data["tier"]),
            source_path=data["source_path"],
            source_title=data["source_title"],
            language=data.get("language", "unknown"),
            text=data["text"],
        )


@dataclass
class SourceRef:
    title: str
    ref: str


@dataclass
class NutritionResponse:
    clinical_summary: str
    clinical_foods_to_eat: list[str]
    clinical_foods_to_avoid: list[str]
    clinical_sources: list[SourceRef]
    peer_summary: str | None
    peer_examples: list[str]
    app_meals: list[str]
    app_hydration: str
    disclaimer: str = field(default="")
    locale: Locale = "bg"

    def render_markdown(self) -> str:
        loc = self.locale
        lines = [
            f"### {ui(loc, 'clinical_heading')}",
            "",
            self.clinical_summary,
            "",
        ]
        if self.clinical_foods_to_eat:
            lines.append(f"**{ui(loc, 'foods_to_eat')}:**")
            for item in self.clinical_foods_to_eat:
                lines.append(f"- {item}")
        if self.clinical_foods_to_avoid:
            lines.append(f"**{ui(loc, 'foods_to_avoid')}:**")
            for item in self.clinical_foods_to_avoid:
                lines.append(f"- {item}")
        if self.clinical_sources:
            lines.append("")
            lines.append(f"*{ui(loc, 'sources')}:* " + ", ".join(s.title for s in self.clinical_sources))

        if self.peer_summary or self.peer_examples:
            lines.extend(["", f"### {ui(loc, 'peer_heading')}", ""])
            if self.peer_summary:
                lines.append(self.peer_summary)
            lines.append(f"*{ui(loc, 'peer_disclaimer')}*")
            for ex in self.peer_examples:
                lines.append(f"- {ex}")

        lines.extend(["", f"### {ui(loc, 'app_heading')}", ""])
        for meal in self.app_meals:
            lines.append(f"- {meal}")
        if self.app_hydration:
            lines.append(f"- **{ui(loc, 'hydration')}:** {self.app_hydration}")

        disclaimer = self.disclaimer or DEFAULT_DISCLAIMER[loc]
        lines.extend(["", "---", f"⚕️ {disclaimer}"])
        return "\n".join(lines)

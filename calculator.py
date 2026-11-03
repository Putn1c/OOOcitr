from __future__ import annotations

import json
from pathlib import Path
from typing import TypedDict

PRICES_FILE = Path(__file__).parent / "data" / "prices.json"

# Нормативные сроки выполнения (рабочие дни) по видам изысканий,
# в зависимости от площади участка (га). Источник — внутренние
# нормативы ООО «ЦИТР» на основе СП 47.13330.2016.
NORMATIVE_DEADLINES: dict[str, list[tuple[float, int]]] = {
    "geodesic": [(10, 15), (50, 30), (100, 45), (500, 60), (float("inf"), 90)],
    "geological": [(10, 20), (50, 40), (100, 60), (500, 80), (float("inf"), 120)],
    "ecological": [(10, 15), (50, 25), (100, 35), (500, 50), (float("inf"), 70)],
    "hydrometeorological": [(10, 20), (50, 35), (100, 50), (500, 70), (float("inf"), 100)],
}

SURVEY_NAMES: dict[str, str] = {
    "geodesic": "Инженерно-геодезические изыскания",
    "geological": "Инженерно-геологические изыскания",
    "ecological": "Инженерно-экологические изыскания",
    "hydrometeorological": "Инженерно-гидрометеорологические изыскания",
}

COMPLEXITY_COEF: dict[str, float] = {
    "simple": 1.0,   # простая категория сложности
    "medium": 1.3,   # средней сложности
    "complex": 1.6,  # сложная
}

REGION_COEF: dict[str, float] = {
    "moscow": 1.2,   # г. Москва
    "mo": 1.0,       # Московская область
    "region": 0.85,  # прочие регионы
}


class CalculationResult(TypedDict):
    survey_type: str
    survey_name: str
    area_ha: float
    complexity: str
    region: str
    cost_rub: float
    deadline_days: int


def load_prices() -> dict:
    """Загружает справочник базовых цен."""
    with open(PRICES_FILE, encoding="utf-8") as f:
        return json.load(f)


def normative_deadline(survey_type: str, area_ha: float) -> int:
    """Возвращает нормативный срок выполнения изысканий в рабочих днях."""
    if survey_type not in NORMATIVE_DEADLINES:
        raise ValueError(f"Неизвестный вид изысканий: {survey_type}")
    for limit, days in NORMATIVE_DEADLINES[survey_type]:
        if area_ha <= limit:
            return days
    return NORMATIVE_DEADLINES[survey_type][-1][1]


def calculate(
    survey_type: str,
    area_ha: float,
    complexity: str,
    region: str,
) -> CalculationResult:
    """Выполняет расчёт стоимости и сроков изысканий.

    :raises ValueError: при некорректных входных параметрах.
    """
    prices = load_prices()

    if survey_type not in prices:
        raise ValueError(f"Неизвестный вид изысканий: {survey_type}")
    if complexity not in COMPLEXITY_COEF:
        raise ValueError("Недопустимая категория сложности")
    if region not in REGION_COEF:
        raise ValueError("Недопустимый регион")
    if area_ha <= 0:
        raise ValueError("Площадь участка должна быть больше 0")

    base = prices[survey_type]["base_price"]
    per_ha = prices[survey_type]["price_per_ha"]

    cost = (base + per_ha * area_ha) * COMPLEXITY_COEF[complexity] * REGION_COEF[region]
    deadline = normative_deadline(survey_type, area_ha)

    return CalculationResult(
        survey_type=survey_type,
        survey_name=SURVEY_NAMES[survey_type],
        area_ha=area_ha,
        complexity=complexity,
        region=region,
        cost_rub=round(cost, 2),
        deadline_days=deadline,
    )

from __future__ import annotations

from io import BytesIO

from flask import Flask, render_template, request, send_file
from openpyxl import Workbook

from calculator import (
    COMPLEXITY_COEF,
    REGION_COEF,
    SURVEY_NAMES,
    calculate,
)

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return render_template(
        "index.html",
        surveys=SURVEY_NAMES,
        complexity=COMPLEXITY_COEF,
        regions=REGION_COEF,
    )


@app.route("/calculate", methods=["POST"])
def calc():
    try:
        result = _read_and_calculate(request.form)
    except (ValueError, KeyError) as exc:
        return (
            render_template(
                "index.html",
                surveys=SURVEY_NAMES,
                complexity=COMPLEXITY_COEF,
                regions=REGION_COEF,
                error=f"Ошибка ввода: {exc}",
            ),
            400,
        )
    return render_template("result.html", result=result)


@app.route("/export", methods=["POST"])
def export():
    """Формирует XLSX-отчёт по введённым параметрам."""
    try:
        result = _read_and_calculate(request.form)
    except (ValueError, KeyError) as exc:
        return f"Ошибка экспорта: {exc}", 400

    wb = Workbook()
    ws = wb.active
    ws.title = "Расчёт изысканий"

    rows = [
        ("Показатель", "Значение"),
        ("Вид изысканий", result["survey_name"]),
        ("Площадь участка, га", result["area_ha"]),
        ("Категория сложности", result["complexity"]),
        ("Регион", result["region"]),
        ("Стоимость, руб.", result["cost_rub"]),
        ("Нормативный срок, раб. дней", result["deadline_days"]),
    ]
    for row in rows:
        ws.append(row)

    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)
    return send_file(
        stream,
        as_attachment=True,
        download_name="расчёт_изысканий.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


def _read_and_calculate(form) -> dict:
    return calculate(
        survey_type=form["survey_type"],
        area_ha=float(form["area_ha"]),
        complexity=form["complexity"],
        region=form["region"],
    )


if __name__ == "__main__":
    app.run(debug=True)

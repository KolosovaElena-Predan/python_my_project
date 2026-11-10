""" Приложение на gradio с графическим интерфейсом модели линейной регрессии"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import gradio as gr
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
from sklearn.linear_model import LinearRegression

import model


DF: pd.DataFrame = pd.read_csv(model.DATA_PATH)   
"""Датасет для отрисовки"""

MAIN_FEATURE: str = "grade"
"""Признак, который наиболее влияет на цену"""

TARGET = model.TARGET       
"Целевой признак price_ln"

MODEL: LinearRegression = model.load_model()
"""Модель линейной регрессии"""

FEATURES: list[str] = model.get_features(MODEL)               
"""Признаки, на которых была обучена модель"""

R2_TEST: float = model.compute_r2_test(MODEL, FEATURES)
"""R² на тесте"""



def on_submit(bedrooms, bathrooms, sqft_living, sqft_lot, floors, waterfront, view, condition, grade, sqft_above, sqft_basement, yr_built, lat, long, sqft_living15, sqft_lot15) -> tuple[str, Figure]:
    """Собирает признаки в словарь, вызывает модель, возвращает основную информацию о модели и графики"""
    values = {
        "bedrooms": bedrooms, "bathrooms": bathrooms,
        "sqft_living": sqft_living, "sqft_lot": sqft_lot,
        "floors": floors, "waterfront": waterfront,
        "view": view, "condition": condition,
        "grade": grade, "sqft_above": sqft_above,
        "sqft_basement": sqft_basement, "yr_built": yr_built,
        "lat": lat, "long": long,
        "sqft_living15": sqft_living15, "sqft_lot15": sqft_lot15,
    }

    #Валидация значений
    SIGNED_FEATURES: set[str] = {"lat", "long"}
    """Признаки, которые могут быть отрицательными"""

    for name, value in values.items():
        if value is None:
            raise gr.Error(f"Признак '{name}' не заполнен!", duration=5)
        if name not in SIGNED_FEATURES and value < 0:
            raise gr.Error(f"Признак '{name}' должен быть неотрицательным!", duration=5)

    #Предсказание цены по значениям
    pred = model.predict_price(MODEL, FEATURES, values)

    #Построение уравнения ЛР
    equation = model.get_equation_latex(MODEL, FEATURES)

    # Текст результата в Markdown (LaTeX рендерится через gr.Markdown)
    result_md = (
        f"### Предсказанная цена (логарифм): **{pred:.2f}**\n\n"
        f"**Уравнение регрессии:**\n\n"
        f"$$ {equation} $$\n\n"
        f"**R² на тестовой выборке:** `{R2_TEST:.4f}`"
    )

    # График
    fig = build_scatter_plot(values, pred)
    return result_md, fig

def build_scatter_plot(values: dict[str, float], pred: float) -> Figure:
    """Строит диаграмму рассеяния, где 
        values - значения признаков 
        pred - предсказанон значение модели для этих значений"""
    fig, ax = plt.subplots(figsize=(8, 5))

    # Точки из датасета
    sample: pd.DataFrame = DF.sample(min(500, len(DF)), random_state=42)
    sns.scatterplot(data=sample, x=MAIN_FEATURE, y=TARGET, alpha=0.3, ax=ax, label="Данные")

    # Линия регрессии
    mean_values: dict[str, float] = {f: float(DF[f].mean()) for f in FEATURES}
    x_range: np.ndarray = np.linspace(DF[MAIN_FEATURE].min(), DF[MAIN_FEATURE].max(), 100)
    y_line: list[float] = [model.predict_price(MODEL, FEATURES, {**mean_values, MAIN_FEATURE: x}) for x in x_range]
    ax.plot(x_range, y_line, color="red", linestyle="--", label="Линия регрессии")

    # Точка пользователя
    ax.scatter(values[MAIN_FEATURE], pred, color="green", s=160, edgecolors="black", zorder=5, label="Ваша точка")

    ax.set_xlabel(MAIN_FEATURE)
    ax.set_ylabel(TARGET)
    ax.legend()
    plt.tight_layout()
    return fig



"""Поля ввода со значениями по умолчанию"""
inputs: list[gr.Number] = [
    gr.Number(label="bedrooms (спальни)",           value=3.0),
    gr.Number(label="bathrooms (ванные)",           value=2.0),
    gr.Number(label="sqft_living (жилая площадь)",  value=1800.0),
    gr.Number(label="sqft_lot (площадь участка)",   value=5000.0),
    gr.Number(label="floors (этажи)",               value=1.0),
    gr.Number(label="waterfront (вид на воду)",     value=0.0),
    gr.Number(label="view (обзор)",                 value=0.0),
    gr.Number(label="condition (состояние)",        value=3.0),
    gr.Number(label="grade (класс отделки)",        value=7.0),
    gr.Number(label="sqft_above (площадь над землей)", value=1800.0),
    gr.Number(label="sqft_basement (площадь подвала)", value=0.0),
    gr.Number(label="yr_built (год постройки)",     value=1990.0),
    gr.Number(label="lat (широта)",                 value=47.5),
    gr.Number(label="long (долгота)",               value=-122.2),
    gr.Number(label="sqft_living15 (жилая площадь соседей)", value=1700.0),
    gr.Number(label="sqft_lot15 (площадь участка соседей)",  value=5000.0),
]

"""Форма с данными"""
form: gr.Interface = gr.Interface(
    fn=on_submit,
    inputs=inputs,
    outputs=[
    gr.Markdown(
        label="Результат",
        latex_delimiters=[
            {"left": "$$", "right": "$$", "display": True},
        ],
    ),
    gr.Plot(label="Диаграмма"),
    ],
    title="Линейная регрессия для предсказания цены дома(ln)",
    flagging_mode="never",
)

if __name__ == "__main__":
    form.launch()

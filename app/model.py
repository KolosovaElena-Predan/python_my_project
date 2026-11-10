"""Бизнес-логика приложения.
Отвечает за загрузку обученной модели и предсказание"""

import pickle
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split

MODEL_PATH = "models/LinReg_sklern_ver_1.9.1__pickle_ver_4.0.pkl"
DATA_PATH = "data/subsample_9.csv"
TARGET = "price_ln"


def load_model(path:str=MODEL_PATH) -> LinearRegression:
    """Возвращает обученную модель из pickle-файла, где path - путь к этому файлу"""
    with open(path, "rb") as f:
        return pickle.load(f)


def get_features(model:LinearRegression) -> list[str]:
    """Возвращает имена признаков в порядке обучения модели model"""
    return list(model.feature_names_in_)


def predict_price(model:LinearRegression, features:list[str], values:dict[str, float]) -> float:
    """Предсказывает логарифм цены дома, где
        model - обученная модель
        features - имена признаков
        values - значения признаков, например {"grade": 7, "sqft_living": 2000, ...}"""
    return float(model.predict(pd.DataFrame([values])[features])[0])


def get_equation_latex(model:LinearRegression, features:list[str]) -> str:
    """Уравнение регрессии в LaTeX, коэффициенты до 2 знаков по модели model и именам признаков features"""
    parts = [f"{model.intercept_:.2f}"]
    for feat, coef in zip(features, model.coef_):
        sign = "+" if coef >= 0 else "-"
        
        safe_feat = feat.replace("_", r"\_")
        
        parts.append(rf" {sign} {abs(coef):.2f} \cdot x_{{\text{{{safe_feat}}}}}")
        
    return "y = " + " ".join(parts)


def compute_r2_test(model:LinearRegression, features:list[str], data_path:str = DATA_PATH) -> float:
    """Вычисляет R² модели на отложенной тестовой выборке, где model - обученная модель
        features - имена признаков
        data_path - путь к CSV с исходными данными"""
    df = pd.read_csv(data_path)
    train, test = train_test_split(df, test_size=0.2, random_state=42)
    y_pred = model.predict(test[features])
    return float(r2_score(test[TARGET], y_pred))
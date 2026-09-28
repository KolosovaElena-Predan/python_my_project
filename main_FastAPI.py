'''fastapi — веб-фреймворк: описывает эндпоинты (что вернуть по какому адресу),
         сам преобразует dict в JSON, генерирует /docs'''
from fastapi import FastAPI

''' uvicorn — ASGI-сервер: слушает порт, принимает HTTP-запросы
           и передаёт их в приложение FastAPI'''
import uvicorn


# Создаём приложение
# uvicorn ищет объект FastAPI именно по переменной с именем app!
app = FastAPI()


# Регистрируем GET /ping, возвращаем JSON {"status": "ok"}
@app.get("/ping")
def ping():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
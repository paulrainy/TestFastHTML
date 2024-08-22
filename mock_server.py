from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()


# Модель данных для клиента
class Client(BaseModel):
    name: str
    date_of_birth: str


# Имитация базы данных
mock_db = {
    "1": Client(name="Иван Иванов", date_of_birth="1990-01-01"),
    "2": Client(name="Анна Петрова", date_of_birth="1985-05-15"),
}


# Эндпоинт для получения информации о клиенте по ID
@app.get("/api/clients/{client_id}", response_model=Client)
async def get_client(client_id: str):
    client_data = mock_db.get(client_id)
    if client_data:
        return client_data
    else:
        raise HTTPException(status_code=404, detail="Клиент не найден.")


# Эндпоинт для добавления нового клиента
@app.post("/api/clients/", response_model=Client, status_code=201)
async def add_client(client: Client):
    client_id = str(len(mock_db) + 1)  # Генерируем новый ID на основе размера словаря
    mock_db[client_id] = client
    return client


# Запуск сервера
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)

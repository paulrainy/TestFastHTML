from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI()


# Модель данных для клиента
class Client(BaseModel):
    name: str
    date_of_birth: str


# Модель данных для вклада
class Deposit(BaseModel):
    amount: float
    term: int  # срок в месяцах
    type: str  # вид вклада
    replenishment_method: str  # способ пополнения
    opened_by_third_party: bool  # открывает ли третье лицо
    is_premium_client: bool  # премиальный ли клиент
    client_id: str  # ID клиента


# Имитация базы данных
mock_db = {
    "1": Client(name="Иван Иванов", date_of_birth="1990-01-01"),
    "2": Client(name="Анна Петрова", date_of_birth="1985-05-15"),
}

# Имитация базы данных для вкладов
deposits_db = {
    "1": Deposit(
        amount=1000.0,
        term=12,
        type="Срочный",
        replenishment_method="Ежемесячно",
        opened_by_third_party=False,
        is_premium_client=True,
        client_id="1"  # Привязка к клиенту с ID "1"
    ),
    # Добавьте дополнительные депозиты с различными client_id
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


# Эндпоинт для добавления нового вклада
@app.post("/api/deposits/", response_model=Deposit, status_code=201)
async def add_deposit(deposit: Deposit):
    deposit_id = str(len(deposits_db) + 1)
    deposits_db[deposit_id] = deposit
    return deposit


# Эндпоинт для получения информации о вкладах клиента по ID клиента
@app.get("/api/deposits/{client_id}", response_model=List[Deposit])
async def get_deposits(client_id: str):
    # Фильтрация по client_id
    client_deposits = [deposit for deposit in deposits_db.values() if deposit.client_id == client_id]

    return client_deposits


# Запуск сервера
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)

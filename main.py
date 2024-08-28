# uvicorn main:app --host 127.0.0.1 --port 5001 --reload

from fasthtml.common import *
from fastapi import FastAPI, Request
import httpx  # Импортируем библиотеку для выполнения HTTP-запросов

# Инициализация приложения FastHTML
app, rt = fast_app()

# URL бэкенда
BASE_URL = "http://localhost:8000"  # Измени на адрес своего бэкенда


# Главная страница для ввода ID клиента
@rt("/")
def get():
    return Titled("Клиентское приложение",
                  Div(
                      H1("Введите ID клиента"),
                      Form(
                          Fieldset(
                              Input(type="text", name="client_id", placeholder="ID клиента", required=True),
                              Button("Показать информацию", type="submit", hx_post="/get_client",
                                     hx_target="#client_info")
                          )
                      ),
                      Div(id="client_info")  # Место для отображения информации о клиенте
                  )
                  )


@rt("/get_client", methods=["POST"])
async def get_client(request: Request):
    form_data = await request.form()  # Асинхронно получаем данные формы
    client_id = form_data.get("client_id")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/clients/{client_id}")

        if response.status_code == 200:
            client_data = response.json()

            # Начинаем создание client_info_div
            client_info_div = Div(
                P(f"ФИО: {client_data['name']}"),
                P(f"Дата рождения: {client_data['date_of_birth']}")
            )

            # Получаем информацию о вкладах клиента
            deposits_response = await client.get(f"{BASE_URL}/api/deposits/{client_id}")

            if deposits_response.status_code == 200:
                deposits_data = deposits_response.json()
                client_info_div += H2("Информация о вкладах:")
                for deposit in deposits_data:
                    client_info_div += Div(
                        P(f"Сумма: {deposit['amount']}"),
                        P(f"Срок: {deposit['term']} месяцев"),
                        P(f"Тип: {deposit['type']}"),
                        P(f"Способ пополнения: {deposit['replenishment_method']}"),
                        P(f"Открыт третьим лицом: {deposit['opened_by_third_party']}"),
                        P(f"Премиальный клиент: {deposit['is_premium_client']}")
                    )
            else:
                client_info_div += P("Вклады не найдены.")

            return client_info_div
        else:
            return Div(
                P("Клиент не найден."),
                H2("Добавьте нового клиента:"),
                Form(
                    Fieldset(
                        Input(type="text", name="name", placeholder="ФИО", required=True),
                        Input(type="date", name="date_of_birth", placeholder="Дата рождения", required=True),
                        Button("Добавить клиента", type="submit", hx_post="/add_client", hx_target="#client_info")
                    )
                )
            )


# Обработка добавления нового клиента
@rt("/add_client", methods=["POST"])
async def add_client(request: Request):
    form_data = await request.form()  # Асинхронно получаем данные формы
    name = form_data.get("name")
    date_of_birth = form_data.get("date_of_birth")

    # Отправляем HTTP-запрос к бэкенду для добавления нового клиента
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/api/clients/", json={
            "name": name,
            "date_of_birth": date_of_birth
        })

    if response.status_code == 201:  # Если данные успешно добавлены
        return P("Новый клиент добавлен.")
    else:  # Произошла ошибка при добавлении
        return P("Ошибка при добавлении клиента.")


# Обработка добавления нового вклада
@rt("/add_deposit", methods=["POST"])
async def add_deposit(request: Request):
    form_data = await request.form()
    amount = form_data.get("amount")
    term = form_data.get("term")
    deposit_type = form_data.get("type")
    replenishment_method = form_data.get("replenishment_method")
    opened_by_third_party = 'opened_by_third_party' in form_data
    is_premium_client = 'is_premium_client' in form_data
    client_id = form_data.get("client_id")  # Получаем ID клиента из формы

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/api/deposits/", json={
            "amount": amount,
            "term": term,
            "type": deposit_type,
            "replenishment_method": replenishment_method,
            "opened_by_third_party": opened_by_third_party,
            "is_premium_client": is_premium_client,
            "client_id": client_id  # Добавляем ID клиента
        })

    # Обработка ответа от сервера
    if response.status_code == 201:
        return P("Новый вклад добавлен.")
    else:
        return P("Ошибка при добавлении вклада.")


if __name__ == "__main__":
    serve(app)

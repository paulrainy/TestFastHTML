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


# Обработка данных и отображение информации о клиенте
@rt("/get_client", methods=["POST"])
async def get_client(request: Request):
    form_data = await request.form()  # Асинхронно получаем данные формы
    client_id = form_data.get("client_id")

    # Отправляем HTTP-запрос к бэкенду для получения данных клиента
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/clients/{client_id}")

    if response.status_code == 200:  # Если данные успешно получены
        client_data = response.json()  # Получаем данные в формате JSON
        return Div(P(f"ФИО: {client_data['name']}"),
                   P(f"Дата рождения: {client_data['date_of_birth']}"))
    else:  # Клиент не найден, предоставляем форму для добавления нового клиента
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


if __name__ == "__main__":
    serve(app)

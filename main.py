import flet as ft
import smtplib
import random
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import session
import os

# Вместо прямой строки читаем из системы:
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

nickname = ""
password = ""
email = ""
result_text = ""
error_text = ""
code = ""

# Адрес твоего локального сервера (или сервера на Render)
API_REGISTER_URL = "https://type-launcher.onrender.com"

SMTP_SERVER = "smtp.yandex.ru"
SMTP_PORT = 465

SENDER_EMAIL = "typeid.no-reply@yandex.ru"
SENDER_PASSWORD = "ktmumirxndjlixxj"

def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    generated_code = ""
    user_nickname = ""
    user_password = ""
    user_email = ""

    def go_to_register():
        page.controls.clear()
        page.add(register_frame)
        page.update()

    def go_to_mainmenu():
        page.controls.clear()
        page.add(main_menu)
        page.update()

    def send_email(target_email, code):
        try:
            msg = MIMEMultipart()
            msg['From'] = SENDER_EMAIL
            msg['To'] = target_email
            msg['Subject'] = "Код подтверждения"

            body = f"Ваш код регистрации: {code}"
            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            # Подключаемся именно по SSL к smtp.yandex.ru на порт 465
            print("[DEBUG] Подключаемся к SMTP-серверу Яндекса...")
            server = smtplib.SMTP_SSL("smtp.yandex.ru", 465,
                                      timeout=10)  # Добавили тайм-аут 10 секунд, чтобы скрипт не висел вечно

            print("[DEBUG] Авторизуемся...")
            server.login(SENDER_EMAIL, SENDER_PASSWORD)

            print("[DEBUG] Отправляем письмо...")
            server.sendmail(SENDER_EMAIL, target_email, msg.as_string())

            server.quit()
            print("[DEBUG] Письмо успешно отправлено!")
            return True
        except Exception as ex:
            print(f"[DEBUG] Ошибка отправки почты: {ex}")
            return False

    def verify_email(e):
        nonlocal generated_code, user_nickname, user_password, user_email

        user_nickname = nickname_input.value.strip()
        user_password = password_input.value
        user_email = email_input.value.strip()

        # Проверка на заполнение полей
        if not user_nickname:
            error_text.value = "Введите никнейм"
            page.update()
            return
        if not user_password:
            error_text.value = "Введите пароль"
            page.update()
            return
        if not user_email:
            error_text.value = "Введите email"
            page.update()
            return

        if not agree_checkbox.value:
            error_text.value = "Нужно согласиться с условиями"
            page.update()
            return

        # Если всё заполнено и галочка стоит — генерируем код и отправляем email
        error_text.value = ""
        generated_code = str(random.randint(100000, 999999))
        print(f"[DEBUG] Сгенерирован код: {generated_code}")

        # Отправляем письмо во внешнем потоке (или просто так, если не боишься секундного зависания UI)
        email_sent = send_email(user_email, generated_code)

        if email_sent:
            page.controls.clear()
            page.add(verify_email_frame)
            page.update()
        else:
            error_text.value = "Не удалось отправить код на почту!"
            page.update()

    def check_code(e):
        # Используем сохраненные ранее данные пользователя и сгенерированный код
        nonlocal generated_code, user_nickname, user_password, user_email

        entered_code = enter_code.value.strip()

        if entered_code == generated_code:
            # Код подтвержден! Теперь отправляем данные на наш сервер
            try:
                # Формируем тело запроса (в зависимости от того, как у тебя настроен бэкенд)
                payload = {
                    "username": user_nickname,
                    "email": user_email,
                    "password": user_password
                }

                # Делаем POST-запрос к нашему FastAPI
                response = requests.post(API_REGISTER_URL, json=payload, timeout=8)

                if response.status_code == 200:
                    # Успех! Supabase сохранил пользователя
                    print("[DEBUG] Регистрация на сервере прошла успешно!")

                    # Здесь ты можешь сразу сохранить сессию в файл session.json через твой импортированный модуль session
                    # session.save_session(...)

                    # Переводим игрока в главное меню
                    go_to_mainmenu()
                else:
                    # Сервер вернул ошибку (например, никнейм уже занят)
                    server_error = response.json().get("detail", "Ошибка сервера при регистрации")
                    # Выведем ошибку на экран верификации (можешь добавить элемент ft.Text в verify_email_frame)
                    print(f"[DEBUG] Ошибка от сервера: {server_error}")
                    enter_code.error_text = server_error
                    page.update()

            except requests.exceptions.RequestException as ex:
                enter_code.error_text = "Нет связи с сервером авторизации."
                page.update()
                print(f"[DEBUG] Ошибка запроса к FastAPI: {ex}")
        else:
            enter_code.error_text = "Неверный код подтверждения!"
            page.update()

    nickname_input = ft.TextField(
        label = "Ваш никнейм",
        hint_text = "",
        width = 300,
        border_radius = 15,
    )

    password_input = ft.TextField(
        label = "Введите пароль",
        hint_text = "",
        width = 300,
        border_radius = 15,
        password = True
    )

    email_input = ft.TextField(
        label = "Введите ваш Email",
        hint_text = "",
        width = 300,
        border_radius = 15,
    )

    agree_checkbox = ft.Checkbox(
        label = "Я согласен(-на) на условия использования лаунчера (прочитать их можно у нас на сайте)",
        value = False,
        active_color = ft.Colors.BLUE_500
    )

    result_text = ft.Text("", size=16, color=ft.Colors.GREEN_300)
    error_text = ft.Text("", size=16, color=ft.Colors.RED_300)

    register_button = ft.FilledButton(
        content = ft.Row(
            [
                ft.Icon(ft.Icons.CHEVRON_RIGHT),
                ft.Text("Продолжить", weight=ft.FontWeight.BOLD)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        ),
        width=300,
        on_click=verify_email
    )

    go_to_register_button = ft.FilledButton(
        # Помещаем и текст, и иконку внутрь content с помощью Row (строки)
        content=ft.Row(
            [
                ft.Icon(ft.Icons.CHEVRON_RIGHT),
                ft.Text("Дальше", weight=ft.FontWeight.BOLD)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        ),
        width=300,
        on_click=go_to_register
    )
    welcome_frame = ft.Container(
        content=ft.Column(
            [
                ft.Text("Привет! Чтобы зайти в лаунчер нужно пройти регистрацию!", size=24, weight=ft.FontWeight.BOLD),
                go_to_register_button,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15
        ),
        bgcolor=ft.Colors.SURFACE_CONTAINER,
        padding=25,
        border_radius=15,
    )

    enter_code = ft.TextField(
        label = "Введите свой код",
        hint_text = "",
        width = 170,
        border_radius = 15,
    )

    verify_email_button = ft.FilledButton(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.CHEVRON_RIGHT),
                ft.Text("Продолжить", weight=ft.FontWeight.BOLD)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        ),
        width=170,
        on_click=check_code  # <--- Просто передаем имя функции!
    )

    register_frame = ft.Container(
        content=ft.Column(
            [
                ft.Text("Регистрация", weight=ft.FontWeight.BOLD, size=36),
                nickname_input,
                password_input,
                email_input,
                agree_checkbox,
                register_button,
                error_text
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15
        ),
        bgcolor=ft.Colors.SURFACE_CONTAINER,
        padding=25,
        border_radius=15,
    )

    verify_email_frame = ft.Container(
        content=ft.Column(
            [
                ft.Text("Подтвердите почту", weight=ft.FontWeight.BOLD, size=36),
                enter_code,
                verify_email_button,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15
        ),
        bgcolor=ft.Colors.SURFACE_CONTAINER,
        padding=25,
        border_radius=15,
    )

    main_menu = ft.Container(

    )

    page.add(welcome_frame)

ft.app(target=main)
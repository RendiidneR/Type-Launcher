import flet as ft
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import session

nickname = ""
password = ""
email = ""
result_text = ""
error_text = ""
code = ""

SMTP_SERVER = "smtp.yandex.ru"
SMTP_PORT = 465

SENDER_EMAIL = "typeid.no-reply@yandex.ru"
SENDER_PASSWORD = "ktmumirxndjlixxj"

def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

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

    def verify_email(e):  # Добавьте аргумент 'e' (event), так как эта функция вызывается кнопкой!
        nickname = nickname_input.value
        password = password_input.value
        email = email_input.value

        if agree_checkbox.value:
            # 1. Генерируем 6-значный код и сохраняем его в глобальную/внешнюю переменную,
            # чтобы потом сравнить его на следующем экране
            global code  # Если generated_code объявлена на уровне main(), используйте nonlocal generated_code
            code = str(random.randint(100000, 999999))
            print(f"[DEBUG] Сгенерирован код: {code}")  # Для проверки в консоли

            # 2. Отправляем на почту, которую ввёл пользователь, сгенерированный код
            send_email(email, code)

            # 3. Переключаем экран
            page.controls.clear()
            page.add(verify_email_frame)
            page.update()
        else:
            error_text.value = "Нужно согласиться с условиями"
            page.update()
        if nickname == "":
            error_text.value = "Введите никнейм"
        elif password == "":
            error_text.value = "Введите пароль"
        elif email == "":
            error_text.value = "Введите email"
        if nickname == "" and agree_checkbox.value:
            error_text.value = "Введите никнейм"
        elif password == "" and agree_checkbox.value:
            error_text.value = "Введите пароль"
        elif email == "" and agree_checkbox.value:
            error_text.value = "Введите email"

    def check_code(code):
        entered_code = enter_code.value
        if entered_code == code:
            result_text = "Регистрация успешна!"
            page.update()
        else:
            result_text = "Неверный код!"
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
        content = ft.Row(
            [
                ft.Icon(ft.Icons.CHEVRON_RIGHT),
                ft.Text("Продолжить", weight=ft.FontWeight.BOLD)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        ),
        width=170,
        on_click=check_code
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
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Line
from kivy.core.text import LabelBase
import bcrypt
import re
from utils import db, cursor

# Регистрируем шрифт Ubuntu
LabelBase.register(name="Ubuntu", fn_regular="Ubuntu-Regular.ttf")

current_user = None

class ResetPasswordWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = 20

        # Устанавливаем размер окна на основе размера экрана устройства
        Window.size = (360, 640)

        # Добавляем кастомный фон для всего окна
        with self.canvas.before:
            Color(0.043, 0.255, 0.337, 1)  # Цвет фона
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        # Добавляем изображение "сброс.png" в верхнюю часть окна
        self.reset_image = Image(source='сброс.png', size_hint=(None, None), size=(250, 200))
        self.reset_image.center_x = self.center_x  # Центрируем по горизонтали
        self.add_widget(self.reset_image)

        # Заголовок "Сброс пароля"
        self.title_label = Label(
            text="Сброс пароля",
            size_hint_y=None,
            height=50,
            font_name="Ubuntu",
            font_size=30,
            color=(0.815, 0.624, 0.541, 1),  # Цвет текста
            bold=True,
            halign='center',  # Выравнивание по центру
        )
        self.add_widget(self.title_label)

        # Поле для ввода имени пользователя
        self.username_input = TextInput(
            hint_text="Введите имя пользователя",
            size_hint_y=None,
            height=40,
            background_normal='',
            background_color=(0.043, 0.255, 0.337, 1),
            foreground_color=(0.815, 0.624, 0.541, 1),
            padding=(10, 10),
            font_name="Ubuntu"  # Применяем шрифт Ubuntu
        )
        self.add_widget(self.username_input)
        self.add_border(self.username_input)

        # Поле для ввода email
        self.email_input = TextInput(
            hint_text="Введите email",
            size_hint_y=None,
            height=40,
            background_normal='',
            background_color=(0.043, 0.255, 0.337, 1),
            foreground_color=(0.815, 0.624, 0.541, 1),
            padding=(10, 10),
            font_name="Ubuntu"  # Применяем шрифт Ubuntu
        )
        self.add_widget(self.email_input)
        self.add_border(self.email_input)

        # Поле для ввода ключевого слова
        self.keyword_input = TextInput(
            hint_text="Введите ключевое слово",
            size_hint_y=None,
            height=40,
            password=True,
            background_normal='',
            background_color=(0.043, 0.255, 0.337, 1),
            foreground_color=(0.815, 0.624, 0.541, 1),
            padding=(10, 10),
            font_name="Ubuntu"  # Применяем шрифт Ubuntu
        )
        self.add_widget(self.keyword_input)
        self.add_border(self.keyword_input)

        # Кнопка для проверки данных
        self.verify_button = Button(
            text="Проверить данные",
            size_hint_y=None,
            height=50,
            on_press=self.verify_user,
            background_normal='',
            background_color=(0.043, 0.255, 0.337, 1),
            color=(0.815, 0.624, 0.541, 1),
            font_name="Ubuntu"  # Применяем шрифт Ubuntu
        )
        self.add_widget(self.verify_button)
        self.add_border(self.verify_button)

        # Кнопка для возврата в окно входа
        self.back_button = Button(
            text="Назад",
            size_hint_y=None,
            height=50,
            on_press=self.go_back_to_login,
            background_normal='',
            background_color=(0.043, 0.255, 0.337, 1),
            color=(0.815, 0.624, 0.541, 1),
            font_name="Ubuntu"  # Применяем шрифт Ubuntu
        )
        self.add_widget(self.back_button)
        self.add_border(self.back_button)

    def _update_rect(self, instance, value):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def add_border(self, widget):
        # Добавление границ с использованием Canvas
        with widget.canvas.after:
            Color(0.815, 0.624, 0.541, 1)  # Цвет границ
            widget.border_rect = Line(rectangle=(widget.x, widget.y, widget.width, widget.height), width=2)
        widget.bind(pos=self.update_border, size=self.update_border)

    def update_border(self, instance, value):
        # Обновление размеров и позиции границ при изменении размеров/позиции виджета
        instance.border_rect.rectangle = (instance.x, instance.y, instance.width, instance.height)

    def go_back_to_login(self, instance):
        # Возвращаем пользователя в окно входа
        from main import LoginWindow
        App.get_running_app().root.clear_widgets()
        App.get_running_app().root.add_widget(LoginWindow())

    def verify_user(self, instance):
        username = self.username_input.text.strip()
        email = self.email_input.text.strip()
        keyword = self.keyword_input.text.strip()

        if not username or not email or not keyword:
            self.show_error("Все поля должны\n быть заполнены")
            return

        # Проверка пользователя в базе данных
        cursor.execute("SELECT email, keyword_hash FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()

        if not user:
            self.show_error("Пользователь\n    не найден")
            return

        db_email, db_keyword_hash = user

        # Проверка email
        if email != db_email:
            self.show_error("Неверный email")
            return

        # Проверка ключевого слова
        if not bcrypt.checkpw(keyword.encode(), db_keyword_hash.encode()):
            self.show_error("Неверное ключевое слово")
            return

        # Если все данные верны, открываем окно для ввода нового пароля
        self.open_new_password_window()

    def open_new_password_window(self):
        self.clear_widgets()  # Убираем текущие элементы интерфейса
        self.orientation = 'vertical'

        # Поле для ввода нового пароля
        self.new_password_input = TextInput(
            hint_text="Введите новый пароль",
            size_hint_y=None,
            height=50,
            password=True,
            background_normal='',
            background_color=(0.043, 0.255, 0.337, 1),
            foreground_color=(0.815, 0.624, 0.541, 1),
            padding=(10, 10),
            font_name="Ubuntu"  # Применяем шрифт Ubuntu
        )
        self.add_widget(self.new_password_input)
        self.add_border(self.new_password_input)

        # Поле для подтверждения нового пароля
        self.confirm_password_input = TextInput(
            hint_text="Подтвердите новый пароль",
            size_hint_y=None,
            height=50,
            password=True,
            background_normal='',
            background_color=(0.043, 0.255, 0.337, 1),
            foreground_color=(0.815, 0.624, 0.541, 1),
            padding=(10, 10),
            font_name="Ubuntu"  # Применяем шрифт Ubuntu
        )
        self.add_widget(self.confirm_password_input)
        self.add_border(self.confirm_password_input)

        # Кнопка для сохранения нового пароля
        self.save_button = Button(
            text="Сохранить пароль",
            size_hint_y=None,
            height=50,
            on_press=self.save_new_password,
            background_normal='',
            background_color=(0.043, 0.255, 0.337, 1),
            color=(0.815, 0.624, 0.541, 1),
            font_name="Ubuntu"  # Применяем шрифт Ubuntu
        )
        self.add_widget(self.save_button)
        self.add_border(self.save_button)

        # Кнопка для возврата в окно входа
        self.back_button = Button(
            text="Назад",
            size_hint_y=None,
            height=50,
            on_press=self.go_back_to_login,
            background_normal='',
            background_color=(0.043, 0.255, 0.337, 1),
            color=(0.815, 0.624, 0.541, 1),
            font_name="Ubuntu"  # Применяем шрифт Ubuntu
        )
        self.add_widget(self.back_button)
        self.add_border(self.back_button)

    def save_new_password(self, instance):
        new_password = self.new_password_input.text.strip()
        confirm_password = self.confirm_password_input.text.strip()

        if not new_password or not confirm_password:
            self.show_error("Пароль не может быть пустым")
            return

        if new_password != confirm_password:
            self.show_error("Пароли не совпадают")
            return

        # Хешируем новый пароль и обновляем его в базе данных
        username = self.username_input.text.strip()
        password_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()

        try:
            cursor.execute("UPDATE users SET password_hash=%s WHERE username=%s", (password_hash, username))
            db.commit()
            self.show_error("Пароль успешно обновлен!")
            global current_user
            current_user = username
            self.log_action('Смена пароля')
        except Exception as e:
            self.show_error(f"Ошибка базы данных: {str(e)}")

    def show_error(self, message):
        popup = Popup(title="Сообщение", content=Label(text=message), size_hint=(None, None), size=(300, 200))
        popup.open()

    def log_action(self, action_type):
        if current_user:
            action_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(
                "INSERT INTO user_actions (user_id, action_type, timestamp) VALUES ((SELECT id FROM users WHERE username = %s), %s, %s)",
                (current_user, action_type, action_time))
            db.commit()

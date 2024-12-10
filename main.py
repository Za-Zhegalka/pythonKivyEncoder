import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle, Line
from kivy.core.window import Window  # Для работы с размерами экрана
from kivy.core.text import LabelBase  # Для использования шрифтов
from main_window import MainWindow
from registration_window import RegistrationWindow
from reset_password_window import ResetPasswordWindow
import bcrypt
from datetime import datetime
from utils import db, cursor

kivy.require('2.1.0')

# Регистрируем шрифт Ubuntu
LabelBase.register(name="Ubuntu", fn_regular="Ubuntu-Regular.ttf")

current_user = None


class LoginWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = 20

        # Устанавливаем размер окна на основе размера экрана устройства
        Window.size = (360, 640)  # Размер окна, соответствующий размеру экрана смартфона

        # Добавляем кастомный фон для всего окна
        with self.canvas.before:
            Color(0.043, 0.255, 0.337, 1)  # Цвет фона
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        # Добавляем изображение логотипа по центру
        self.logo_image = Image(source='2433537.png', size_hint=(None, None), size=(250, 250))
        self.logo_image.center_x = self.center_x  # Центрируем по горизонтали
        self.add_widget(self.logo_image)

        # Заголовок
        self.title_label = Label(
            text="Добро пожаловать!",
            size_hint_y=None,
            height=50,
            font_name="Ubuntu",
            font_size=30,
            color=(0.815, 0.624, 0.541, 1),  # Цвет текста
            bold=True,
            halign='center',  # Выравнивание по центру
        )
        self.add_widget(self.title_label)

        # Поле ввода для имени пользователя с границей
        self.username_input = TextInput(
            hint_text="Имя пользователя",
            size_hint_y=None,
            height=50,
            background_normal='',
            background_color=(0.043, 0.255, 0.337, 1),
            foreground_color=(0.815, 0.624, 0.541, 1),
            padding=(10, 10),
            font_name="Ubuntu"  # Применяем шрифт Ubuntu
        )
        self.add_widget(self.username_input)
        self.add_border(self.username_input)

        # Поле ввода для пароля с границей
        self.password_input = TextInput(
            hint_text="Пароль",
            size_hint_y=None,
            height=50,
            password=True,
            background_normal='',
            background_color=(0.043, 0.255, 0.337, 1),
            foreground_color=(0.815, 0.624, 0.541, 1),
            padding=(10, 10),
            font_name="Ubuntu"  # Применяем шрифт Ubuntu
        )
        self.add_widget(self.password_input)
        self.add_border(self.password_input)

        # Кнопка "Войти" с границей
        self.login_button = Button(
            text="Войти",
            size_hint_y=None,
            height=50,
            on_press=self.login,
            background_normal='',
            background_color=(0.043, 0.255, 0.337, 1),
            color=(0.815, 0.624, 0.541, 1),
            font_name="Ubuntu"  # Применяем шрифт Ubuntu
        )
        self.add_widget(self.login_button)
        self.add_border(self.login_button)

        # Кнопка "Регистрация" с границей
        self.register_button = Button(
            text="Регистрация",
            size_hint_y=None,
            height=50,
            on_press=self.open_registration,
            background_normal='',
            background_color=(0.043, 0.255, 0.337, 1),
            color=(0.815, 0.624, 0.541, 1),
            font_name="Ubuntu"  # Применяем шрифт Ubuntu
        )
        self.add_widget(self.register_button)
        self.add_border(self.register_button)

        # Кнопка "Сброс пароля" с границей
        self.reset_password_button = Button(
            text="Сброс пароля",
            size_hint_y=None,
            height=50,
            on_press=self.open_reset_password,
            background_normal='',
            background_color=(0.043, 0.255, 0.337, 1),
            color=(0.815, 0.624, 0.541, 1),
            font_name="Ubuntu"  # Применяем шрифт Ubuntu
        )
        self.add_widget(self.reset_password_button)
        self.add_border(self.reset_password_button)

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

    def login(self, instance):
        global current_user
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()

        if not username or not password:
            self.show_error("         Введите имя\nпользователя и пароль")
            return

        cursor.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
        current_user = username
        result = cursor.fetchone()
        if result and bcrypt.checkpw(password.encode(), result[1].encode()):
            self.log_action('Авторизация')
            App.get_running_app().root.clear_widgets()  # Удаляем окно авторизации
            App.get_running_app().root.add_widget(MainWindow(current_user=current_user))  # Открываем главное окно
        else:
            self.show_error("         Неверные имя\nпользователя или пароль")

    def show_error(self, message):
        popup = Popup(title="Ошибка", content=Label(text=message, color=(0.815, 0.624, 0.541, 1)),
                      size_hint=(None, None), size=(300, 200))
        popup.open()

    def log_action(self, action_type):
        action_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(
            "INSERT INTO user_actions (user_id, action_type, timestamp) VALUES ((SELECT id FROM users WHERE username = %s), %s, %s)",
            (current_user, action_type, action_time))
        db.commit()

    def open_registration(self, instance):
        App.get_running_app().root.clear_widgets()
        App.get_running_app().root.add_widget(RegistrationWindow())

    def open_reset_password(self, instance):
        App.get_running_app().root.clear_widgets()
        App.get_running_app().root.add_widget(ResetPasswordWindow())


class MyApp(App):
    def build(self):
        return LoginWindow()  # Устанавливаем окно авторизации как главное


if __name__ == "__main__":
    MyApp().run()

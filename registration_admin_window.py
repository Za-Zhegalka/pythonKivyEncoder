from datetime import datetime
import bcrypt
import re
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle, Line
from kivy.core.window import Window
from kivy.core.text import LabelBase
from pygments.lexers import dns

from utils import db, cursor

# Регистрируем шрифт Ubuntu
LabelBase.register(name="Ubuntu", fn_regular="Ubuntu-Regular.ttf")

class RegistrationAdminWindow(BoxLayout):
    def __init__(self, current_user, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = 20
        self.current_user = current_user  # Текущий пользователь (администратор)

        # Устанавливаем размер окна
        Window.size = (360, 640)

        # Добавляем кастомный фон
        with self.canvas.before:
            Color(0.043, 0.255, 0.337, 1)  # Цвет фона
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        # Добавляем изображение "регистрация.webp" в верхнюю часть окна
        self.registration_image = Image(source='регистрация.png', size_hint=(None, None), size=(270, 200))
        self.registration_image.center_x = self.center_x  # Центрируем по горизонтали
        self.add_widget(self.registration_image)

        # Заголовок "Регистрация"
        self.title_label = Label(
            text="Регистрация",
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
            hint_text="Имя пользователя",
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

        # Поле для ввода пароля
        self.password_input = TextInput(
            hint_text="Пароль",
            size_hint_y=None,
            height=40,
            password=True,
            background_normal='',
            background_color=(0.043, 0.255, 0.337, 1),
            foreground_color=(0.815, 0.624, 0.541, 1),
            padding=(10, 10),
            font_name="Ubuntu"  # Применяем шрифт Ubuntu
        )
        self.add_widget(self.password_input)
        self.add_border(self.password_input)

        # Поле для ввода ключевого слова
        self.keyword_input = TextInput(
            hint_text="Ключевое слово",
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

        # Поле для ввода email
        self.email_input = TextInput(
            hint_text="Email",
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

        # Кнопка для регистрации
        self.register_button = Button(
            text="Зарегистрироваться",
            size_hint_y=None,
            height=50,
            on_press=self.register,
            background_normal='',
            background_color=(0.043, 0.255, 0.337, 1),
            color=(0.815, 0.624, 0.541, 1),
            font_name="Ubuntu"  # Применяем шрифт Ubuntu
        )
        self.add_widget(self.register_button)
        self.add_border(self.register_button)

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
        # Возвращаемся в окно входа
        from main import LoginWindow
        App.get_running_app().root.clear_widgets()
        App.get_running_app().root.add_widget(LoginWindow())

    def register(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        keyword = self.keyword_input.text.strip()
        email = self.email_input.text.strip()

        # Проверка на пустые поля
        if not username or not password or not keyword or not email:
            self.show_error("Все поля должны\nбыть заполнены")
            return

        # Регулярное выражение для проверки email
        email_regex = r"^[a-zA-Z0-9._%+-]+@([a-zA-Z0-9.-]+)\.[a-zA-Z]{2,}$"

        # Проверка формата email
        if not re.match(email_regex, email):
            self.show_error("Некорректный email.\nИспользуйте только\nанглийские буквы и\nформат '..@..'")
            return

        # Извлекаем домен из email
        domain = email.split('@')[-1]

        # Логическая проверка, что домен существует с использованием DNS-запроса
        try:
            dns.resolver.resolve(domain, 'MX')  # Проверка записи MX для домена
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            self.show_error(f"Домен {domain}\nне существует\nили не имеет\nпочтовых записей.")
            return

        # Проверка на уникальность имени пользователя
        try:
            cursor.execute("SELECT 1 FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                self.show_error("Пользователь с таким\nименем уже существует")
                return
        except Exception as e:
            self.show_error(f"Ошибка базы данных\nпри проверке имени\nпользователя: {str(e)}")
            return

        # Проверка на уникальность email
        try:
            cursor.execute("SELECT 1 FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                self.show_error("    Аккаунт с этим\nemail уже существует")
                return
        except Exception as e:
            self.show_error(f"Ошибка базы данных\nпри проверке email: {str(e)}")
            return

        # Хеширование пароля и ключевого слова
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        keyword_hash = bcrypt.hashpw(keyword.encode(), bcrypt.gensalt()).decode()

        # Вставка данных в базу
        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash, keyword_hash, email, user_type) VALUES (%s, %s, %s, %s, %s)",
                (username, password_hash, keyword_hash, email, 'Admin')
            )
            db.commit()
            self.show_h("Регистрация прошла успешно!")
            global current_user
            current_user = username
            self.log_action('Регистрация')
        except Exception as e:
            self.show_error(f"Ошибка базы данных: {str(e)}")

    def show_error(self, message):
        popup = Popup(title="Ошибка", content=Label(text=message, color=(0.815, 0.624, 0.541, 1)),
                      size_hint=(None, None), size=(300, 200))
        popup.open()

    def show_h(self, message):
        popup = Popup(title="Успех", content=Label(text=message, color=(0.815, 0.624, 0.541, 1)),
                      size_hint=(None, None), size=(300, 200))
        popup.open()

    def log_action(self, action_type):
        if current_user:
            action_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(
                "INSERT INTO user_actions (user_id, action_type, timestamp) VALUES ((SELECT id FROM users WHERE username = %s), %s, %s)",
                (current_user, action_type, action_time))
            db.commit()

# Пример использования в приложении
class RegistrationApp(App):
    def build(self):
        return RegistrationAdminWindow(current_user='Admin')

if __name__ == '__main__':
    RegistrationApp().run()

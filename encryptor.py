from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserIconView
from utils import encrypt, generate_key
from utils import db, cursor
from datetime import datetime


class EncryptorWindow(Popup):
    def __init__(self, current_user, **kwargs):
        super().__init__(**kwargs)
        self.current_user = current_user  # Сохраняем имя пользователя
        self.title = "Шифратор"
        self.size_hint = (0.8, 0.8)  # Всплывающее окно занимает 80% экрана
        self.pos_hint = {'center_x': 0.5, 'center_y': 0.5}  # Размещение по центру

        # Основной layout с вертикальной ориентацией
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Текстовое поле с заголовком
        self.label = Label(
            text="   Введите текст\nдля шифрования:",  # Разделяем фразу на две строки
            font_size=18,
            size_hint_y=None,
            height=40,
            font_name="Ubuntu",
            color=(0.815, 0.624, 0.541, 1)  # Цвет текста
        )
        self.layout.add_widget(self.label)

        # Поле для ввода текста
        self.text_input = TextInput(
            hint_text="Введите текст для шифрования",
            font_size=16,
            size_hint_y=None,
            height=150,
            background_normal='',
            background_color=(0.043, 0.255, 0.337, 1),
            foreground_color=(0.815, 0.624, 0.541, 1),
            padding=(10, 10),
            font_name="Ubuntu"
        )
        self.layout.add_widget(self.text_input)

        # Кнопка шифрования
        self.encrypt_button = Button(
            text="Шифровать",
            size_hint_y=None,
            height=50,
            background_normal='',
            background_color=(0.26, 0.56, 0.94, 1),
            color=(1, 1, 1, 1),
            font_name="Ubuntu",
            on_press=self.encrypt_text
        )
        self.layout.add_widget(self.encrypt_button)

        # Кнопка "Назад"
        self.back_button = Button(
            text="Назад",
            size_hint_y=None,
            height=50,
            background_normal='',
            background_color=(0.85, 0.33, 0.33, 1),
            color=(1, 1, 1, 1),
            font_name="Ubuntu",
            on_press=self.dismiss
        )
        self.layout.add_widget(self.back_button)

        self.add_widget(self.layout)

        self.encrypted_text = None  # Поле для хранения зашифрованного текста
        self.key = None  # Поле для хранения ключа

    def encrypt_text(self, instance):
        text = self.text_input.text.strip()  # Убираем лишние пробелы и переносы строк
        if not text:
            popup = Popup(
                title="Ошибка",
                content=Label(text="Введите текст для шифрования", color=(0.815, 0.624, 0.541, 1)),
                size_hint=(0.5, 0.2),  # Уменьшаем размер окна уведомления
                pos_hint={'center_x': 0.5, 'center_y': 0.5}  # Центрируем на экране
            )
            popup.open()
            return

        # Выполняем шифрование
        self.key = generate_key()
        self.encrypted_text, self.key = encrypt(text, self.key)

        # Отобразим зашифрованный текст в текстовом поле
        self.text_input.text = self.encrypted_text.decode()

        # Сохраняем в базу данных
        self.save_to_db(text, self.encrypted_text.decode(), self.key)

        # Логируем действие шифрования
        self.log_encryption_action()

        # Покажем диалоговые окна для сохранения
        self.show_save_dialog("Сохраните зашифрованный текст", self.encrypted_text, "txt")
        self.show_save_dialog("Сохраните ключ", self.key, "key")

    def save_to_db(self, original_text, encrypted_text, key):
        """
        Сохраняет данные шифрования в базу данных.
        """
        try:
            cursor.execute(
                "INSERT INTO encryption_log (original_text, encrypted_text, encryption_key, user_id) "
                "VALUES (%s, %s, %s, (SELECT id FROM users WHERE username = %s))",
                (original_text, encrypted_text, key, self.current_user)
            )
            db.commit()
        except Exception as e:
            db.rollback()

    def show_save_dialog(self, title, content, file_extension):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        file_chooser = FileChooserIconView()
        layout.add_widget(file_chooser)

        name_input = TextInput(
            hint_text=f"Введите имя файла ({file_extension})",
            size_hint_y=None,
            height=50,
            font_name="Ubuntu"
        )
        layout.add_widget(name_input)

        def save_file(instance):
            if file_chooser.path and name_input.text:
                file_path = f"{file_chooser.path}/{name_input.text.strip()}.{file_extension}"  # Убираем пробелы из имени файла
                with open(file_path, "wb") as file:
                    file.write(content)
                popup.dismiss()

                # Обработка длинного пути и добавление переносов строк
                path_label = Label(
                    text=f"Файл сохранён: {file_path}",
                    size_hint_y=None,
                    height=100,
                    text_size=(400, None),  # Автоматический перенос текста
                    halign="center",  # Выравнивание по центру
                    valign="middle"  # Вертикальное выравнивание по центру
                )
                path_label.bind(width=lambda *args: path_label.setter('text_size')(path_label, (
                    path_label.width, None)))  # Автоматический перенос текста

                # Уменьшаем размер окна успешного сохранения файла
                success_popup = Popup(
                    title="Успех",
                    content=path_label,
                    size_hint=(0.5, 0.3),  # Уменьшаем размер окна уведомления
                    pos_hint={'center_x': 0.5, 'center_y': 0.5}  # Центрируем на экране
                )
                success_popup.open()

        confirm_button = Button(
            text="Сохранить",
            size_hint_y=None,
            height=50,
            background_normal='',
            background_color=(0.26, 0.56, 0.94, 1),
            color=(1, 1, 1, 1),
            font_name="Ubuntu",
            on_press=save_file
        )
        cancel_button = Button(
            text="Отмена",
            size_hint_y=None,
            height=50,
            background_normal='',
            background_color=(0.85, 0.33, 0.33, 1),
            color=(1, 1, 1, 1),
            font_name="Ubuntu",
            on_press=lambda _: popup.dismiss()
        )

        buttons_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        buttons_layout.add_widget(confirm_button)
        buttons_layout.add_widget(cancel_button)
        layout.add_widget(buttons_layout)

        popup = Popup(title=title, content=layout, size_hint=(1, 1), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        popup.open()

    def log_encryption_action(self):
        """Записываем действие шифрования в историю действий пользователя."""
        if self.current_user:
            action_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(
                "INSERT INTO user_actions (user_id, action_type, timestamp) "
                "VALUES ((SELECT id FROM users WHERE username = %s), %s, %s)",
                (self.current_user, 'Шифрование', action_time)
            )
            db.commit()


# Запуск приложения (для тестирования окна отдельно)
class MyApp(App):
    def build(self):
        return EncryptorWindow(current_user="user_placeholder")  # Для теста передаем имя пользователя


if __name__ == '__main__':
    MyApp().run()

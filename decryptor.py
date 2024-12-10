from datetime import datetime
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserIconView
from utils import decrypt
from utils import db, cursor

class DecryptorWindow(Popup):
    def __init__(self, current_user, **kwargs):
        super().__init__(**kwargs)
        self.current_user = current_user
        self.title = "Дешифратор"
        self.size_hint = (0.8, 0.8)  # Уменьшаем размер окна до 80% от экрана
        self.pos_hint = {'center_x': 0.5, 'center_y': 0.5}  # Центрируем окно

        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.label = Label(text="Введите зашифрованный текст\n        или загрузите файл:", font_size=18,
            size_hint_y=None,
            height=40,
            font_name="Ubuntu",
            color=(0.815, 0.624, 0.541, 1))
        self.layout.add_widget(self.label)

        self.text_input = TextInput(hint_text="Введите зашифрованный текст", font_size=16, size_hint_y=None, height=100)
        self.layout.add_widget(self.text_input)

        self.upload_button = Button(text="Загрузить файл", size_hint_y=None, height=50, background_normal='',
                                     background_color=(0.65, 1.00, 0.00, 0.58), color=(1, 1, 1, 1), on_press=self.load_file)
        self.layout.add_widget(self.upload_button)

        self.decrypt_button = Button(text="Дешифровать", size_hint_y=None, height=50, background_normal='',
                                     background_color=(0.26, 0.56, 0.94, 1), color=(1, 1, 1, 1), on_press=self.decrypt_text)
        self.layout.add_widget(self.decrypt_button)

        self.back_button = Button(text="Назад", size_hint_y=None, height=50, background_normal='',
                                     background_color=(0.85, 0.33, 0.33, 1), color=(1, 1, 1, 1), on_press=self.dismiss)
        self.layout.add_widget(self.back_button)

        self.add_widget(self.layout)

    def load_file(self, instance):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        file_chooser = FileChooserIconView()
        file_chooser.filters = ['*.txt']
        layout.add_widget(file_chooser)

        confirm_button = Button(text="Выбрать файл", size_hint_y=None, height=50)
        cancel_button = Button(text="Отмена", size_hint_y=None, height=50, on_press=lambda _: popup.dismiss())

        def confirm_file_selection(instance):
            if file_chooser.selection:
                file_path = file_chooser.selection[0]
                with open(file_path, "rb") as file:
                    encrypted_text = file.read()
                self.text_input.text = encrypted_text.decode()
                popup.dismiss()

        confirm_button.bind(on_press=confirm_file_selection)

        buttons_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        buttons_layout.add_widget(confirm_button)
        buttons_layout.add_widget(cancel_button)
        layout.add_widget(buttons_layout)

        popup = Popup(title="Выбор зашифрованного файла", content=layout, size_hint=(0.9, 0.9))
        popup.open()

    def decrypt_text(self, instance):
        encrypted_text = self.text_input.text.strip().encode()
        if not encrypted_text:
            popup = Popup(
                title="Ошибка",
                content=Label(text="Введите зашифрованный текст или загрузите файл"),
                size_hint=(0.5, 0.2),  # Уменьшаем размер окна уведомления
                pos_hint={'center_x': 0.5, 'center_y': 0.5}  # Центрируем окно
            )
            popup.open()
            return

        self.load_key(encrypted_text)

    def load_key(self, encrypted_text):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        file_chooser = FileChooserIconView()
        file_chooser.filters = ['*.key']
        layout.add_widget(file_chooser)

        confirm_button = Button(text="Выбрать ключ", size_hint_y=None, height=50)
        cancel_button = Button(text="Отмена", size_hint_y=None, height=50, on_press=lambda _: popup.dismiss())

        def confirm_key_selection(instance):
            if file_chooser.selection:
                key_file_path = file_chooser.selection[0]
                with open(key_file_path, "rb") as key_file:
                    key = key_file.read()
                popup.dismiss()
                self.process_decryption(encrypted_text, key)

        confirm_button.bind(on_press=confirm_key_selection)

        buttons_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        buttons_layout.add_widget(confirm_button)
        buttons_layout.add_widget(cancel_button)
        layout.add_widget(buttons_layout)

        popup = Popup(title="Выбор файла ключа", content=layout, size_hint=(0.9, 0.9))
        popup.open()

    def process_decryption(self, encrypted_text, key):
        try:
            decrypted_text = decrypt(encrypted_text, key)
            self.text_input.text = decrypted_text

            popup = Popup(
                title="Успех",
                content=Label(text="Текст успешно дешифрован"),
                size_hint=(0.9, 0.5),  # Уменьшаем размер окна уведомления
                pos_hint={'center_x': 0.5, 'center_y': 0.5}  # Центрируем окно
            )

            # Сохраняем в базу данных
            self.save_to_db(encrypted_text.decode(), decrypted_text, key)

            # Логируем действие дешифрования
            self.log_decryption_action()

            popup.open()
        except Exception as e:
            popup = Popup(
                title="Ошибка",
                content=Label(text=f"Не удалось дешифровать: {e}"),
                size_hint=(0.5, 0.2),  # Уменьшаем размер окна уведомления
                pos_hint={'center_x': 0.5, 'center_y': 0.5}  # Центрируем окно
            )
            popup.open()

    def save_to_db(self, encrypted_text, decrypted_text, key):
        """
        Сохраняет данные дешифрования в базу данных.
        """
        try:
            cursor.execute(
                "INSERT INTO decryption_log (encrypted_text, decrypted_text, decryption_key, user_id) "
                "VALUES (%s, %s, %s, (SELECT id FROM users WHERE username = %s))",
                (encrypted_text, decrypted_text, key, self.current_user)
            )
            db.commit()  # Применить изменения в базе данных
        except Exception as e:
            db.rollback()  # В случае ошибки откатываем изменения
            popup = Popup(
                title="Ошибка",
                content=Label(text=f"Не удалось сохранить в базу: {e}"),
                size_hint=(0.5, 0.2),  # Уменьшаем размер окна уведомления
                pos_hint={'center_x': 0.5, 'center_y': 0.5}  # Центрируем окно
            )
            popup.open()

    def log_decryption_action(self):
        """Записываем действие дешифрования в историю действий пользователя."""
        if self.current_user:
            action_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(
                "INSERT INTO user_actions (user_id, action_type, timestamp) "
                "VALUES ((SELECT id FROM users WHERE username = %s), %s, %s)",
                (self.current_user, 'Дешифрование', action_time)
            )
            db.commit()

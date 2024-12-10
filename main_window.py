from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle, Line
from kivy.core.text import LabelBase
from datetime import datetime
from encryptor import EncryptorWindow
from decryptor import DecryptorWindow
from action_history import ActionHistoryWindow
from statistics_window import StatisticsWindow  # Импортируем StatisticsWindow
from utils import cursor, db

# Registering custom font (same as LoginWindow)
LabelBase.register(name="Ubuntu", fn_regular="Ubuntu-Regular.ttf")


class MainWindow(BoxLayout):
    def __init__(self, current_user, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.current_user = current_user

        self.spacing = 10
        self.padding = 20

        # Set window size similar to LoginWindow (for consistency)
        Window.size = (360, 640)

        # Background color
        with self.canvas.before:
            Color(0.043, 0.255, 0.337, 1)  # Set background color (same as LoginWindow)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        # Add logo image
        self.logo_image = Image(source='меню.png', size_hint=(None, None), size=(300, 200))
        self.logo_image.center_x = self.center_x
        self.add_widget(self.logo_image)

        # Title label
        self.title_label = Label(
            text="Главное меню",
            size_hint_y=None,
            height=50,
            font_name="Ubuntu",
            font_size=30,
            color=(0.815, 0.624, 0.541, 1),
            bold=True,
            halign='center',
        )
        self.add_widget(self.title_label)

        # Action buttons (Encrypt, Decrypt, etc.)
        self.encrypt_button = Button(
            text="Открыть шифратор",
            size_hint_y=None,
            height=50,
            background_normal='',
            background_color=(0.043, 0.255, 0.337, 1),
            color=(0.815, 0.624, 0.541, 1),
            font_name="Ubuntu",
            on_press=self.open_encryptor_window
        )
        self.add_widget(self.encrypt_button)
        self.add_border(self.encrypt_button)

        self.decrypt_button = Button(
            text="Открыть дешифратор",
            size_hint_y=None,
            height=50,
            background_normal='',
            background_color=(0.043, 0.255, 0.337, 1),
            color=(0.815, 0.624, 0.541, 1),
            font_name="Ubuntu",
            on_press=self.open_decryptor_window
        )
        self.add_widget(self.decrypt_button)
        self.add_border(self.decrypt_button)

        # User type check for admin
        user_type = self.get_user_type(self.current_user)
        if user_type == 'Admin':
            self.history_button = Button(
                text="История действий",
                size_hint=(1, None),
                height=50,
                background_normal='',
                background_color=(0.043, 0.255, 0.337, 1),
                color=(0.815, 0.624, 0.541, 1),
                font_name="Ubuntu",
                on_press=self.open_action_history
            )
            self.add_widget(self.history_button)
            self.add_border(self.history_button)

            # Button to open StatisticsWindow
            self.statistics_button = Button(
                text="Открыть статистику",
                size_hint_y=None,
                height=50,
                background_normal='',
                background_color=(0.043, 0.255, 0.337, 1),
                color=(0.815, 0.624, 0.541, 1),
                font_name="Ubuntu",
                on_press=self.open_statistics_window  # Метод для открытия окна статистики
            )
            self.add_widget(self.statistics_button)
            self.add_border(self.statistics_button)

            self.create_admin_button = Button(
                text="Создать нового администратора",
                size_hint_y=None,
                height=50,
                background_normal='',
                background_color=(0.043, 0.255, 0.337, 1),
                color=(0.815, 0.624, 0.541, 1),
                font_name="Ubuntu",
                on_press=self.create_admin
            )
            self.add_widget(self.create_admin_button)
            self.add_border(self.create_admin_button)

        # Logout and Exit buttons
        self.logout_account_button = Button(
            text="Выход из аккаунта",
            size_hint=(1, None),
            height=50,
            background_normal='',
            background_color=(0.043, 0.255, 0.337, 1),
            color=(0.815, 0.624, 0.541, 1),
            font_name="Ubuntu",
            on_press=self.logout_account
        )
        self.add_widget(self.logout_account_button)
        self.add_border(self.logout_account_button)

        self.exit_button = Button(
            text="Выход из программы",
            size_hint=(1, None),
            height=50,
            background_normal='',
            background_color=(0.043, 0.255, 0.337, 1),
            color=(0.815, 0.624, 0.541, 1),
            font_name="Ubuntu",
            on_press=self.exit_app
        )
        self.add_widget(self.exit_button)
        self.add_border(self.exit_button)

        # Handling window close event
        Window.bind(on_request_close=self.on_request_close)

    def open_statistics_window(self, instance):
        """Open StatisticsWindow"""
        statistics_window = StatisticsWindow(current_user=self.current_user)
        statistics_window.open()

    def _update_rect(self, instance, value):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def add_border(self, widget):
        """Adding border to buttons"""
        with widget.canvas.after:
            Color(0.815, 0.624, 0.541, 1)  # Border color
            widget.border_rect = Line(rectangle=(widget.x, widget.y, widget.width, widget.height), width=2)
        widget.bind(pos=self.update_border, size=self.update_border)

    def update_border(self, instance, value):
        """Update border size/position"""
        instance.border_rect.rectangle = (instance.x, instance.y, instance.width, instance.height)

    def get_user_type(self, username):
        """Get user type (Admin or User)"""
        cursor.execute("SELECT user_type FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        return result[0] if result else None

    def open_encryptor_window(self, instance):
        """Open encryptor window"""
        encrypt_window = EncryptorWindow(current_user=self.current_user)
        encrypt_window.open()

    def open_decryptor_window(self, instance):
        """Open decryptor window"""
        decrypt_window = DecryptorWindow(current_user=self.current_user)
        decrypt_window.open()

    def open_action_history(self, instance):
        """Open action history window"""
        action_window = ActionHistoryWindow(current_user=self.current_user)
        action_window.open()

    def create_admin(self, instance):
        """Open admin registration window"""
        from registration_admin_window import RegistrationAdminWindow
        admin_registration_window = RegistrationAdminWindow(current_user=self.current_user)
        App.get_running_app().root.clear_widgets()
        App.get_running_app().root.add_widget(admin_registration_window)

    def logout_account(self, instance):
        """Logout and record action"""
        if self.current_user:
            self.log_action('Выход из аккаунта')
        self.clear_widgets()
        from main import LoginWindow
        login_window = LoginWindow()
        self.add_widget(login_window)

    def exit_app(self, instance):
        """Exit app and record action"""
        if self.current_user:
            self.log_action('Выход из аккаунта')
        App.get_running_app().stop()

    def log_action(self, action_type):
        """Log action to the database"""
        if self.current_user:
            action_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(
                "INSERT INTO user_actions (user_id, action_type, timestamp) VALUES ((SELECT id FROM users WHERE username = %s), %s, %s)",
                (self.current_user, action_type, action_time))
            db.commit()

    def on_request_close(self, *args):
        """Handle window close event"""
        if self.current_user:
            action_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(
                "INSERT INTO user_actions (user_id, action_type, timestamp) VALUES ((SELECT id FROM users WHERE username = %s), %s, %s)",
                (self.current_user, 'Выход из аккаунта', action_time))
            db.commit()
        return False

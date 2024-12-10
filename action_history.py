from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from utils import cursor, db  # db - это объект подключения, который мы импортируем из utils.py


class ActionHistoryWindow(Popup):
    def __init__(self, current_user, **kwargs):
        super().__init__(**kwargs)
        self.title = "История действий"
        self.size_hint = (0.9, 0.9)

        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Создаем ScrollView для отображения истории
        self.scroll_view = ScrollView(
            size_hint=(1, 0.8),  # Ограничиваем высоту ScrollView
            bar_width=10,
            scroll_type=['bars', 'content'],  # Включаем прокрутку по контенту и полосе
            do_scroll_x=True,  # Поддержка горизонтального скроллинга
            do_scroll_y=True,  # Поддержка вертикального скроллинга
        )

        # Внутренний GridLayout
        self.grid_layout = GridLayout(
            cols=3,  # Количество колонок
            spacing=20,
            size_hint=(None, None),
        )
        self.grid_layout.bind(minimum_width=self.grid_layout.setter('width'))
        self.grid_layout.bind(minimum_height=self.grid_layout.setter('height'))

        self.scroll_view.add_widget(self.grid_layout)

        # Добавляем стрелки управления горизонтальной прокруткой
        self.navigation_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=50)
        self.left_button = Button(text="<", size_hint=(None, 1), width=50, background_normal='',
                                     background_color=(0.65, 1.00, 0.00, 0.58), color=(1, 1, 1, 1), on_press=self.scroll_left)
        self.right_button = Button(text=">", size_hint=(None, 1), width=50, background_normal='',
                                     background_color=(0.65, 1.00, 0.00, 0.58), color=(1, 1, 1, 1), on_press=self.scroll_right)
        self.navigation_layout.add_widget(self.left_button)
        self.navigation_layout.add_widget(self.right_button)

        # Добавляем элементы в основной layout
        self.layout.add_widget(self.scroll_view)
        self.layout.add_widget(self.navigation_layout)

        # Кнопка для очистки истории
        self.clear_button = Button(text="Очистить историю", size_hint_y=None, height=50, background_normal='',
                                     background_color=(0.26, 0.56, 0.94, 1), color=(1, 1, 1, 1), on_press=self.clear_history)
        self.layout.add_widget(self.clear_button)

        # Кнопка для закрытия окна
        self.close_button = Button(text="Назад", size_hint_y=None, height=50, background_normal='',
                                     background_color=(0.85, 0.33, 0.33, 1), color=(1, 1, 1, 1), on_press=self.dismiss)
        self.layout.add_widget(self.close_button)

        self.add_widget(self.layout)

        # Заполняем историю
        self.populate_history(current_user)

    def populate_history(self, current_user):
        """Заполнение таблицы данными."""
        self.grid_layout.clear_widgets()

        # Заголовки таблицы
        headers = ["Дата", "Тип действия", "Пользователь"]
        for header in headers:
            self.grid_layout.add_widget(Label(text=header, bold=True, size_hint=(None, None), size=(200, 50)))

        # Получение данных из базы
        cursor.execute("""
            SELECT ua.timestamp, ua.action_type, u.username
            FROM user_actions ua
            JOIN users u ON ua.user_id = u.id
            ORDER BY ua.timestamp DESC
        """)
        actions = cursor.fetchall()

        for action in actions:
            timestamp, action_type, username = action
            self.grid_layout.add_widget(Label(text=timestamp.strftime('%Y-%m-%d %H:%M:%S'), size_hint=(None, None), size=(200, 50)))
            self.grid_layout.add_widget(Label(text=action_type, size_hint=(None, None), size=(200, 50)))
            self.grid_layout.add_widget(Label(text=username, size_hint=(None, None), size=(200, 50)))

        # Обновляем размеры таблицы
        self.grid_layout.width = 3 * 200  # 3 колонки по 200px
        self.grid_layout.height = len(actions) * 50 + 50  # Строки данных + заголовок

    def clear_history(self, instance):
        """Очистка истории действий."""
        cursor.execute("DELETE FROM user_actions")
        db.commit()

        # Сбрасываем auto_increment
        cursor.execute("ALTER TABLE user_actions AUTO_INCREMENT = 1")
        db.commit()

        # Очищаем таблицу в интерфейсе
        self.populate_history(None)

    def scroll_left(self, instance):
        """Сдвиг таблицы влево."""
        current_x = self.scroll_view.scroll_x
        self.scroll_view.scroll_x = max(current_x - 0.1, 0)

    def scroll_right(self, instance):
        """Сдвиг таблицы вправо."""
        current_x = self.scroll_view.scroll_x
        self.scroll_view.scroll_x = min(current_x + 0.1, 1)

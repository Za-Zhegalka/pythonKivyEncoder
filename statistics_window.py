from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from datetime import datetime, timedelta
from utils import cursor


class StatisticsWindow(Popup):
    def __init__(self, current_user, **kwargs):
        super().__init__(**kwargs)
        self.current_user = current_user
        self.title = 'Статистика'

        # Установим размер окна на весь экран
        self.size_hint = (1, 1)  # Окно будет на весь размер экрана
        self.auto_dismiss = False  # Чтобы окно не закрывалось по клику вне его

        # Основной контейнер
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=20)

        # Выбор действия (Шифрование/Дешифрование)
        self.action_spinner = Spinner(
            text='Выберите действие',
            values=('Шифрование', 'Дешифрование'),
            size_hint=(None, None),
            size=(200, 44),
            background_color=(0.26, 0.56, 0.94, 1),
            color=(1, 1, 1, 1),
            pos_hint={'center_x': 0.5}
        )
        self.layout.add_widget(self.action_spinner)

        # Выбор периода
        self.period_spinner = Spinner(
            text='Выберите период',
            values=('Сегодня', 'За неделю', 'За месяц', 'За год'),
            size_hint=(None, None),
            size=(200, 44),
            background_color=(0.26, 0.56, 0.94, 1),
            color=(1, 1, 1, 1),
            pos_hint={'center_x': 0.5}
        )
        self.layout.add_widget(self.period_spinner)

        # Кнопка для отображения статистики (на всю ширину окна)
        self.show_button = Button(
            text='Показать статистику',
            size_hint=(1, None),  # Кнопка будет растягиваться на всю ширину
            height=50,
            background_normal='',
            background_color=(0.043, 0.255, 0.337, 1),
            color=(0.815, 0.624, 0.541, 1),
            on_press=self.show_statistics
        )
        self.layout.add_widget(self.show_button)

        # Место для вывода статистики (с возможностью прокрутки, если данных много)
        self.stat_label = Label(
            text='',
            size_hint_y=None,
            height=100,  # Местоположение для вывода текста статистики
            valign='top',  # Вертикальное выравнивание текста
            halign='left',  # Горизонтальное выравнивание текста
            #text_size=(self.width - 0, None)  # Установка размера текста с учетом ширины окна
        )
        self.layout.add_widget(self.stat_label)

        # Закрытие окна
        self.close_button = Button(
            text="Закрыть",
            size_hint=(None, None),
            height=50,
            background_normal='',
            background_color=(0.043, 0.255, 0.337, 1),
            color=(0.815, 0.624, 0.541, 1),
            on_press=self.dismiss
        )
        self.layout.add_widget(self.close_button)

        self.add_widget(self.layout)

    def show_statistics(self, instance):
        """Показать статистику в зависимости от выбранного периода и действия"""
        # Проверяем, что выбраны оба параметра
        action = self.action_spinner.text
        period = self.period_spinner.text

        # Если не выбран период или действие
        if action == 'Выберите действие':
            self.stat_label.text = "Ошибка: выберите\nдействие\n(Шифрование/Дешифрование)"
            return

        if period == 'Выберите период':
            self.stat_label.text = "Ошибка: выберите\nпериод (Сегодня,\nЗа неделю, За месяц, За год)"
            return

        # Определяем дату начала в зависимости от выбранного периода
        end_date = datetime.now()
        if period == 'Сегодня':
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'За неделю':
            start_date = end_date - timedelta(weeks=1)
        elif period == 'За месяц':
            start_date = end_date - timedelta(days=30)
        elif period == 'За год':
            start_date = end_date - timedelta(days=365)

        # Получаем данные из базы данных
        try:
            if action == 'Шифрование':
                cursor.execute("""
                    SELECT COUNT(*) FROM encryption_log
                    WHERE user_id = (SELECT id FROM users WHERE username = %s)
                    AND timestamp BETWEEN %s AND %s
                """, (self.current_user, start_date, end_date))
            elif action == 'Дешифрование':
                cursor.execute("""
                    SELECT COUNT(*) FROM decryption_log
                    WHERE user_id = (SELECT id FROM users WHERE username = %s)
                    AND timestamp BETWEEN %s AND %s
                """, (self.current_user, start_date, end_date))

            result = cursor.fetchone()
            if result:
                self.stat_label.text = f"Количество действий\n({action}): {result[0]}"
            else:
                self.stat_label.text = f"Нет данных для\nвыбранного периода\n({action})"
        except Exception as e:
            self.stat_label.text = f"Ошибка при получении\nданных: {str(e)}"

import random, string, datetime, json, os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.anchorlayout import AnchorLayout

# Глобальные настройки дизайна
Window.clearcolor = (0.05, 0.07, 0.1, 1) 
MAIN_BLUE = (0, 0.47, 0.85, 1)
SIDE_PANEL = (0.1, 0.13, 0.18, 1)
MY_MSG_COLOR = "00dbff"
FRIEND_MSG_COLOR = "cccccc"

class RegScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = AnchorLayout(anchor_x='center', anchor_y='center', padding=20)
        
        form = BoxLayout(orientation='vertical', spacing=12, size_hint=(None, None), width='320dp', height='480dp')
        
        form.add_widget(Label(text="[b]Dotto Messenger[/b]", markup=True, font_size='30sp', color=MAIN_BLUE, size_hint_y=None, height='70dp'))
        form.add_widget(Label(text="Регистрация нового аккаунта", font_size='14sp', color=(0.6, 0.6, 0.6, 1), size_hint_y=None, height='30dp'))
        
        self.login = TextInput(hint_text="Логин", multiline=False, size_hint_y=None, height='45dp', background_color=(0.1, 0.15, 0.2, 1), foreground_color=(1,1,1,1))
        self.pw1 = TextInput(hint_text="Пароль", password=True, multiline=False, size_hint_y=None, height='45dp', background_color=(0.1, 0.15, 0.2, 1), foreground_color=(1,1,1,1))
        self.pw2 = TextInput(hint_text="Повторите пароль", password=True, multiline=False, size_hint_y=None, height='45dp', background_color=(0.1, 0.15, 0.2, 1), foreground_color=(1,1,1,1))
        
        form.add_widget(self.login); form.add_widget(self.pw1); form.add_widget(self.pw2)
        
        self.err = Label(text="", color=(1, 0.2, 0.2, 1), size_hint_y=None, height='30dp', font_size='12sp')
        form.add_widget(self.err)
        
        reg_btn = Button(text="СОЗДАТЬ АККАУНТ", size_hint_y=None, height='55dp', background_color=MAIN_BLUE, bold=True)
        reg_btn.bind(on_release=self.do_reg)
        form.add_widget(reg_btn); root.add_widget(form)

        # Кнопка ИНФО
        h_box = AnchorLayout(anchor_x='left', anchor_y='top', padding=20)
        h_btn = Button(text="?", size_hint=(None, None), size=('45dp', '45dp'), background_color=MAIN_BLUE, bold=True)
        h_btn.bind(on_release=self.show_fancy_info)
        h_box.add_widget(h_btn)
        
        self.add_widget(root); self.add_widget(h_box)

    def show_fancy_info(self, *args):
        content = BoxLayout(orientation='vertical', padding=15, spacing=15)
        info_header = Label(text="[b][color=00dbff]О ПРИЛОЖЕНИИ[/color][/b]", markup=True, size_hint_y=None, height='40dp', font_size='20sp')
        
        body_text = (
            "Это твой личный мессенджер [b]Dotto[/b].\n\n"
            "• [b]ID:[/b] Твой личный код (напр. #1234)\n"
            "• [b]Чаты:[/b] Ищи друзей по их ID и логину\n"
            "• [b]Облако:[/b] Все сообщения сохраняются в файл\n"
            "• [b]Дизайн:[/b] Свои сообщения справа, чужие слева\n\n"
            "[color=888888]Версия: 1.0 (Release)[/color]"
        )
        
        content.add_widget(info_header)
        content.add_widget(Label(text=body_text, markup=True, halign='center', valign='middle'))
        
        close = Button(text="ЗАКРЫТЬ", size_hint_y=None, height='50dp', background_color=MAIN_BLUE)
        content.add_widget(close)
        
        pop = Popup(title="Справочный центр", content=content, size_hint=(0.85, 0.6))
        close.bind(on_release=pop.dismiss); pop.open()

    def do_reg(self, *args):
        if self.login.text and self.pw1.text == self.pw2.text and len(self.pw1.text) >= 3:
            app = App.get_running_app()
            app.user_name = self.login.text
            app.user_id = "#" + "".join(random.choices(string.digits, k=4))
            self.manager.current = 'main'
        else:
            self.err.text = "Ошибка: поля пусты или пароли не совпали!"

class MainScreen(Screen):
    current_chat = None

    def on_enter(self):
        self.clear_widgets()
        app = App.get_running_app()
        app.load_db()
        
        main_box = BoxLayout(orientation='horizontal')
        
        # Левая колонка (Список)
        left = BoxLayout(orientation='vertical', size_hint_x=0.35)
        top = BoxLayout(size_hint_y=None, height='50dp', padding=5)
        add = Button(text="+", size_hint_x=None, width='45dp', background_color=MAIN_BLUE, bold=True)
        add.bind(on_release=self.add_popup)
        top.add_widget(add); top.add_widget(Label(text="ЧАТЫ", bold=True))
        left.add_widget(top)

        self.chat_list_ui = BoxLayout(orientation='vertical', spacing=2, size_hint_y=None)
        self.chat_list_ui.bind(minimum_height=self.chat_list_ui.setter('height'))
        scroll = ScrollView(); scroll.add_widget(self.chat_list_ui)
        left.add_widget(scroll)

        for name in app.db_chats.keys(): self.draw_chat_btn(name)

        prof = Button(text="👤 ПРОФИЛЬ", size_hint_y=None, height='55dp', background_color=SIDE_PANEL)
        prof.bind(on_release=self.show_prof); left.add_widget(prof)

        # Правая колонка (Чат)
        self.work_area = BoxLayout(orientation='vertical', size_hint_x=0.65)
        self.work_area.add_widget(Label(text="Выберите чат в меню слева", color=(0.4, 0.4, 0.4, 1), halign='center'))

        main_box.add_widget(left); main_box.add_widget(self.work_area)
        self.add_widget(main_box)

    def add_popup(self, *args):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        id_in = TextInput(hint_text="ID друга (#0000)", multiline=False)
        name_in = TextInput(hint_text="Имя (Логин)", multiline=False)
        error_lab = Label(text="", color=(1,0,0,1), size_hint_y=None, height='20dp', font_size='11sp')
        btn = Button(text="НАЙТИ И ДОБАВИТЬ", background_color=MAIN_BLUE, bold=True)
        content.add_widget(id_in); content.add_widget(name_in); content.add_widget(error_lab); content.add_widget(btn)
        
        pop = Popup(title="Новый диалог", content=content, size_hint=(0.85, 0.45))
        
        def confirm(*a):
            f_id, f_name = id_in.text.strip(), name_in.text.strip()
            if not f_id.startswith("#") or not f_id[1:].isdigit():
                error_lab.text = "Неверный формат ID!"
                return
            if f_name:
                app = App.get_running_app()
                if f_name not in app.db_chats:
                    app.db_chats[f_name] = []; app.save_db(); self.draw_chat_btn(f_name)
                pop.dismiss()
        btn.bind(on_release=confirm); pop.open()

    def draw_chat_btn(self, name):
        b = Button(text=f" {name}", halign='left', size_hint_y=None, height='65dp', background_color=SIDE_PANEL)
        b.bind(on_release=lambda x: self.open_chat(name))
        self.chat_list_ui.add_widget(b)

    def open_chat(self, name):
        self.current_chat = name
        app = App.get_running_app()
        self.work_area.clear_widgets()
        
        self.work_area.add_widget(Label(text=f"[b]{name}[/b]", markup=True, size_hint_y=None, height='50dp', color=MAIN_BLUE))

        self.history_box = BoxLayout(orientation='vertical', spacing=8, size_hint_y=None, padding=10)
        self.history_box.bind(minimum_height=self.history_box.setter('height'))
        
        self.scroller = ScrollView(); self.scroller.add_widget(self.history_box)
        self.work_area.add_widget(self.scroller)

        for msg in app.db_chats[name]: self.add_msg_ui(msg)

        box = BoxLayout(size_hint_y=None, height='65dp', padding=10, spacing=10)
        self.field = TextInput(hint_text="Введите сообщение...", multiline=False)
        btn = Button(text=">", size_hint_x=0.2, background_color=MAIN_BLUE, bold=True)
        btn.bind(on_release=self.send_msg)
        box.add_widget(self.field); box.add_widget(btn)
        self.work_area.add_widget(box)

    def add_msg_ui(self, text):
        is_mine = "Вы:" in text
        halign = 'right' if is_mine else 'left'
        color = MY_MSG_COLOR if is_mine else FRIEND_MSG_COLOR
        
        lbl = Label(text=f"[color={color}]{text}[/color]", markup=True, size_hint_y=None, height='40dp', 
                    halign=halign, valign='middle', padding=(10, 0))
        lbl.bind(size=lbl.setter('text_size'))
        self.history_box.add_widget(lbl)

    def send_msg(self, *args):
        if self.field.text and self.current_chat:
            app = App.get_running_app()
            t = datetime.datetime.now().strftime("%H:%M")
            msg_text = f"{t} Вы: {self.field.text} ✓"
            app.db_chats[self.current_chat].append(msg_text); app.save_db()
            self.add_msg_ui(msg_text); self.field.text = ""
            Clock.schedule_once(lambda dt: setattr(self.scroller, 'scroll_y', 0), 0.1)

    def show_prof(self, *args):
        app = App.get_running_app()
        c = BoxLayout(orientation='vertical', padding=10)
        c.add_widget(Label(text=f"Твой ник: [b]{app.user_name}[/b]\nТвой ID: [color=00dbff]{app.user_id}[/color]", markup=True, halign='center'))
        Popup(title="Мой профиль", content=c, size_hint=(0.7, 0.35)).open()

class MyMessengerApp(App):
    user_name = ""; user_id = ""; db_chats = {}
    def save_db(self):
        with open("messenger_db.json", "w", encoding="utf-8") as f:
            json.dump(self.db_chats, f, ensure_ascii=False)
    def load_db(self):
        if os.path.exists("messenger_db.json"):
            with open("messenger_db.json", "r", encoding="utf-8") as f:
                self.db_chats = json.load(f)
    def build(self):
        sm = ScreenManager()
        sm.add_widget(RegScreen(name='reg')); sm.add_widget(MainScreen(name='main'))
        return sm

if __name__ == '__main__':
    MyMessengerApp().run()
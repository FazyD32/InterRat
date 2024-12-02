from kivymd.app import MDApp
import sqlite3
import datetime
from kivymd.uix.navigationdrawer import MDNavigationLayout
from kivy.uix.screenmanager import Screen
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.datatables import MDDataTable

# ЭТО СТУДЕНЧЕСКИЙ ПРОЕКТ ДЛЯ СДАЧИ РАБОТЫ, НАПИСАННЫЙ НА ПАЙТОН 3.8 И KIVYMD 1.2, ТАК ЧТО ВОЗМОЖНО КОМУ-ТО МОЖЕТ
# ОКАЗАТЬСЯ ПОЛЕЗНЫМ НЕБОЛЬШОЙ ОПЫТ РАБОТЫ С БАЗОЙ, АЛГОРИТМОМ И ИНТЕРФЕЙСОМ, В БЛИЖАЙШИЕ НЕСКОЛЬКО ДНЕЙ ПРОЕКТ БУДЕТ ДОРАБАТЫВАТЬСЯ
# ЕСЛИ ЕСТЬ ИДЕИ КАК МОЖНО ЧТО-ТО УЛУЧШИТЬ НЕ МЕНЯЯ ВЕРСИИ ФРЕЙМВОРКА, ТО БУДУ РАД ПОСЛУШАТЬ...

# КОММЕНТАРИИ К КОДУ БУДУТ ЗАВТРА.

class BaseControl:
    def __init__(self):
        try:
            connect = sqlite3.connect('InterCof.db')
            cursor = connect.cursor()

            # 1. модели
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS Model (
                id    INTEGER         PRIMARY KEY AUTOINCREMENT
                                    UNIQUE
                                    NOT NULL,
                title TEXT,
                cost  INTEGER (10, 2) 
            );
                        ''')
            
            # 2.  пк категории 
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS PCCategories (
                id    INTEGER PRIMARY KEY AUTOINCREMENT
                            UNIQUE
                            NOT NULL,
                title TEXT
            );
                        ''')
            
            # 3. компы
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS PC (
                id       INTEGER         PRIMARY KEY AUTOINCREMENT
                                        UNIQUE
                                        NOT NULL,
                id_model INTEGER         REFERENCES Model (id) ON DELETE SET NULL
                                                            ON UPDATE RESTRICT,
                id_cat   INTEGER         REFERENCES PCCategories (id) ON DELETE SET NULL
                                                                    ON UPDATE RESTRICT,
                tarif    INTEGER (10, 2) 
            );
                        ''')
            
            # 4. юзер категория
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS UserCat (
                id    INTEGER PRIMARY KEY AUTOINCREMENT
                            UNIQUE
                            NOT NULL,
                title TEXT
            );
                        ''')
            
            # 5. пользователь
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                id       INTEGER PRIMARY KEY AUTOINCREMENT
                                UNIQUE
                                NOT NULL,
                fullname TEXT,
                birthday TEXT,
                login    TEXT,
                password TEXT,
                cat_id   INTEGER REFERENCES UserCat (id) ON DELETE SET NULL
                                                        ON UPDATE RESTRICT
            );
                        ''')
            
            # 6. бронь
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS Tickets (
                id      INTEGER     PRIMARY KEY AUTOINCREMENT
                                    UNIQUE
                                    NOT NULL,
                date    TEXT,
                user_id INTEGER     REFERENCES Users (id),
                pc_id   INTEGER     REFERENCES PC (id),
                time    INTEGER (2) 
            );
                        ''')
            
            connect.commit()
            connect.close()
            self.add_root_admin()
        except Exception:
            with open('baseerr.txt', 'a') as file:
                file.write(f'{datetime.datetime.now()} Ошибка при подключении или создании базы \n')


    def add_root_role(self):
        try:
            connect = sqlite3.connect('InterCof.db')
            cursor = connect.cursor()
            cursor.execute('''
            INSERT INTO UserCat (title) 
            VALUES ("Администратор")
                        ''')
            
            cursor.execute('''
            INSERT INTO UserCat (title) 
            VALUES ("Клиент")
                        ''')
            
            cursor.execute('''
            INSERT INTO PCCategories (title) 
            VALUES ("Игровой")
                        ''')
            
            cursor.execute('''
            INSERT INTO Models (title) 
            VALUES ("Игровой компьютер SmartDigital "1STPLAYER", процессор Intel i7, 32GB DDR4", 56183)
                        ''')
            
            connect.commit()
            connect.close()
        except Exception:
            with open('baseerr.txt', 'a') as file:
                file.write(f'{datetime.datetime.now()} Ошибка добавления роли администратора \n')
    

    def add_root_admin(self):
        try:
            connect = sqlite3.connect('InterCof.db')
            cursor = connect.cursor()
            usr_list = cursor.execute('''
            SELECT * FROM UserCat 
            WHERE title = "Администратор"
                                    ''').fetchall()
            if len(usr_list) <= 0:               
                self.add_root_role()
                cursor.execute('''
                INSERT INTO Users (fullname, birthday, login, password, cat_id)
                VALUES ("root", "2000-12-12", "root", "admin", (SELECT id FROM UserCat WHERE title = "Администратор" LIMIT 1))    
                            ''')
            connect.commit()
            connect.close()
        except Exception:
            with open('baseerr.txt', 'a') as file:
                file.write(f'{datetime.datetime.now()} Ошибка добавления корневого администратора \n')


class MyMainLayout(MDNavigationLayout):
    pass


class UsersTable(MDGridLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            connect = sqlite3.connect('InterCof.db')
            cursor = connect.cursor()
            self.data = cursor.execute('''
            SELECT id, fullname FROM Users
                                ''').fetchall()
            self.table = MDDataTable(size_hint=(1, 1),
                                     pos_hint = {'center_x': 0.5,'y': 0.4},
                                    rows_num = 1000,
                                    column_data = [('id', 24), ('ФИО', self.width - 24)],
                                    row_data = [(e[0], e[1]) for e in self.data])
            self.add_widget(self.table)
            self.table.bind(on_row_press=self.print_usertable)
        except Exception:
            with open('baseerr.txt', 'a') as file:
                file.write(f'{datetime.datetime.now()} Ошибка отображения таблицы пользователей \n')


    def print_usertable(self, instance_table, instance_row):
        id = (instance_row.text)

        if id in '0123456789':
            connect = sqlite3.connect('InterCof.db')
            cursor = connect.cursor()
            self.data = cursor.execute('''
            SELECT * FROM Users WHERE id = ? LIMIT 1
                           ''', (id,)).fetchall()
            self.app = MDApp.get_running_app()
            self.ids = self.app.root.ids.user_screen_id.ids
            self.ids.user_id.text = str(self.data[0][0])
            self.ids.user_namefull.text = str(self.data[0][1])
            self.ids.birthday.text = str(self.data[0][2])
            self.ids.user_login.text = str(self.data[0][3])
            self.ids.user_password.text = str(self.data[0][4])
            user_categ = cursor.execute('''
            SELECT title FROM UserCat 
            WHERE id = ? LIMIT 1
                                        ''', (str(self.data[0][5]))).fetchall()
            self.ids.user_cat.text = str(user_categ[0][0])
            print(*self.data, id)

            connect.commit()
            connect.close()
        

class UsersScreenAdd(Screen):
    def add_user_to_base(self, fullname, birthday, login, password):
        try:
            connect = sqlite3.connect('InterCof.db')
            cursor = connect.cursor()

            cursor.execute('''
            INSERT INTO Users (fullname, birthday, login, password, cat_id)
            VALUES (?, ?, ?, ?, ?)
                        ''', (fullname, birthday, login, password, '2'))
            self.manager.current = 'users'

            connect.commit()
            connect.close()
        except Exception:
            with open('baseerr.txt', 'a') as file:
                file.write(f'{datetime.datetime.now()} Ошибка добавления пользователя \n')




class InterRatApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base = BaseControl()
        with open('baseerr.txt', 'a') as file:
            file.write(f'{datetime.datetime.now()} Программа запущена: \n\n')
    

    def build(self):
        self.theme_cls.primary_palette = 'Amber'
        return MyMainLayout()


    def open_drawer(self, *arg):
       self.root.ids.nav_drawer.set_state('open')


    def enter(self, login, password, label, manager):
        try:
            connect = sqlite3.connect('InterCof.db')
            cursor = connect.cursor()
            lg_list = cursor.execute('''
            SELECT login, password FROM Users
                                    ''').fetchall()
            connect.commit()
            connect.close()

            for e in lg_list:               
                if login == e[0] and password == e[1]:
                    print(lg_list)
                    manager.current = 'menu'
                    break
                else:
                    print(lg_list)
                    label.text = 'Неверный логин или пароль'
                    label.color = 'red'
        except Exception:
            with open('baseerr.txt', 'a') as file:
                file.write(f'{datetime.datetime.now()} Ошибка авторизации \n')
            
    
InterRatApp().run()
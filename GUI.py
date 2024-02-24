import flet as ft
from flet_core import page

from Backend import Backend
import asyncio


# flet run GUI.py

class UserManager(ft.UserControl):
    """Класс, отвечающий за авторизацию, регистрацию, выход из аккаунта, сброс пароля и показ welcome страницы."""

    def __init__(self, backend, step: str = 'login'):
        super(UserManager, self).__init__()
        self.backend = backend
        self.backend.load_user_data()
        self.step = step
        self.username = ft.Ref[ft.TextField]()
        self.password = ft.Ref[ft.TextField]()
        # Словарь для использования в build.
        self.variables_dict = {
            'login': {'message': 'Неверный логин или пароль!', 'hint_text': 'Пароль', 'step_name': 'Авторизация',
                      'button_name': 'Войти', 'footer': self.login_footer},
            'register': {
                'message': 'Ошибка при регистрации!', 'hint_text': 'Пароль',
                'step_name': 'Регистрация', 'button_name': 'Зарегистрироваться',
                'footer': self.register_footer},
            'welcome': {'message': 'Вы действительно хотите выйти?'},
            'password_drop': {'message': 'Пользователь с таким именем не найден!',
                              'step_name': 'Сброс пароля', 'hint_text': 'Новый пароль',
                              'button_name': 'Установить новый пароль', 'footer': self.password_drop_footer},
        }
        self.step_variables = self.variables_dict[step]
        # error_message по умолчанию, меняется на исключение, если оно возбуждается
        self._alert_dialog = self.create_error_dialog(self.step_variables['message'])

    def create_error_dialog(self, message: str):  # передается текст исключения
        """Отрисовывает всплывающее окно."""
        if self.step in ('login', 'register'):
            # actions: действия, которые предлагаются после появления всплывающего окна
            actions = [ft.ElevatedButton("Попробовать снова",
                                         on_click=self.close_dialog_window
                                         )
                       ]
        elif self.step == 'welcome':
            actions = [ft.TextButton('Да', on_click=self.handle_logout),
                       ft.TextButton('Нет', on_click=self.close_dialog_window)]
        else:
            actions = [ft.TextButton('Ок', on_click=self.handle_logout)]
        return ft.AlertDialog(
            title=ft.Text(message, text_align=ft.TextAlign.CENTER),
            actions=actions,
            actions_alignment=ft.MainAxisAlignment.CENTER,
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )

    @property
    def alert_dialog(self):
        return self._alert_dialog

    @alert_dialog.setter
    def alert_dialog(self, message):
        self._alert_dialog = self.create_error_dialog(message)

    def open_dialog_window(self, e):
        """Открывает всплывающее окно с сообщением или ошибкой."""
        e.page.dialog = self.alert_dialog
        self.alert_dialog.open = True
        e.page.update()

    def close_dialog_window(self, e):
        """Закрывает всплывающее окно с сообщением или ошибкой."""
        self.alert_dialog.open = False
        e.page.update()

    def build(self):
        """Отрисовывает окна авторизации, регистрации, сброса пароля и welcome страницы."""
        if self.step in ('login', 'register', 'password_drop'):
            return ft.Stack([
                ft.Container(
                    border_radius=11,
                    rotate=ft.Rotate(0.98 * 3.14),
                    width=400,
                    height=560,
                    bgcolor='#22ffffff'
                ),
                ft.Container(
                    ft.Container(
                        ft.Column(
                            [
                                ft.Container(
                                    ft.Image(
                                        src='logo.png',
                                        width=60,
                                    ), padding=ft.padding.only(140, 30),
                                ),
                                ft.Text('MyCalendar',
                                        width=360,
                                        size=30,
                                        weight='w900',
                                        text_align='center',
                                        ),
                                ft.Container(
                                    bgcolor=ft.colors.TRANSPARENT,
                                    padding=10,
                                    content=ft.Column([
                                        ft.Container(
                                            ft.Text(self.step_variables['step_name'], text_align=ft.alignment.center,
                                                    size=20),
                                            alignment=ft.alignment.center),
                                        ft.Container(ft.TextField(ref=self.username,
                                                                  width=280,
                                                                  height=60, hint_text='Имя пользователя',
                                                                  border='underline', color='#303030',
                                                                  prefix_icon=ft.icons.ACCOUNT_CIRCLE_OUTLINED, ),
                                                     padding=ft.padding.only(25)),
                                        ft.Container(ft.TextField(ref=self.password, password=True,
                                                                  width=280,
                                                                  height=60, hint_text=self.step_variables['hint_text'],
                                                                  border='underline',
                                                                  color='#303030',
                                                                  prefix_icon=ft.icons.LOCK, ),
                                                     padding=ft.padding.only(25, 0)),
                                        ft.Container(
                                            ft.ElevatedButton(
                                                content=ft.Text(self.step_variables['button_name'],
                                                                color="white",
                                                                weight='w500'),
                                                width=280,
                                                bgcolor='black',
                                                on_click=lambda e: self.handle_auth(e, operation=self.step)
                                            ), padding=ft.padding.only(25, 10)),
                                        self.step_variables['footer']]))

                            ]
                        )

                    ),
                    width=360,
                    height=560,
                    bgcolor='#22ffffff',
                    border_radius=11,
                )
            ])
        elif self.step == 'welcome':
            return ft.Container(
                ft.Column([ft.Container(ft.TextButton(icon=ft.icons.LOGOUT, on_click=self.open_dialog_window),
                                        alignment=ft.alignment.top_right, padding=15),
                           ft.Container(
                               content=ft.Container(
                                   ft.Text(f'Добро пожаловать в MyCalendar, {self.backend.logged_in_user}!', width=360,
                                           size=30,
                                           weight='w900',
                                           text_align='center', )
                                   , alignment=ft.alignment.center, padding=ft.padding.only(0, 250)
                               )
                           )]),
                width=580,
                height=740,
                gradient=ft.LinearGradient(['#333399', "#ff00cc"]))

    @property
    def login_footer(self):
        """Кнопки навигации внизу у страницы авторизации."""
        return ft.Column(
            [ft.Row(
                [ft.Container(ft.Text('Нет аккаунта?'), padding=ft.padding.only(35, 0)),
                 ft.Container(content=ft.TextButton("Перейти к регистрации",
                                                    on_click=lambda
                                                        e: e.page.go(
                                                        '/register')),
                              )
                 ],
                spacing=0),
                ft.Container(content=ft.TextButton('Сбросить пароль',
                                                   on_click=lambda e: e.page.go('/password_drop')),
                             padding=ft.padding.only(100, 0))], )

    @property
    def password_drop_footer(self):
        """Кнопки навигации внизу у страницы сброса пароля."""
        return ft.Column([
            ft.Container(
                ft.Text("*Используйте свое имя пользователя."),
                padding=ft.padding.only(30, 10, )), ft.Row(
                [ft.Container(ft.Text('Нет аккаунта?'), padding=ft.padding.only(35, 0)),
                 ft.Container(content=ft.TextButton("Перейти к регистрации",
                                                    on_click=lambda
                                                        e: e.page.go(
                                                        '/register')),
                              )
                 ],
                spacing=0),

            ft.TextButton(icon=ft.icons.ARROW_BACK, on_click=lambda e: e.page.go('/'))])
    @property
    def register_footer(self):
        """Кнопки навигации внизу у страницы регистрации нового пользователя."""
        return ft.Column([
            ft.Container(
                ft.Text("*Убедитесь, что пароль содержит не менее 8 символов, включая цифру и строчную букву."),
                padding=10),
            ft.TextButton(icon=ft.icons.ARROW_BACK, on_click=lambda e: e.page.go('/'))])

    def handle_auth(self, e, operation):
        """Отвечает за связь с backend и выполнение необходимых действий по авторизации, регистрации и сбросу пароля на бэке."""
        # считывание ввода пользователя
        username = self.username.current.value
        password = self.password.current.value
        try:
            if operation == 'login':
                self.backend.login(username, password)
                print("Вход в систему произведен успешно.")
                e.page.go("/home")
            elif operation == 'register':
                self.backend.validate_pass_by_regexp(password)
                self.backend.create_user(username, password)
                print("Учетная запись создана успешно.")
                self.backend.login(username, password)
                e.page.go('/home')
            elif operation == 'password_drop':
                self.backend.drop_password(username, password)
                print("Пароль успешно изменен.")
                self.backend.login(username, password)
                e.page.go('/home')

        except Exception as ex:
            self.alert_dialog = str(ex)
            self.open_dialog_window(e)
        self.backend.save_user_data()

    def handle_logout(self, e):
        """Выход из аккаунта"""
        e.page.go('/')
        self.backend.logout()

def main(page: ft.Page):
    """Создает экземпляр класса Backend, передает его в ManagerUser class"""
    backend = Backend()
    backend.load_user_data()
    login_page = UserManager(backend, step='login')
    registration_page = UserManager(backend, step='register')
    welcome_page = UserManager(backend, step='welcome')
    password_drop_page = UserManager(backend, step='password_drop')


    def create_view(view):
        """Отрисовывает начальный view для всех страниц, кроме welcome"""
        body = ft.Container(
            ft.Container(view,
                                         padding=110,
                                         width=360,
                                         height=560,
                                         ),
                            width=580,
                            height=740,
                            gradient=ft.LinearGradient(['#333399', "#ff00cc"]), padding=0
                            )
        return body

    page.title = 'CalendarApp'
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 580
    page.window_height = 740
    page.window_resizable = False

    def route_change(e):
        page.views.clear()
        page.views.append(ft.View('/', [create_view(login_page)], padding=0

                                  ))

        if page.route == '/home':
            page.views.append(
                ft.View(
                    "/home",
                    [welcome_page], padding=0
                )
            )
        elif page.route == '/register':
            page.views.append(
                ft.View(
                    "/register",
                    [create_view(registration_page)], padding=0))
        elif page.route == '/password_drop':
            page.views.append(
                ft.View(
                    "/password_drop",
                    [create_view(password_drop_page)], padding=0))
        page.update()

    #
    def view_pop(e):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

if __name__ == "__main__":
    ft.app(target=main)

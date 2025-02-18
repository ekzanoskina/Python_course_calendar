"""
Позволяет зайти по логину-паролю или создать нового пользователя (а так же выйти из аккаунта)
Позволяет выбрать календарь, узнать ближайшие события, события из промежутка времени, а также
Создать событие или удалить событие
После создания события можно добавить туда пользователей
Если нас добавили в событие или удалили мы получаем уведомление

в main можно использовать ТОЛЬКО interface
"""
import locale


locale.setlocale(locale.LC_ALL, "")

from Backend import Backend

from time import sleep


class Interface:
    """
    Класс Interface реализует пользовательский интерфейс для взаимодействия
    с системой календаря MyCalendar.
    """
    backend = None # Ссылка на экземпляр класса Backend, через который осуществляется работа с данными.
    func_request = list() # Очередь функций, которые должны быть выполнены.

    @staticmethod
    def work():
        """Запускает цикл обработки запрошенных функций."""
        Interface.func_request = [Interface.start]
        while Interface.func_request:
            Interface.func_request[0]()
            del Interface.func_request[0]

        print("Работа календаря завершена.")

    @staticmethod
    def start():
        """Инициализирует интерфейс и запрашивает загрузку данных пользователя и календаря."""
        print("Добро пожаловать в MyCalendar!")
        print('Использование календаря доступно только зарегистрированным пользователям.')
        Interface.backend = Backend()
        # Добавляем последовательность функций для выполнения.
        Interface.func_request.append(Interface.backend.load_user_data)
        Interface.func_request.append(Interface.backend.load_calendar_data)
        Interface.func_request.append(Interface.manage_user)


    @staticmethod
    def manage_user():
        """Предлагает пользователю варианты управления учетной записью: войти, создать нового пользователя или закончить работу."""
        # Запрашиваем выбор пользователя, с валидацией введенного значения.
        user_choice = Interface.backend.input_with_validation("""Что Вы бы хотели сделать?\n1: Войти в систему,\n2: Создать нового пользователя,\n3: Закончить работу.\nВведите соответствующую цифру: """, Interface.backend.validate_number_input)
        if user_choice == '1':
            Interface.func_request.append(Interface.login)
        elif user_choice == '2':
            Interface.func_request.append(Interface.create_user)
        elif user_choice == '3':
            return

    @staticmethod
    def create_user():
        """Позволяет создать нового пользователя."""
        while True:
            username = Interface.backend.input_with_validation("Введите имя пользователя: ", Interface.backend.validate_username_by_regex)

            # Проверяем, существует ли уже пользователь
            if Interface.backend.check_username_exists(username):
                print(f"Пользователь с именем {username} уже существует. Попробуйте войти или использовать другое имя.")
                continue_login = input("Хотите войти? (да/нет): ").lower()
                if continue_login == "да":
                    Interface.func_request.append(lambda: Interface.login(username))
                    break  # Выходим из цикла, если пользователь выбрал входить
                else:
                    # Возвращаемся к началу цикла, чтобы предложить ввести новое имя пользователя
                    print('Попробуйте снова.')
                    continue
            else:
                # Пользователя нет в системе, предлагаем создать новый пароль
                password = Interface.backend.input_with_validation(
                    """Придумайте пароль.Пароль должен содержать восемь и более символов,\nвключая не менее одной цифры, одной буквы в верхнем регистре и одной буквы в нижнем регистре.\n""",
                    Interface.backend.validate_pass_by_regexp)
                Interface.backend.create_user(username, password)
                print("Учетная запись создана успешно.")
                Interface.backend.save_user_data()
                Interface.func_request.append(Interface.main_menu)
                break

        # Interface.func_request.append(Interface.manage_user)

    @staticmethod
    def login(username=None):
        """Аутентификациует пользователя."""
        if not username:
            username = input('Введите имя пользователя: ')
        password = input('Введите пароль: ')
        try:
            Interface.backend.login(username, password)
            print(f'Добро пожаловать, {username}!')
            Interface.backend.save_calendar_data()
            Interface.func_request.append(Interface.show_notifications)
            Interface.func_request.append(Interface.manage_unprocessed_evens)

        except Exception as e:
            print(str(e))
            sleep(1)
            Interface.func_request.append(Interface.manage_user)

    @staticmethod
    def manage_unprocessed_evens():
        """Предлагает пользователю варианты обработки необработанных событий"""
        unprocessed_events = Interface.backend.manage_unprocessed_evens()
        if unprocessed_events:
            print(
                'У вас есть необработанные события.\nДалее по одному будут показаны события, на которые вас пригласили.')
            for event in unprocessed_events:
                print(event)
                reply = Interface.backend.input_with_validation(
                    'Введите\n1: чтобы добавить событие в свой календарь,\n2: чтобы отказаться от участия.\n3: чтобы ответить позже. ',
                    Interface.backend.validate_number_input)
                if reply == '1':
                    try:
                        Interface.backend.accept_invitation(event)
                        print('Событие успешно добавлено в Ваш календарь. Другие участники получат уведомление о том, что вы присоединитесь к собранию.')
                    except Exception as e:
                        print(str(e))
                elif reply == '2':
                    Interface.backend.decline_invitation(event)
                    print('Вы отказались от участия в событии. Об этом будет сообщено организатору.')
                elif reply == '3':
                    continue
        Interface.backend.save_calendar_data()
        Interface.func_request.append(Interface.main_menu)

    @staticmethod
    def main_menu():
        """Отображает главное меню и обрабатывает выбор пользователя"""
        menu_options = [Interface.get_today_events, Interface.get_coming_events,
                        Interface.get_events_in_range, Interface.create_event, Interface.change_event, Interface.logout]
        ans = Interface.backend.input_with_validation("""Что вы хотите сделать?
1: Посмотреть события на сегодня,
2: Посмотреть события на ближайшую неделю, 
3: Посмотреть события из промежутка времени,
4: Создать событие,
5: Изменить/покинуть/удалить событие,
6: Выйти из системы.
""", Interface.backend.validate_number_input)
        Interface.func_request.append(menu_options[int(ans) - 1])

    @staticmethod
    def get_today_events():
        """Показывает события на сегодня."""
        Interface.backend.get_today_events()
        Interface.func_request.append(Interface.main_menu)


    @staticmethod
    def create_event():
        """Метод для создания нового события в календаре пользователя."""
        title = Interface.backend.input_with_validation("Введите название события: ", Interface.backend.validate_not_empty)
        while True:
            start_time = Interface.backend.input_with_validation(
                "Введите время начала события в формате dd.mm.yyyy hh:mm: ", Interface.backend.validate_date_format)
            end_time = Interface.backend.input_with_validation(
                "Введите время окончания события в формате dd.mm.yyyy hh:mm: ", Interface.backend.validate_date_format)
            try:
                Interface.backend.compare_dates(start_time, end_time)
                break
            except Exception as e:
                print(str(e))

        recurrence = Interface.backend.input_with_validation(
            "Введите частоту повторения события (0: никогда, 1: каждый день, 2: каждую неделю, 3: каждый месяц, 4: каждый год): ",
            Interface.backend.validate_recurrence)
        description = input("Введите описание события или оставьте поле пустым: ")
        new_event = Interface.backend.create_event(title=title, start_time=start_time, end_time=end_time,
                                                   description=description, recurrence=recurrence)
        if new_event:
            print('Событие успешно создано и добавлено в Ваш календарь.')
        while True:
            user_input = Interface.backend.input_with_validation(
                "Если хотите пригласить участников на мероприятие, введите их имена пользователей через пробел, в противном случае оставьте поле пустым: ",
                Interface.backend.validate_participants)
            if user_input is None:
                break
            try:
                Interface.backend.invite_participants(new_event, user_input)
                break
            except Exception as e:
                print(str(e))
        Interface.backend.save_calendar_data()

        sleep(1)
        Interface.func_request.append(Interface.main_menu)

    @staticmethod
    def get_coming_events():
        """Метод для получения информации о предстоящих событиях. Ближайшие 7 дней."""
        try:
            Interface.backend.get_coming_events()
        except Exception as e:
            print(str(e))
        Interface.func_request.append(Interface.main_menu)

    @staticmethod
    def get_events_in_range():
        """позволяет пользователю получить список событий за определенный временной интерва"""
        while True:
            start_time = Interface.backend.input_with_validation(
                "Введите начало интервала в формате dd.mm.yyyy hh:mm: ",
                Interface.backend.validate_date_format)
            end_time = Interface.backend.input_with_validation("Введите конец интервала в формате dd.mm.yyyy hh:mm: ",
                                                               Interface.backend.validate_date_format)
            try:
                Interface.backend.compare_dates(start_time, end_time)
                break
            except Exception as e:
                print(str(e))
        events_in_range = Interface.backend.get_events_in_range(start_time, end_time)
        for event in events_in_range:
            print(event)
        Interface.func_request.append(Interface.main_menu)

    @staticmethod
    def logout():
        """Позволяет пользователю выйти из системы."""
        logout_confirmation = Interface.backend.input_with_validation('Вы действительно хотите выйти? (да/нет): ',
                                                                      Interface.backend.validate_str_input)
        if logout_confirmation == 'да':
            Interface.backend.logout()
            Interface.func_request.append(Interface.start)
        elif logout_confirmation == 'нет':
            Interface.func_request.append(Interface.main_menu)

    @staticmethod
    def change_event():
        """Метод для редактирования события."""
        all_events = Interface.backend.show_all_events()
        if all_events:
            prompt = ''
            for i, event in enumerate(all_events, 1):
                prompt += f'{i}: {event}\n'
            user_choice = Interface.backend.input_with_validation(
                f'{prompt}Введите номер события, которое хотите изменить: ', Interface.backend.validate_number_input)
            event_for_change = all_events[int(user_choice) - 1]
            user_request = Interface.backend.input_with_validation("""Выберите, что хотите сделать:
1: изменить название, 
2: изменить дату и время начала и окончания,
3: изменить частоту,
4: изменить описание, 
5: удалить участников, 
6: добавить участников, 
7: удалить событие, 
8: покинуть событие
9: вернуться в главное меню.\n""", Interface.backend.validate_number_input)
            if user_request == '1':
                print(f'Текущие название: {event_for_change.title}')
                title = input("Введите новое название события: ")
                try:
                    Interface.backend.update_event(event_for_change, title=title)
                    print('Событие успешно изменено.')
                except Exception as e:
                    print(str(e))
            elif user_request == '2':
                print(f'Текущие значения даты и времени: {event_for_change.start_time}, {event_for_change.end_time}')
                while True:
                    start_time = Interface.backend.input_with_validation(
                        "Введите новое время начала события в формате dd.mm.yyyy hh:mm: ",
                        Interface.backend.validate_date_format)
                    end_time = Interface.backend.input_with_validation(
                        "Введите новое время окончания события в формате dd.mm.yyyy hh:mm: ",
                        Interface.backend.validate_date_format)
                    try:
                        Interface.backend.compare_dates(start_time, end_time)
                        print('Событие успешно изменено.')
                        break
                    except Exception as e:
                        print(str(e))
                try:
                    Interface.backend.update_event(event_for_change, start_time=start_time, end_time=end_time)
                except Exception as e:
                    print(str(e))

            elif user_request == '3':
                recurrence = Interface.backend.input_with_validation(
                    "Введите новую частоту повторения события (0: никогда, 1: каждый день, 2: каждую неделю, 3: каждый месяц, 4: каждый год): ",
                    Interface.backend.validate_recurrence)
                try:
                    Interface.backend.update_event(event_for_change, recurrence=recurrence)
                    print('Событие успешно изменено.')
                except Exception as e:
                        print(str(e))

            elif user_request == '4':
                description = input("Введите новое описание события или оставьте поле пустым: ")
                try:
                    Interface.backend.update_event(event_for_change, description=description)
                    print('Событие успешно изменено.')
                except Exception as e:
                        print(str(e))
            elif user_request == '5':
                while True:
                    user_input = Interface.backend.input_with_validation(
                        "Чтобы удалить участников из события, введите их имена пользователей через пробел, в противном случае оставьте поле пустым: ",
                        Interface.backend.validate_participants)
                    if user_input is None:
                        break
                    try:
                        Interface.backend.remove_participants(event_for_change, user_input)
                        print(f"Пользователь(-и) удален(-ы) из события.")
                        break
                    except Exception as e:
                        print(str(e))
            elif user_request == '6':
                Interface.func_request.append(lambda: Interface.invite_participants(event_for_change))
            elif user_request == '7':
                delete_confirmation = Interface.backend.input_with_validation(
                    'Вы действительно хотите удалить событие? (да/нет): ', Interface.backend.validate_str_input)
                if delete_confirmation == 'да':
                    try:
                        Interface.backend.delete_event(event_for_change)
                        print(f"Вы успешно удалили событие '{event_for_change.title}'.")
                    except Exception as e:
                        print(str(e))
                elif delete_confirmation == 'нет':
                    Interface.func_request.append(Interface.main_menu)
            elif user_request == '8':
                delete_confirmation = Interface.backend.input_with_validation(
                    'Вы действительно хотите покинуть событие? (да/нет)\nОрганизатор не может покинуть событие! ', Interface.backend.validate_str_input)
                if delete_confirmation == 'да':
                    try:
                        Interface.backend.leave_event(event_for_change)
                        print(f"Вы успешно покинули событие '{event_for_change.title}'.")
                    except Exception as e:
                        print(str(e))
                elif delete_confirmation == 'нет':
                    Interface.func_request.append(Interface.main_menu)
        else:
            print('У вас пока нет ни одного события.')
        Interface.backend.save_calendar_data()
        Interface.func_request.append(Interface.main_menu)

    @staticmethod
    def show_notifications():
        """Показывает уведомления пользователя."""
        notifications = Interface.backend.get_unread_notifications()
        for n in notifications:
            print(n)
        Interface.backend.save_calendar_data()


Interface.work()

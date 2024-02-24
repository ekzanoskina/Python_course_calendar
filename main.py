# from Interface import Interface
import GUI
import flet as ft




def main():
    # Запускаем основной цикл работы консольного интерфейса
    # Interface.work()

    # Запускаем основной цикл работы GUI интерфейса
    ft.app(target=GUI.main)
    """
    Данные для тестирования интерфейса:
    username: valentin
    password: Valentin12345
    
    username: kate
    password: Kate12345
    """

if __name__ == "__main__":
    main()
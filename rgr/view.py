class View:
    def display_menu(self):
        print("\nМеню:")
        print("1. Вивід назв таблиць")
        print("2. Вивід імен стовпчиків таблиці")
        print("3. Перегляд даних у таблиці")
        print("4. Додавання даних в таблицю")
        print("5. Оновлення даних в таблиці")
        print("6. Видалення даних в таблиці")
        print("7. Генерування даних в таблицю")
        print("8. Вихід")
        return input("Оберіть опцію: ")

    def prompt(self, message):
        return input(message)

    def display_result(self, result):
        if not result:
            print("Немає даних для відображення.")
        else:
            for row in result:
                print(row)

    def display_message(self, message):
        print(message)

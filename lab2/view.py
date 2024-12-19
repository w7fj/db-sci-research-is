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
        return input("Оберіть опцію: ").strip()

    def display_result(self, result):
        if not result:
            print("Немає даних для відображення.")
        else:
            for row in result:
                print(row)

    def display_message(self, message):
        print(message)

    def get_table_name(self):
        return input("Введіть назву таблиці: ").strip()

    def get_insert_data(self):
        table_name = self.get_table_name()
        columns_input = input("Введіть назви стовпців через кому: ")
        values_input = input("Введіть значення через кому: ")
        columns = [col.strip() for col in columns_input.split(',')]
        values = [val.strip() for val in values_input.split(',')]
        return table_name, columns, values

    def get_update_data(self):
        table_name = self.get_table_name()
        column = input("Введіть назву стовпчика для оновлення: ").strip()
        new_value = input("Введіть нове значення: ").strip()
        row_id = input("Введіть номер рядка: ").strip()
        return table_name, column, row_id, new_value

    def get_delete_data(self):
        table_name = self.get_table_name()
        row_id = input("Введіть номер рядка для видалення: ").strip()
        return table_name, row_id

    def get_generate_data_params(self):
        table_name = self.get_table_name()
        count_input = input("Введіть кількість записів для генерації: ").strip()
        return table_name, count_input

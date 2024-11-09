from model import Model
from view import View

class Controller:
    def __init__(self):
        self.model = Model(db_name="postgres", user="postgres", password="root")
        self.view = View()

    def run(self):
        while True:
            choice = self.view.display_menu()
            if choice == '1':
                self.view_tables()
            elif choice == '2':
                self.view_columns()
            elif choice == '3':
                self.view_table_data()
            elif choice == '4':
                self.add_data()
            elif choice == '5':
                self.update_data()
            elif choice == '6':
                self.delete_data()
            elif choice == '7':
                self.generate_data()
            elif choice == '8':
                self.model.close_connection()
                self.view.display_message("Вихід з програми.")
                break
            else:
                self.view.display_message("Невірний вибір. Спробуйте ще раз.")

    def view_tables(self):
        try:
            tables = self.model.list_tables()
            self.view.display_result(tables)
        except Exception as e:
            self.view.display_message(f"Помилка при отриманні списку таблиць: {e}")

    def view_columns(self):
        table_name = self.view.prompt("Введіть назву таблиці: ")
        try:
            columns = self.model.list_columns(table_name)
            self.view.display_result(columns)
        except Exception as e:
            self.view.display_message(f"Помилка при отриманні стовпців таблиці {table_name}: {e}")

    def view_table_data(self):
        table_name = self.view.prompt("Введіть назву таблиці: ")
        try:
            data = self.model.view_table_data(table_name)
            self.view.display_result(data)
        except Exception as e:
            self.view.display_message(f"Помилка при перегляді даних таблиці {table_name}: {e}")

    def add_data(self):
        table_name = self.view.prompt("Введіть назву таблиці: ")
        columns_input = self.view.prompt("Введіть назви стовпців через кому: ")
        values_input = self.view.prompt("Введіть значення через кому: ")
        
        columns = [col.strip() for col in columns_input.split(',')]
        values = [val.strip() for val in values_input.split(',')]
        
        try:
            self.model.insert_data(table_name, columns, values)
            self.view.display_message("Дані додано успішно.")
        except Exception as e:
            self.view.display_message(f"Помилка додавання даних: {e}")

    def update_data(self):
        table_name = self.view.prompt("Введіть назву таблиці: ")
        column = self.view.prompt("Введіть назву стовпчика для оновлення: ")
        new_value = self.view.prompt("Введіть нове значення: ")
        row_id = self.view.prompt("Введіть номер рядка: ")

        try:
            self.model.update_data(table_name, column, row_id, new_value)
            self.view.display_message("Дані оновлено успішно.")
        except Exception as e:
            self.view.display_message(f"Помилка оновлення даних: {e}")

    def delete_data(self):
        table_name = self.view.prompt("Введіть назву таблиці: ")
        row_id = self.view.prompt("Введіть номер рядка для видалення: ")

        try:
            self.model.delete_data(table_name, row_id)
            self.view.display_message("Дані видалено успішно.")
        except Exception as e:
            self.view.display_message(f"Помилка видалення даних: {e}")

    def generate_data(self):
        table_name = self.view.prompt("Введіть назву таблиці для генерації даних: ")
        count_input = self.view.prompt("Введіть кількість записів для генерації: ")

        try:
            count = int(count_input)
        except ValueError:
            self.view.display_message("Неправильний формат числа. Будь ласка, введіть ціле число.")
            return

        try:
            self.model.generate_data(table_name, count)
            self.view.display_message(f"Успішно згенеровано {count} записів для таблиці {table_name}.")
        except Exception as e:
            self.view.display_message(f"Помилка генерації даних для таблиці {table_name}: {e}")

from model import Model
from view import View

class Controller:
    def __init__(self):
        self.model = Model(db_name="postgres", user="postgres", password="root")
        self.view = View()
        self.actions = {
            '1': self.view_tables,
            '2': self.view_columns,
            '3': self.view_table_data,
            '4': self.add_data,
            '5': self.update_data,
            '6': self.delete_data,
            '7': self.generate_data,
            '8': self.exit_program
        }

    def run(self):
        while True:
            choice = self.view.display_menu()
            action = self.actions.get(choice)
            if action:
                action()
            else:
                self.view.display_message("Невірний вибір. Спробуйте ще раз.")

    def view_tables(self):
        try:
            tables = self.model.list_tables()
            self.view.display_result(tables)
        except Exception as e:
            self.view.display_message(f"Помилка при отриманні списку таблиць: {e}")

    def view_columns(self):
        table_name = self.view.get_table_name()
        try:
            columns = self.model.list_columns(table_name)
            self.view.display_result(columns)
        except Exception as e:
            self.view.display_message(f"Помилка при отриманні стовпців таблиці {table_name}: {e}")

    def view_table_data(self):
        table_name = self.view.get_table_name()
        try:
            data = self.model.view_table_data(table_name)
            self.view.display_result(data)
        except Exception as e:
            self.view.display_message(f"Помилка при перегляді даних таблиці {table_name}: {e}")

    def add_data(self):
        table_name, columns, values = self.view.get_insert_data()
        try:
            self.model.insert_data(table_name, columns, values)
            self.view.display_message("Дані додано успішно.")
        except Exception as e:
            self.view.display_message(f"Помилка додавання даних: {e}")

    def update_data(self):
        table_name, column, row_id, new_value = self.view.get_update_data()
        try:
            self.model.update_data(table_name, column, row_id, new_value)
            self.view.display_message("Дані оновлено успішно.")
        except Exception as e:
            self.view.display_message(f"Помилка оновлення даних: {e}")

    def delete_data(self):
        table_name, row_id = self.view.get_delete_data()
        try:
            self.model.delete_data(table_name, row_id)
            self.view.display_message("Дані видалено успішно.")
        except Exception as e:
            self.view.display_message(f"Помилка видалення даних: {e}")

    def generate_data(self):
        table_name, count_input = self.view.get_generate_data_params()
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

    def exit_program(self):
        self.view.display_message("Вихід з програми.")
        exit(0)

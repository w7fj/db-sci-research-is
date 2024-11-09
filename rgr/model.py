import psycopg2
from psycopg2 import OperationalError, IntegrityError
import random

class Model:
    def __init__(self, db_name, user, password, host='localhost', port='5432'):
        try:
            self.connection = psycopg2.connect(
                dbname=db_name, user=user, password=password, host=host, port=port
            )
            self.cursor = self.connection.cursor()
        except OperationalError as e:
            raise OperationalError(f"Помилка підключення до бази даних: {e}")

    def list_tables(self):
        try:
            self.cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
            return self.cursor.fetchall()
        except Exception as e:
            raise Exception(f"Помилка отримання таблиць: {e}")

    def list_columns(self, table_name):
        try:
            self.cursor.execute(
                "SELECT column_name FROM information_schema.columns WHERE table_name=%s AND table_schema='public'",
                (table_name.lower(),)
            )
            return self.cursor.fetchall()
        except Exception as e:
            raise Exception(f"Помилка отримання стовпчиків: {e}")

    def view_table_data(self, table_name):
        try:
            identifier_column = f'{table_name.lower()}_id'
            self.cursor.execute(f"SELECT * FROM {table_name} ORDER BY {identifier_column}")
            return self.cursor.fetchall()
        except Exception as e:
            self.connection.rollback()
            raise Exception(f"Помилка перегляду даних таблиці: {e}")

    def insert_data(self, table_name, columns, values):
        try:
            if len(columns) != len(values):
                raise ValueError("Кількість стовпців не відповідає кількості значень.")

            for column, value in zip(columns, values):
                if column == f'{table_name.lower()}_id':
                    try:
                        value = int(value)
                    except ValueError:
                        raise ValueError(f"Значення ідентифікатора повинно бути цілим числом для стовпця {column}.")

                    self.cursor.execute(f'SELECT {column} FROM {table_name}')
                    existing_identifiers = [item for sublist in self.cursor.fetchall() for item in sublist]
                    if value in existing_identifiers:
                        raise ValueError("Ідентифікатор вже існує.")
                elif column.endswith('_id') and column != f'{table_name.lower()}_id':
                    try:
                        value = int(value)
                    except ValueError:
                        raise ValueError(f"Значення для {column} повинно бути цілим числом.")

                    referenced_table = column[:-3]
                    self.cursor.execute(f'SELECT {referenced_table}_id FROM {referenced_table}')
                    referenced_values = [item for sublist in self.cursor.fetchall() for item in sublist]
                    if value not in referenced_values:
                        raise ValueError(f"Значення зовнішнього ключа для {column} не існує.")

            columns_str = ', '.join(columns)
            placeholders = ', '.join(['%s'] * len(values))
            query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            self.cursor.execute(query, values)
            self.connection.commit()
        except IntegrityError as e:
            self.connection.rollback()
            raise ValueError(f"Помилка вставки даних (можливо, порушення обмежень цілісності): {e}")
        except Exception as e:
            self.connection.rollback()
            raise e

    def update_data(self, table_name, column, row_id, new_value):
        identifier_column = f'{table_name.lower()}_id'
        is_unique_identifier = identifier_column == column

        if is_unique_identifier:
            try:
                val_id = int(new_value)
            except ValueError:
                raise ValueError("Значення ідентифікатора повинно бути цілим числом.")

            self.cursor.execute(f'SELECT {identifier_column} FROM {table_name}')
            existing_identifiers = [item for sublist in self.cursor.fetchall() for item in sublist]
            if val_id in existing_identifiers:
                raise ValueError("Ідентифікатор вже існує.")
        elif column.endswith('_id') and column != f'{table_name.lower()}_id':
            try:
                val_id = int(new_value)
            except ValueError:
                raise ValueError(f"Значення для {column} повинно бути цілим числом.")

            referenced_table = column[:-3]
            self.cursor.execute(f'SELECT {referenced_table}_id FROM {referenced_table}')
            referenced_values = [item for sublist in self.cursor.fetchall() for item in sublist]
            if val_id not in referenced_values:
                raise ValueError(f"Значення зовнішнього ключа для {column} не існує.")

        try:
            query = f"UPDATE {table_name} SET {column} = %s WHERE {identifier_column} = %s"
            self.cursor.execute(query, (new_value, row_id))
            if self.cursor.rowcount == 0:
                raise ValueError(f"Рядок з id {row_id} не знайдено в таблиці {table_name}.")
            self.connection.commit()
        except IntegrityError as e:
            self.connection.rollback()
            raise ValueError(f"Помилка оновлення даних (можливо, порушення обмежень цілісності): {e}")
        except Exception as e:
            self.connection.rollback()
            raise e

    def delete_data(self, table_name, row_id):
        try:
            identifier_column = f'{table_name.lower()}_id'
            row_id = int(row_id)
            query = f"DELETE FROM {table_name} WHERE {identifier_column} = %s"
            self.cursor.execute(query, (row_id,))
            if self.cursor.rowcount == 0:
                raise ValueError(f"Рядок з id {row_id} не знайдено в таблиці {table_name}.")
            self.connection.commit()
        except ValueError as ve:
            self.connection.rollback()
            raise ve
        except IntegrityError as e:
            self.connection.rollback()
            raise ValueError(f"Помилка видалення даних (можливо, є залежні записи): {e}")
        except Exception as e:
            self.connection.rollback()
            raise e

    def generate_data(self, table_name, count):
        try:
            self.cursor.execute(
                """
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = %s AND table_schema = 'public'
                """,
                (table_name.lower(),)
            )
            columns_info = self.cursor.fetchall()

            if not columns_info:
                raise ValueError(f"Таблиця {table_name} не має стовпців або неправильна назва таблиці.")

            self.cursor.execute(
                """
                SELECT kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
                WHERE tc.constraint_type = 'PRIMARY KEY'
                AND tc.table_name = %s
                AND tc.table_schema = 'public'
                """,
                (table_name.lower(),)
            )
            pk_info = self.cursor.fetchone()
            if pk_info:
                id_column = pk_info[0]
            else:
                raise ValueError(f"Таблиця {table_name} не має первинного ключа.")

            for _ in range(count):
                insert_query = f'INSERT INTO {table_name} ('
                select_subquery = ""

                for column_info in columns_info:
                    column_name = column_info[0]
                    column_type = column_info[1]

                    if column_name == id_column:
                        select_subquery += f"(SELECT COALESCE(MAX({id_column}), 0) + 1 FROM {table_name}),"
                    elif column_name.endswith('_id') and column_name != id_column:
                        related_table_name = column_name[:-3]
                        select_subquery += f"(SELECT {related_table_name}_id FROM {related_table_name} ORDER BY RANDOM() LIMIT 1),"
                    elif column_type == 'integer':
                        if column_name.lower() == 'year':
                            select_subquery += '(2000 + FLOOR(RANDOM() * 100)),' 
                        else:
                            select_subquery += 'FLOOR(RANDOM() * 100 + 1),'
                    elif column_type in ['character varying', 'varchar']:
                        select_subquery += f"'Random {column_name} ' || substr(md5(random()::text), 1, 5),"
                    elif column_type == 'date':
                        if column_name == 'end_date':
                            select_subquery += "current_date + (FLOOR(RANDOM() * 365))::int,"
                        else:
                            select_subquery += "current_date - (FLOOR(RANDOM() * 365))::int,"
                    elif column_type == 'timestamp with time zone':
                        if column_name == 'end_date':
                            select_subquery += "NOW() + (FLOOR(RANDOM() * 365) || ' days')::interval,"
                        else:
                            select_subquery += "NOW() - (FLOOR(RANDOM() * 365) || ' days')::interval,"
                    else:
                        select_subquery += 'NULL,'

                    insert_query += f'{column_name},'

                insert_query = insert_query.rstrip(',') + f') VALUES ({select_subquery.rstrip(",")})'
                self.cursor.execute(insert_query)

            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise e


    def close_connection(self):
        try:
            self.cursor.close()
            self.connection.close()
        except Exception as e:
            raise Exception(f"Помилка закриття підключення: {e}")

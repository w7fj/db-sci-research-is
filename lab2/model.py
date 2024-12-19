from sqlalchemy import (create_engine, Column, Integer, String, DateTime, ForeignKey, inspect)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import IntegrityError
import psycopg2

Base = declarative_base()

class Researcher(Base):
    __tablename__ = 'researcher'
    researcher_id = Column(Integer, primary_key=True, autoincrement=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    specialization = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)

    projects = relationship('ResearchProject', secondary='researcher_project', back_populates='researchers')
    experiments = relationship('Experiment', secondary='researcher_experiment', back_populates='researchers')
    publications = relationship('Publication', secondary='researcher_publication', back_populates='researchers')


class ResearchProject(Base):
    __tablename__ = 'research_project'
    research_project_id = Column(Integer, primary_key=True, autoincrement=False)
    title = Column(String(100), nullable=False)
    description = Column(String(500), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)

    experiments = relationship('Experiment', back_populates='project')
    publications = relationship('Publication', back_populates='project')
    researchers = relationship('Researcher', secondary='researcher_project', back_populates='projects')


class Experiment(Base):
    __tablename__ = 'experiment'
    experiment_id = Column(Integer, primary_key=True, autoincrement=False)
    description = Column(String(500), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    research_project_id = Column(Integer, ForeignKey('research_project.research_project_id'), nullable=False)

    project = relationship('ResearchProject', back_populates='experiments')
    researchers = relationship('Researcher', secondary='researcher_experiment', back_populates='experiments')


class Publication(Base):
    __tablename__ = 'publication'
    publication_id = Column(Integer, primary_key=True, autoincrement=False)
    title = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    journal = Column(String(100), nullable=False)
    research_project_id = Column(Integer, ForeignKey('research_project.research_project_id'), nullable=False)

    project = relationship('ResearchProject', back_populates='publications')
    researchers = relationship('Researcher', secondary='researcher_publication', back_populates='publications')


class ResearcherProject(Base):
    __tablename__ = 'researcher_project'
    tab_id = Column(Integer, primary_key=True, autoincrement=False)
    researcher_id = Column(Integer, ForeignKey('researcher.researcher_id'), nullable=False)
    research_project_id = Column(Integer, ForeignKey('research_project.research_project_id'), nullable=False)


class ResearcherExperiment(Base):
    __tablename__ = 'researcher_experiment'
    tab_id = Column(Integer, primary_key=True, autoincrement=False)
    researcher_id = Column(Integer, ForeignKey('researcher.researcher_id'), nullable=False)
    experiment_id = Column(Integer, ForeignKey('experiment.experiment_id'), nullable=False)


class ResearcherPublication(Base):
    __tablename__ = 'researcher_publication'
    tab_id = Column(Integer, primary_key=True, autoincrement=False)
    researcher_id = Column(Integer, ForeignKey('researcher.researcher_id'), nullable=False)
    publication_id = Column(Integer, ForeignKey('publication.publication_id'), nullable=False)


class Model:
    def __init__(self, db_name, user, password, host='localhost', port='5432'):
        connection_string = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
        self.engine = create_engine(connection_string)
        self.Session = sessionmaker(bind=self.engine)
        self.inspector = inspect(self.engine)

        self.class_map = {}
        for mapper in Base.registry.mappers:
            mapped_cls = mapper.class_
            if hasattr(mapped_cls, '__tablename__'):
                self.class_map[mapped_cls.__tablename__] = mapped_cls
        
        self.connection = psycopg2.connect(
                dbname=db_name, user=user, password=password, host=host, port=port
            )
        self.cursor = self.connection.cursor()

    def list_tables(self):
        return [(table,) for table in self.inspector.get_table_names(schema='public')]

    def list_columns(self, table_name):
        columns = self.inspector.get_columns(table_name, schema='public')
        return [(col['name'],) for col in columns]

    def view_table_data(self, table_name):
        table_class = self.class_map.get(table_name.lower())
        if table_class is None:
            raise ValueError(f"Таблиця {table_name} не знайдена.")

        session = self.Session()
        try:
            data = session.query(table_class).all()
            columns = [c.name for c in table_class.__table__.columns]
            result = []
            for obj in data:
                row = tuple(getattr(obj, col) for col in columns)
                result.append(row)
            return result
        finally:
            session.close()

    def insert_data(self, table_name, columns, values):
        if len(columns) != len(values):
            raise ValueError("Кількість стовпців не відповідає кількості значень.")

        table_class = self.class_map.get(table_name.lower())
        if table_class is None:
            raise ValueError(f"Невідома таблиця {table_name}")

        data_dict = {col: val for col, val in zip(columns, values)}

        session = self.Session()
        try:
            new_obj = table_class(**data_dict)
            session.add(new_obj)
            session.commit()
        except IntegrityError as e:
            session.rollback()
            raise ValueError(f"Помилка вставки даних: {e}")
        finally:
            session.close()

    def update_data(self, table_name, column, row_id, new_value):
        table_class = self.class_map.get(table_name.lower())
        if table_class is None:
            raise ValueError(f"Невідома таблиця {table_name}")

        session = self.Session()
        try:
            obj = session.query(table_class).get(row_id)
            if not obj:
                raise ValueError(f"Рядок з id {row_id} не знайдено в таблиці {table_name}.")

            setattr(obj, column, new_value)
            session.commit()
        except IntegrityError as e:
            session.rollback()
            raise ValueError(f"Помилка оновлення даних: {e}")
        finally:
            session.close()

    def delete_data(self, table_name, row_id):
        table_class = self.class_map.get(table_name.lower())
        if table_class is None:
            raise ValueError(f"Невідома таблиця {table_name}")

        session = self.Session()
        try:
            obj = session.query(table_class).get(row_id)
            if not obj:
                raise ValueError(f"Рядок з id {row_id} не знайдено в таблиці {table_name}.")
            session.delete(obj)
            session.commit()
        except IntegrityError as e:
            session.rollback()
            raise ValueError(f"Помилка видалення даних: {e}")
        finally:
            session.close()

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

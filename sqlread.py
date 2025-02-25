import sqlite3
import os

def create_database():
    """Создает новую базу данных."""
    db_name = input("Введите имя новой базы данных (без расширения): ") + ".db"
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    print(f"База данных {db_name} успешно создана.")
    return conn, cursor, db_name

def open_database():
    """Открывает существующую базу данных."""
    current_dir = os.getcwd()
    db_files = [f for f in os.listdir(current_dir) if f.endswith('.db')]
    
    if not db_files:
        print("В текущей директории нет файлов баз данных (.db).")
        return None, None, None
    
    print("\nДоступные базы данных (.db) в текущей директории:")
    for idx, db_file in enumerate(db_files, start=1):
        print(f"{idx}. {db_file}")
    
    while True:
        choice = input("Выберите номер базы данных или введите имя файла (.db): ").strip()  # Удаляем лишние пробелы
        normalized_choice = choice.lower()  # Приводим к нижнему регистру для регистронезависимого сравнения
        
        if choice.isdigit() and 1 <= int(choice) <= len(db_files):
            db_name = db_files[int(choice) - 1]
            break
        elif any(normalized_choice == db_file.lower() for db_file in db_files):  # Проверяем наличие файла без учёта регистра
            db_name = next(db_file for db_file in db_files if db_file.lower() == normalized_choice)
            break
        else:
            print("Некорректный выбор. Пожалуйста, выберите номер из списка или введите корректное имя файла.")
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    print(f"База данных {db_name} успешно открыта.")
    return conn, cursor, db_name

def create_table(cursor):
    """Создает новую таблицу в текущей базе данных."""
    table_name = input("Введите название таблицы: ")
    fields = []
    
    while True:
        field_name = input("Введите название поля (или 'exit' для завершения): ")
        if field_name.lower() == 'exit':
            break
        
        field_type_code = input("Введите тип поля (t - TEXT, i - INTEGER, r - REAL): ").lower()
        type_mapping = {'t': 'TEXT', 'i': 'INTEGER', 'r': 'REAL'}
        field_type = type_mapping.get(field_type_code)
        
        if not field_type:
            print("Некорректный тип поля. Доступные варианты: t (TEXT), i (INTEGER), r (REAL).")
            continue
        
        fields.append(f"{field_name} {field_type}")
    
    if not fields:
        print("Необходимо определить хотя бы одно поле для создания таблицы.")
        return
    
    query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(fields)})"
    cursor.execute(query)
    print(f"Таблица {table_name} успешно создана.")
    display_table_structure(cursor, table_name)

def delete_table(cursor):
    """Удаляет таблицу из текущей базы данных."""
    list_tables(cursor)
    
    # Получаем список всех таблиц
    tables = [table[0] for table in cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
    
    if not tables:
        print("В базе данных нет таблиц для удаления.")
        return
    
    while True:
        choice = input("Введите номер или имя таблицы для удаления: ").strip()
        
        if choice.isdigit():  # Если введён номер
            index = int(choice) - 1
            if 0 <= index < len(tables):
                table_name = tables[index]
                break
            else:
                print("Некорректный номер таблицы. Пожалуйста, попробуйте снова.")
        elif choice in tables:  # Если введено имя таблицы
            table_name = choice
            break
        else:
            print("Таблица с таким именем не существует. Пожалуйста, попробуйте снова.")
    
    confirm = input(f"Вы уверены, что хотите удалить таблицу '{table_name}'? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Операция удаления отменена.")
        return
    
    try:
        cursor.execute(f"DROP TABLE {table_name};")
        print(f"Таблица {table_name} успешно удалена.")
    except sqlite3.OperationalError as e:
        print(f"Ошибка при удалении таблицы: {e}")

def display_table_structure(cursor, table_name):
    """Отображает структуру указанной таблицы."""
    try:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        if columns:
            print(f"\nСтруктура таблицы {table_name}:")
            print(f"{'ID':<5} {'Имя':<15} {'Тип':<10} {'NULL':<5} {'PK':<5}")
            for column in columns:
                cid, name, type_, notnull, dflt_value, pk = column
                print(f"{cid:<5} {name:<15} {type_:<10} {notnull:<5} {pk:<5}")
        else:
            print(f"Таблица {table_name} пуста или не существует.")
    except sqlite3.OperationalError:
        print(f"Ошибка: Таблица {table_name} не существует.")

def list_tables(cursor):
    """Выводит список всех таблиц в текущей базе данных."""
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        if tables:
            print("\nСписок существующих таблиц:")
            for idx, table in enumerate(tables, start=1):
                print(f"{idx}. {table[0]}")
        else:
            print("В базе данных нет таблиц.")
    except sqlite3.OperationalError as e:
        print(f"Ошибка при получении списка таблиц: {e}")

def view_table_structure(cursor):
    """Позволяет пользователю выбрать таблицу и показать её структуру."""
    list_tables(cursor)
    
    # Получаем список всех таблиц
    tables = [table[0] for table in cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
    
    if not tables:
        print("Нет таблиц для просмотра.")
        return
    
    while True:
        choice = input("Введите номер или имя таблицы для просмотра структуры: ").strip()
        
        if choice.isdigit():  # Если введён номер
            index = int(choice) - 1
            if 0 <= index < len(tables):
                table_name = tables[index]
                break
            else:
                print("Некорректный номер таблицы. Пожалуйста, попробуйте снова.")
        elif choice in tables:  # Если введено имя таблицы
            table_name = choice
            break
        else:
            print("Таблица с таким именем не существует. Пожалуйста, попробуйте снова.")
    
    display_table_structure(cursor, table_name)

def save_table_as(cursor):
    """Сохраняет таблицу как новую с другим именем."""
    list_tables(cursor)
    
    # Получаем список всех таблиц
    tables = [table[0] for table in cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
    
    if not tables:
        print("В базе данных нет таблиц для сохранения.")
        return
    
    while True:
        choice = input("Введите номер или имя таблицы для сохранения: ").strip()
        
        if choice.isdigit():  # Если введён номер
            index = int(choice) - 1
            if 0 <= index < len(tables):
                original_table_name = tables[index]
                break
            else:
                print("Некорректный номер таблицы. Пожалуйста, попробуйте снова.")
        elif choice in tables:  # Если введено имя таблицы
            original_table_name = choice
            break
        else:
            print("Таблица с таким именем не существует. Пожалуйста, попробуйте снова.")
    
    new_table_name = input("Введите новое имя для таблицы: ").strip()
    if not new_table_name:
        print("Имя новой таблицы не может быть пустым.")
        return
    
    if new_table_name in tables:
        overwrite = input(f"Таблица с именем '{new_table_name}' уже существует. Хотите перезаписать её? (yes/no): ").strip().lower()
        if overwrite != 'yes':
            print("Операция сохранения отменена.")
            return
    
    try:
        # Создаем новую таблицу с данными из старой
        cursor.execute(f"CREATE TABLE {new_table_name} AS SELECT * FROM {original_table_name};")
        print(f"Таблица '{original_table_name}' успешно сохранена как '{new_table_name}'.")
    except sqlite3.OperationalError as e:
        print(f"Ошибка при сохранении таблицы: {e}")

def save_database_as(conn):
    """Сохраняет текущую базу данных под новым именем."""
    new_db_name = input("Введите новое имя для базы данных (без расширения): ").strip()
    if not new_db_name:
        print("Имя новой базы данных не может быть пустым.")
        return
    
    new_db_name += ".db"  # Добавляем расширение .db
    if os.path.exists(new_db_name):
        overwrite = input(f"База данных '{new_db_name}' уже существует. Хотите перезаписать её? (yes/no): ").strip().lower()
        if overwrite != 'yes':
            print("Операция сохранения отменена.")
            return
    
    try:
        # Создаем новое соединение для целевой базы данных
        new_conn = sqlite3.connect(new_db_name)
        # Создаем резервную копию текущей базы данных
        conn.backup(new_conn)
        print(f"База данных успешно сохранена как '{new_db_name}'.")
        new_conn.close()
    except sqlite3.Error as e:
        print(f"Ошибка при сохранении базы данных: {e}")

def insert_data(cursor):
    """Добавляет новую запись в таблицу."""
    list_tables(cursor)
    
    # Получаем список всех таблиц
    tables = [table[0] for table in cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
    
    if not tables:
        print("В базе данных нет таблиц для добавления данных.")
        return
    
    while True:
        choice = input("Введите номер или имя таблицы для добавления данных: ").strip()
        
        if choice.isdigit():  # Если введён номер
            index = int(choice) - 1
            if 0 <= index < len(tables):
                table_name = tables[index]
                break
            else:
                print("Некорректный номер таблицы. Пожалуйста, попробуйте снова.")
        elif choice in tables:  # Если введено имя таблицы
            table_name = choice
            break
        else:
            print("Таблица с таким именем не существует. Пожалуйста, попробуйте снова.")
    
    try:
        # Получаем информацию о столбцах таблицы
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        if not columns:
            print(f"Таблица {table_name} пуста или не имеет столбцов.")
            return
        
        print(f"\nСтруктура таблицы {table_name}:")
        for column in columns:
            cid, name, type_, notnull, dflt_value, pk = column
            print(f"{name} ({type_})")
        
        # Собираем значения для новых данных
        values = []
        for column in columns:
            column_name = column[1]
            value = input(f"Введите значение для поля '{column_name}': ").strip()
            values.append(value)
        
        # Создаем запрос для вставки данных
        placeholders = ", ".join(["?" for _ in columns])
        columns_names = ", ".join([col[1] for col in columns])
        query = f"INSERT INTO {table_name} ({columns_names}) VALUES ({placeholders})"
        cursor.execute(query, values)
        print(f"Запись успешно добавлена в таблицу {table_name}.")
    
    except sqlite3.Error as e:
        print(f"Ошибка при добавлении данных: {e}")

def edit_data(cursor):
    """Редактирует существующую запись в таблице по номеру строки."""
    list_tables(cursor)
    
    # Получаем список всех таблиц
    tables = [table[0] for table in cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
    
    if not tables:
        print("В базе данных нет таблиц для редактирования данных.")
        return
    
    while True:
        choice = input("Введите номер или имя таблицы для редактирования данных: ").strip()
        
        if choice.isdigit():  # Если введён номер
            index = int(choice) - 1
            if 0 <= index < len(tables):
                table_name = tables[index]
                break
            else:
                print("Некорректный номер таблицы. Пожалуйста, попробуйте снова.")
        elif choice in tables:  # Если введено имя таблицы
            table_name = choice
            break
        else:
            print("Таблица с таким именем не существует. Пожалуйста, попробуйте снова.")
    
    try:
        # Выводим все записи из таблицы
        cursor.execute(f"SELECT rowid, * FROM {table_name}")
        rows = cursor.fetchall()
        if not rows:
            print(f"Таблица {table_name} пуста.")
            return
        
        print(f"\nСодержимое таблицы {table_name}:")
        for idx, row in enumerate(rows, start=1):
            print(f"{idx}. {row}")
        
        # Выбор строки для редактирования
        row_choice = input("Введите номер строки для редактирования: ").strip()
        if not row_choice.isdigit() or not (1 <= int(row_choice) <= len(rows)):
            print("Некорректный номер строки.")
            return
        
        row_id = rows[int(row_choice) - 1][0]  # Получаем rowid выбранной строки
        
        # Получаем информацию о столбцах таблицы
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        # Редактируем каждое поле
        updates = []
        for column in columns:
            column_name = column[1]
            current_value = rows[int(row_choice) - 1][columns.index(column) + 1]
            new_value = input(f"Текущее значение '{column_name}': {current_value}. Введите новое значение (Enter для пропуска): ").strip()
            if new_value:
                updates.append((column_name, new_value))
        
        # Обновляем данные в таблице
        if updates:
            set_clause = ", ".join([f"{col} = ?" for col, _ in updates])
            values = [value for _, value in updates]
            values.append(row_id)
            query = f"UPDATE {table_name} SET {set_clause} WHERE rowid = ?"
            cursor.execute(query, values)
            print(f"Запись с rowid={row_id} успешно обновлена.")
        else:
            print("Нет изменений для сохранения.")
    
    except sqlite3.Error as e:
        print(f"Ошибка при редактировании данных: {e}")

def view_table_contents(cursor):
    """Просматривает содержимое таблицы."""
    list_tables(cursor)
    
    # Получаем список всех таблиц
    tables = [table[0] for table in cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
    
    if not tables:
        print("В базе данных нет таблиц для просмотра содержимого.")
        return
    
    while True:
        choice = input("Введите номер или имя таблицы для просмотра содержимого: ").strip()
        
        if choice.isdigit():  # Если введён номер
            index = int(choice) - 1
            if 0 <= index < len(tables):
                table_name = tables[index]
                break
            else:
                print("Некорректный номер таблицы. Пожалуйста, попробуйте снова.")
        elif choice in tables:  # Если введено имя таблицы
            table_name = choice
            break
        else:
            print("Таблица с таким именем не существует. Пожалуйста, попробуйте снова.")
    
    try:
        # Выводим содержимое таблицы
        cursor.execute(f"SELECT rowid, * FROM {table_name}")
        rows = cursor.fetchall()
        
        if not rows:
            print(f"Таблица {table_name} пуста.")
            return
        
        # Получаем информацию о столбцах таблицы
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        column_names = ["rowid"] + [col[1] for col in columns]
        
        # Выводим заголовки столбцов
        print(f"\nСодержимое таблицы {table_name}:")
        print(" | ".join(column_names))
        
        # Выводим данные
        for row in rows:
            print(" | ".join(map(str, row)))
    
    except sqlite3.Error as e:
        print(f"Ошибка при просмотре содержимого таблицы: {e}")

def close_database(conn):
    """Закрывает текущую базу данных."""
    if conn:
        conn.commit()
        conn.close()
        print("База данных закрыта.")
    else:
        print("Нет открытой базы данных для закрытия.")

def main_menu():
    while True:
        print("\nОсновное меню:")
        print("1. Создать новую базу данных")
        print("2. Открыть существующую базу данных")
        print("3. Выход из программы")
        
        choice = input("Введите номер действия: ").strip()
        
        if choice == '1':
            conn, cursor, db_name = create_database()
            break
        elif choice == '2':
            conn, cursor, db_name = open_database()
            if conn is None:
                continue
            break
        elif choice == '3':
            print("Завершение работы программы...")
            return None, None, None
        else:
            print("Некорректный выбор. Пожалуйста, выберите 1, 2 или 3.")
    
    return conn, cursor, db_name

def database_menu(conn, cursor, db_name):
    while True:
        print(f"\nМеню работы с базой данных '{db_name}':")
        print("1. Создать новую таблицу")
        print("2. Удалить таблицу")
        print("3. Сохранить таблицу как...")
        print("4. Сохранить базу данных как...")
        print("5. Просмотреть список существующих таблиц")
        print("6. Просмотреть структуру таблицы")
        print("7. Просмотреть содержимое таблицы")  # Новый пункт
        print("8. Добавить данные в таблицу")
        print("9. Редактировать данные в таблице")
        print("0. Закрыть базу данных")
        
        action = input("Введите номер действия: ").strip()
        
        if action == '1':
            create_table(cursor)
        elif action == '2':
            delete_table(cursor)
        elif action == '3':
            save_table_as(cursor)
        elif action == '4':
            save_database_as(conn)
        elif action == '5':
            list_tables(cursor)
        elif action == '6':
            view_table_structure(cursor)
        elif action == '7':
            view_table_contents(cursor)  # Вызов новой функции
        elif action == '8':
            insert_data(cursor)
        elif action == '9':
            edit_data(cursor)
        elif action == '0':
            close_database(conn)
            return  # Возвращаемся к основному меню
        else:
            print("Некорректный выбор. Пожалуйста, выберите 1-0.")
def main():
    print("Добро пожаловать в программу управления базами данных SQLite!")
    
    while True:
        conn, cursor, db_name = main_menu()
        if conn is None:  # Если выбран выход из программы
            break
        
        database_menu(conn, cursor, db_name)  # Переходим к меню работы с базой данных
    
    print("Программа завершена. До свидания!")

if __name__ == "__main__":
    main()

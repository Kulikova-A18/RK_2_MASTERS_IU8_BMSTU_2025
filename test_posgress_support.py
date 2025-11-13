#!/usr/bin/env python3
"""
Скрипт для вывода всей информации из базы данных support_system.
"""

import psycopg2
import pandas as pd

# --- Настройки подключения ---
# ЗАМЕНИТЕ 'your_postgres_password' НА РЕАЛЬНЫЙ ПАРОЛЬ ПОЛЬЗОВАТЕЛЯ postgres
DB_PASSWORD = 'new_secure_password' 
DB_NAME = 'support_system'
DB_USER = 'postgres'
DB_HOST = 'localhost'
DB_PORT = '5432'

def connect_to_db():
    """Устанавливает соединение с базой данных."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        print("✅ Успешное подключение к базе данных.")
        return conn
    except psycopg2.Error as e:
        print(f"❌ Ошибка подключения к базе данных: {e}")
        return None

def get_all_tables(conn):
    """Получает список всех таблиц в базе данных."""
    cur = conn.cursor()
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    tables = [row[0] for row in cur.fetchall()]
    cur.close()
    return tables

def print_table_data(conn, table_name):
    """Выводит все данные из указанной таблицы."""
    print(f"\n--- Данные из таблицы: {table_name} ---")
    try:
        # Используем pandas.read_sql_query для удобного вывода
        query = f"SELECT * FROM {table_name};"
        df = pd.read_sql_query(query, conn)
        if df.empty:
            print("Таблица пуста.")
        else:
            print(df.to_string(index=False)) # Вывод без индекса pandas
    except Exception as e:
        print(f"❌ Ошибка при чтении данных из таблицы {table_name}: {e}")

def main():
    """Основная функция."""
    print("🚀 Запуск скрипта вывода данных из базы support_system...")
    
    # Подключаемся к базе данных
    conn = connect_to_db()
    if not conn:
        return # Выходим, если не удалось подключиться

    try:
        # Получаем список таблиц
        tables = get_all_tables(conn)
        if not tables:
            print("❌ В базе данных не найдено таблиц в схеме 'public'.")
            return

        print(f"📋 Найдены таблицы: {', '.join(tables)}")
        print("-" * 50)

        # Выводим данные из каждой таблицы
        for table in tables:
            print_table_data(conn, table)
            print("-" * 50) # Разделитель между таблицами

    except Exception as e:
        print(f"❌ Произошла ошибка в основной части скрипта: {e}")

    finally:
        # Закрываем соединение
        if conn:
            conn.close()
            print("\n🔌 Соединение с базой данных закрыто.")

if __name__ == "__main__":
    main()
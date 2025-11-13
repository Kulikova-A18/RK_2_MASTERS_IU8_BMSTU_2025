#!/usr/bin/env python3
"""
Программа для составления статистики по отделам из базы данных поддержки
"""

import psycopg2
from psycopg2 import sql
import pandas as pd
from datetime import datetime, timedelta
import sys


class DepartmentStatistics:
    def __init__(self, dbname="support_system", user="postgres", password="", host="localhost", port="5432"):
        self.connection_params = {
            'dbname': dbname,
            'user': user,
            'password': password,
            'host': host,
            'port': port
        }
        self.conn = None

    def connect(self):
        """Установка соединения с базой данных"""
        try:
            self.conn = psycopg2.connect(**self.connection_params)
            print("✅ Успешное подключение к базе данных")
            return True
        except Exception as e:
            print(f"❌ Ошибка подключения к базе данных: {e}")
            return False

    def disconnect(self):
        """Закрытие соединения с базой данных"""
        if self.conn:
            self.conn.close()
            print("🔌 Соединение с базой данных закрыто")

    def get_departments_list(self):
        """Получение списка всех отделов"""
        try:
            query = "SELECT DISTINCT department FROM Staff ORDER BY department;"
            df = pd.read_sql_query(query, self.conn)
            return df['department'].tolist()
        except Exception as e:
            print(f"❌ Ошибка при получении списка отделов: {e}")
            return []

    def get_general_statistics(self):
        """Общая статистика по базе данных"""
        try:
            query = """
            SELECT 
                (SELECT COUNT(*) FROM Users) as total_users,
                (SELECT COUNT(*) FROM Staff) as total_staff,
                (SELECT COUNT(*) FROM Tickets) as total_tickets,
                (SELECT COUNT(*) FROM TicketComments) as total_comments,
                (SELECT COUNT(*) FROM TicketLogs) as total_logs;
            """
            df = pd.read_sql_query(query, self.conn)
            return df.iloc[0].to_dict()
        except Exception as e:
            print(f"❌ Ошибка при получении общей статистики: {e}")
            return {}

    def get_department_statistics(self, department):
        """Статистика по конкретному отделу"""
        try:
            query = """
            SELECT 
                -- Основная информация об отделе
                d.department,
                COUNT(DISTINCT s.staff_id) as staff_count,
                COUNT(DISTINCT CASE WHEN s.is_active THEN s.staff_id END) as active_staff_count,

                -- Статистика по тикетам
                COUNT(DISTINCT t.ticket_id) as total_tickets,
                COUNT(DISTINCT CASE WHEN t.closed_at IS NOT NULL THEN t.ticket_id END) as closed_tickets,
                COUNT(DISTINCT CASE WHEN t.closed_at IS NULL THEN t.ticket_id END) as open_tickets,

                -- Распределение по статусам
                COUNT(DISTINCT CASE WHEN ts.status_name = 'Новый' THEN t.ticket_id END) as new_tickets,
                COUNT(DISTINCT CASE WHEN ts.status_name = 'В работе' THEN t.ticket_id END) as in_progress_tickets,
                COUNT(DISTINCT CASE WHEN ts.status_name = 'Ожидает ответа пользователя' THEN t.ticket_id END) as waiting_tickets,
                COUNT(DISTINCT CASE WHEN ts.status_name = 'Решено' THEN t.ticket_id END) as resolved_tickets,
                COUNT(DISTINCT CASE WHEN ts.status_name = 'Закрыт' THEN t.ticket_id END) as closed_status_tickets,

                -- Статистика по времени
                AVG(EXTRACT(EPOCH FROM (t.closed_at - t.created_at))/3600) as avg_resolution_hours,
                COUNT(DISTINCT tc.comment_id) as total_comments,
                COUNT(DISTINCT tl.log_id) as total_logs

            FROM Staff s
            LEFT JOIN Tickets t ON s.staff_id = t.assigned_staff_id
            LEFT JOIN TicketStatuses ts ON t.status_id = ts.status_id
            LEFT JOIN TicketComments tc ON t.ticket_id = tc.ticket_id
            LEFT JOIN TicketLogs tl ON t.ticket_id = tl.ticket_id
            WHERE s.department = %s
            GROUP BY d.department;
            """

            # Создаем псевдо-столбец для группировки
            query = query.replace("d.department", f"'{department}' as department")

            df = pd.read_sql_query(query, self.conn, params=(department,))
            if not df.empty:
                return df.iloc[0].to_dict()
            else:
                return self.get_empty_department_stats(department)

        except Exception as e:
            print(f"❌ Ошибка при получении статистики для отдела {department}: {e}")
            return self.get_empty_department_stats(department)

    def get_empty_department_stats(self, department):
        """Возвращает пустую статистику для отдела без данных"""
        return {
            'department': department,
            'staff_count': 0,
            'active_staff_count': 0,
            'total_tickets': 0,
            'closed_tickets': 0,
            'open_tickets': 0,
            'new_tickets': 0,
            'in_progress_tickets': 0,
            'waiting_tickets': 0,
            'resolved_tickets': 0,
            'closed_status_tickets': 0,
            'avg_resolution_hours': 0,
            'total_comments': 0,
            'total_logs': 0
        }

    def get_staff_performance(self, department):
        """Статистика производительности сотрудников отдела"""
        try:
            query = """
            SELECT 
                s.staff_id,
                s.full_name,
                s.position,
                s.is_active,
                COUNT(DISTINCT t.ticket_id) as assigned_tickets,
                COUNT(DISTINCT CASE WHEN t.closed_at IS NOT NULL THEN t.ticket_id END) as closed_tickets,
                COUNT(DISTINCT CASE WHEN t.closed_at IS NULL THEN t.ticket_id END) as open_tickets,
                AVG(EXTRACT(EPOCH FROM (t.closed_at - t.created_at))/3600) as avg_resolution_hours,
                COUNT(DISTINCT tc.comment_id) as comments_written
            FROM Staff s
            LEFT JOIN Tickets t ON s.staff_id = t.assigned_staff_id
            LEFT JOIN TicketComments tc ON s.staff_id = tc.author_id AND tc.author_type = 'staff'
            WHERE s.department = %s
            GROUP BY s.staff_id, s.full_name, s.position, s.is_active
            ORDER BY assigned_tickets DESC;
            """

            df = pd.read_sql_query(query, self.conn, params=(department,))
            return df
        except Exception as e:
            print(f"❌ Ошибка при получении статистики сотрудников для отдела {department}: {e}")
            return pd.DataFrame()

    def get_ticket_categories_stats(self, department):
        """Статистика по категориям проблем для отдела"""
        try:
            query = """
            SELECT 
                pc.category_name,
                COUNT(DISTINCT t.ticket_id) as ticket_count,
                COUNT(DISTINCT CASE WHEN t.closed_at IS NOT NULL THEN t.ticket_id END) as closed_count,
                AVG(EXTRACT(EPOCH FROM (t.closed_at - t.created_at))/3600) as avg_resolution_hours
            FROM Staff s
            JOIN Tickets t ON s.staff_id = t.assigned_staff_id
            JOIN ProblemCategories pc ON t.category_id = pc.category_id
            WHERE s.department = %s
            GROUP BY pc.category_name
            ORDER BY ticket_count DESC;
            """

            df = pd.read_sql_query(query, self.conn, params=(department,))
            return df
        except Exception as e:
            print(f"❌ Ошибка при получении статистики категорий для отдела {department}: {e}")
            return pd.DataFrame()

    def get_monthly_statistics(self, department):
        """Ежемесячная статистика для отдела"""
        try:
            query = """
            SELECT 
                DATE_TRUNC('month', t.created_at) as month,
                COUNT(DISTINCT t.ticket_id) as tickets_created,
                COUNT(DISTINCT CASE WHEN t.closed_at IS NOT NULL THEN t.ticket_id END) as tickets_closed,
                AVG(EXTRACT(EPOCH FROM (t.closed_at - t.created_at))/3600) as avg_resolution_hours
            FROM Staff s
            JOIN Tickets t ON s.staff_id = t.assigned_staff_id
            WHERE s.department = %s
            GROUP BY DATE_TRUNC('month', t.created_at)
            ORDER BY month DESC
            LIMIT 12;
            """

            df = pd.read_sql_query(query, self.conn, params=(department,))
            return df
        except Exception as e:
            print(f"❌ Ошибка при получении месячной статистики для отдела {department}: {e}")
            return pd.DataFrame()

    def print_department_report(self, department_stats, staff_stats, category_stats, monthly_stats):
        """Печать отчета по отделу"""
        stats = department_stats

        print(f"\n{'=' * 80}")
        print(f"📊 ОТЧЕТ ПО ОТДЕЛУ: {stats['department']}")
        print(f"{'=' * 80}")

        # Основная статистика
        print(f"\n👥 СОТРУДНИКИ:")
        print(f"   • Всего сотрудников: {stats['staff_count']}")
        print(f"   • Активных сотрудников: {stats['active_staff_count']}")

        # Статистика тикетов
        print(f"\n🎫 ТИКЕТЫ:")
        print(f"   • Всего тикетов: {stats['total_tickets']}")
        print(f"   • Закрыто тикетов: {stats['closed_tickets']}")
        print(f"   • Открыто тикетов: {stats['open_tickets']}")

        if stats['total_tickets'] > 0:
            completion_rate = (stats['closed_tickets'] / stats['total_tickets']) * 100
            print(f"   • Процент завершения: {completion_rate:.1f}%")

        # Статусы тикетов
        print(f"\n📋 РАСПРЕДЕЛЕНИЕ ПО СТАТУСАМ:")
        print(f"   • Новые: {stats['new_tickets']}")
        print(f"   • В работе: {stats['in_progress_tickets']}")
        print(f"   • Ожидают ответа: {stats['waiting_tickets']}")
        print(f"   • Решены: {stats['resolved_tickets']}")
        print(f"   • Закрыты: {stats['closed_status_tickets']}")

        # Время решения
        if stats['avg_resolution_hours'] and stats['avg_resolution_hours'] > 0:
            print(f"\n⏱️  СРЕДНЕЕ ВРЕМЯ РЕШЕНИЯ: {stats['avg_resolution_hours']:.1f} часов")

        # Активность
        print(f"\n💬 АКТИВНОСТЬ:")
        print(f"   • Комментариев: {stats['total_comments']}")
        print(f"   • Логов действий: {stats['total_logs']}")

        # Статистика сотрудников
        if not staff_stats.empty:
            print(f"\n👤 ПРОИЗВОДИТЕЛЬНОСТЬ СОТРУДНИКОВ:")
            for _, staff in staff_stats.head(5).iterrows():
                status = "✅ Активен" if staff['is_active'] else "❌ Неактивен"
                print(f"   • {staff['full_name']} ({staff['position']}) - {status}")
                print(f"     Тикетов: {staff['assigned_tickets']} (закрыто: {staff['closed_tickets']})")
                if staff['avg_resolution_hours'] and staff['avg_resolution_hours'] > 0:
                    print(f"     Среднее время: {staff['avg_resolution_hours']:.1f}ч")

        # Категории проблем
        if not category_stats.empty:
            print(f"\n🔧 КАТЕГОРИИ ПРОБЛЕМ:")
            for _, category in category_stats.head(5).iterrows():
                print(f"   • {category['category_name']}: {category['ticket_count']} тикетов")

        # Месячная статистика
        if not monthly_stats.empty:
            print(f"\n📈 СТАТИСТИКА ПО МЕСЯЦАМ (последние 12 месяцев):")
            for _, month in monthly_stats.head(6).iterrows():
                month_str = month['month'].strftime('%Y-%m')
                print(f"   • {month_str}: создано {month['tickets_created']}, закрыто {month['tickets_closed']}")

    def generate_all_reports(self):
        """Генерация отчетов по всем отделам"""
        if not self.connect():
            return

        try:
            # Общая статистика
            general_stats = self.get_general_statistics()
            print("📈 ОБЩАЯ СТАТИСТИКА СИСТЕМЫ:")
            print(f"   • Пользователей: {general_stats.get('total_users', 0)}")
            print(f"   • Сотрудников: {general_stats.get('total_staff', 0)}")
            print(f"   • Тикетов: {general_stats.get('total_tickets', 0)}")
            print(f"   • Комментариев: {general_stats.get('total_comments', 0)}")
            print(f"   • Логов действий: {general_stats.get('total_logs', 0)}")

            # Получаем список отделов
            departments = self.get_departments_list()
            print(f"\n🏢 НАЙДЕНО ОТДЕЛОВ: {len(departments)}")

            if not departments:
                print("❌ Отделы не найдены в базе данных")
                return

            # Генерируем отчеты для каждого отдела
            for department in departments:
                print(f"\n{'─' * 50}")
                print(f"📋 ОБРАБОТКА ОТДЕЛА: {department}")
                print(f"{'─' * 50}")

                # Получаем все виды статистики для отдела
                dept_stats = self.get_department_statistics(department)
                staff_stats = self.get_staff_performance(department)
                category_stats = self.get_ticket_categories_stats(department)
                monthly_stats = self.get_monthly_statistics(department)

                # Печатаем отчет
                self.print_department_report(dept_stats, staff_stats, category_stats, monthly_stats)

        except Exception as e:
            print(f"❌ Ошибка при генерации отчетов: {e}")
        finally:
            self.disconnect()

    def save_reports_to_excel(self, filename="department_statistics.xlsx"):
        """Сохранение отчетов в Excel файл"""
        if not self.connect():
            return

        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                departments = self.get_departments_list()

                # Сводный отчет по всем отделам
                all_departments_data = []
                for department in departments:
                    stats = self.get_department_statistics(department)
                    all_departments_data.append(stats)

                if all_departments_data:
                    summary_df = pd.DataFrame(all_departments_data)
                    summary_df.to_excel(writer, sheet_name='Сводка по отделам', index=False)

                # Детальные отчеты по каждому отделу
                for department in departments:
                    # Статистика сотрудников
                    staff_stats = self.get_staff_performance(department)
                    if not staff_stats.empty:
                        staff_stats.to_excel(writer, sheet_name=f'{department[:25]}_сотрудники', index=False)

                    # Статистика категорий
                    category_stats = self.get_ticket_categories_stats(department)
                    if not category_stats.empty:
                        category_stats.to_excel(writer, sheet_name=f'{department[:25]}_категории', index=False)

                    # Месячная статистика
                    monthly_stats = self.get_monthly_statistics(department)
                    if not monthly_stats.empty:
                        monthly_stats.to_excel(writer, sheet_name=f'{department[:25]}_месяцы', index=False)

                print(f"✅ Отчеты сохранены в файл: {filename}")

        except Exception as e:
            print(f"❌ Ошибка при сохранении в Excel: {e}")
        finally:
            self.disconnect()


def main():
    """Основная функция программы"""
    print("🚀 ПРОГРАММА СТАТИСТИКИ ПО ОТДЕЛАМ")
    print("=" * 50)

    # Параметры подключения к БД
    db_params = {
        'dbname': 'support_system',
        'user': 'postgres',
        'password': 'password',  # Замените на ваш пароль
        'host': 'localhost',
        'port': '5432'
    }

    # Создаем экземпляр класса статистики
    stats = DepartmentStatistics(**db_params)

    while True:
        print("\n📊 МЕНЮ СТАТИСТИКИ:")
        print("1. Показать отчеты по всем отделам")
        print("2. Сохранить отчеты в Excel")
        print("3. Выход")

        choice = input("\nВыберите действие (1-3): ").strip()

        if choice == '1':
            print("\n📋 ГЕНЕРАЦИЯ ОТЧЕТОВ...")
            stats.generate_all_reports()

        elif choice == '2':
            filename = input("Введите имя файла для сохранения (по умолчанию: department_statistics.xlsx): ").strip()
            if not filename:
                filename = "department_statistics.xlsx"
            stats.save_reports_to_excel(filename)

        elif choice == '3':
            print("👋 Выход из программы")
            break

        else:
            print("❌ Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    # Если переданы аргументы командной строки
    if len(sys.argv) > 1:
        db_params = {
            'dbname': sys.argv[1] if len(sys.argv) > 1 else 'support_system',
            'user': sys.argv[2] if len(sys.argv) > 2 else 'postgres',
            'password': sys.argv[3] if len(sys.argv) > 3 else 'password',
            'host': sys.argv[4] if len(sys.argv) > 4 else 'localhost',
            'port': sys.argv[5] if len(sys.argv) > 5 else '5432'
        }

        stats = DepartmentStatistics(**db_params)
        stats.generate_all_reports()

        if '--excel' in sys.argv:
            stats.save_reports_to_excel()
    else:
        main()
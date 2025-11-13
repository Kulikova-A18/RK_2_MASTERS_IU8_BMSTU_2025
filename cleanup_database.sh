#!/bin/bash

# Скрипт для полной очистки всех данных из базы данных поддержки
# usage: ./cleanup_database.sh [database_name]

set -e

# Параметры
DB_NAME=${1:-"support_system"}
HOST=${2:-"localhost"}
PORT=${3:-"5432"}

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функции для вывода
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка подключения к PostgreSQL
check_connection() {
    log_info "Проверка подключения к PostgreSQL..."
    if sudo -u postgres psql -c "SELECT 1;" &> /dev/null; then
        log_info "Подключение успешно установлено"
    else
        log_error "Не удалось подключиться к PostgreSQL"
        exit 1
    fi
}

# Проверка существования базы данных
check_database_exists() {
    log_info "Проверка существования базы данных '$DB_NAME'..."
    if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
        log_info "База данных '$DB_NAME' найдена"
        return 0
    else
        log_error "База данных '$DB_NAME' не существует"
        exit 1
    fi
}

# Показать статистику перед очисткой
show_statistics() {
    log_info "Текущая статистика базы данных:"

    sudo -u postgres psql -d "$DB_NAME" << 'EOF'
SELECT
    (SELECT COUNT(*) FROM Users) as users_count,
    (SELECT COUNT(*) FROM Staff) as staff_count,
    (SELECT COUNT(*) FROM Tickets) as tickets_count,
    (SELECT COUNT(*) FROM TicketComments) as comments_count,
    (SELECT COUNT(*) FROM TicketLogs) as logs_count,
    (SELECT COUNT(*) FROM TicketStatuses) as statuses_count,
    (SELECT COUNT(*) FROM ProblemCategories) as categories_count;
EOF
}

# Очистка всех данных (сохраняя структуру)
clear_all_data() {
    log_info "Очистка всех данных из базы данных..."

    sudo -u postgres psql -d "$DB_NAME" << 'EOF'
-- Отключить триггеры для ускорения (если есть)
-- Очистка данных в правильном порядке (с учетом foreign keys)
TRUNCATE TABLE TicketLogs CASCADE;
TRUNCATE TABLE TicketComments CASCADE;
TRUNCATE TABLE Tickets CASCADE;
TRUNCATE TABLE Users CASCADE;
TRUNCATE TABLE Staff CASCADE;

-- Сохраняем справочные данные (статусы и категории), но можно очистить и их
-- TRUNCATE TABLE TicketStatuses CASCADE;
-- TRUNCATE TABLE ProblemCategories CASCADE;
EOF

    log_info "Все данные очищены"
}

# Очистка ВСЕХ данных включая справочные
clear_all_data_complete() {
    log_info "Полная очистка ВСЕХ данных включая справочные..."

    sudo -u postgres psql -d "$DB_NAME" << 'EOF'
-- Очистка всех таблиц
TRUNCATE TABLE TicketLogs CASCADE;
TRUNCATE TABLE TicketComments CASCADE;
TRUNCATE TABLE Tickets CASCADE;
TRUNCATE TABLE Users CASCADE;
TRUNCATE TABLE Staff CASCADE;
TRUNCATE TABLE TicketStatuses CASCADE;
TRUNCATE TABLE ProblemCategories CASCADE;
EOF

    log_info "Все данные полностью очищены (включая справочные)"
}

# Восстановление справочных данных
restore_reference_data() {
    log_info "Восстановление справочных данных..."

    sudo -u postgres psql -d "$DB_NAME" << 'EOF'
-- Восстановление статусов тикетов
INSERT INTO TicketStatuses (status_name) VALUES
('Новый'),
('В работе'),
('Ожидает ответа пользователя'),
('Решено'),
('Закрыт');

-- Восстановление категорий проблем
INSERT INTO ProblemCategories (category_name) VALUES
('Проблема с входом в систему'),
('Ошибка в отчете'),
('Вопрос по оплате'),
('Технический сбой'),
('Настройка доступа'),
('Проблемы с оборудованием'),
('Вопрос по функционалу'),
('Баг в системе'),
('Консультация'),
('Запрос на доработку');
EOF

    log_info "Справочные данные восстановлены"
}

# Удаление базы данных полностью
drop_database() {
    log_warn "ОПАСНО: Эта операция полностью удалит базу данных '$DB_NAME'"
    read -p "Вы уверены, что хотите полностью удалить базу данных? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Удаление базы данных '$DB_NAME'..."
        sudo -u postgres psql -c "DROP DATABASE IF EXISTS $DB_NAME;"
        log_info "База данных '$DB_NAME' полностью удалена"
    else
        log_info "Удаление базы данных отменено"
    fi
}

# Пересоздание базы данных (полный reset)
recreate_database() {
    log_warn "Эта операция полностью пересоздаст базу данных"
    read -p "Продолжить? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        drop_database
        log_info "Создание новой базы данных '$DB_NAME'..."
        sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;"
        log_info "База данных '$DB_NAME' создана"
    else
        log_info "Пересоздание базы данных отменено"
    fi
}

# Показать меню
show_menu() {
    echo
    echo "=========================================="
    echo " Очистка базы данных поддержки"
    echo "=========================================="
    echo "1. Показать текущую статистику"
    echo "2. Очистить все данные (сохранить структуру)"
    echo "3. Очистить ВСЕ данные (включая справочные)"
    echo "4. Очистить и восстановить справочные данные"
    echo "5. Полностью удалить базу данных"
    echo "6. Полностью пересоздать базу данных"
    echo "7. Выход"
    echo "=========================================="
}

# Основная функция
main() {
    log_info "Скрипт очистки базы данных поддержки"
    log_info "База данных: $DB_NAME"

    check_connection
    check_database_exists

    while true; do
        show_menu
        read -p "Выберите действие [1-7]: " choice

        case $choice in
            1)
                show_statistics
                ;;
            2)
                log_warn "Очистка всех данных (структура сохранится)"
                read -p "Продолжить? (y/N): " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    clear_all_data
                    show_statistics
                else
                    log_info "Очистка отменена"
                fi
                ;;
            3)
                log_warn "Очистка ВСЕХ данных (включая справочные)"
                read -p "Продолжить? (y/N): " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    clear_all_data_complete
                    show_statistics
                else
                    log_info "Очистка отменена"
                fi
                ;;
            4)
                log_info "Очистка и восстановление справочных данных"
                read -p "Продолжить? (y/N): " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    clear_all_data_complete
                    restore_reference_data
                    show_statistics
                else
                    log_info "Операция отменена"
                fi
                ;;
            5)
                drop_database
                break
                ;;
            6)
                recreate_database
                break
                ;;
            7)
                log_info "Выход"
                break
                ;;
            *)
                log_error "Неверный выбор. Попробуйте снова."
                ;;
        esac

        echo
        read -p "Нажмите Enter для продолжения..."
    done
}

# Обработка аргументов командной строки
if [[ $# -gt 0 ]]; then
    case $1 in
        --stats|--statistics|-s)
            check_connection
            check_database_exists
            show_statistics
            exit 0
            ;;
        --clear|-c)
            check_connection
            check_database_exists
            clear_all_data
            show_statistics
            exit 0
            ;;
        --clear-all|-C)
            check_connection
            check_database_exists
            clear_all_data_complete
            show_statistics
            exit 0
            ;;
        --reset|-r)
            check_connection
            check_database_exists
            clear_all_data_complete
            restore_reference_data
            show_statistics
            exit 0
            ;;
        --drop|-d)
            check_connection
            drop_database
            exit 0
            ;;
        --recreate|-R)
            check_connection
            recreate_database
            exit 0
            ;;
        --help|-h)
            echo "Использование: $0 [ОПЦИИ] [имя_базы]"
            echo
            echo "ОПЦИИ:"
            echo "  -s, --stats        Показать статистику"
            echo "  -c, --clear        Очистить все данные"
            echo "  -C, --clear-all    Очистить ВСЕ данные (включая справочные)"
            echo "  -r, --reset        Очистить и восстановить справочные данные"
            echo "  -d, --drop         Полностью удалить базу данных"
            echo "  -R, --recreate     Полностью пересоздать базу данных"
            echo "  -h, --help         Показать эту справку"
            echo
            echo "ПРИМЕРЫ:"
            echo "  $0                          # Интерактивный режим"
            echo "  $0 --stats                  # Показать статистику"
            echo "  $0 --clear my_database      # Очистить данные в my_database"
            echo "  $0 --drop                   # Удалить базу данных"
            exit 0
            ;;
        *)
            # Первый аргумент - имя базы данных
            DB_NAME=$1
            ;;
    esac
fi

# Запуск основной функции
main "$@"
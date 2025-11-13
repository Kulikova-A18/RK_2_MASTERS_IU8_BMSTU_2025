#!/bin/bash

# Скрипт для создания базы данных поддержки и заполнения тестовыми данными
# Использует sudo для доступа к PostgreSQL

set -e

DB_NAME="support_system"
HOST="localhost"
PORT="5432"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
  echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
  echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

check_postgresql() {
  log_info "Проверка статуса PostgreSQL..."
  if ! sudo systemctl is-active --quiet postgresql; then
    log_warn "PostgreSQL не запущен. Пытаюсь запустить..."
    sudo systemctl start postgresql
    sleep 2
  fi

  if sudo systemctl is-active --quiet postgresql; then
    log_info "PostgreSQL запущен"
  else
    log_error "Не удалось запустить PostgreSQL"
    exit 1
  fi
}

check_connection() {
  log_info "Проверка подключения к PostgreSQL..."
  if sudo -u postgres psql -c "SELECT 1;" &> /dev/null; then
    log_info "Подключение успешно установлено"
  else
    log_error "Не удалось подключиться к PostgreSQL"
    exit 1
  fi
}

# Обновление версии сортировки для template1 и postgres (если возможно)
refresh_collation_versions() {
  log_info "Проверка и обновление версии сортировки для template1 и postgres..."
  # Эти команды могут завершиться с предупреждением или ошибкой, если collation mismatch не позволяет выполнить ALTER.
  # Мы подавляем вывод ошибок для этих команд, но можем попытаться их выполнить.
  # Если они не выполнены, PostgreSQL будет использовать старую версию collation для новых баз данных,
  # что может привести к предупреждениям, но не должно останавливать процесс.
  sudo -u postgres psql -c "ALTER DATABASE template1 REFRESH COLLATION VERSION;" 2>/dev/null || \
    log_warn "Не удалось обновить версию сортировки для template1. Возможно, она не требуется или collation mismatch критичен."
  sudo -u postgres psql -c "ALTER DATABASE postgres REFRESH COLLATION VERSION;" 2>/dev/null || \
    log_warn "Не удалось обновить версию сортировки для postgres. Возможно, она не требуется или collation mismatch критичен."
}

create_database() {
  log_info "Создание базы данных '$DB_NAME'..."

  if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    log_warn "База данных '$DB_NAME' уже существует"
    read -p "Удалить существующую базу данных? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      log_info "Удаление существующей базы данных..."
      sudo -u postgres psql -c "DROP DATABASE IF EXISTS $DB_NAME;"
    else
      log_info "Продолжение работы с существующей базой данных"
      return 0
    fi
  fi

  # Обновляем версии сортировки перед созданием новой базы
  refresh_collation_versions

  # Пытаемся создать базу данных. Команда CREATE DATABASE может выдать предупреждения,
  # если template1 все еще имеет mismatched collation version, но это не критично.
  sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;"
  log_info "База данных '$DB_NAME' создана успешно"
}

create_tables() {
  log_info "Создание таблиц..."
  sudo -u postgres psql -d "$DB_NAME" << 'EOF'
-- Создание таблиц
CREATE TABLE Users (
  user_id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  full_name VARCHAR(100) NOT NULL,
  registration_date TIMESTAMP NOT NULL
);

CREATE TABLE Staff (
  staff_id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  full_name VARCHAR(100) NOT NULL,
  email VARCHAR(255) NOT NULL,
  department VARCHAR(100) NOT NULL,
  position VARCHAR(100) NOT NULL,
  is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE TicketStatuses (
  status_id SERIAL PRIMARY KEY,
  status_name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE ProblemCategories (
  category_id SERIAL PRIMARY KEY,
  category_name VARCHAR(100) NOT NULL
);

CREATE TABLE Tickets (
  ticket_id SERIAL PRIMARY KEY,
  subject VARCHAR(255) NOT NULL,
  description TEXT,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP,
  closed_at TIMESTAMP,
  user_id INTEGER NOT NULL REFERENCES Users(user_id),
  assigned_staff_id INTEGER REFERENCES Staff(staff_id),
  status_id INTEGER NOT NULL REFERENCES TicketStatuses(status_id),
  category_id INTEGER NOT NULL REFERENCES ProblemCategories(category_id)
);

CREATE TABLE TicketComments (
  comment_id SERIAL PRIMARY KEY,
  ticket_id INTEGER NOT NULL REFERENCES Tickets(ticket_id),
  author_id INTEGER NOT NULL,
  author_type VARCHAR(10) CHECK (author_type IN ('user', 'staff')) NOT NULL,
  comment_text TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL
);

CREATE TABLE TicketLogs (
  log_id SERIAL PRIMARY KEY,
  ticket_id INTEGER NOT NULL REFERENCES Tickets(ticket_id),
  action VARCHAR(255) NOT NULL,
  performed_by_staff_id INTEGER REFERENCES Staff(staff_id),
  performed_at TIMESTAMP NOT NULL
);
EOF
}

insert_reference_data() {
  log_info "Заполнение справочных данных..."
  sudo -u postgres psql -d "$DB_NAME" << 'EOF'
-- Заполнение статусов тикетов
INSERT INTO TicketStatuses (status_name) VALUES
  ('Новый'),
  ('В работе'),
  ('Ожидает ответа пользователя'),
  ('Решено'),
  ('Закрыт');

-- Заполнение категорий проблем
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
}

generate_test_data() {
  log_info "Генерация тестовых данных с реалистичными ФИО и отделами..."
  sudo -u postgres psql -d "$DB_NAME" << 'EOF'
-- Генерация пользователей (100 пользователей с реалистичными ФИО)
INSERT INTO Users (email, full_name, registration_date)
SELECT
  'user' || seq || '@company.com',
  CASE (seq % 20)
    WHEN 0 THEN 'Иванов Александр Сергеевич'
    WHEN 1 THEN 'Петрова Мария Владимировна'
    WHEN 2 THEN 'Сидоров Дмитрий Иванович'
    WHEN 3 THEN 'Кузнецова Елена Петровна'
    WHEN 4 THEN 'Васильев Андрей Николаевич'
    WHEN 5 THEN 'Николаева Ольга Сергеевна'
    WHEN 6 THEN 'Морозов Павел Александрович'
    WHEN 7 THEN 'Орлова Анна Дмитриевна'
    WHEN 8 THEN 'Лебедев Михаил Викторович'
    WHEN 9 THEN 'Семенова Ирина Олеговна'
    WHEN 10 THEN 'Федоров Артем Юрьевич'
    WHEN 11 THEN 'Жукова Татьяна Васильевна'
    WHEN 12 THEN 'Громов Сергей Павлович'
    WHEN 13 THEN 'Волкова Надежда Игоревна'
    WHEN 14 THEN 'Тихонов Алексей Владимирович'
    WHEN 15 THEN 'Андреева Юлия Михайловна'
    WHEN 16 THEN 'Белов Роман Станиславович'
    WHEN 17 THEN 'Ковалева Екатерина Алексеевна'
    WHEN 18 THEN 'Данилов Виктор Петрович'
    WHEN 19 THEN 'Соколова Людмила Андреевна'
  END,
  NOW() - (random() * 365)::INTEGER * INTERVAL '1 day'
FROM generate_series(1, 100) seq;

-- Генерация сотрудников поддержки (20 сотрудников с ИТ-отделами)
INSERT INTO Staff (username, full_name, email, department, position, is_active)
SELECT
  'support' || seq,
  CASE (seq % 20)
    WHEN 0 THEN 'Смирнов Алексей Владимирович'
    WHEN 1 THEN 'Козлова Ирина Петровна'
    WHEN 2 THEN 'Новиков Денис Сергеевич'
    WHEN 3 THEN 'Макарова Ольга Александровна'
    WHEN 4 THEN 'Зайцев Артем Игоревич'
    WHEN 5 THEN 'Попова Наталья Викторовна'
    WHEN 6 THEN 'Соловьев Максим Дмитриевич'
    WHEN 7 THEN 'Воробьева Елена Сергеевна'
    WHEN 8 THEN 'Фролов Иван Алексеевич'
    WHEN 9 THEN 'Алексеева Светлана Юрьевна'
    WHEN 10 THEN 'Егоров Павел Николаевич'
    WHEN 11 THEN 'Карпова Марина Олеговна'
    WHEN 12 THEN 'Кириллов Антон Васильевич'
    WHEN 13 THEN 'Титова Юлия Денисовна'
    WHEN 14 THEN 'Исаев Роман Андреевич'
    WHEN 15 THEN 'Федотова Анна Владимировна'
    WHEN 16 THEN 'Гусев Дмитрий Павлович'
    WHEN 17 THEN 'Комарова Ирина Игоревна'
    WHEN 18 THEN 'Тарасов Виталий Сергеевич'
    WHEN 19 THEN 'Субботина Оксана Михайловна'
  END,
  'support' || seq || '@company.com',
  CASE (seq % 10)
    WHEN 0 THEN 'Отдел технической поддержки'
    WHEN 1 THEN 'Отдел системного администрирования'
    WHEN 2 THEN 'Отдел сетевой инфраструктуры'
    WHEN 3 THEN 'Отдел информационной безопасности'
    WHEN 4 THEN 'Отдел разработки и внедрения'
    WHEN 5 THEN 'Отдел баз данных'
    WHEN 6 THEN 'Отдел облачных технологий'
    WHEN 7 THEN 'Отдел мониторинга и аналитики'
    WHEN 8 THEN 'Сервисный деск Level 1'
    WHEN 9 THEN 'Сервисный деск Level 2'
  END,
  CASE (seq % 5)
    WHEN 0 THEN 'Специалист технической поддержки'
    WHEN 1 THEN 'Системный администратор'
    WHEN 2 THEN 'Сетевой инженер'
    WHEN 3 THEN 'Инженер по информационной безопасности'
    WHEN 4 THEN 'Старший специалист'
  END,
  CASE WHEN random() > 0.1 THEN TRUE ELSE FALSE END
FROM generate_series(1, 20) seq;

-- Генерация тикетов (1000+ тикетов с реалистичными темами)
INSERT INTO Tickets (
  subject,
  description,
  created_at,
  updated_at,
  closed_at,
  user_id,
  assigned_staff_id,
  status_id,
  category_id
)
SELECT
  CASE (random() * 9)::INTEGER
    WHEN 0 THEN 'Проблема с доступом к корпоративному порталу'
    WHEN 1 THEN 'Ошибка при формировании отчета в 1С'
    WHEN 2 THEN 'Не работает почтовый клиент Outlook'
    WHEN 3 THEN 'Запрос на предоставление прав доступа'
    WHEN 4 THEN 'Проблема с VPN подключением'
    WHEN 5 THEN 'Не печатает сетевой принтер'
    WHEN 6 THEN 'Вопрос по работе с CRM системой'
    WHEN 7 THEN 'Сбой в работе базы данных'
    WHEN 8 THEN 'Запрос на обновление программного обеспечения'
    WHEN 9 THEN 'Проблема с видеоконференцией'
  END || ' - ' || (user_seq * 10 + ticket_seq),
  CASE (random() * 4)::INTEGER
    WHEN 0 THEN 'Пользователь сообщает о проблеме с доступом к системе. Необходимо проверить учетные данные и настройки доступа.'
    WHEN 1 THEN 'В системе наблюдается ошибка при выполнении операции. Пользователь предоставил подробное описание шагов воспроизведения.'
    WHEN 2 THEN 'Запрос на техническую консультацию по использованию функционала системы. Требуется разъяснение рабочих процессов.'
    WHEN 3 THEN 'Обнаружен сбой в работе оборудования. Необходима диагностика и восстановление работоспособности.'
    WHEN 4 THEN 'Запрос на изменение конфигурации или настройки системы в соответствии с новыми требованиями.'
  END,
  NOW() - (random() * 30)::INTEGER * INTERVAL '1 day',
  CASE WHEN random() > 0.3 THEN NOW() - (random() * 20)::INTEGER * INTERVAL '1 day' ELSE NULL END,
  CASE WHEN random() > 0.7 THEN NOW() - (random() * 10)::INTEGER * INTERVAL '1 day' ELSE NULL END,
  (random() * 99)::INTEGER + 1,
  CASE WHEN random() > 0.2 THEN (random() * 19)::INTEGER + 1 ELSE NULL END,
  (random() * 4)::INTEGER + 1,
  (random() * 9)::INTEGER + 1
FROM generate_series(1, 100) user_seq, generate_series(1, 10) ticket_seq;

-- Генерация комментариев
INSERT INTO TicketComments (ticket_id, author_id, author_type, comment_text, created_at)
-- Комментарии от пользователей
SELECT
  ticket_id,
  user_id,
  'user',
  CASE (random() * 3)::INTEGER
    WHEN 0 THEN 'Добрый день! Проблема все еще актуальна, не могли бы вы уточнить сроки решения?'
    WHEN 1 THEN 'Спасибо за оперативный ответ. Дополнительная информация: ошибка возникает при выполнении определенных действий.'
    WHEN 2 THEN 'Прошу прояснить следующий вопрос по заявке. Какие дополнительные данные требуются для решения проблемы?'
    WHEN 3 THEN 'Подтверждаю, что проблема решена. Благодарю за помощь!'
  END,
  created_at + (random() * 5)::INTEGER * INTERVAL '1 hour'
FROM Tickets
WHERE random() > 0.1
UNION ALL
-- Комментарии от сотрудников
SELECT
  ticket_id,
  (random() * 19)::INTEGER + 1,
  'staff',
  CASE (random() * 4)::INTEGER
    WHEN 0 THEN 'Принял заявку в работу. Провожу диагностику проблемы.'
    WHEN 1 THEN 'Для решения проблемы требуются дополнительные данные. Прошу предоставить скриншот ошибки.'
    WHEN 2 THEN 'Проблема идентифицирована. Выполняю работы по восстановлению.'
    WHEN 3 THEN 'Решение применено. Прошу проверить работоспособность и подтвердить решение заявки.'
    WHEN 4 THEN 'Передал заявку в смежный отдел для дальнейшего рассмотрения.'
  END,
  created_at + (random() * 15)::INTEGER * INTERVAL '1 day'
FROM Tickets
WHERE random() > 0.4;

-- Генерация логов
INSERT INTO TicketLogs (ticket_id, action, performed_by_staff_id, performed_at)
-- Логи создания
SELECT
  ticket_id,
  'Тикет создан в системе',
  NULL,
  created_at
FROM Tickets
UNION ALL
-- Логи назначения
SELECT
  ticket_id,
  'Тикет назначен на сотрудника ' || (random() * 19 + 1)::INTEGER,
  (random() * 19)::INTEGER + 1,
  created_at + (random() * 2)::INTEGER * INTERVAL '1 hour'
FROM Tickets
WHERE random() > 0.3
UNION ALL
-- Логи изменения статуса
SELECT
  ticket_id,
  CASE (random() * 4)::INTEGER
    WHEN 0 THEN 'Статус изменен на "В работе"'
    WHEN 1 THEN 'Статус изменен на "Ожидает ответа пользователя"'
    WHEN 2 THEN 'Статус изменен на "Решено"'
    WHEN 3 THEN 'Статус изменен на "Закрыт"'
    WHEN 4 THEN 'Статус изменен на "Новый"'
  END,
  (random() * 19)::INTEGER + 1,
  created_at + (random() * 25)::INTEGER * INTERVAL '1 day'
FROM Tickets
WHERE random() > 0.5;
EOF
}

create_indexes() {
  log_info "Создание индексов..."
  sudo -u postgres psql -d "$DB_NAME" << 'EOF'
-- Индексы для оптимизации запросов
CREATE INDEX idx_tickets_user_id ON Tickets(user_id);
CREATE INDEX idx_tickets_assigned_staff_id ON Tickets(assigned_staff_id);
CREATE INDEX idx_tickets_status_id ON Tickets(status_id);
CREATE INDEX idx_tickets_category_id ON Tickets(category_id);
CREATE INDEX idx_tickets_created_at ON Tickets(created_at);
CREATE INDEX idx_tickets_closed_at ON Tickets(closed_at);
CREATE INDEX idx_ticket_comments_ticket_id ON TicketComments(ticket_id);
CREATE INDEX idx_ticket_comments_author_type ON TicketComments(author_type);
CREATE INDEX idx_ticket_comments_created_at ON TicketComments(created_at);
CREATE INDEX idx_ticket_logs_ticket_id ON TicketLogs(ticket_id);
CREATE INDEX idx_ticket_logs_performed_at ON TicketLogs(performed_at);
CREATE INDEX idx_users_email ON Users(email);
CREATE INDEX idx_staff_username ON Staff(username);
CREATE INDEX idx_staff_department ON Staff(department);
EOF
}

verify_data() {
  log_info "Проверка созданных данных..."
  echo "Статистика базы данных:"
  sudo -u postgres psql -d "$DB_NAME" << 'EOF'
SELECT
  (SELECT COUNT(*) FROM Users) as users_count,
  (SELECT COUNT(*) FROM Staff) as staff_count,
  (SELECT COUNT(*) FROM Tickets) as tickets_count,
  (SELECT COUNT(*) FROM TicketComments) as comments_count,
  (SELECT COUNT(*) FROM TicketLogs) as logs_count;

\echo ''
\echo 'Примеры данных:'
\echo '--- Пользователи ---'
SELECT user_id, full_name, email FROM Users LIMIT 5;

\echo ''
\echo '--- Сотрудники поддержки ---'
SELECT staff_id, full_name, department, position FROM Staff LIMIT 5;

\echo ''
\echo '--- Распределение сотрудников по отделам ---'
SELECT department, COUNT(*) as count FROM Staff GROUP BY department ORDER BY count DESC;

\echo ''
\echo '--- Тикеты ---'
SELECT ticket_id, subject, created_at FROM Tickets LIMIT 5;

\echo ''
\echo '--- Статистика тикетов по статусам ---'
SELECT s.status_name, COUNT(*) as count
FROM Tickets t
JOIN TicketStatuses s ON t.status_id = s.status_id
GROUP BY s.status_name
ORDER BY count DESC;
EOF
}

# --- Функция для установки пароля пользователя postgres ---
set_postgres_password() {
  local desired_password="new_secure_password"
  local db_host="localhost" # По умолчанию localhost
  local db_port="5432"      # По умолчанию 5432

  if [[ -z "$desired_password" ]]; then
    log_error "Функция set_postgres_password: не передан пароль."
    return 1
  fi

  log_info "Проверка необходимости установки/изменения пароля для пользователя 'postgres'..."

  if echo "ALTER USER postgres PASSWORD '$desired_password';" | sudo -u postgres psql -v ON_ERROR_STOP=1 -h "$db_host" -p "$db_port" -d postgres > /dev/null 2>&1; then
      log_info "Пароль для пользователя 'postgres' успешно установлен или изменен."
  else
      log_error "Не удалось установить пароль для пользователя 'postgres'. Проверьте права доступа и логи PostgreSQL."
      return 1
  fi
}


main() {
  log_info "Запуск скрипта создания базы данных поддержки"
  log_info "База данных: $DB_NAME"

  check_postgresql
  check_connection
  create_database
  create_tables
  insert_reference_data
  generate_test_data
  create_indexes
  verify_data
  set_postgres_password

  log_info "База данных '$DB_NAME' успешно создана и заполнена тестовыми данными!"
  log_info "Для подключения используйте: sudo -u postgres psql -d $DB_NAME"
}

main "$@"

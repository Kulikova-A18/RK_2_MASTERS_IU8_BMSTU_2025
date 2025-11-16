-- db/create_support_db.sql

-- 1. Создание таблиц
-- Создание таблицы пользователей
CREATE TABLE IF NOT EXISTS Users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL, -- Добавлено UNIQUE
    full_name VARCHAR(100) NOT NULL,
    registration_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы персонала
CREATE TABLE IF NOT EXISTS Staff (
    staff_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL, -- Добавлено UNIQUE
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    department VARCHAR(100) NOT NULL,
    position VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Создание таблицы статусов тикетов
CREATE TABLE IF NOT EXISTS TicketStatuses (
    status_id SERIAL PRIMARY KEY,
    status_name VARCHAR(50) UNIQUE NOT NULL -- Добавлено UNIQUE
);

-- Создание таблицы категорий проблем
CREATE TABLE IF NOT EXISTS ProblemCategories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) UNIQUE NOT NULL -- Добавлено UNIQUE
);

-- Создание таблицы тикетов
CREATE TABLE IF NOT EXISTS Tickets (
    ticket_id SERIAL PRIMARY KEY,
    subject VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    closed_at TIMESTAMP,
    user_id INTEGER NOT NULL REFERENCES Users(user_id),
    assigned_staff_id INTEGER REFERENCES Staff(staff_id),
    status_id INTEGER NOT NULL REFERENCES TicketStatuses(status_id),
    category_id INTEGER NOT NULL REFERENCES ProblemCategories(category_id)
);

-- Создание таблицы комментариев к тикетам
CREATE TABLE IF NOT EXISTS TicketComments (
    comment_id SERIAL PRIMARY KEY,
    ticket_id INTEGER NOT NULL REFERENCES Tickets(ticket_id) ON DELETE CASCADE,
    author_id INTEGER NOT NULL, -- Может ссылаться на user_id или staff_id, требует дополнительной логики
    author_type VARCHAR(10) CHECK (author_type IN ('user', 'staff')) NOT NULL,
    comment_text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы логов тикетов
CREATE TABLE IF NOT EXISTS TicketLogs (
    log_id SERIAL PRIMARY KEY,
    ticket_id INTEGER NOT NULL REFERENCES Tickets(ticket_id) ON DELETE CASCADE,
    action VARCHAR(255) NOT NULL,
    performed_by_staff_id INTEGER REFERENCES Staff(staff_id),
    performed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 4. Создание индексов
-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_tickets_user_id ON Tickets(user_id);
CREATE INDEX IF NOT EXISTS idx_tickets_assigned_staff_id ON Tickets(assigned_staff_id);
CREATE INDEX IF NOT EXISTS idx_tickets_status_id ON Tickets(status_id);
CREATE INDEX IF NOT EXISTS idx_tickets_category_id ON Tickets(category_id);
CREATE INDEX IF NOT EXISTS idx_tickets_created_at ON Tickets(created_at);
CREATE INDEX IF NOT EXISTS idx_tickets_closed_at ON Tickets(closed_at);
CREATE INDEX IF NOT EXISTS idx_ticket_comments_ticket_id ON TicketComments(ticket_id);
CREATE INDEX IF NOT EXISTS idx_ticket_comments_author_type ON TicketComments(author_type);
CREATE INDEX IF NOT EXISTS idx_ticket_comments_created_at ON TicketComments(created_at);
CREATE INDEX IF NOT EXISTS idx_ticket_logs_ticket_id ON TicketLogs(ticket_id);
CREATE INDEX IF NOT EXISTS idx_ticket_logs_performed_at ON TicketLogs(performed_at);
CREATE INDEX IF NOT EXISTS idx_users_email ON Users(email);
CREATE INDEX IF NOT EXISTS idx_staff_username ON Staff(username);
CREATE INDEX IF NOT EXISTS idx_staff_department ON Staff(department);

-- 2. Заполнение справочных данных
-- Заполнение статусов тикетов
INSERT INTO TicketStatuses (status_name) VALUES
    ('Новый'),
    ('В работе'),
    ('Ожидает ответа пользователя'),
    ('Решено'),
    ('Закрыт')
ON CONFLICT (status_name) DO NOTHING; -- Работает благодаря UNIQUE на status_name

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
    ('Запрос на доработку')
ON CONFLICT (category_name) DO NOTHING; -- Работает благодаря UNIQUE на category_name

-- 3. Генерация тестовых данных с реалистичными ФИО и отделами
-- Генерация пользователей (200 пользователей с реалистичными ФИО)
INSERT INTO Users (email, full_name, registration_date) SELECT
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
FROM generate_series(1, 200) seq
ON CONFLICT (email) DO NOTHING; -- Работает благодаря UNIQUE на email

-- Генерация сотрудников поддержки (20 сотрудников с ИТ-отделами)
INSERT INTO Staff (username, full_name, email, department, position, is_active) SELECT
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
FROM generate_series(1, 20) seq
ON CONFLICT (username) DO NOTHING; -- Работает благодаря UNIQUE на username

-- Генерация тикетов (200 тикетов с реалистичными темами)
-- ВАЖНО: Генерация тикетов теперь происходит *после* вставки пользователей и сотрудников
-- и *после* вставки статусов и категорий, чтобы внешние ключи были корректны.
INSERT INTO Tickets (subject, description, created_at, updated_at, closed_at, user_id, assigned_staff_id, status_id, category_id) SELECT
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
    END || ' - ' || (seq),
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
    (random() * 199)::INTEGER + 1, -- user_id из существующих пользователей
    CASE WHEN random() > 0.2 THEN (random() * 19)::INTEGER + 1 ELSE NULL END, -- staff_id из существующих сотрудников
    (random() * 4)::INTEGER + 1, -- status_id из существующих статусов
    (random() * 9)::INTEGER + 1 -- category_id из существующих категорий
FROM generate_series(1, 200) seq;

-- Генерация комментариев
-- Комментарии от пользователей
INSERT INTO TicketComments (ticket_id, author_id, author_type, comment_text, created_at)
SELECT
    ticket_id,
    user_id, -- author_id как user_id
    'user',
    CASE (random() * 3)::INTEGER
        WHEN 0 THEN 'Добрый день! Проблема все еще актуальна, не могли бы вы уточнить сроки решения?'
        WHEN 1 THEN 'Спасибо за оперативный ответ. Дополнительная информация: ошибка возникает при выполнении определенных действий.'
        WHEN 2 THEN 'Прошу прояснить следующий вопрос по заявке. Какие дополнительные данные требуются для решения проблемы?'
        WHEN 3 THEN 'Подтверждаю, что проблема решена. Благодарю за помощь!'
    END,
    created_at + (random() * 5)::INTEGER * INTERVAL '1 hour'
FROM Tickets
WHERE random() > 0.1 AND user_id IS NOT NULL; -- author_id как user_id

-- Комментарии от сотрудников
INSERT INTO TicketComments (ticket_id, author_id, author_type, comment_text, created_at)
SELECT
    ticket_id,
    (random() * 19)::INTEGER + 1, -- author_id как staff_id
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
WHERE random() > 0.4 AND assigned_staff_id IS NOT NULL; -- author_id как staff_id

-- Генерация логов
-- Логи создания
INSERT INTO TicketLogs (ticket_id, action, performed_by_staff_id, performed_at)
SELECT
    ticket_id,
    'Тикет создан в системе',
    NULL, -- Создание не выполняется сотрудником
    created_at
FROM Tickets;

-- Логи назначения
INSERT INTO TicketLogs (ticket_id, action, performed_by_staff_id, performed_at)
SELECT
    ticket_id,
    'Тикет назначен на сотрудника ' || (random() * 19 + 1)::INTEGER,
    (random() * 19)::INTEGER + 1,
    created_at + (random() * 2)::INTEGER * INTERVAL '1 hour'
FROM Tickets
WHERE random() > 0.3;

-- Логи изменения статуса
INSERT INTO TicketLogs (ticket_id, action, performed_by_staff_id, performed_at)
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

# Схема связей базы данных `support_system`

## Таблицы и их столбцы

### `Users`
| Столбец            | Тип данных     | Описание                     |
|--------------------|----------------|------------------------------|
| `user_id`          | `SERIAL`       | Первичный ключ               |
| `email`            | `VARCHAR(255)` | Уникальный email пользователя|
| `full_name`        | `VARCHAR(100)` | Полное имя                   |
| `registration_date`| `TIMESTAMP`    | Дата регистрации             |

### `Staff`
| Столбец        | Тип данных     | Описание                                   |
|----------------|----------------|--------------------------------------------|
| `staff_id`     | `SERIAL`       | Первичный ключ                             |
| `username`     | `VARCHAR(50)`  | Уникальное имя сотрудника                  |
| `full_name`    | `VARCHAR(100)` | Полное имя                                 |
| `email`        | `VARCHAR(255)` | Email                                      |
| `department`   | `VARCHAR(100)` | Отдел                                      |
| `position`     | `VARCHAR(100)` | Должность                                  |
| `is_active`    | `BOOLEAN`      | Активен ли сотрудник (по умолчанию `TRUE`) |

### `TicketStatuses`
| Столбец        | Тип данных     | Описание               |
|----------------|----------------|------------------------|
| `status_id`    | `SERIAL`       | Первичный ключ         |
| `status_name`  | `VARCHAR(50)`  | Название статуса       |

### `ProblemCategories`
| Столбец          | Тип данных     | Описание                     |
|------------------|----------------|------------------------------|
| `category_id`    | `SERIAL`       | Первичный ключ               |
| `category_name`  | `VARCHAR(100)` | Название категории проблемы  |

### `Tickets`
| Столбец              | Тип данных     | Описание                                |
|----------------------|----------------|-----------------------------------------|
| `ticket_id`          | `SERIAL`       | Первичный ключ                          |
| `subject`            | `VARCHAR(255)` | Тема тикета                             |
| `description`        | `TEXT`         | Описание проблемы                       |
| `created_at`         | `TIMESTAMP`    | Время создания                          |
| `updated_at`         | `TIMESTAMP`    | Время последнего обновления             |
| `closed_at`          | `TIMESTAMP`    | Время закрытия                          |
| `user_id`            | `INTEGER`      | → `Users(user_id)`                      |
| `assigned_staff_id`  | `INTEGER`      | → `Staff(staff_id)` (может быть `NULL`) |
| `status_id`          | `INTEGER`      | → `TicketStatuses(status_id)`           |
| `category_id`        | `INTEGER`      | → `ProblemCategories(category_id)`      |

### `TicketComments`
| Столбец         | Тип данных     | Описание                                           |
|-----------------|----------------|----------------------------------------------------|
| `comment_id`    | `SERIAL`       | Первичный ключ                                     |
| `ticket_id`     | `INTEGER`      | → `Tickets(ticket_id)`                             |
| `author_id`     | `INTEGER`      | ID автора (см. `author_type`)                      |
| `author_type`   | `VARCHAR(10)`  | `'user'` или `'staff'`                             |
| `comment_text`  | `TEXT`         | Текст комментария                                  |
| `created_at`    | `TIMESTAMP`    | Время комментария                                  |

> **Примечание**: `author_id` не является строгим внешним ключом, так как может ссылаться либо на `Users(user_id)`, либо на `Staff(staff_id)`, в зависимости от `author_type`.

### `TicketLogs`
| Столбец                 | Тип данных     | Описание                                          |
|-------------------------|----------------|---------------------------------------------------|
| `log_id`                | `SERIAL`       | Первичный ключ                                    |
| `ticket_id`             | `INTEGER`      | → `Tickets(ticket_id)`                            |
| `action`                | `VARCHAR(255)` | Описание действия                                 |
| `performed_by_staff_id` | `INTEGER`      | → `Staff(staff_id)` (может быть `NULL`)           |
| `performed_at`          | `TIMESTAMP`    | Время действия                                    |


## Схема связей (ER-диаграмма в тексте)

| Родительская таблица | Дочерняя таблица     | Связь (столбец → столбец)                      |
|----------------------|----------------------|-----------------------------------------------|
| `Users`              | `Tickets`            | `Users.user_id` → `Tickets.user_id`           |
| `Staff`              | `Tickets`            | `Staff.staff_id` → `Tickets.assigned_staff_id`|
| `TicketStatuses`     | `Tickets`            | `TicketStatuses.status_id` → `Tickets.status_id` |
| `ProblemCategories`  | `Tickets`            | `ProblemCategories.category_id` → `Tickets.category_id` |
| `Tickets`            | `TicketComments`     | `Tickets.ticket_id` → `TicketComments.ticket_id` |
| `Tickets`            | `TicketLogs`         | `Tickets.ticket_id` → `TicketLogs.ticket_id`  |
| `Staff`              | `TicketLogs`         | `Staff.staff_id` → `TicketLogs.performed_by_staff_id` |

#!/bin/bash

if [ -f "db_config.env" ]; then
    source db_config.env
    echo "Конфигурация загружена из db_config.env"
else
    echo "Файл конфигурации db_config.env не найден, используются значения по умолчанию"
fi

./create_support_db.sh "$DB_NAME" "$DB_USER" "$DB_PASSWORD" "$HOST" "$PORT"
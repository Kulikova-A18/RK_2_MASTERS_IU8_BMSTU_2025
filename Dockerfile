FROM python:3.9-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    gnupg \
    lsb-release \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*
RUN install -d /etc/apt/keyrings && \
    curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /etc/apt/keyrings/postgres.gpg && \
    gpg --no-default-keyring --keyring /etc/apt/keyrings/postgres.gpg --list-keys # Для проверки ключа

RUN echo "deb [signed-by=/etc/apt/keyrings/postgres.gpg] http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-13 \
    postgresql-client-13 \
    postgresql-contrib-13 \
    postgresql-client-common \
    && rm -rf /var/lib/apt/lists/*
RUN set -ex; \
    dpkgArch="$(dpkg --print-architecture)"; \
    case "${dpkgArch##*-}" in \
      amd64) gosuArch='amd64' ;; \
      arm64) gosuArch='arm64' ;; \
      *) echo >&2 "Unsupported architecture: ${dpkgArch}"; exit 1 ;; \
    esac; \
    gosuURL="https://github.com/tianon/gosu/releases/download/1.17/gosu-${gosuArch}"; \
    gosuPath="/usr/local/bin/gosu"; \
    wget -O "${gosuPath}" "${gosuURL}"; \
    chmod +x "${gosuPath}";

RUN mkdir -p /var/lib/postgresql/data && chown -R postgres:postgres /var/lib/postgresql/data

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY db/create_support_db.sql /docker-entrypoint-initdb.d/create_support_db.sql
RUN chown postgres:postgres /docker-entrypoint-initdb.d/create_support_db.sql

COPY . /app
WORKDIR /app

RUN mkdir -p logs
RUN echo '#!/bin/bash\n\

set -e\n\
\n\
# Запускаем PostgreSQL как демон\n\
echo "Запуск PostgreSQL..." \n\
gosu postgres /usr/lib/postgresql/13/bin/pg_ctl -D /var/lib/postgresql/data -o "-c listen_addresses=localhost" -w start\n\
\n\
# Ждем, пока PostgreSQL не будет готов принимать подключения\n\
echo "Ожидание готовности PostgreSQL..." \n\
# pg_isready может проверить готовность, даже если база данных не существует\n\
# но она должна уметь подключиться к *какой-то* базе, например, postgres\n\
until /usr/lib/postgresql/13/bin/pg_isready -h localhost -p 5432 -U postgres -d postgres; do \n\
  sleep 1 \n\
done\n\
echo "PostgreSQL готов."\n\
\n\
# Создаем базу данных support_system\n\
echo "Создание базы данных support_system..." \n\
gosu postgres /usr/lib/postgresql/13/bin/psql -U postgres -d postgres -c "CREATE DATABASE support_system OWNER postgres;"\n\
echo "База данных support_system создана."\n\
\n\
# Выполняем скрипт инициализации БД в новой базе\n\
echo "Выполняем скрипт инициализации БД в базе support_system..." \n\
gosu postgres /usr/lib/postgresql/13/bin/psql -U postgres -d support_system -f /docker-entrypoint-initdb.d/create_support_db.sql\n\
echo "Скрипт инициализации БД выполнен."\n\
\n\
# Запускаем основное приложение\n\
echo "Запуск main.py..." \n\
exec python main.py\n\
' > /start.sh && chmod +x /start.sh
RUN echo "listen_addresses = 'localhost'" > /etc/postgresql/13/main/postgresql.conf && \
    echo "local all all peer" > /etc/postgresql/13/main/pg_hba.conf && \
    echo "host all all 127.0.0.1/32 md5" >> /etc/postgresql/13/main/pg_hba.conf && \
    echo "host all all ::1/128 md5" >> /etc/postgresql/13/main/pg_hba.conf
RUN gosu postgres /usr/lib/postgresql/13/bin/initdb -D /var/lib/postgresql/data
RUN echo "ALTER USER postgres PASSWORD 'new_secure_password';" | gosu postgres /usr/lib/postgresql/13/bin/postgres --single -D /var/lib/postgresql/data -c config_file=/etc/postgresql/13/main/postgresql.conf

ENTRYPOINT ["/start.sh"]

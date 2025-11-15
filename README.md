# RK_2_MASTERS_IU8_BMSTU_2025

## Цель задания

Реализовать клиента, который реализует API запросы на сервер

## Требование

* Использовать python
* Реализовать графики по полученным данным
* Составить отчет

> На 15.11.2025 данные IP-адреса: 193.233.171.205:5000

## Варианты


Для вариантов были созданы следующие логин/пароль с установкой доступа

#### **Задание для всех**

На основе данных из API системы технической поддержки создать комплексную аналитическую панель, включающую графики и статистические показатели, которые помогут руководству принимать обоснованные управленческие решения

Источники данных:

* Эндпоинт ```/api/v1/tickets``` — список всех тикетов, назначенных пользователю
* Эндпоинт ```/api/v1/tickets/<ticket_id>``` — детальная информация по конкретному тикету

Постройте следующие графики:

* Линейный график: динамика создания тикетов по дням за последние 30 дней
* Столбчатая диаграмма: распределение тикетов по часам суток (когда чаще всего создаются обращения)
* Тепловая карта: активность по дням недели и часам

Создайте визуализации:

* Круговая диаграмма: распределение тикетов по категориям проблем
* Горизонтальная столбчатая диаграмма: среднее время решения (от created_at до closed_at) по каждой категории
* Таблица: топ-5 самых проблемных категорий по количеству тикетов


#### 1. **Отдел технической поддержки**  
> Постройте график динамики количества открытых и закрытых тикетов за последние 30 дней.  
> **Логин**: `analyst_ts`  
> **Пароль**: `XyZ67iOp89Ij`  
> **Эндпоинт**: `GET /api/v1/timeline?days=30`

---

#### 2. **Отдел системного администрирования**  
> Постройте круговую диаграмму распределения тикетов по категориям проблем.  
> **Логин**: `analyst_sa`  
> **Пароль**: `BcD01oLm23Kl`  
> **Эндпоинт**: `GET /api/v1/categories`

---

#### 3. **Отдел сетевой инфраструктуры**  
> Постройте столбчатый график активности сотрудников отдела: назначенных, активных и решённых тикетов.  
> **Логин**: `analyst_ni`  
> **Пароль**: `EfG45pQr67Mn`  
> **Эндпоинт**: `GET /api/v1/staff`

---

#### 4. **Отдел информационной безопасности**  
> Постройте график сравнения производительности сотрудника с отделом по скорости решения.  
> **Логин**: `analyst_is`  
> **Пароль**: `HjK89sTu01Op`  
> **Эндпоинты**: `GET /api/v1/comparison` и `GET /api/v1/metrics`

---

#### 5. **Отдел разработки и внедрения**  
> Постройте график роста нагрузки на отдел за 7/14/30 дней.  
> **Логин**: `analyst_di`  
> **Пароль**: `LmN23vWx45Qr`  
> **Эндпоинт**: `GET /api/v1/timeline?days=30`

---

#### 6. **Отдел баз данных**  
> Постройте график зависимости между количеством тикетов и удовлетворённостью пользователей.  
> **Логин**: `analyst_db`  
> **Пароль**: `PqR67zAb89St`  
> **Эндпоинт**: `GET /api/v1/timeline?days=30`

---

#### 7. **Отдел облачных технологий**  
> Постройте график прогноза нагрузки: фактические vs прогнозируемые тикеты.  
> **Логин**: `analyst_ct`  
> **Пароль**: `TuV01cDe23Uv`  
> **Эндпоинты**: `GET /api/v1/timeline?days=7` + `GET /api/v1/forecast`

---

#### 8. **Сервисный деск Level 1 и Level 2**  
> Постройте сравнительный график активности Level 1 и Level 2.  
> **Для Level 1**:  
> &nbsp;&nbsp;– Логин: `analyst_l1`  
> &nbsp;&nbsp;– Пароль: `AbC89jKl01Xy`  
> **Для Level 2**:  
> &nbsp;&nbsp;– Логин: `analyst_l2`  
> &nbsp;&nbsp;– Пароль: `DeF23mNo45Za`  
> **Эндпоинт (для обоих)**: `GET /api/v1/timeline?days=30`

## Пример запросов

| № | Отдел | Задача | Логин | Пароль | Команда `curl` |
|---|-------|--------|-------|--------|----------------|
| **1** | Отдел технической поддержки | Динамика открытых и закрытых тикетов за 30 дней | `analyst_ts` | `XyZ67iOp89Ij` | ```bash curl -X GET "http://localhost:5000/api/v1/timeline?login=analyst_ts&code=XyZ67iOp89Ij&days=30" ``` |
| **2** | Отдел системного администрирования | Распределение тикетов по категориям проблем | `analyst_sa` | `BcD01oLm23Kl` | ```bash curl -X GET "http://localhost:5000/api/v1/categories?login=analyst_sa&code=BcD01oLm23Kl" ``` |
| **3** | Отдел сетевой инфраструктуры | Активность сотрудников: назначенных, активных и решённых тикетов | `analyst_ni` | `EfG45pQr67Mn` | ```bash curl -X GET "http://localhost:5000/api/v1/staff?login=analyst_ni&code=EfG45pQr67Mn" ``` |
| **4** | Отдел информационной безопасности | Сравнение производительности сотрудника с отделом | `analyst_is` | `HjK89sTu01Op` | ```bash curl -X GET "http://localhost:5000/api/v1/comparison?login=analyst_is&code=HjK89sTu01Op" ``` |
| **5** | Отдел разработки и внедрения | Рост нагрузки на отдел за 30 дней | `analyst_di` | `LmN23vWx45Qr` | ```bash curl -X GET "http://localhost:5000/api/v1/timeline?login=analyst_di&code=LmN23vWx45Qr&days=30" ``` |
| **6** | Отдел баз данных | Зависимость между количеством тикетов и удовлетворённостью | `analyst_db` | `PqR67zAb89St` | ```bash curl -X GET "http://localhost:5000/api/v1/timeline?login=analyst_db&code=PqR67zAb89St&days=30" ``` |
| **7** | Отдел облачных технологий | Прогноз vs фактические данные (неделя) | `analyst_ct` | `TuV01cDe23Uv` | ```bash # Фактические данные<br>curl -X GET "http://localhost:5000/api/v1/timeline?login=analyst_ct&code=TuV01cDe23Uv&days=7"<br><br># Прогноз<br>curl -X GET "http://localhost:5000/api/v1/forecast?login=analyst_ct&code=TuV01cDe23Uv" ``` |
| **8** | Сервисный деск Level 1 и Level 2 | Сравнение активности Level 1 и Level 2 | **Level 1**: `analyst_l1`<br>**Level 2**: `analyst_l2` | **Level 1**: `AbC89jKl01Xy`<br>**Level 2**: `DeF23mNo45Za` | ```bash # Level 1<br>curl -X GET "http://localhost:5000/api/v1/timeline?login=analyst_l1&code=AbC89jKl01Xy&days=30"<br><br># Level 2<br>curl -X GET "http://localhost:5000/api/v1/timeline?login=analyst_l2&code=DeF23mNo45Za&days=30" ``` |


## Пример программы

```
import requests
import json

BASE_URL = "http://192.168.5.199:5000"

DEFAULT_USERS = {
    'manager_ts': {
        'role': 'manager',
        'code': "DeF34mNo56Pq"
    },
    'manager_sa': {
        'role': 'manager',
        'code': "GhI78wXy12Rt"
    }
}

def check_server_health():
    """
    Performs a GET request to the health endpoint to check if the server is running.

    @return: JSON response from the server or None if request failed
    """
    endpoint = '/api/v1/health'
    url = f"{BASE_URL}{endpoint}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None
    except json.JSONDecodeError:
        print("Error: Invalid JSON response.")
        return None

def make_authenticated_request(endpoint, login, code, params=None):
    """
    Performs an authenticated GET request to the specified API endpoint.

    @param endpoint: API endpoint (e.g., '/api/v1/timeline')
    @param login: Username for authentication
    @param code: Password for authentication
    @param params: Additional request parameters (optional)
    @return: JSON response from the API or None if request failed
    """
    url = f"{BASE_URL}{endpoint}"
    params = params or {}
    params['login'] = login
    params['code'] = code

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None
    except json.JSONDecodeError:
        print("Error: Invalid JSON response.")
        return None

def main():
    """
    Main function to check server health and make authenticated requests for all users.
    """
    health_data = check_server_health()

    if not health_data:
        return
    print(json.dumps(health_data, indent=2, ensure_ascii=False))

    for username, user_info in DEFAULT_USERS.items():
        login = username
        code = user_info['code']
        print(f"\nTesting user: {login} (role: {user_info['role']})")

        # Example endpoint (you can change this)
        endpoint = '/api/v1/profile'
        params = {}

        data = make_authenticated_request(endpoint, login, code, params)

        if not data:
            print(f"Failed to get authenticated request response for user {login}")
        else:
            print(json.dumps(data, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
```

### Примечания:
- Все запросы выполняются к `http://localhost:5000` (если сервер запущен локально).
- Если сервер работает на другом хосте/порту — замените `localhost:5000` на актуальный адрес.
- Ответы приходят в формате **JSON**, их можно сохранить в файлы и использовать для построения графиков:
  ```bash
  curl -X GET "http://localhost:5000/api/v1/timeline?login=analyst_ts&code=XyZ67iOp89Ij&days=30" > ts_timeline.json
  ```
- Для удобства можно добавить заголовок `Content-Type: application/json` (не обязателен для GET):
  ```bash
  curl -H "Content-Type: application/json" -X GET "http://localhost:5000/api/v1/profile?login=analyst_ts&code=XyZ67iOp89Ij"
  ```

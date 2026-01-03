# amochka

Официальная документация API amocrm - https://www.amocrm.ru/developers/content/crm_platform/api-reference

**amochka** — библиотека для работы с API amoCRM на Python. Она поддерживает:
- Получение данных сделок с вложенными сущностями (контакты, компании, теги, и т.д.)
- Редактирование сделок, включая обновление стандартных и кастомных полей
- Поддержку нескольких amoCRM-аккаунтов с персистентным кэшированием кастомных полей для каждого аккаунта отдельно
- Ограничение запросов (7 запросов в секунду) с использованием декораторов из библиотеки `ratelimit`
- **Полнофункциональный ETL модуль** для синхронизации данных amoCRM в PostgreSQL

## Возможности

### API клиент

- `get_deal_by_id(deal_id)` — получение детальной информации по сделке
- `get_pipelines()` — список воронок и статусов
- `fetch_updated_leads_raw(pipeline_id, updated_from, ...)` — выгрузка необработанных сделок за период

### ETL модуль

- **Extractors**: извлечение данных из amoCRM (сделки, контакты, события, примечания)
- **Transformers**: преобразование в табличный формат для БД
- **Loaders**: загрузка в PostgreSQL с UPSERT логикой и сохранением внутренних ID
- **Migrations**: автоматическое создание таблиц и схем
- **Incremental sync**: инкрементальная синхронизация по updated_at
- Интеграция с **Apache Airflow** для автоматизации ETL процессов

## Требования к окружению

Python 3.6 или новее.

## Установка

```bash
pip install amochka
```

Для использования ETL модуля установите дополнительные зависимости:

```bash
pip install amochka psycopg2-binary python-dotenv
```

## Кэширование кастомных полей

Для уменьшения количества запросов к API кастомные поля кэшируются персистентно. Если параметр cache_file не указан, имя файла кэша генерируется автоматически на основе домена amoCRM-аккаунта. Вы можете обновлять кэш принудительно, передавая параметр force_update=True в метод get_custom_fields_mapping() или настроить время жизни кэша (по умолчанию — 24 часа).

## Примеры использования

### Быстрый старт: выгрузка обновленных сделок

```python
from datetime import datetime, timedelta
from amochka import AmoCRMClient, CacheConfig

client = AmoCRMClient(
    base_url="https://example.amocrm.ru",
    token_file="token.json",
    cache_config=CacheConfig.disabled(),
    disable_logging=True
)

three_hours_ago = datetime.utcnow() - timedelta(hours=3)
leads = client.fetch_updated_leads_raw(
    pipeline_id=123456,
    updated_from=three_hours_ago,
    save_to_file="leads.json",
    include_contacts=True
)
```

### ETL: синхронизация в PostgreSQL

```python
from etl.config import DatabaseConfig, AmoCRMAccount
from etl.extractors import AmoCRMExtractor
from etl.loaders import PostgresLoader
from etl.run_etl import sync_leads_with_contacts
from datetime import datetime, timezone

# Настройка БД
db_config = DatabaseConfig(
    host="localhost",
    port=5432,
    dbname="amocrm",
    user="postgres",
    password="password",
    schema="public"
)

# Настройка amoCRM аккаунта
account = AmoCRMAccount(
    id=1,
    name="main",
    base_url="https://example.amocrm.ru",
    token_path="token.json",
    mybi_account_id=1,
    pipeline_ids=[123456]
)

# ETL процесс
loader = PostgresLoader(db_config)
extractor = AmoCRMExtractor(account)

result = sync_leads_with_contacts(
    extractor=extractor,
    loader=loader,
    mybi_account_id=1,
    updated_from=datetime(2025, 1, 1, tzinfo=timezone.utc),
    updated_to=datetime.now(timezone.utc),
    pipeline_ids=[123456]
)

print(f"Загружено сделок: {result['leads_count']}")
print(f"Загружено контактов: {result['contacts_count']}")
```

### Пример структуры данных

```json
[
  {
    "id": 12345678,
    "name": "Сделка: Заявка от клиента",
    "custom_fields_values": [
      {
        "field_name": "utm_source",
        "values": [{"value": "google"}]
      }
    ],
    "_embedded": {
      "tags": [
        {"id": 123, "name": "Приоритетный клиент"}
      ]
    }
  }
]
```

## Интеграция с Apache Airflow

Модуль ETL разработан для использования в Airflow DAG. Пример минимального DAG:

```python
from airflow.decorators import dag, task
from etl.config import DatabaseConfig, AmoCRMAccount
from etl.run_etl import sync_leads_with_contacts

@dag(schedule_interval=None)
def amocrm_sync():
    @task
    def sync_data():
        db_config = DatabaseConfig.from_env()
        account = AmoCRMAccount.from_env()
        # ... ETL процесс

amocrm_sync()
```

## Тесты

Запустить тесты можно командой:

```bash
pytest -q
```

Тесты проверяют основную функциональность API клиента и помогают убедиться, что изменения в коде не ломают работу библиотеки.

## Лицензия

MIT

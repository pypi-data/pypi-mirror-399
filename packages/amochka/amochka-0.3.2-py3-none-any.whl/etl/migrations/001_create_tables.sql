-- Миграция: создание таблиц для ETL amoCRM
-- Структура ПОЛНОСТЬЮ совместима с mybi.ru для работы с существующими dbt-моделями
-- Схема: public (как в mybi)
-- ВАЖНО: Все типы данных соответствуют реальной структуре mybi

-- ============================================================================
-- СПРАВОЧНИКИ
-- ============================================================================

-- Справочник дат (точная копия general_dates в mybi)
CREATE TABLE IF NOT EXISTS general_dates (
    id SERIAL PRIMARY KEY,
    full_date TIMESTAMP NOT NULL UNIQUE,
    year INTEGER,
    quarter INTEGER,
    quarter_label VARCHAR,
    month INTEGER,
    month_label VARCHAR,
    week INTEGER,
    weekday INTEGER,
    weekday_label VARCHAR,
    day INTEGER,
    hour INTEGER,
    minute INTEGER,
    date_hash VARCHAR,
    simple_date DATE,
    time_zone INTEGER                   -- Добавлено как в mybi
);

CREATE INDEX IF NOT EXISTS idx_general_dates_full_date ON general_dates(full_date);
CREATE INDEX IF NOT EXISTS idx_general_dates_simple_date ON general_dates(simple_date);

-- Воронки
CREATE TABLE IF NOT EXISTS amocrm_pipelines (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL,
    pipeline_id INTEGER NOT NULL,
    name VARCHAR,
    sort INTEGER,
    is_main BOOLEAN DEFAULT FALSE,
    is_unsorted_on BOOLEAN DEFAULT FALSE,
    is_archive BOOLEAN DEFAULT FALSE,
    UNIQUE (account_id, pipeline_id)
);

-- Статусы этапов продаж
CREATE TABLE IF NOT EXISTS amocrm_statuses (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL,
    pipeline_id INTEGER NOT NULL,
    status_id INTEGER NOT NULL,
    name VARCHAR,
    color VARCHAR,
    sort INTEGER,
    is_editable BOOLEAN DEFAULT TRUE,
    type INTEGER DEFAULT 0,
    UNIQUE (account_id, pipeline_id, status_id)
);

-- Пользователи
CREATE TABLE IF NOT EXISTS amocrm_users (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    login VARCHAR,
    name VARCHAR,
    phone VARCHAR,
    email VARCHAR,
    group_name VARCHAR,
    group_id INTEGER,
    role_id INTEGER,
    role_name VARCHAR,
    is_admin BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    is_free BOOLEAN DEFAULT FALSE,
    mail_access BOOLEAN DEFAULT FALSE,
    catalog_access BOOLEAN DEFAULT FALSE,
    UNIQUE (account_id, user_id)
);

-- ============================================================================
-- ОСНОВНЫЕ ТАБЛИЦЫ ИЗМЕРЕНИЙ
-- ============================================================================

-- Сделки (leads) - точная копия структуры mybi
CREATE TABLE IF NOT EXISTS amocrm_leads (
    id SERIAL PRIMARY KEY,              -- Внутренний ID (автоинкремент)
    account_id INTEGER NOT NULL,
    lead_id INTEGER NOT NULL,           -- ID сделки из amoCRM
    name VARCHAR,
    pipeline VARCHAR,                   -- Название воронки (денормализовано)
    pipeline_id INTEGER,
    status VARCHAR,                     -- Название статуса (денормализовано)
    status_id INTEGER,
    status_order INTEGER,               -- Очередность статуса
    request_id VARCHAR,                 -- ID заявки (для неразобранного)
    loss_reason VARCHAR,                -- Причина отказа (денормализовано)
    loss_reason_id INTEGER,
    is_deleted BOOLEAN DEFAULT FALSE,
    UNIQUE (account_id, lead_id)
);

CREATE INDEX IF NOT EXISTS idx_amocrm_leads_account_pipeline ON amocrm_leads(account_id, pipeline_id);
CREATE INDEX IF NOT EXISTS idx_amocrm_leads_status ON amocrm_leads(status_id);

-- Атрибуты сделок (custom fields)
-- ВАЖНО: leads_id ссылается на amocrm_leads.id (внутренний), НЕ на lead_id!
CREATE TABLE IF NOT EXISTS amocrm_leads_attributes (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL,
    leads_id INTEGER NOT NULL,          -- FK на amocrm_leads.id (внутренний!)
    attribute_id VARCHAR NOT NULL,      -- field_id из amoCRM (строка)
    name VARCHAR NOT NULL,              -- field_name
    value TEXT
);

CREATE INDEX IF NOT EXISTS idx_amocrm_leads_attributes_leads ON amocrm_leads_attributes(leads_id, account_id);
CREATE INDEX IF NOT EXISTS idx_amocrm_leads_attributes_attr ON amocrm_leads_attributes(attribute_id);
CREATE INDEX IF NOT EXISTS idx_amocrm_leads_attributes_name ON amocrm_leads_attributes(name);

-- Теги сделок
CREATE TABLE IF NOT EXISTS amocrm_leads_tags (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL,
    leads_id INTEGER NOT NULL,          -- FK на amocrm_leads.id (внутренний!)
    tag_id INTEGER NOT NULL,
    name VARCHAR NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_amocrm_leads_tags_leads ON amocrm_leads_tags(leads_id, account_id);

-- События сделок (история изменений)
CREATE TABLE IF NOT EXISTS amocrm_leads_events (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL,
    leads_id INTEGER NOT NULL,          -- FK на amocrm_leads.id (внутренний!)
    event_id VARCHAR NOT NULL,          -- ID события из amoCRM (строка)
    type VARCHAR NOT NULL,              -- Тип события
    created_by INTEGER,                 -- Кто создал событие
    created_at TIMESTAMP,               -- Когда создано (без timezone как в mybi)
    value_after TEXT,                   -- JSON состояния после
    value_before TEXT,                  -- JSON состояния до
    UNIQUE (account_id, event_id)
);

CREATE INDEX IF NOT EXISTS idx_amocrm_leads_events_leads ON amocrm_leads_events(leads_id, account_id);
CREATE INDEX IF NOT EXISTS idx_amocrm_leads_events_type ON amocrm_leads_events(type);
CREATE INDEX IF NOT EXISTS idx_amocrm_leads_events_created ON amocrm_leads_events(created_at);

-- Примечания сделок
CREATE TABLE IF NOT EXISTS amocrm_leads_notes (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL,
    leads_id INTEGER NOT NULL,          -- FK на amocrm_leads.id (внутренний!)
    creator_id INTEGER,
    responsible_id INTEGER,
    note_id INTEGER NOT NULL,
    note_type VARCHAR,
    note_type_id INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    text TEXT,
    params TEXT,                        -- JSON дополнительных параметров
    UNIQUE (account_id, note_id)
);

CREATE INDEX IF NOT EXISTS idx_amocrm_leads_notes_leads ON amocrm_leads_notes(leads_id, account_id);

-- Связь сделок с контактами
CREATE TABLE IF NOT EXISTS amocrm_leads_contacts (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL,
    leads_id INTEGER NOT NULL,          -- FK на amocrm_leads.id (внутренний!)
    contacts_id INTEGER NOT NULL,       -- FK на amocrm_contacts.id (внутренний!)
    main BOOLEAN DEFAULT FALSE          -- Основной контакт
);

CREATE INDEX IF NOT EXISTS idx_amocrm_leads_contacts_leads ON amocrm_leads_contacts(leads_id, account_id);
CREATE INDEX IF NOT EXISTS idx_amocrm_leads_contacts_contacts ON amocrm_leads_contacts(contacts_id, account_id);

-- ============================================================================
-- КОНТАКТЫ
-- ============================================================================

-- Контакты (точная копия структуры mybi)
CREATE TABLE IF NOT EXISTS amocrm_contacts (
    id SERIAL PRIMARY KEY,              -- Внутренний ID (автоинкремент)
    account_id INTEGER NOT NULL,
    contact_id INTEGER NOT NULL,        -- ID контакта из amoCRM
    name VARCHAR,
    company VARCHAR,
    post VARCHAR,                       -- Должность
    phone VARCHAR,                      -- Телефон(ы)
    email VARCHAR,                      -- Email
    request_id VARCHAR,
    is_deleted BOOLEAN DEFAULT FALSE,
    first_name VARCHAR,
    last_name VARCHAR,
    UNIQUE (account_id, contact_id)
);

CREATE INDEX IF NOT EXISTS idx_amocrm_contacts_account ON amocrm_contacts(account_id);
CREATE INDEX IF NOT EXISTS idx_amocrm_contacts_phone ON amocrm_contacts(phone);

-- Атрибуты контактов
CREATE TABLE IF NOT EXISTS amocrm_contacts_attributes (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL,
    contacts_id INTEGER NOT NULL,       -- FK на amocrm_contacts.id (внутренний!)
    attribute_id VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    value TEXT
);

CREATE INDEX IF NOT EXISTS idx_amocrm_contacts_attributes_contacts ON amocrm_contacts_attributes(contacts_id, account_id);

-- ============================================================================
-- ТАБЛИЦЫ ФАКТОВ
-- ============================================================================

-- Факты по сделкам (точная копия структуры mybi)
CREATE TABLE IF NOT EXISTS amocrm_leads_facts (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL,
    clientids_id INTEGER,               -- ID клиента
    traffic_id INTEGER,                 -- ID источника трафика
    users_id INTEGER,                   -- Ответственный (FK на amocrm_users.id)
    leads_id INTEGER NOT NULL,          -- FK на amocrm_leads.id (внутренний!)
    contacts_id INTEGER,                -- FK на amocrm_contacts.id (внутренний!)
    companies_id INTEGER,               -- Компания
    unsorteds_id INTEGER,               -- ID неразобранного
    created_id INTEGER,                 -- FK на general_dates.id
    closed_id INTEGER,                  -- FK на general_dates.id
    price NUMERIC,                      -- Сумма сделки (NUMERIC как в mybi)
    created_date TIMESTAMP,             -- Дата создания
    modified_date TIMESTAMP,            -- Дата последнего изменения
    labor_cost NUMERIC,                 -- Стоимость труда
    score INTEGER,                      -- Скоринг
    UNIQUE (account_id, leads_id)
);

CREATE INDEX IF NOT EXISTS idx_amocrm_leads_facts_leads ON amocrm_leads_facts(leads_id, account_id);
CREATE INDEX IF NOT EXISTS idx_amocrm_leads_facts_contacts ON amocrm_leads_facts(contacts_id);
CREATE INDEX IF NOT EXISTS idx_amocrm_leads_facts_created ON amocrm_leads_facts(created_id);

-- Факты по контактам
CREATE TABLE IF NOT EXISTS amocrm_contacts_facts (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL,
    contacts_id INTEGER NOT NULL,       -- FK на amocrm_contacts.id (внутренний!)
    companies_id INTEGER,
    users_id INTEGER,                   -- Ответственный
    registered_id INTEGER,              -- FK на general_dates.id
    created_date TIMESTAMP,
    modified_date TIMESTAMP,
    UNIQUE (account_id, contacts_id)
);

-- ============================================================================
-- ETL STATE (служебная таблица, не из mybi)
-- ============================================================================

CREATE TABLE IF NOT EXISTS etl_state (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR NOT NULL,       -- leads, contacts, events, notes, etc.
    account_id INTEGER NOT NULL,
    pipeline_id INTEGER,                -- NULL = все воронки
    last_updated_at TIMESTAMP,          -- Последний updated_at из данных
    last_run_at TIMESTAMP,              -- Время последнего запуска ETL
    records_loaded INTEGER DEFAULT 0,   -- Количество загруженных записей
    error_message TEXT                  -- Сообщение об ошибке (если была)
);

-- Уникальный индекс с COALESCE для etl_state
CREATE UNIQUE INDEX IF NOT EXISTS idx_etl_state_unique
ON etl_state (entity_type, account_id, COALESCE(pipeline_id, 0));

-- ============================================================================
-- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
-- ============================================================================

-- Функция для получения или создания ID даты в general_dates
-- Принимает TIMESTAMPTZ (timestamp with time zone)
CREATE OR REPLACE FUNCTION get_or_create_date_id(ts TIMESTAMPTZ)
RETURNS INTEGER AS $$
DECLARE
    date_id INTEGER;
    truncated_ts TIMESTAMP;
BEGIN
    IF ts IS NULL THEN
        RETURN NULL;
    END IF;

    -- Усекаем до минуты (как в mybi)
    truncated_ts := date_trunc('minute', ts);

    -- Пытаемся найти существующую запись
    SELECT id INTO date_id FROM general_dates WHERE full_date = truncated_ts;

    -- Если не нашли, создаём
    IF date_id IS NULL THEN
        INSERT INTO general_dates (
            full_date, year, quarter, quarter_label, month, month_label,
            week, weekday, weekday_label, day, hour, minute, simple_date, time_zone
        ) VALUES (
            truncated_ts,
            EXTRACT(YEAR FROM truncated_ts)::INTEGER,
            EXTRACT(QUARTER FROM truncated_ts)::INTEGER,
            'Q' || EXTRACT(QUARTER FROM truncated_ts)::TEXT,
            EXTRACT(MONTH FROM truncated_ts)::INTEGER,
            TO_CHAR(truncated_ts, 'Month'),
            EXTRACT(WEEK FROM truncated_ts)::INTEGER,
            EXTRACT(ISODOW FROM truncated_ts)::INTEGER,
            TO_CHAR(truncated_ts, 'Day'),
            EXTRACT(DAY FROM truncated_ts)::INTEGER,
            EXTRACT(HOUR FROM truncated_ts)::INTEGER,
            EXTRACT(MINUTE FROM truncated_ts)::INTEGER,
            truncated_ts::DATE,
            0  -- time_zone по умолчанию
        )
        ON CONFLICT (full_date) DO NOTHING
        RETURNING id INTO date_id;

        -- Если INSERT не вернул id (из-за ON CONFLICT), получаем его SELECT-ом
        IF date_id IS NULL THEN
            SELECT id INTO date_id FROM general_dates WHERE full_date = truncated_ts;
        END IF;
    END IF;

    RETURN date_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- КОММЕНТАРИИ
-- ============================================================================

COMMENT ON TABLE amocrm_leads IS 'Сделки из amoCRM. Структура идентична mybi.';
COMMENT ON TABLE amocrm_leads_attributes IS 'Кастомные поля сделок. leads_id = внутренний id из amocrm_leads.';
COMMENT ON TABLE amocrm_leads_events IS 'События сделок. leads_id = внутренний id из amocrm_leads.';
COMMENT ON TABLE amocrm_leads_facts IS 'Факты по сделкам. leads_id/contacts_id = внутренние id.';
COMMENT ON TABLE amocrm_contacts IS 'Контакты из amoCRM. Структура идентична mybi.';
COMMENT ON TABLE general_dates IS 'Справочник дат для join-ов по created_id/closed_id.';
COMMENT ON TABLE etl_state IS 'Состояние ETL для инкрементальной загрузки (служебная).';

COMMENT ON FUNCTION get_or_create_date_id IS 'Получает или создаёт запись в general_dates для timestamp.';

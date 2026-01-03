#!/usr/bin/env python3
"""
Главный скрипт ETL для выгрузки данных из amoCRM в PostgreSQL.

Использование:
    python -m etl.run_etl [--env .env] [--migrate] [--full] [--entities leads,contacts,events]

Примеры:
    # Инкрементальная выгрузка сделок
    python -m etl.run_etl

    # Запуск миграций + полная выгрузка
    python -m etl.run_etl --migrate --full

    # Только события за последние 24 часа
    python -m etl.run_etl --entities events --window 1440
"""

import argparse
import logging
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional, Set

from .config import AmoCRMAccount, ETLConfig, get_config
from .extractors import AmoCRMExtractor
from .loaders import PostgresLoader
from .transformers import (
    ContactTransformer,
    EventTransformer,
    LeadTransformer,
    NoteTransformer,
    PipelineTransformer,
    UserTransformer,
)

logger = logging.getLogger(__name__)


def setup_logging(level: str = "INFO") -> None:
    """Настраивает логирование."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def run_migrations(loader: PostgresLoader, migrations_dir: Path) -> None:
    """Выполняет SQL-миграции."""
    logger.info("Выполняем миграции из %s", migrations_dir)
    loader.run_migrations(migrations_dir)


def sync_pipelines_and_users(
    extractor: AmoCRMExtractor,
    loader: PostgresLoader,
    mybi_account_id: int,
) -> None:
    """Синхронизирует воронки, статусы и пользователей."""
    pipeline_transformer = PipelineTransformer(mybi_account_id)
    user_transformer = UserTransformer(mybi_account_id)

    with loader.connection() as conn:
        with conn.cursor() as cursor:
            # Воронки и статусы
            logger.info("Синхронизируем воронки и статусы")
            for pipeline in extractor.iter_pipelines():
                pipeline_record, statuses = pipeline_transformer.transform_pipeline(pipeline)
                loader.upsert_pipeline(cursor, pipeline_record)
                for status in statuses:
                    loader.upsert_status(cursor, status)

            # Пользователи
            logger.info("Синхронизируем пользователей")
            for user in extractor.iter_users():
                user_record = user_transformer.transform(user)
                loader.upsert_user(cursor, user_record)

            conn.commit()


def sync_leads_with_contacts(
    extractor: AmoCRMExtractor,
    loader: PostgresLoader,
    mybi_account_id: int,
    updated_from: Optional[datetime] = None,
    updated_to: Optional[datetime] = None,
    pipeline_ids: Optional[List[int]] = None,
    batch_size: int = 100,
) -> dict:
    """
    Синхронизирует сделки вместе с их контактами.

    Порядок:
    1. Выгружаем сделки из API и собираем ID контактов
    2. Загружаем недостающие контакты по их ID
    3. Загружаем сделки с корректным маппингом contacts_id

    Returns:
        dict с ключами: leads_count, contacts_count
    """
    contact_transformer = ContactTransformer(mybi_account_id)

    # Загружаем справочники для денормализации
    pipelines_map, statuses_map = extractor.load_pipelines_and_statuses()
    lead_transformer = LeadTransformer(mybi_account_id, pipelines_map, statuses_map)

    # 1. Собираем сделки и ID контактов из API
    leads_iter = extractor.iter_leads(
        updated_from=updated_from,
        updated_to=updated_to,
        pipeline_ids=pipeline_ids,
        include_contacts=True,
    )

    leads_list, contact_ids = extractor.collect_contact_ids_from_leads(leads_iter)

    if not leads_list:
        logger.info("Нет сделок для загрузки")
        return {"leads_count": 0, "contacts_count": 0}

    logger.info(
        "Найдено %d сделок, %d уникальных контактов",
        len(leads_list),
        len(contact_ids),
    )

    # 2. Загружаем недостающие контакты
    contacts_loaded = 0
    if contact_ids:
        with loader.connection() as conn:
            with conn.cursor() as cursor:
                # Проверяем какие контакты уже есть в БД
                existing_contacts = loader.build_contact_id_map(cursor, mybi_account_id)
                missing_contact_ids = contact_ids - set(existing_contacts.keys())

                if missing_contact_ids:
                    logger.info("Загружаем %d недостающих контактов", len(missing_contact_ids))

                    for contact in extractor.iter_contacts(contact_ids=list(missing_contact_ids)):
                        transformed = contact_transformer.transform(contact)
                        loader.load_transformed_contact(cursor, transformed)
                        contacts_loaded += 1

                        if contacts_loaded % batch_size == 0:
                            conn.commit()

                    conn.commit()
                    logger.info("Загружено %d контактов", contacts_loaded)

    # 3. Загружаем сделки
    leads_loaded = 0
    max_updated_at = updated_from or datetime.min.replace(tzinfo=timezone.utc)

    with loader.connection() as conn:
        with conn.cursor() as cursor:
            # Строим маппинги для внутренних ID (теперь включая новые контакты)
            user_id_map = loader.build_user_id_map(cursor, mybi_account_id)
            contact_id_map = loader.build_contact_id_map(cursor, mybi_account_id)
            logger.debug("Маппинги: users=%d, contacts=%d", len(user_id_map), len(contact_id_map))

            for i, lead in enumerate(leads_list):
                transformed = lead_transformer.transform(lead)
                loader.load_transformed_lead(cursor, transformed, user_id_map, contact_id_map)
                leads_loaded += 1

                # Отслеживаем максимальный updated_at
                lead_updated = lead.get("updated_at")
                if lead_updated:
                    lead_dt = datetime.fromtimestamp(lead_updated, tz=timezone.utc)
                    if lead_dt > max_updated_at:
                        max_updated_at = lead_dt

                if (i + 1) % batch_size == 0:
                    conn.commit()
                    logger.debug("Закоммичено %d сделок", i + 1)

            # Обновляем состояние ETL
            if leads_loaded > 0:
                loader.update_etl_state(
                    cursor,
                    entity_type="leads",
                    account_id=mybi_account_id,
                    last_updated_at=max_updated_at,
                    records_loaded=leads_loaded,
                    pipeline_id=pipeline_ids[0] if pipeline_ids and len(pipeline_ids) == 1 else None,
                )

            conn.commit()

    logger.info("Загружено %d сделок, %d контактов", leads_loaded, contacts_loaded)
    return {"leads_count": leads_loaded, "contacts_count": contacts_loaded}


def mark_deleted_leads(
    extractor: AmoCRMExtractor,
    loader: PostgresLoader,
    mybi_account_id: int,
    pipeline_ids: Optional[List[int]] = None,
) -> int:
    """
    Помечает удалённые сделки в БД (is_deleted = true).

    Выгружает список удалённых сделок из amoCRM (корзина) и обновляет
    соответствующие записи в БД.

    Returns:
        Количество помеченных сделок
    """
    # Выгружаем ID удалённых сделок из amoCRM
    deleted_lead_ids = []
    for lead in extractor.iter_leads(
        pipeline_ids=pipeline_ids,
        only_deleted=True,
    ):
        deleted_lead_ids.append(lead.get("id"))

    if not deleted_lead_ids:
        logger.info("Нет удалённых сделок для пометки")
        return 0

    logger.info("Найдено %d удалённых сделок в amoCRM", len(deleted_lead_ids))

    # Помечаем в БД
    marked_count = 0
    with loader.connection() as conn:
        with conn.cursor() as cursor:
            for lead_id in deleted_lead_ids:
                cursor.execute(
                    """
                    UPDATE amocrm_leads
                    SET is_deleted = true
                    WHERE account_id = %s AND lead_id = %s AND is_deleted = false
                    """,
                    (mybi_account_id, lead_id),
                )
                if cursor.rowcount > 0:
                    marked_count += 1

            conn.commit()

    logger.info("Помечено как удалённые: %d сделок", marked_count)
    return marked_count


def sync_contacts(
    extractor: AmoCRMExtractor,
    loader: PostgresLoader,
    mybi_account_id: int,
    contact_ids: Optional[Set[int]] = None,
    updated_from: Optional[datetime] = None,
    updated_to: Optional[datetime] = None,
    batch_size: int = 100,
) -> int:
    """
    Синхронизирует контакты.

    Args:
        contact_ids: Фильтр - загружать только эти контакты (если указан)
        updated_from: Начало периода по updated_at
        updated_to: Конец периода по updated_at

    Логика:
        1. Загружаем все обновлённые контакты за период
        2. Если contact_ids указан - фильтруем, оставляя только нужные
        3. Обновляем etl_state

    Returns:
        Количество загруженных контактов
    """
    contact_transformer = ContactTransformer(mybi_account_id)

    # Загружаем все обновлённые контакты за период
    contacts_iter = extractor.iter_contacts(
        updated_from=updated_from,
        updated_to=updated_to,
    )

    loaded_count = 0
    skipped_count = 0
    max_updated_at = updated_from or datetime.min.replace(tzinfo=timezone.utc)

    with loader.connection() as conn:
        with conn.cursor() as cursor:
            for i, contact in enumerate(contacts_iter):
                contact_id = contact.get("id")

                # Фильтруем по contact_ids если указан
                if contact_ids and contact_id not in contact_ids:
                    skipped_count += 1
                    continue

                transformed = contact_transformer.transform(contact)
                loader.load_transformed_contact(cursor, transformed)
                loaded_count += 1

                # Отслеживаем максимальный updated_at
                contact_updated = contact.get("updated_at")
                if contact_updated:
                    contact_dt = datetime.fromtimestamp(contact_updated, tz=timezone.utc)
                    if contact_dt > max_updated_at:
                        max_updated_at = contact_dt

                if loaded_count % batch_size == 0:
                    conn.commit()
                    logger.debug("Закоммичено %d контактов", loaded_count)

            # Обновляем etl_state
            if max_updated_at > (updated_from or datetime.min.replace(tzinfo=timezone.utc)):
                loader.update_etl_state(
                    cursor,
                    entity_type="contacts",
                    account_id=mybi_account_id,
                    last_updated_at=max_updated_at,
                    records_loaded=loaded_count,
                )

            conn.commit()

    if contact_ids:
        logger.info("Загружено %d контактов (пропущено %d - не в воронках)", loaded_count, skipped_count)
    else:
        logger.info("Загружено %d контактов", loaded_count)
    return loaded_count


def sync_events(
    extractor: AmoCRMExtractor,
    loader: PostgresLoader,
    mybi_account_id: int,
    created_from: Optional[datetime] = None,
    created_to: Optional[datetime] = None,
    event_types: Optional[List[str]] = None,
    batch_size: int = 100,
) -> int:
    """
    Синхронизирует события.

    ВАЖНО: События должны загружаться ПОСЛЕ сделок, т.к. leads_id ссылается
    на внутренний id из amocrm_leads, а не на lead_id из amoCRM.

    Args:
        event_types: Фильтр по типам (по умолчанию lead_added, lead_status_changed)

    Returns:
        Количество загруженных событий
    """
    if event_types is None:
        event_types = ["lead_added", "lead_status_changed"]

    event_transformer = EventTransformer(mybi_account_id)

    events_iter = extractor.iter_events(
        entity_type="lead",
        event_types=event_types,
        created_from=created_from,
        created_to=created_to,
    )

    loaded_count = 0
    skipped_count = 0
    max_created_at = created_from or datetime.min.replace(tzinfo=timezone.utc)

    with loader.connection() as conn:
        with conn.cursor() as cursor:
            # Строим маппинг lead_id -> internal_id
            logger.info("Загружаем маппинг lead_id -> internal_id")
            lead_id_map = loader.build_lead_id_map(cursor, mybi_account_id)
            logger.info("Загружено %d сделок в маппинг", len(lead_id_map))

            for i, event in enumerate(events_iter):
                transformed = event_transformer.transform(event, entity_type="lead")

                # Подставляем внутренний leads_id вместо entity_id из amoCRM
                amo_lead_id = event.get("entity_id")
                internal_lead_id = lead_id_map.get(amo_lead_id)

                if internal_lead_id is None:
                    # Сделка не найдена в БД - пропускаем событие
                    skipped_count += 1
                    continue

                transformed.event["leads_id"] = internal_lead_id
                loader.upsert_event(cursor, transformed.event)
                loaded_count += 1

                # Отслеживаем максимальный created_at
                event_created = event.get("created_at")
                if event_created:
                    event_dt = datetime.fromtimestamp(event_created, tz=timezone.utc)
                    if event_dt > max_created_at:
                        max_created_at = event_dt

                if (i + 1) % batch_size == 0:
                    conn.commit()
                    logger.debug("Закоммичено %d событий", i + 1)

            if loaded_count > 0:
                loader.update_etl_state(
                    cursor,
                    entity_type="events",
                    account_id=mybi_account_id,
                    last_updated_at=max_created_at,
                    records_loaded=loaded_count,
                )

            conn.commit()

    logger.info("Загружено %d событий (пропущено %d - сделки не найдены)", loaded_count, skipped_count)
    return loaded_count


def sync_notes(
    extractor: AmoCRMExtractor,
    loader: PostgresLoader,
    mybi_account_id: int,
    updated_from: Optional[datetime] = None,
    updated_to: Optional[datetime] = None,
    note_type: Optional[str] = "common",
    batch_size: int = 100,
) -> int:
    """
    Синхронизирует примечания.

    ВАЖНО: Примечания должны загружаться ПОСЛЕ сделок, т.к. leads_id ссылается
    на внутренний id из amocrm_leads.
    """
    note_transformer = NoteTransformer(mybi_account_id)

    notes_iter = extractor.iter_notes(
        entity_type="lead",
        note_type=note_type,
        updated_from=updated_from,
        updated_to=updated_to,
    )

    loaded_count = 0
    skipped_count = 0

    with loader.connection() as conn:
        with conn.cursor() as cursor:
            # Строим маппинг lead_id -> internal_id
            lead_id_map = loader.build_lead_id_map(cursor, mybi_account_id)

            for i, note in enumerate(notes_iter):
                note_record = note_transformer.transform(note, entity_type="lead")

                # Подставляем внутренний leads_id
                amo_lead_id = note.get("entity_id")
                internal_lead_id = lead_id_map.get(amo_lead_id)

                if internal_lead_id is None:
                    skipped_count += 1
                    continue

                note_record["leads_id"] = internal_lead_id
                loader.upsert_note(cursor, note_record)
                loaded_count += 1

                if (i + 1) % batch_size == 0:
                    conn.commit()

            conn.commit()

    logger.info("Загружено %d примечаний (пропущено %d)", loaded_count, skipped_count)
    return loaded_count


def run_etl_for_account(
    account: AmoCRMAccount,
    loader: PostgresLoader,
    entities: List[str],
    window_minutes: int,
    full_sync: bool = False,
    batch_size: int = 100,
) -> dict:
    """
    Запускает ETL для одного аккаунта.

    Returns:
        Статистика по загруженным записям
    """
    mybi_id = account.mybi_account_id

    logger.info("=" * 60)
    logger.info("Начинаем ETL для аккаунта: %s (amo_id=%d, mybi_id=%d)", account.name, account.id, mybi_id)
    logger.info("=" * 60)

    extractor = AmoCRMExtractor(account)
    stats = {}

    # Определяем временное окно
    now = datetime.now(timezone.utc)

    if full_sync:
        updated_from = None
        updated_to = None
        logger.info("Режим полной синхронизации (без фильтра по дате)")
    else:
        updated_from = now - timedelta(minutes=window_minutes)
        updated_to = now
        logger.info("Инкрементальная синхронизация: %s - %s", updated_from.isoformat(), updated_to.isoformat())

    # Синхронизируем справочники (всегда)
    if "pipelines" in entities or "users" in entities or "leads" in entities or "contacts" in entities:
        sync_pipelines_and_users(extractor, loader, mybi_id)
        stats["pipelines_users"] = "synced"

    # Сделки + контакты (загружаем вместе для корректного маппинга contacts_id)
    if "leads" in entities:
        leads_updated_from = updated_from
        if not full_sync:
            with loader.connection() as conn:
                with conn.cursor() as cursor:
                    last_updated = loader.get_etl_state(cursor, "leads", mybi_id)
                    if last_updated:
                        leads_updated_from = last_updated
                        logger.info("Используем last_updated_at из БД: %s", leads_updated_from.isoformat())

        # Основная загрузка: сделки + их контакты
        result = sync_leads_with_contacts(
            extractor,
            loader,
            mybi_id,
            updated_from=leads_updated_from,
            updated_to=updated_to,
            pipeline_ids=account.pipeline_ids,
            batch_size=batch_size,
        )
        stats["leads"] = result["leads_count"]
        stats["contacts_from_leads"] = result["contacts_count"]

        # Помечаем удалённые сделки (is_deleted = true)
        deleted_count = mark_deleted_leads(
            extractor,
            loader,
            mybi_id,
            pipeline_ids=account.pipeline_ids,
        )
        stats["leads_marked_deleted"] = deleted_count

    # Обновлённые контакты (только те, у которых есть сделки в наших воронках)
    if "contacts" in entities or "leads" in entities:
        contacts_updated_from = updated_from
        if not full_sync:
            with loader.connection() as conn:
                with conn.cursor() as cursor:
                    last_updated = loader.get_etl_state(cursor, "contacts", mybi_id)
                    if last_updated:
                        contacts_updated_from = last_updated

        # Получаем contact_ids из сделок в наших воронках
        with loader.connection() as conn:
            with conn.cursor() as cursor:
                contact_ids_in_pipelines = loader.get_contact_ids_from_leads(
                    cursor, mybi_id, account.pipeline_ids
                )

        if contact_ids_in_pipelines:
            stats["contacts_updated"] = sync_contacts(
                extractor,
                loader,
                mybi_id,
                contact_ids=contact_ids_in_pipelines,  # Только контакты из наших воронок
                updated_from=contacts_updated_from,
                updated_to=updated_to,
                batch_size=batch_size,
            )
        else:
            stats["contacts_updated"] = 0

    # События
    if "events" in entities:
        if not full_sync:
            with loader.connection() as conn:
                with conn.cursor() as cursor:
                    last_updated = loader.get_etl_state(cursor, "events", mybi_id)
                    if last_updated:
                        updated_from = last_updated

        stats["events"] = sync_events(
            extractor,
            loader,
            mybi_id,
            created_from=updated_from,
            created_to=updated_to,
            batch_size=batch_size,
        )

    # Примечания
    if "notes" in entities:
        stats["notes"] = sync_notes(
            extractor,
            loader,
            mybi_id,
            updated_from=updated_from,
            updated_to=updated_to,
            batch_size=batch_size,
        )

    logger.info("ETL для аккаунта %s завершён. Статистика: %s", account.name, stats)
    return stats


def main():
    """Главная функция."""
    parser = argparse.ArgumentParser(description="ETL amoCRM → PostgreSQL")
    parser.add_argument("--env", type=str, help="Путь к .env файлу")
    parser.add_argument("--migrate", action="store_true", help="Выполнить SQL-миграции")
    parser.add_argument("--full", action="store_true", help="Полная синхронизация (без инкремента)")
    parser.add_argument(
        "--entities",
        type=str,
        default="leads,contacts,events",
        help="Сущности для синхронизации (через запятую): leads,contacts,events,notes,pipelines,users",
    )
    parser.add_argument("--window", type=int, help="Окно выгрузки в минутах (перезаписывает конфиг)")
    parser.add_argument("--account", type=str, help="Имя конкретного аккаунта (по умолчанию все)")
    parser.add_argument("--log-level", type=str, default="INFO", help="Уровень логирования")

    args = parser.parse_args()

    # Настраиваем логирование
    setup_logging(args.log_level)

    # Загружаем конфигурацию
    env_path = Path(args.env) if args.env else None
    config = get_config(env_path)

    if args.window:
        config.window_minutes = args.window

    entities = [e.strip() for e in args.entities.split(",")]
    logger.info("Сущности для синхронизации: %s", entities)

    # Инициализируем loader
    loader = PostgresLoader(config.database)

    # Выполняем миграции если нужно
    if args.migrate:
        migrations_dir = Path(__file__).parent / "migrations"
        run_migrations(loader, migrations_dir)

    # Фильтруем аккаунты
    accounts = config.accounts
    if args.account:
        accounts = [a for a in accounts if a.name == args.account]
        if not accounts:
            logger.error("Аккаунт '%s' не найден в конфигурации", args.account)
            sys.exit(1)

    if not accounts:
        logger.error("Нет аккаунтов для обработки. Проверьте конфигурацию.")
        sys.exit(1)

    # Запускаем ETL для каждого аккаунта
    all_stats = {}
    for account in accounts:
        try:
            stats = run_etl_for_account(
                account,
                loader,
                entities,
                config.window_minutes,
                full_sync=args.full,
                batch_size=config.batch_size,
            )
            all_stats[account.name] = stats
        except Exception as e:
            logger.exception("Ошибка при обработке аккаунта %s: %s", account.name, e)
            all_stats[account.name] = {"error": str(e)}

    # Итоговая статистика
    logger.info("=" * 60)
    logger.info("ETL завершён. Итоговая статистика:")
    for account_name, stats in all_stats.items():
        logger.info("  %s: %s", account_name, stats)
    logger.info("=" * 60)


if __name__ == "__main__":
    main()

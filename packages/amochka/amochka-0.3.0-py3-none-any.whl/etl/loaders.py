"""
Загрузка данных в PostgreSQL.

Реализует UPSERT-логику для инкрементальной загрузки.
"""

import json
import logging
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Set, Tuple

from .config import DatabaseConfig
from .transformers import TransformedContact, TransformedEvent, TransformedLead

logger = logging.getLogger(__name__)


class PostgresLoader:
    """Загрузчик данных в PostgreSQL."""

    def __init__(self, config: DatabaseConfig):
        """
        Инициализирует загрузчик.

        Args:
            config: Конфигурация подключения к БД
        """
        self.config = config
        self._connection = None
        self._psycopg = None
        self._sql = None
        self._json_module = None

    def _ensure_imports(self):
        """Ленивый импорт psycopg."""
        if self._psycopg is None:
            try:
                import psycopg
                from psycopg import sql
                from psycopg.types import json as psycopg_json

                self._psycopg = psycopg
                self._sql = sql
                self._json_module = psycopg_json
            except ImportError:
                raise ImportError("psycopg не установлен. Установите: pip install psycopg[binary]")

    @contextmanager
    def connection(self):
        """Context manager для подключения к БД."""
        self._ensure_imports()
        conn = self._psycopg.connect(**self.config.connection_kwargs())
        try:
            # Устанавливаем search_path на нужную схему
            with conn.cursor() as cursor:
                cursor.execute(
                    self._sql.SQL("SET search_path TO {}").format(
                        self._sql.Identifier(self.config.schema)
                    )
                )
            yield conn
        finally:
            conn.close()

    def run_migrations(self, migrations_dir: Path) -> None:
        """
        Выполняет SQL-миграции из указанной директории.

        Args:
            migrations_dir: Путь к директории с .sql файлами
        """
        self._ensure_imports()

        migration_files = sorted(migrations_dir.glob("*.sql"))
        if not migration_files:
            logger.warning("Файлы миграций не найдены в %s", migrations_dir)
            return

        # Сначала создаём схему если её нет (без search_path)
        conn = self._psycopg.connect(**self.config.connection_kwargs())
        try:
            with conn.cursor() as cursor:
                # Создаём схему
                cursor.execute(
                    self._sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(
                        self._sql.Identifier(self.config.schema)
                    )
                )
                logger.info("Схема '%s' готова", self.config.schema)
            conn.commit()
        finally:
            conn.close()

        # Теперь выполняем миграции в нужной схеме
        with self.connection() as conn:
            with conn.cursor() as cursor:
                for migration_file in migration_files:
                    logger.info("Выполняем миграцию: %s", migration_file.name)
                    sql_content = migration_file.read_text(encoding="utf-8")
                    cursor.execute(sql_content)
                conn.commit()
                logger.info("Миграции выполнены успешно")

    def _get_or_create_date_id(self, cursor, ts: Optional[datetime]) -> Optional[int]:
        """
        Получает или создаёт ID даты в general_dates.

        Args:
            cursor: Курсор БД
            ts: Timestamp для поиска/создания

        Returns:
            ID записи в general_dates или None
        """
        if ts is None:
            return None

        cursor.execute("SELECT get_or_create_date_id(%s)", (ts,))
        result = cursor.fetchone()
        return result[0] if result else None

    def upsert_lead(self, cursor, lead_data: Dict[str, Any]) -> int:
        """
        Вставляет или обновляет сделку.

        Returns:
            ID записи в amocrm_leads (внутренний автоинкремент)
        """
        cursor.execute(
            """
            INSERT INTO amocrm_leads (
                account_id, lead_id, name, pipeline, pipeline_id, status, status_id,
                status_order, request_id, loss_reason, loss_reason_id, is_deleted
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (account_id, lead_id) DO UPDATE SET
                name = EXCLUDED.name,
                pipeline = EXCLUDED.pipeline,
                pipeline_id = EXCLUDED.pipeline_id,
                status = EXCLUDED.status,
                status_id = EXCLUDED.status_id,
                status_order = EXCLUDED.status_order,
                request_id = EXCLUDED.request_id,
                loss_reason = EXCLUDED.loss_reason,
                loss_reason_id = EXCLUDED.loss_reason_id,
                is_deleted = EXCLUDED.is_deleted
            RETURNING id
            """,
            (
                lead_data["account_id"],
                lead_data["lead_id"],
                lead_data.get("name"),
                lead_data.get("pipeline"),
                lead_data.get("pipeline_id"),
                lead_data.get("status"),
                lead_data.get("status_id"),
                lead_data.get("status_order"),
                lead_data.get("request_id"),
                lead_data.get("loss_reason"),
                lead_data.get("loss_reason_id"),
                lead_data.get("is_deleted", False),
            ),
        )
        result = cursor.fetchone()
        return result[0] if result else None

    def upsert_lead_facts(self, cursor, facts_data: Dict[str, Any], leads_id: int) -> int:
        """Вставляет или обновляет факты по сделке."""
        # Получаем ID дат
        created_id = self._get_or_create_date_id(cursor, facts_data.get("created_date"))
        closed_at_raw = facts_data.get("_closed_at_raw")
        closed_id = None
        if closed_at_raw:
            from .transformers import _timestamp_to_datetime
            closed_id = self._get_or_create_date_id(cursor, _timestamp_to_datetime(closed_at_raw))

        cursor.execute(
            """
            INSERT INTO amocrm_leads_facts (
                account_id, leads_id, contacts_id, companies_id, users_id,
                created_id, closed_id, price, labor_cost, score,
                created_date, modified_date
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (account_id, leads_id) DO UPDATE SET
                contacts_id = EXCLUDED.contacts_id,
                companies_id = EXCLUDED.companies_id,
                users_id = EXCLUDED.users_id,
                created_id = EXCLUDED.created_id,
                closed_id = EXCLUDED.closed_id,
                price = EXCLUDED.price,
                labor_cost = EXCLUDED.labor_cost,
                score = EXCLUDED.score,
                created_date = EXCLUDED.created_date,
                modified_date = EXCLUDED.modified_date
            RETURNING id
            """,
            (
                facts_data["account_id"],
                leads_id,
                facts_data.get("contacts_id"),
                facts_data.get("companies_id"),
                facts_data.get("users_id"),
                created_id,
                closed_id,
                facts_data.get("price"),
                facts_data.get("labor_cost"),
                facts_data.get("score"),
                facts_data.get("created_date"),
                facts_data.get("modified_date"),
            ),
        )
        result = cursor.fetchone()
        return result[0] if result else None

    def upsert_lead_attributes(self, cursor, attributes: List[Dict[str, Any]], leads_id: int) -> int:
        """
        Вставляет атрибуты сделки.

        Удаляет старые атрибуты и вставляет новые (полная замена).
        """
        if not attributes:
            return 0

        account_id = attributes[0]["account_id"]

        # Удаляем старые атрибуты
        cursor.execute(
            "DELETE FROM amocrm_leads_attributes WHERE account_id = %s AND leads_id = %s",
            (account_id, leads_id),
        )

        # Вставляем новые
        inserted = 0
        for attr in attributes:
            cursor.execute(
                """
                INSERT INTO amocrm_leads_attributes (account_id, leads_id, attribute_id, name, value)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (account_id, leads_id, attr["attribute_id"], attr["name"], attr.get("value")),
            )
            inserted += 1

        return inserted

    def upsert_lead_tags(self, cursor, tags: List[Dict[str, Any]], leads_id: int) -> int:
        """Вставляет теги сделки (полная замена)."""
        if not tags:
            return 0

        account_id = tags[0]["account_id"]

        # Удаляем старые теги
        cursor.execute(
            "DELETE FROM amocrm_leads_tags WHERE account_id = %s AND leads_id = %s",
            (account_id, leads_id),
        )

        # Вставляем новые
        inserted = 0
        for tag in tags:
            cursor.execute(
                """
                INSERT INTO amocrm_leads_tags (account_id, leads_id, tag_id, name)
                VALUES (%s, %s, %s, %s)
                """,
                (account_id, leads_id, tag["tag_id"], tag["name"]),
            )
            inserted += 1

        return inserted

    def upsert_lead_contacts(self, cursor, contacts: List[Dict[str, Any]], leads_id: int) -> int:
        """Вставляет связи сделки с контактами (полная замена)."""
        if not contacts:
            return 0

        account_id = contacts[0]["account_id"]

        # Удаляем старые связи
        cursor.execute(
            "DELETE FROM amocrm_leads_contacts WHERE account_id = %s AND leads_id = %s",
            (account_id, leads_id),
        )

        # Вставляем новые
        inserted = 0
        for contact in contacts:
            cursor.execute(
                """
                INSERT INTO amocrm_leads_contacts (account_id, leads_id, contacts_id, main)
                VALUES (%s, %s, %s, %s)
                """,
                (account_id, leads_id, contact["contacts_id"], contact.get("main", False)),
            )
            inserted += 1

        return inserted

    def load_transformed_lead(
        self,
        cursor,
        transformed: TransformedLead,
        user_id_map: Optional[Dict[int, int]] = None,
        contact_id_map: Optional[Dict[int, int]] = None,
    ) -> int:
        """
        Загружает полностью трансформированную сделку.

        Args:
            cursor: Курсор БД
            transformed: Трансформированная сделка
            user_id_map: Маппинг {amo_user_id -> internal_id} для users_id
            contact_id_map: Маппинг {amo_contact_id -> internal_id} для contacts_id

        Returns:
            ID записи в amocrm_leads
        """
        # 1. Сначала upsert основной записи leads
        leads_id = self.upsert_lead(cursor, transformed.lead)

        # 2. Обновляем leads_id в связанных данных и загружаем
        transformed.lead_facts["leads_id"] = leads_id

        # Преобразуем users_id из amoCRM ID во внутренний ID
        if user_id_map:
            amo_user_id = transformed.lead_facts.get("users_id")
            if amo_user_id is not None:
                internal_user_id = user_id_map.get(amo_user_id)
                transformed.lead_facts["users_id"] = internal_user_id

        # Преобразуем contacts_id из amoCRM ID во внутренний ID
        if contact_id_map:
            amo_contact_id = transformed.lead_facts.get("contacts_id")
            if amo_contact_id is not None:
                internal_contact_id = contact_id_map.get(amo_contact_id)
                transformed.lead_facts["contacts_id"] = internal_contact_id

        self.upsert_lead_facts(cursor, transformed.lead_facts, leads_id)

        # 3. Атрибуты
        self.upsert_lead_attributes(cursor, transformed.attributes, leads_id)

        # 4. Теги
        self.upsert_lead_tags(cursor, transformed.tags, leads_id)

        # 5. Связи с контактами - преобразуем contacts_id и фильтруем ненайденные
        if transformed.contacts_links:
            valid_contacts_links = []
            for link in transformed.contacts_links:
                amo_contact_id = link.get("contacts_id")
                if amo_contact_id is not None:
                    if contact_id_map:
                        internal_id = contact_id_map.get(amo_contact_id)
                        if internal_id is not None:
                            link["contacts_id"] = internal_id
                            valid_contacts_links.append(link)
                        # Пропускаем если контакт не найден в маппинге
                    else:
                        # Без маппинга - используем как есть (amo_id)
                        valid_contacts_links.append(link)
            self.upsert_lead_contacts(cursor, valid_contacts_links, leads_id)
        else:
            self.upsert_lead_contacts(cursor, [], leads_id)

        return leads_id

    def upsert_contact(self, cursor, contact_data: Dict[str, Any]) -> int:
        """Вставляет или обновляет контакт."""
        cursor.execute(
            """
            INSERT INTO amocrm_contacts (
                account_id, contact_id, name, company, post, phone, email,
                request_id, is_deleted, first_name, last_name
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (account_id, contact_id) DO UPDATE SET
                name = EXCLUDED.name,
                company = EXCLUDED.company,
                post = EXCLUDED.post,
                phone = EXCLUDED.phone,
                email = EXCLUDED.email,
                request_id = EXCLUDED.request_id,
                is_deleted = EXCLUDED.is_deleted,
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name
            RETURNING id
            """,
            (
                contact_data["account_id"],
                contact_data["contact_id"],
                contact_data.get("name"),
                contact_data.get("company"),
                contact_data.get("post"),
                contact_data.get("phone"),
                contact_data.get("email"),
                contact_data.get("request_id"),
                contact_data.get("is_deleted", False),
                contact_data.get("first_name"),
                contact_data.get("last_name"),
            ),
        )
        result = cursor.fetchone()
        return result[0] if result else None

    def load_transformed_contact(self, cursor, transformed: TransformedContact) -> int:
        """Загружает полностью трансформированный контакт."""
        contacts_id = self.upsert_contact(cursor, transformed.contact)

        # Факты по контакту
        transformed.contact_facts["contacts_id"] = contacts_id
        registered_id = self._get_or_create_date_id(cursor, transformed.contact_facts.get("created_date"))

        cursor.execute(
            """
            INSERT INTO amocrm_contacts_facts (
                account_id, contacts_id, companies_id, users_id,
                registered_id, created_date, modified_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (account_id, contacts_id) DO UPDATE SET
                companies_id = EXCLUDED.companies_id,
                users_id = EXCLUDED.users_id,
                registered_id = EXCLUDED.registered_id,
                created_date = EXCLUDED.created_date,
                modified_date = EXCLUDED.modified_date
            """,
            (
                transformed.contact_facts["account_id"],
                contacts_id,
                transformed.contact_facts.get("companies_id"),
                transformed.contact_facts.get("users_id"),
                registered_id,
                transformed.contact_facts.get("created_date"),
                transformed.contact_facts.get("modified_date"),
            ),
        )

        # Атрибуты контакта
        if transformed.attributes:
            cursor.execute(
                "DELETE FROM amocrm_contacts_attributes WHERE account_id = %s AND contacts_id = %s",
                (transformed.contact["account_id"], contacts_id),
            )
            for attr in transformed.attributes:
                cursor.execute(
                    """
                    INSERT INTO amocrm_contacts_attributes (account_id, contacts_id, attribute_id, name, value)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        transformed.contact["account_id"],
                        contacts_id,
                        attr["attribute_id"],
                        attr["name"],
                        attr.get("value"),
                    ),
                )

        return contacts_id

    def upsert_event(self, cursor, event_data: Dict[str, Any]) -> int:
        """Вставляет или обновляет событие."""
        cursor.execute(
            """
            INSERT INTO amocrm_leads_events (
                account_id, leads_id, event_id, type, created_by,
                created_at, value_after, value_before
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (account_id, event_id) DO UPDATE SET
                leads_id = EXCLUDED.leads_id,
                type = EXCLUDED.type,
                created_by = EXCLUDED.created_by,
                created_at = EXCLUDED.created_at,
                value_after = EXCLUDED.value_after,
                value_before = EXCLUDED.value_before
            RETURNING id
            """,
            (
                event_data["account_id"],
                event_data.get("leads_id"),
                event_data["event_id"],
                event_data["type"],
                event_data.get("created_by"),
                event_data.get("created_at"),
                event_data.get("value_after"),
                event_data.get("value_before"),
            ),
        )
        result = cursor.fetchone()
        return result[0] if result else None

    def upsert_pipeline(self, cursor, pipeline_data: Dict[str, Any]) -> int:
        """Вставляет или обновляет воронку."""
        cursor.execute(
            """
            INSERT INTO amocrm_pipelines (
                account_id, pipeline_id, name, sort, is_main, is_unsorted_on, is_archive
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (account_id, pipeline_id) DO UPDATE SET
                name = EXCLUDED.name,
                sort = EXCLUDED.sort,
                is_main = EXCLUDED.is_main,
                is_unsorted_on = EXCLUDED.is_unsorted_on,
                is_archive = EXCLUDED.is_archive
            RETURNING id
            """,
            (
                pipeline_data["account_id"],
                pipeline_data["pipeline_id"],
                pipeline_data.get("name"),
                pipeline_data.get("sort"),
                pipeline_data.get("is_main", False),
                pipeline_data.get("is_unsorted_on", False),
                pipeline_data.get("is_archive", False),
            ),
        )
        result = cursor.fetchone()
        return result[0] if result else None

    def upsert_status(self, cursor, status_data: Dict[str, Any]) -> int:
        """Вставляет или обновляет статус."""
        cursor.execute(
            """
            INSERT INTO amocrm_statuses (
                account_id, pipeline_id, status_id, name, color, sort, is_editable, type
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (account_id, pipeline_id, status_id) DO UPDATE SET
                name = EXCLUDED.name,
                color = EXCLUDED.color,
                sort = EXCLUDED.sort,
                is_editable = EXCLUDED.is_editable,
                type = EXCLUDED.type
            RETURNING id
            """,
            (
                status_data["account_id"],
                status_data["pipeline_id"],
                status_data["status_id"],
                status_data.get("name"),
                status_data.get("color"),
                status_data.get("sort"),
                status_data.get("is_editable", True),
                status_data.get("type", 0),
            ),
        )
        result = cursor.fetchone()
        return result[0] if result else None

    def upsert_user(self, cursor, user_data: Dict[str, Any]) -> int:
        """Вставляет или обновляет пользователя."""
        cursor.execute(
            """
            INSERT INTO amocrm_users (
                account_id, user_id, login, name, phone, email,
                group_name, group_id, role_id, role_name,
                is_admin, is_active, is_free, mail_access, catalog_access
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (account_id, user_id) DO UPDATE SET
                login = EXCLUDED.login,
                name = EXCLUDED.name,
                phone = EXCLUDED.phone,
                email = EXCLUDED.email,
                group_name = EXCLUDED.group_name,
                group_id = EXCLUDED.group_id,
                role_id = EXCLUDED.role_id,
                role_name = EXCLUDED.role_name,
                is_admin = EXCLUDED.is_admin,
                is_active = EXCLUDED.is_active,
                is_free = EXCLUDED.is_free,
                mail_access = EXCLUDED.mail_access,
                catalog_access = EXCLUDED.catalog_access
            RETURNING id
            """,
            (
                user_data["account_id"],
                user_data["user_id"],
                user_data.get("login"),
                user_data.get("name"),
                user_data.get("phone"),
                user_data.get("email"),
                user_data.get("group_name"),
                user_data.get("group_id"),
                user_data.get("role_id"),
                user_data.get("role_name"),
                user_data.get("is_admin", False),
                user_data.get("is_active", True),
                user_data.get("is_free", False),
                user_data.get("mail_access", False),
                user_data.get("catalog_access", False),
            ),
        )
        result = cursor.fetchone()
        return result[0] if result else None

    def upsert_note(self, cursor, note_data: Dict[str, Any]) -> int:
        """Вставляет или обновляет примечание."""
        cursor.execute(
            """
            INSERT INTO amocrm_leads_notes (
                account_id, leads_id, creator_id, responsible_id,
                note_id, note_type, note_type_id, created_at, updated_at, text, params
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (account_id, note_id) DO UPDATE SET
                leads_id = EXCLUDED.leads_id,
                creator_id = EXCLUDED.creator_id,
                responsible_id = EXCLUDED.responsible_id,
                note_type = EXCLUDED.note_type,
                note_type_id = EXCLUDED.note_type_id,
                created_at = EXCLUDED.created_at,
                updated_at = EXCLUDED.updated_at,
                text = EXCLUDED.text,
                params = EXCLUDED.params
            RETURNING id
            """,
            (
                note_data["account_id"],
                note_data.get("leads_id"),
                note_data.get("creator_id"),
                note_data.get("responsible_id"),
                note_data["note_id"],
                note_data.get("note_type"),
                note_data.get("note_type_id"),
                note_data.get("created_at"),
                note_data.get("updated_at"),
                note_data.get("text"),
                note_data.get("params"),
            ),
        )
        result = cursor.fetchone()
        return result[0] if result else None

    # =========================================================================
    # Маппинг внешних ID на внутренние
    # =========================================================================

    def get_internal_lead_id(self, cursor, account_id: int, lead_id: int) -> Optional[int]:
        """
        Получает внутренний ID сделки по (account_id, lead_id).

        Args:
            account_id: mybi account_id
            lead_id: ID сделки из amoCRM

        Returns:
            Внутренний id из amocrm_leads или None
        """
        cursor.execute(
            "SELECT id FROM amocrm_leads WHERE account_id = %s AND lead_id = %s",
            (account_id, lead_id),
        )
        result = cursor.fetchone()
        return result[0] if result else None

    def get_internal_contact_id(self, cursor, account_id: int, contact_id: int) -> Optional[int]:
        """
        Получает внутренний ID контакта по (account_id, contact_id).

        Args:
            account_id: mybi account_id
            contact_id: ID контакта из amoCRM

        Returns:
            Внутренний id из amocrm_contacts или None
        """
        cursor.execute(
            "SELECT id FROM amocrm_contacts WHERE account_id = %s AND contact_id = %s",
            (account_id, contact_id),
        )
        result = cursor.fetchone()
        return result[0] if result else None

    def build_lead_id_map(self, cursor, account_id: int) -> Dict[int, int]:
        """
        Строит маппинг {lead_id -> internal_id} для аккаунта.

        Полезно для пакетной загрузки events/notes.

        Args:
            account_id: mybi account_id

        Returns:
            Dict[lead_id, internal_id]
        """
        cursor.execute(
            "SELECT lead_id, id FROM amocrm_leads WHERE account_id = %s",
            (account_id,),
        )
        return {row[0]: row[1] for row in cursor.fetchall()}

    def build_contact_id_map(self, cursor, account_id: int) -> Dict[int, int]:
        """
        Строит маппинг {contact_id -> internal_id} для аккаунта.

        Args:
            account_id: mybi account_id

        Returns:
            Dict[contact_id, internal_id]
        """
        cursor.execute(
            "SELECT contact_id, id FROM amocrm_contacts WHERE account_id = %s",
            (account_id,),
        )
        return {row[0]: row[1] for row in cursor.fetchall()}

    def get_contact_ids_from_leads(
        self, cursor, account_id: int, pipeline_ids: Optional[List[int]] = None
    ) -> Set[int]:
        """
        Получает contact_id из сделок в указанных воронках.

        Args:
            account_id: mybi account_id
            pipeline_ids: Список ID воронок (если None - все воронки)

        Returns:
            Set[contact_id] - amoCRM contact_ids из сделок
        """
        if pipeline_ids:
            cursor.execute(
                """
                SELECT DISTINCT c.contact_id
                FROM amocrm_leads_contacts lc
                JOIN amocrm_leads l ON lc.leads_id = l.id
                JOIN amocrm_contacts c ON lc.contacts_id = c.id
                WHERE l.account_id = %s AND l.pipeline_id = ANY(%s)
                """,
                (account_id, pipeline_ids),
            )
        else:
            cursor.execute(
                """
                SELECT DISTINCT c.contact_id
                FROM amocrm_leads_contacts lc
                JOIN amocrm_leads l ON lc.leads_id = l.id
                JOIN amocrm_contacts c ON lc.contacts_id = c.id
                WHERE l.account_id = %s
                """,
                (account_id,),
            )
        return {row[0] for row in cursor.fetchall()}

    def build_user_id_map(self, cursor, account_id: int) -> Dict[int, int]:
        """
        Строит маппинг {user_id -> internal_id} для аккаунта.

        Args:
            account_id: mybi account_id

        Returns:
            Dict[user_id, internal_id]
        """
        cursor.execute(
            "SELECT user_id, id FROM amocrm_users WHERE account_id = %s",
            (account_id,),
        )
        return {row[0]: row[1] for row in cursor.fetchall()}

    # =========================================================================
    # ETL State
    # =========================================================================

    def get_etl_state(
        self, cursor, entity_type: str, account_id: int, pipeline_id: Optional[int] = None
    ) -> Optional[datetime]:
        """Получает last_updated_at из etl_state."""
        cursor.execute(
            """
            SELECT last_updated_at FROM etl_state
            WHERE entity_type = %s AND account_id = %s AND COALESCE(pipeline_id, 0) = COALESCE(%s, 0)
            """,
            (entity_type, account_id, pipeline_id),
        )
        result = cursor.fetchone()
        return result[0] if result else None

    def update_etl_state(
        self,
        cursor,
        entity_type: str,
        account_id: int,
        last_updated_at: datetime,
        records_loaded: int,
        pipeline_id: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> None:
        """Обновляет состояние ETL."""
        cursor.execute(
            """
            INSERT INTO etl_state (entity_type, account_id, pipeline_id, last_updated_at, last_run_at, records_loaded, error_message)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (entity_type, account_id, COALESCE(pipeline_id, 0)) DO UPDATE SET
                last_updated_at = EXCLUDED.last_updated_at,
                last_run_at = EXCLUDED.last_run_at,
                records_loaded = etl_state.records_loaded + EXCLUDED.records_loaded,
                error_message = EXCLUDED.error_message
            """,
            (
                entity_type,
                account_id,
                pipeline_id,
                last_updated_at,
                datetime.now(timezone.utc),
                records_loaded,
                error_message,
            ),
        )

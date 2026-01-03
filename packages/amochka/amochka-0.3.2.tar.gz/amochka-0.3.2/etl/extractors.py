"""
Выгрузка данных из amoCRM через библиотеку amochka.

Обёртки для инкрементальной выгрузки с поддержкой фильтрации.
"""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional, Set, Tuple, Union

from .config import AmoCRMAccount

logger = logging.getLogger(__name__)


class AmoCRMExtractor:
    """Экстрактор данных из amoCRM."""

    def __init__(self, account: AmoCRMAccount, cache_lifetime_hours: int = 24):
        """
        Инициализирует экстрактор.

        Args:
            account: Конфигурация аккаунта amoCRM
            cache_lifetime_hours: Время жизни кэша custom_fields в часах
        """
        self.account = account
        self.cache_lifetime_hours = cache_lifetime_hours
        self._client = None
        self._pipelines_map: Dict[int, str] = {}
        self._statuses_map: Dict[int, Dict[str, Any]] = {}

    def _ensure_client(self):
        """Ленивая инициализация клиента amochka."""
        if self._client is None:
            try:
                from amochka import AmoCRMClient, CacheConfig
            except ImportError:
                raise ImportError("amochka не установлена. Установите: pip install amochka")

            cache_config = CacheConfig.file_cache(
                base_dir=str(self.account.cache_dir) if self.account.cache_dir else ".cache",
                lifetime_hours=self.cache_lifetime_hours,
            )

            self._client = AmoCRMClient(
                base_url=self.account.base_url,
                token_file=str(self.account.token_path),
                cache_config=cache_config,
                rate_limit=self.account.rate_limit,
            )

    @property
    def client(self):
        """Возвращает клиент amoCRM."""
        self._ensure_client()
        return self._client

    def load_pipelines_and_statuses(self) -> Tuple[Dict[int, str], Dict[int, Dict[str, Any]]]:
        """
        Загружает воронки и статусы для денормализации.

        Returns:
            Tuple[pipelines_map, statuses_map]
            - pipelines_map: {pipeline_id: name}
            - statuses_map: {status_id: {"name": ..., "sort": ..., "pipeline_id": ...}}
        """
        if self._pipelines_map and self._statuses_map:
            return self._pipelines_map, self._statuses_map

        logger.info("Загружаем воронки и статусы для аккаунта %s", self.account.name)

        for pipeline in self.client.iter_pipelines():
            pipeline_id = pipeline.get("id")
            self._pipelines_map[pipeline_id] = pipeline.get("name")

            # Статусы из _embedded
            embedded = pipeline.get("_embedded", {})
            for status in embedded.get("statuses", []):
                status_id = status.get("id")
                self._statuses_map[status_id] = {
                    "name": status.get("name"),
                    "sort": status.get("sort"),
                    "pipeline_id": pipeline_id,
                }

        logger.info("Загружено %d воронок, %d статусов", len(self._pipelines_map), len(self._statuses_map))
        return self._pipelines_map, self._statuses_map

    def iter_leads(
        self,
        updated_from: Optional[datetime] = None,
        updated_to: Optional[datetime] = None,
        pipeline_ids: Optional[List[int]] = None,
        include_contacts: bool = True,
        only_deleted: bool = False,
    ) -> Iterator[Dict[str, Any]]:
        """
        Итератор по сделкам.

        Args:
            updated_from: Начало периода (по updated_at)
            updated_to: Конец периода (по updated_at)
            pipeline_ids: Фильтр по воронкам (None = из конфига аккаунта)
            include_contacts: Включать вложенные контакты
            only_deleted: Выгружать только удалённые сделки (из корзины)

        Yields:
            Dict с данными сделки из amoCRM API
        """
        # Используем pipeline_ids из аккаунта если не указаны явно
        if pipeline_ids is None:
            pipeline_ids = self.account.pipeline_ids

        logger.info(
            "Выгружаем сделки: updated_from=%s, updated_to=%s, pipeline_ids=%s, only_deleted=%s",
            updated_from,
            updated_to,
            pipeline_ids,
            only_deleted,
        )

        count = 0
        # Формируем extra_params для only_deleted
        extra_params = {}
        if only_deleted:
            extra_params["filter[only_deleted]"] = "true"

        for lead in self.client.iter_leads(
            updated_from=updated_from,
            updated_to=updated_to,
            pipeline_ids=pipeline_ids,
            include_contacts=include_contacts,
            extra_params=extra_params if extra_params else None,
        ):
            count += 1
            if count % 100 == 0:
                logger.debug("Выгружено %d сделок", count)
            yield lead

        logger.info("Всего выгружено %d сделок", count)

    def iter_contacts(
        self,
        contact_ids: Optional[List[int]] = None,
        updated_from: Optional[datetime] = None,
        updated_to: Optional[datetime] = None,
    ) -> Iterator[Dict[str, Any]]:
        """
        Итератор по контактам.

        Args:
            contact_ids: Список ID контактов для выгрузки
            updated_from: Начало периода (по updated_at)
            updated_to: Конец периода (по updated_at)

        Yields:
            Dict с данными контакта из amoCRM API
        """
        logger.info(
            "Выгружаем контакты: contact_ids=%s, updated_from=%s, updated_to=%s",
            f"{len(contact_ids)} шт" if contact_ids else "все",
            updated_from,
            updated_to,
        )

        count = 0
        for contact in self.client.iter_contacts(
            contact_ids=contact_ids,
            updated_from=updated_from,
            updated_to=updated_to,
        ):
            count += 1
            if count % 100 == 0:
                logger.debug("Выгружено %d контактов", count)
            yield contact

        logger.info("Всего выгружено %d контактов", count)

    def iter_events(
        self,
        entity_type: Optional[str] = "lead",
        event_types: Optional[List[str]] = None,
        created_from: Optional[datetime] = None,
        created_to: Optional[datetime] = None,
    ) -> Iterator[Dict[str, Any]]:
        """
        Итератор по событиям.

        Args:
            entity_type: Тип сущности (lead, contact, company, etc.)
            event_types: Фильтр по типам событий
            created_from: Начало периода (по created_at)
            created_to: Конец периода (по created_at)

        Yields:
            Dict с данными события из amoCRM API
        """
        logger.info(
            "Выгружаем события: entity_type=%s, event_types=%s, created_from=%s",
            entity_type,
            event_types,
            created_from,
        )

        count = 0
        for event in self.client.iter_events(
            entity_type=entity_type,
            event_type=event_types[0] if event_types and len(event_types) == 1 else None,
            start=created_from,
            end=created_to,
        ):
            # Фильтруем по типам если указано несколько
            if event_types and len(event_types) > 1:
                if event.get("type") not in event_types:
                    continue

            count += 1
            if count % 500 == 0:
                logger.debug("Выгружено %d событий", count)
            yield event

        logger.info("Всего выгружено %d событий", count)

    def iter_notes(
        self,
        entity_type: str = "lead",
        note_type: Optional[str] = None,
        entity_ids: Optional[List[int]] = None,
        updated_from: Optional[datetime] = None,
        updated_to: Optional[datetime] = None,
    ) -> Iterator[Dict[str, Any]]:
        """
        Итератор по примечаниям.

        Args:
            entity_type: Тип сущности (lead, contact, company)
            note_type: Тип примечания (common, call_in, call_out, etc.)
            entity_ids: Список ID сущностей
            updated_from: Начало периода
            updated_to: Конец периода

        Yields:
            Dict с данными примечания из amoCRM API
        """
        logger.info(
            "Выгружаем примечания: entity_type=%s, note_type=%s, entity_ids=%s",
            entity_type,
            note_type,
            f"{len(entity_ids)} шт" if entity_ids else "все",
        )

        count = 0
        for note in self.client.iter_notes(
            entity=entity_type,
            note_type=note_type,
            start=updated_from,
            end=updated_to,
        ):
            count += 1
            if count % 100 == 0:
                logger.debug("Выгружено %d примечаний", count)
            yield note

        logger.info("Всего выгружено %d примечаний", count)

    def iter_users(self, with_groups: bool = True, with_roles: bool = True) -> Iterator[Dict[str, Any]]:
        """
        Итератор по пользователям.

        Args:
            with_groups: Включать информацию о группах
            with_roles: Включать информацию о ролях

        Yields:
            Dict с данными пользователя из amoCRM API
        """
        logger.info("Выгружаем пользователей")

        extra_params = {}
        with_parts = []
        if with_groups:
            with_parts.append("groups")
        if with_roles:
            with_parts.append("roles")
        if with_parts:
            extra_params["with"] = ",".join(with_parts)

        count = 0
        for user in self.client.iter_users(extra_params=extra_params):
            count += 1
            yield user

        logger.info("Всего выгружено %d пользователей", count)

    def iter_pipelines(self) -> Iterator[Dict[str, Any]]:
        """
        Итератор по воронкам.

        Yields:
            Dict с данными воронки и статусами в _embedded
        """
        logger.info("Выгружаем воронки")

        count = 0
        for pipeline in self.client.iter_pipelines():
            count += 1
            yield pipeline

        logger.info("Всего выгружено %d воронок", count)

    def collect_contact_ids_from_leads(
        self,
        leads: Iterator[Dict[str, Any]],
    ) -> Tuple[List[Dict[str, Any]], Set[int]]:
        """
        Собирает ID контактов из сделок.

        Полезно для последующей выгрузки связанных контактов.

        Args:
            leads: Итератор сделок

        Returns:
            Tuple[leads_list, contact_ids_set]
        """
        leads_list = []
        contact_ids: Set[int] = set()

        for lead in leads:
            leads_list.append(lead)

            embedded = lead.get("_embedded", {})
            for contact in embedded.get("contacts", []):
                contact_id = contact.get("id")
                if contact_id:
                    contact_ids.add(int(contact_id))

        logger.info("Собрано %d уникальных контактов из %d сделок", len(contact_ids), len(leads_list))
        return leads_list, contact_ids


def create_extractor(account: AmoCRMAccount, **kwargs) -> AmoCRMExtractor:
    """
    Фабричный метод для создания экстрактора.

    Args:
        account: Конфигурация аккаунта
        **kwargs: Дополнительные параметры для AmoCRMExtractor

    Returns:
        Инициализированный экстрактор
    """
    return AmoCRMExtractor(account, **kwargs)

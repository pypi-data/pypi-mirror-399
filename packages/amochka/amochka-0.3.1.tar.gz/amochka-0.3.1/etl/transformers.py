"""
Трансформация данных из amoCRM JSON в структуру mybi.

Преобразует payload из amochka в записи для таблиц PostgreSQL.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterator, List, Optional, Tuple


def _timestamp_to_datetime(ts: Optional[int]) -> Optional[datetime]:
    """Преобразует Unix timestamp в datetime с UTC."""
    if ts is None:
        return None
    try:
        return datetime.fromtimestamp(ts, tz=timezone.utc)
    except (ValueError, OSError, OverflowError):
        return None


def _extract_phone_email(custom_fields: List[Dict]) -> Tuple[Optional[str], Optional[str]]:
    """
    Извлекает основной телефон и email из custom_fields_values контакта.

    В amoCRM телефон и email хранятся как multitext поля.
    """
    phone = None
    email = None

    for cf in custom_fields:
        field_code = cf.get("field_code", "")
        values = cf.get("values", [])

        if field_code == "PHONE" and values:
            # Собираем все телефоны через запятую
            phones = [v.get("value") for v in values if v.get("value")]
            if phones:
                phone = ", ".join(phones)

        elif field_code == "EMAIL" and values:
            # Собираем все email через запятую
            emails = [v.get("value") for v in values if v.get("value")]
            if emails:
                email = ", ".join(emails)

    return phone, email


@dataclass
class TransformedLead:
    """Результат трансформации одной сделки."""

    lead: Dict[str, Any]
    lead_facts: Dict[str, Any]
    attributes: List[Dict[str, Any]]
    tags: List[Dict[str, Any]]
    contacts_links: List[Dict[str, Any]]


@dataclass
class TransformedContact:
    """Результат трансформации одного контакта."""

    contact: Dict[str, Any]
    contact_facts: Dict[str, Any]
    attributes: List[Dict[str, Any]]


@dataclass
class TransformedEvent:
    """Результат трансформации одного события."""

    event: Dict[str, Any]


class LeadTransformer:
    """Трансформер для сделок (leads)."""

    def __init__(self, account_id: int, pipelines_map: Optional[Dict[int, str]] = None, statuses_map: Optional[Dict[int, Dict]] = None):
        """
        Инициализирует трансформер.

        Args:
            account_id: ID аккаунта amoCRM
            pipelines_map: {pipeline_id: name} для денормализации
            statuses_map: {status_id: {"name": ..., "sort": ...}} для денормализации
        """
        self.account_id = account_id
        self.pipelines_map = pipelines_map or {}
        self.statuses_map = statuses_map or {}

    def transform(self, lead: Dict[str, Any]) -> TransformedLead:
        """
        Преобразует сделку из amoCRM в структуру mybi.

        Args:
            lead: JSON сделки из amoCRM API

        Returns:
            TransformedLead с данными для всех таблиц
        """
        lead_id = lead.get("id")
        pipeline_id = lead.get("pipeline_id")
        status_id = lead.get("status_id")

        # Основная запись сделки
        lead_record = {
            "account_id": self.account_id,
            "lead_id": lead_id,
            "name": lead.get("name"),
            "pipeline": self.pipelines_map.get(pipeline_id),
            "pipeline_id": pipeline_id,
            "status": self.statuses_map.get(status_id, {}).get("name"),
            "status_id": status_id,
            "status_order": self.statuses_map.get(status_id, {}).get("sort"),
            "request_id": None,  # Заполняется из неразобранного
            "loss_reason": None,
            "loss_reason_id": lead.get("loss_reason_id"),
            "is_deleted": lead.get("is_deleted", False),
        }

        # Извлекаем loss_reason из _embedded
        embedded = lead.get("_embedded", {})
        loss_reason = embedded.get("loss_reason")
        if loss_reason:
            lead_record["loss_reason"] = loss_reason.get("name")
            if not lead_record["loss_reason_id"]:
                lead_record["loss_reason_id"] = loss_reason.get("id")

        # Факты по сделке
        created_at = _timestamp_to_datetime(lead.get("created_at"))
        updated_at = _timestamp_to_datetime(lead.get("updated_at"))
        closed_at = _timestamp_to_datetime(lead.get("closed_at"))

        # Основной контакт из _embedded.contacts
        contacts = embedded.get("contacts", [])
        main_contact_id = None
        for contact in contacts:
            if contact.get("is_main"):
                main_contact_id = contact.get("id")
                break
        if not main_contact_id and contacts:
            main_contact_id = contacts[0].get("id")

        # Компания из _embedded.companies
        companies = embedded.get("companies", [])
        company_id = companies[0].get("id") if companies else None

        lead_facts_record = {
            "account_id": self.account_id,
            "leads_id": None,  # Будет заполнено после INSERT в leads
            "contacts_id": main_contact_id,
            "companies_id": company_id,
            "users_id": lead.get("responsible_user_id"),
            "created_id": None,  # Будет заполнено через get_or_create_date_id()
            "closed_id": None,  # Будет заполнено через get_or_create_date_id()
            "price": lead.get("price"),
            "labor_cost": lead.get("labor_cost"),
            "score": lead.get("score"),
            "created_date": created_at,
            "modified_date": updated_at,
            "_created_at_raw": lead.get("created_at"),  # Для вычисления created_id
            "_closed_at_raw": lead.get("closed_at"),  # Для вычисления closed_id
        }

        # Атрибуты (custom_fields_values)
        attributes = []
        custom_fields = lead.get("custom_fields_values") or []
        for cf in custom_fields:
            field_id = cf.get("field_id")
            field_name = cf.get("field_name", "")
            values = cf.get("values", [])

            for val in values:
                value = val.get("value")
                if value is None:
                    # Для enum-полей берём enum_id или значение из enums
                    enum_id = val.get("enum_id")
                    if enum_id is not None:
                        value = str(enum_id)

                attributes.append({
                    "account_id": self.account_id,
                    "leads_id": None,  # Будет заполнено после INSERT
                    "attribute_id": str(field_id) if field_id else "",
                    "name": field_name,
                    "value": str(value) if value is not None else None,
                })

        # Теги из _embedded.tags
        tags = []
        for tag in embedded.get("tags", []):
            tags.append({
                "account_id": self.account_id,
                "leads_id": None,
                "tag_id": tag.get("id"),
                "name": tag.get("name"),
            })

        # Связи с контактами
        contacts_links = []
        for i, contact in enumerate(contacts):
            contacts_links.append({
                "account_id": self.account_id,
                "leads_id": None,
                "contacts_id": contact.get("id"),
                "main": contact.get("is_main", i == 0),
            })

        return TransformedLead(
            lead=lead_record,
            lead_facts=lead_facts_record,
            attributes=attributes,
            tags=tags,
            contacts_links=contacts_links,
        )


class ContactTransformer:
    """Трансформер для контактов."""

    def __init__(self, account_id: int):
        self.account_id = account_id

    def transform(self, contact: Dict[str, Any]) -> TransformedContact:
        """Преобразует контакт из amoCRM в структуру mybi."""
        contact_id = contact.get("id")
        custom_fields = contact.get("custom_fields_values") or []

        # Извлекаем телефон и email из custom_fields
        phone, email = _extract_phone_email(custom_fields)

        # Основная запись контакта
        contact_record = {
            "account_id": self.account_id,
            "contact_id": contact_id,
            "name": contact.get("name"),
            "first_name": contact.get("first_name"),
            "last_name": contact.get("last_name"),
            "company": None,  # Заполняется из _embedded.companies
            "post": None,  # Должность из custom_fields
            "phone": phone,
            "email": email,
            "request_id": None,
            "is_deleted": contact.get("is_deleted", False),
        }

        # Компания из _embedded
        embedded = contact.get("_embedded", {})
        companies = embedded.get("companies", [])
        if companies:
            contact_record["company"] = companies[0].get("name")

        # Факты по контакту
        created_at = _timestamp_to_datetime(contact.get("created_at"))
        updated_at = _timestamp_to_datetime(contact.get("updated_at"))

        contact_facts_record = {
            "account_id": self.account_id,
            "contacts_id": None,  # Будет заполнено после INSERT
            "companies_id": companies[0].get("id") if companies else None,
            "users_id": contact.get("responsible_user_id"),
            "registered_id": None,  # Будет заполнено через get_or_create_date_id()
            "created_date": created_at,
            "modified_date": updated_at,
            "_created_at_raw": contact.get("created_at"),
        }

        # Атрибуты
        attributes = []
        for cf in custom_fields:
            field_id = cf.get("field_id")
            field_name = cf.get("field_name", "")
            field_code = cf.get("field_code", "")

            # Пропускаем стандартные поля PHONE и EMAIL (они уже в основной записи)
            if field_code in ("PHONE", "EMAIL"):
                continue

            values = cf.get("values", [])
            for val in values:
                value = val.get("value")
                if value is None:
                    enum_id = val.get("enum_id")
                    if enum_id is not None:
                        value = str(enum_id)

                attributes.append({
                    "account_id": self.account_id,
                    "contacts_id": None,
                    "attribute_id": str(field_id) if field_id else "",
                    "name": field_name,
                    "value": str(value) if value is not None else None,
                })

        return TransformedContact(
            contact=contact_record,
            contact_facts=contact_facts_record,
            attributes=attributes,
        )


class EventTransformer:
    """Трансформер для событий."""

    def __init__(self, account_id: int):
        self.account_id = account_id

    def transform(self, event: Dict[str, Any], entity_type: str = "lead") -> TransformedEvent:
        """
        Преобразует событие из amoCRM в структуру mybi.

        Args:
            event: JSON события из amoCRM API
            entity_type: Тип сущности (lead, contact, company)
        """
        created_at = _timestamp_to_datetime(event.get("created_at"))

        # value_before и value_after могут быть списками или объектами
        value_before = event.get("value_before")
        value_after = event.get("value_after")

        # Сериализуем в JSON-строку для хранения
        if value_before is not None:
            value_before = json.dumps(value_before, ensure_ascii=False)
        if value_after is not None:
            value_after = json.dumps(value_after, ensure_ascii=False)

        # Определяем leads_id из entity_id если это событие по сделке
        leads_id = None
        if entity_type == "lead":
            leads_id = event.get("entity_id")

        event_record = {
            "account_id": self.account_id,
            "leads_id": leads_id,
            "event_id": event.get("id"),
            "type": event.get("type"),
            "created_by": event.get("created_by"),
            "created_at": created_at,
            "value_after": value_after,
            "value_before": value_before,
        }

        return TransformedEvent(event=event_record)


class NoteTransformer:
    """Трансформер для примечаний."""

    def __init__(self, account_id: int):
        self.account_id = account_id

    def transform(self, note: Dict[str, Any], entity_type: str = "lead") -> Dict[str, Any]:
        """Преобразует примечание из amoCRM в структуру mybi."""
        created_at = _timestamp_to_datetime(note.get("created_at"))
        updated_at = _timestamp_to_datetime(note.get("updated_at"))

        # params может быть словарём с дополнительными данными
        params = note.get("params")
        if params is not None:
            params = json.dumps(params, ensure_ascii=False)

        # entity_id определяет к какой сущности привязано примечание
        entity_id = note.get("entity_id")

        return {
            "account_id": self.account_id,
            "leads_id": entity_id if entity_type == "lead" else None,
            "creator_id": note.get("created_by"),
            "responsible_id": note.get("responsible_user_id"),
            "note_id": note.get("id"),
            "note_type": note.get("note_type"),
            "note_type_id": None,  # В API v4 нет отдельного type_id
            "created_at": created_at,
            "updated_at": updated_at,
            "text": note.get("params", {}).get("text") if isinstance(note.get("params"), dict) else None,
            "params": params,
        }


class PipelineTransformer:
    """Трансформер для воронок и статусов."""

    def __init__(self, account_id: int):
        self.account_id = account_id

    def transform_pipeline(self, pipeline: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Преобразует воронку из amoCRM.

        Returns:
            Tuple[pipeline_record, list_of_status_records]
        """
        pipeline_id = pipeline.get("id")

        pipeline_record = {
            "account_id": self.account_id,
            "pipeline_id": pipeline_id,
            "name": pipeline.get("name"),
            "sort": pipeline.get("sort"),
            "is_main": pipeline.get("is_main", False),
            "is_unsorted_on": pipeline.get("is_unsorted_on", False),
            "is_archive": pipeline.get("is_archive", False),
        }

        # Статусы из _embedded.statuses
        statuses = []
        embedded = pipeline.get("_embedded", {})
        for status in embedded.get("statuses", []):
            statuses.append({
                "account_id": self.account_id,
                "pipeline_id": pipeline_id,
                "status_id": status.get("id"),
                "name": status.get("name"),
                "color": status.get("color"),
                "sort": status.get("sort"),
                "is_editable": status.get("is_editable", True),
                "type": status.get("type", 0),
            })

        return pipeline_record, statuses


class UserTransformer:
    """Трансформер для пользователей."""

    def __init__(self, account_id: int):
        self.account_id = account_id

    def transform(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """Преобразует пользователя из amoCRM в структуру mybi."""
        # Группа из _embedded
        embedded = user.get("_embedded", {})
        groups = embedded.get("groups", [])
        roles = embedded.get("roles", [])

        group_name = None
        group_id = None
        if groups:
            group_name = groups[0].get("name")
            group_id = groups[0].get("id")

        role_name = None
        role_id = None
        if roles:
            role_name = roles[0].get("name")
            role_id = roles[0].get("id")

        rights = user.get("rights", {})

        return {
            "account_id": self.account_id,
            "user_id": user.get("id"),
            "login": user.get("email"),  # В API v4 login = email
            "name": user.get("name"),
            "phone": user.get("phone"),
            "email": user.get("email"),
            "group_name": group_name,
            "group_id": group_id,
            "role_id": role_id,
            "role_name": role_name,
            "is_admin": rights.get("is_admin", False),
            "is_active": rights.get("is_active", True),
            "is_free": rights.get("is_free", False),
            "mail_access": rights.get("mail_access", False),
            "catalog_access": rights.get("catalog_access", False),
        }

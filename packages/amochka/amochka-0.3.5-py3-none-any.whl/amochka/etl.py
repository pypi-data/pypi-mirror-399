import json
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Sequence, Set, Union

from .client import AmoCRMClient


def _ensure_path(path: Union[str, Path]) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


def _resolve_timestamp(record: dict, timestamp_fields: Sequence[str]) -> Optional[Union[int, float, str]]:
    for field in timestamp_fields:
        if not field:
            continue
        value = record.get(field)
        if value is not None:
            return value
    return None


def write_ndjson(
    records: Iterable[dict],
    output_path: Union[str, Path],
    *,
    entity: str,
    account_id: Optional[Union[int, str]] = None,
    timestamp_fields: Sequence[str] = ("updated_at", "created_at"),
    transform: Optional[Callable[[dict], dict]] = None,
    on_record: Optional[Callable[[dict], None]] = None,
) -> int:
    """
    Записывает переданные записи в формат NDJSON.

    Возвращает количество записанных строк.
    """
    path = _ensure_path(output_path)
    count = 0
    with path.open("w", encoding="utf-8") as handler:
        for original in records:
            payload = transform(original) if transform else original
            timestamp = _resolve_timestamp(original, timestamp_fields)
            line = {
                "entity": entity,
                "account_id": account_id,
                "updated_at": timestamp,
                "payload": payload,
            }
            handler.write(json.dumps(line, ensure_ascii=False))
            handler.write("\n")
            count += 1
            if on_record:
                on_record(original)
    return count


def export_leads_to_ndjson(
    client: AmoCRMClient,
    output_path: Union[str, Path],
    account_id: Union[int, str],
    *,
    start=None,
    end=None,
    pipeline_ids=None,
    include_contacts: bool = True,
    include=None,
    limit: int = 250,
    extra_params: Optional[dict] = None,
    on_record: Optional[Callable[[dict], None]] = None,
) -> int:
    """
    Выгружает сделки и записывает их в NDJSON.
    """
    records = client.iter_leads(
        updated_from=start,
        updated_to=end,
        pipeline_ids=pipeline_ids,
        include_contacts=include_contacts,
        include=include,
        limit=limit,
        extra_params=extra_params,
    )
    return write_ndjson(
        records,
        output_path,
        entity="lead",
        account_id=account_id,
        timestamp_fields=("updated_at", "created_at"),
        on_record=on_record,
    )


def export_contacts_to_ndjson(
    client: AmoCRMClient,
    output_path: Union[str, Path],
    account_id: Union[int, str],
    *,
    start=None,
    end=None,
    contact_ids=None,
    limit: int = 250,
    extra_params: Optional[dict] = None,
    on_record: Optional[Callable[[dict], None]] = None,
) -> int:
    """
    Выгружает контакты и записывает их в NDJSON.
    """
    contact_id_list: Optional[List[int]] = None
    if contact_ids is not None:
        if isinstance(contact_ids, (list, tuple, set)):
            contact_id_list = [int(cid) for cid in contact_ids if cid is not None]
        else:
            contact_id_list = [int(contact_ids)]

    def _iter_contacts():
        seen: Set[int] = set()
        if contact_id_list:
            params = dict(extra_params or {})
            params["filter[id][]"] = [str(cid) for cid in contact_id_list]
            params["page"] = 1
            params["limit"] = limit
            while True:
                response = client._make_request("GET", "/api/v4/contacts", params=params)
                embedded = (response or {}).get("_embedded", {})
                contacts = embedded.get("contacts") or []
                if not contacts:
                    break
                for contact in contacts:
                    cid = contact.get("id")
                    if cid is not None:
                        seen.add(int(cid))
                    yield contact
                total_pages = response.get("_page_count", params["page"])
                if params["page"] >= total_pages:
                    break
                params["page"] += 1
        else:
            for contact in client.iter_contacts(
                updated_from=start,
                updated_to=end,
                contact_ids=None,
                limit=limit,
                extra_params=extra_params,
            ):
                cid = contact.get("id")
                if cid is not None:
                    seen.add(int(cid))
                yield contact

        if contact_id_list:
            missing = [cid for cid in contact_id_list if cid not in seen]
            for cid in missing:
                try:
                    contact = client.get_contact_by_id(cid)
                except Exception:
                    continue
                retrieved_id = contact.get("id")
                if retrieved_id is not None and int(retrieved_id) not in seen:
                    seen.add(int(retrieved_id))
                    yield contact

    return write_ndjson(
        _iter_contacts(),
        output_path,
        entity="contact",
        account_id=account_id,
        timestamp_fields=("updated_at", "created_at"),
        on_record=on_record,
    )


def export_notes_to_ndjson(
    client: AmoCRMClient,
    output_path: Union[str, Path],
    account_id: Union[int, str],
    *,
    entity: str = "lead",
    start=None,
    end=None,
    note_type=None,
    entity_ids=None,
    limit: int = 250,
    extra_params: Optional[dict] = None,
    on_record: Optional[Callable[[dict], None]] = None,
) -> int:
    """
    Выгружает примечания и записывает их в NDJSON.
    """
    records = client.iter_notes(
        entity=entity,
        updated_from=start,
        updated_to=end,
        note_type=note_type,
        entity_ids=entity_ids,
        limit=limit,
        extra_params=extra_params,
    )
    entity_name = f"{entity}_note" if entity else "note"
    return write_ndjson(
        records,
        output_path,
        entity=entity_name,
        account_id=account_id,
        timestamp_fields=("updated_at", "created_at"),
        on_record=on_record,
    )


def export_events_to_ndjson(
    client: AmoCRMClient,
    output_path: Union[str, Path],
    account_id: Union[int, str],
    *,
    entity: Optional[str] = "lead",
    start=None,
    end=None,
    event_type=None,
    entity_ids=None,
    limit: int = 250,
    extra_params: Optional[dict] = None,
    on_record: Optional[Callable[[dict], None]] = None,
) -> int:
    """
    Выгружает события и записывает их в NDJSON.
    """
    records = client.iter_events(
        entity=entity,
        entity_ids=entity_ids,
        event_type=event_type,
        created_from=start,
        created_to=end,
        limit=limit,
        extra_params=extra_params,
    )
    entity_name = f"{entity}_event" if entity else "event"
    return write_ndjson(
        records,
        output_path,
        entity=entity_name,
        account_id=account_id,
        timestamp_fields=("created_at", "updated_at"),
        on_record=on_record,
    )


def export_users_to_ndjson(
    client: AmoCRMClient,
    output_path: Union[str, Path],
    account_id: Union[int, str],
    *,
    limit: int = 250,
    extra_params: Optional[dict] = None,
    on_record: Optional[Callable[[dict], None]] = None,
) -> int:
    """
    Выгружает пользователей и записывает их в NDJSON.
    """
    records = client.iter_users(limit=limit, extra_params=extra_params)
    return write_ndjson(
        records,
        output_path,
        entity="user",
        account_id=account_id,
        timestamp_fields=("updated_at", "created_at"),
        on_record=on_record,
    )


def export_pipelines_to_ndjson(
    client: AmoCRMClient,
    output_path: Union[str, Path],
    account_id: Union[int, str],
    *,
    limit: int = 250,
    extra_params: Optional[dict] = None,
    on_record: Optional[Callable[[dict], None]] = None,
) -> int:
    """
    Выгружает воронки и записывает их в NDJSON.
    """
    records = client.iter_pipelines(limit=limit, extra_params=extra_params)
    return write_ndjson(
        records,
        output_path,
        entity="pipeline",
        account_id=account_id,
        timestamp_fields=("updated_at", "created_at"),
        on_record=on_record,
    )


__all__ = [
    "write_ndjson",
    "export_leads_to_ndjson",
    "export_contacts_to_ndjson",
    "export_notes_to_ndjson",
    "export_events_to_ndjson",
    "export_users_to_ndjson",
    "export_pipelines_to_ndjson",
]

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from amochka import (
    AmoCRMClient,
    CacheConfig,
    export_contacts_to_ndjson,
    export_events_to_ndjson,
    export_leads_to_ndjson,
    export_notes_to_ndjson,
    export_pipelines_to_ndjson,
    export_users_to_ndjson,
)


class DummyClient(AmoCRMClient):
    def __init__(self):
        token_data = {
            "access_token": "x",
            "expires_at": str(int(datetime.utcnow().timestamp()) + 3600)
        }
        super().__init__(
            base_url="https://example.com",
            token_file=json.dumps(token_data),
            cache_config=CacheConfig.disabled(),
            disable_logging=True
        )
        self.calls = []
        contact_11 = {
            "id": 11,
            "updated_at": 110,
        }
        contact_12 = {
            "id": 12,
            "updated_at": 111,
        }

        self._data = {
            "/api/v4/leads": [
                {
                    "_embedded": {
                        "leads": [
                            {"id": 1, "updated_at": 100, "_embedded": {"contacts": [{"id": 11}, {"id": 12}]}}
                        ]
                    },
                    "_page_count": 2,
                },
                {
                    "_embedded": {
                        "leads": [
                            {"id": 2, "updated_at": 101, "_embedded": {"contacts": [{"id": 11}]}}
                        ]
                    },
                    "_page_count": 2,
                },
            ],
            "/api/v4/contacts": [
                {
                    "_embedded": {
                        "contacts": [
                            contact_11,
                        ]
                    },
                    "_page_count": 1,
                }
            ],
            "/api/v4/leads/notes": [
                {
                    "_embedded": {
                        "notes": [
                            {"id": 21, "updated_at": 120, "entity_id": 1}
                        ]
                    },
                    "_page_count": 1,
                }
            ],
            "/api/v4/events": [
                {
                    "_embedded": {
                        "events": [
                            {"id": 31, "created_at": 130, "entity_id": 1}
                        ]
                    },
                    "_page_count": 1,
                }
            ],
            "/api/v4/users": [
                {
                    "_embedded": {"users": [{"id": 41, "updated_at": 140}]},
                    "_page_count": 1,
                }
            ],
            "/api/v4/leads/pipelines": [
                {
                    "_embedded": {"pipelines": [{"id": 51, "updated_at": 150}]},
                    "_page_count": 1,
                }
            ],
        }

        self._single_contacts = {
            11: contact_11,
            12: contact_12,
        }

    def _make_request(self, method, endpoint, params=None, data=None, timeout=10):
        self.calls.append((method, endpoint, params, data, timeout))
        params = params or {}
        page = params.get("page", 1)
        payloads = self._data.get(endpoint, [])
        index = max(page - 1, 0)
        if isinstance(payloads, list) and index < len(payloads):
            return payloads[index]
        if endpoint.startswith("/api/v4/contacts/"):
            contact_id = int(endpoint.rsplit("/", 1)[-1])
            return self._single_contacts.get(contact_id, {})
        return {"_embedded": {}}

def test_fetch_updated_leads_raw(tmp_path):
    client = DummyClient()
    file_path = tmp_path / "leads.json"
    leads = client.fetch_updated_leads_raw(
        1,
        updated_from=datetime.utcnow(),
        save_to_file=str(file_path),
        include_contacts=True,
    )

    assert [lead["id"] for lead in leads] == [1, 2]
    method, endpoint, params, data, timeout = client.calls[0]
    assert endpoint == "/api/v4/leads"
    assert params.get("with") == "contacts"
    assert params.get("filter[pipeline_id]") == "1"
    assert timeout == 10
    assert file_path.exists()
    data = json.loads(file_path.read_text())
    assert len(data) == 2


def test_export_helpers_write_expected_files(tmp_path):
    client = DummyClient()
    export_dir = tmp_path / "exports"
    export_dir.mkdir()

    window_end = datetime.utcnow()
    window_start = window_end - timedelta(minutes=15)

    collected_contacts = set()

    def _collect(lead):
        embedded = lead.get("_embedded") or {}
        for contact in embedded.get("contacts", []):
            contact_id = contact.get("id")
            if contact_id is not None:
                collected_contacts.add(int(contact_id))

    leads_file = export_dir / "leads.ndjson"
    leads_count = export_leads_to_ndjson(
        client,
        leads_file,
        account_id=123,
        start=window_start,
        end=window_end,
        include_contacts=True,
        on_record=_collect,
    )
    assert leads_count == 2
    assert collected_contacts == {11, 12}

    contacts_file = export_dir / "contacts.ndjson"
    contacts_count = export_contacts_to_ndjson(
        client,
        contacts_file,
        account_id=123,
        contact_ids=sorted(collected_contacts),
    )
    assert contacts_count == 2

    notes_file = export_dir / "lead_notes.ndjson"
    notes_count = export_notes_to_ndjson(
        client,
        notes_file,
        account_id=123,
        entity="lead",
        start=window_start,
        end=window_end,
    )
    assert notes_count == 1

    events_file = export_dir / "lead_events.ndjson"
    events_count = export_events_to_ndjson(
        client,
        events_file,
        account_id=123,
        entity="lead",
        start=window_start,
        end=window_end,
    )
    assert events_count == 1

    users_file = export_dir / "users.ndjson"
    users_count = export_users_to_ndjson(
        client,
        users_file,
        account_id=123,
    )
    assert users_count == 1

    pipelines_file = export_dir / "pipelines.ndjson"
    pipelines_count = export_pipelines_to_ndjson(
        client,
        pipelines_file,
        account_id=123,
    )
    assert pipelines_count == 1

    def _read_lines(path: Path):
        return [json.loads(line) for line in path.read_text().splitlines() if line]

    leads_lines = _read_lines(leads_file)
    assert leads_lines[0]["entity"] == "lead"
    assert leads_lines[0]["account_id"] == 123
    assert leads_lines[0]["updated_at"] == 100
    assert leads_lines[0]["payload"]["id"] == 1

    contacts_lines = _read_lines(contacts_file)
    assert contacts_lines[0]["entity"] == "contact"
    assert contacts_lines[0]["payload"]["id"] == 11

    notes_lines = _read_lines(notes_file)
    assert notes_lines[0]["entity"] == "lead_note"
    assert notes_lines[0]["updated_at"] == 120

    events_lines = _read_lines(events_file)
    assert events_lines[0]["entity"] == "lead_event"
    assert events_lines[0]["updated_at"] == 130

    users_lines = _read_lines(users_file)
    assert users_lines[0]["entity"] == "user"

    pipelines_lines = _read_lines(pipelines_file)
    assert pipelines_lines[0]["entity"] == "pipeline"

    contacts_call = next(item for item in client.calls if item[1] == "/api/v4/contacts")
    assert contacts_call[2]["filter[id]"] == "11,12"
    assert "filter[updated_at][from]" not in contacts_call[2]

    events_call = next(item for item in client.calls if item[1] == "/api/v4/events")
    assert events_call[2]["filter[entity]"] == "lead"

    notes_call = next(item for item in client.calls if item[1] == "/api/v4/leads/notes")
    assert notes_call[2]["filter[updated_at][from]"] is None or notes_call[2]["filter[updated_at][from]"] >= 0

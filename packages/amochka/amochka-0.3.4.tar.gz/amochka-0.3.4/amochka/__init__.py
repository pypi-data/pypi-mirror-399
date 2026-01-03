"""
amochka: Библиотека для работы с API amoCRM.
"""

__version__ = "0.2.0"

from .client import AmoCRMClient, CacheConfig
from .etl import (
    write_ndjson,
    export_leads_to_ndjson,
    export_contacts_to_ndjson,
    export_notes_to_ndjson,
    export_events_to_ndjson,
    export_users_to_ndjson,
    export_pipelines_to_ndjson,
)

__all__ = [
    "AmoCRMClient",
    "CacheConfig",
    "write_ndjson",
    "export_leads_to_ndjson",
    "export_contacts_to_ndjson",
    "export_notes_to_ndjson",
    "export_events_to_ndjson",
    "export_users_to_ndjson",
    "export_pipelines_to_ndjson",
]

"""
Конфигурация ETL для amoCRM.

Настройки загружаются из переменных окружения или .env файла.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


def _load_env_file(path: Path) -> Dict[str, str]:
    """Загружает переменные из .env файла."""
    if not path.exists():
        return {}

    env: Dict[str, str] = {}
    with path.open("r", encoding="utf-8") as handler:
        for raw_line in handler:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if value.startswith(('"', "'")) and value.endswith(('"', "'")) and len(value) >= 2:
                value = value[1:-1]
            env[key] = value
    return env


@dataclass
class DatabaseConfig:
    """Конфигурация подключения к PostgreSQL."""

    host: str
    port: int
    dbname: str
    user: str
    password: str
    schema: str = "public"
    sslmode: Optional[str] = None
    connect_timeout: int = 30

    def connection_kwargs(self) -> Dict[str, Any]:
        """Возвращает kwargs для psycopg.connect()."""
        kwargs: Dict[str, Any] = {
            "host": self.host,
            "port": self.port,
            "dbname": self.dbname,
            "user": self.user,
            "password": self.password,
            "connect_timeout": self.connect_timeout,
        }
        if self.sslmode:
            kwargs["sslmode"] = self.sslmode
        return kwargs

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "DatabaseConfig":
        """Создаёт конфигурацию из словаря (для Airflow DAG)."""
        return cls(
            host=d.get("host", "localhost"),
            port=int(d.get("port", 5432)),
            dbname=d.get("dbname", "amocrm"),
            user=d.get("user", "postgres"),
            password=d.get("password", ""),
            schema=d.get("schema", "public"),
            sslmode=d.get("sslmode"),
            connect_timeout=int(d.get("connect_timeout", 30)),
        )

    @classmethod
    def from_env(cls, env_path: Optional[Path] = None) -> "DatabaseConfig":
        """Создаёт конфигурацию из переменных окружения."""
        if env_path:
            file_env = _load_env_file(env_path)
            for key, value in file_env.items():
                os.environ.setdefault(key, value)

        def _get(key: str, default: Optional[str] = None) -> Optional[str]:
            return os.environ.get(key, default)

        return cls(
            host=_get("ETL_DB_HOST", "localhost") or "localhost",
            port=int(_get("ETL_DB_PORT", "5432") or "5432"),
            dbname=_get("ETL_DB_NAME", "amocrm") or "amocrm",
            user=_get("ETL_DB_USER", "postgres") or "postgres",
            password=_get("ETL_DB_PASSWORD", "") or "",
            schema=_get("ETL_DB_SCHEMA", "public") or "public",
            sslmode=_get("ETL_DB_SSLMODE"),
            connect_timeout=int(_get("ETL_DB_CONNECT_TIMEOUT", "30") or "30"),
        )


@dataclass
class AmoCRMAccount:
    """Конфигурация одного аккаунта amoCRM."""

    id: int  # ID аккаунта в amoCRM (из URL или API)
    name: str
    base_url: str
    token_path: Path
    mybi_account_id: int  # Внутренний account_id как в mybi.ru (для совместимости)
    pipeline_ids: Optional[List[int]] = None  # None = все воронки
    cache_dir: Optional[Path] = None

    def __post_init__(self):
        if isinstance(self.token_path, str):
            self.token_path = Path(self.token_path)
        if isinstance(self.cache_dir, str):
            self.cache_dir = Path(self.cache_dir)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AmoCRMAccount":
        """Создаёт конфигурацию аккаунта из словаря (для Airflow DAG)."""
        return cls(
            id=int(d.get("id", 0)),
            name=d.get("name", "account"),
            base_url=d.get("base_url", ""),
            token_path=Path(d.get("token_path", "token.json")),
            mybi_account_id=int(d.get("mybi_account_id", 0)),
            pipeline_ids=d.get("pipeline_ids"),
            cache_dir=Path(d.get("cache_dir", ".cache")) if d.get("cache_dir") else None,
        )


@dataclass
class ETLConfig:
    """Главная конфигурация ETL."""

    database: DatabaseConfig
    accounts: List[AmoCRMAccount]
    batch_size: int = 100
    window_minutes: int = 120  # Окно выгрузки по умолчанию (2 часа)
    log_level: str = "INFO"

    @classmethod
    def from_env(cls, env_path: Optional[Path] = None) -> "ETLConfig":
        """Создаёт конфигурацию из переменных окружения и файла настроек."""
        if env_path:
            file_env = _load_env_file(env_path)
            for key, value in file_env.items():
                os.environ.setdefault(key, value)

        db_config = DatabaseConfig.from_env(env_path)

        # Парсим аккаунты из переменных окружения
        # Формат: AMO_ACCOUNT_1_ID, AMO_ACCOUNT_1_NAME, AMO_ACCOUNT_1_URL, etc.
        accounts = []
        for i in range(1, 10):  # Поддерживаем до 9 аккаунтов
            prefix = f"AMO_ACCOUNT_{i}_"
            account_id = os.environ.get(f"{prefix}ID")
            if not account_id:
                continue

            pipeline_ids_str = os.environ.get(f"{prefix}PIPELINE_IDS", "")
            pipeline_ids = None
            if pipeline_ids_str:
                pipeline_ids = [int(pid.strip()) for pid in pipeline_ids_str.split(",") if pid.strip()]

            mybi_id = os.environ.get(f"{prefix}MYBI_ACCOUNT_ID")
            if not mybi_id:
                raise ValueError(f"Не указан {prefix}MYBI_ACCOUNT_ID для аккаунта {account_id}")

            accounts.append(
                AmoCRMAccount(
                    id=int(account_id),
                    name=os.environ.get(f"{prefix}NAME", f"account_{i}") or f"account_{i}",
                    base_url=os.environ.get(f"{prefix}URL", "") or "",
                    token_path=Path(os.environ.get(f"{prefix}TOKEN_PATH", f"token_{i}.json") or f"token_{i}.json"),
                    mybi_account_id=int(mybi_id),
                    pipeline_ids=pipeline_ids if pipeline_ids else None,
                    cache_dir=Path(os.environ.get(f"{prefix}CACHE_DIR", ".cache") or ".cache"),
                )
            )

        return cls(
            database=db_config,
            accounts=accounts,
            batch_size=int(os.environ.get("ETL_BATCH_SIZE", "100") or "100"),
            window_minutes=int(os.environ.get("ETL_WINDOW_MINUTES", "120") or "120"),
            log_level=os.environ.get("ETL_LOG_LEVEL", "INFO") or "INFO",
        )


# Пример конфигурации для разработки (можно переопределить в .env)
DEFAULT_CONFIG = ETLConfig(
    database=DatabaseConfig(
        host="localhost",
        port=5432,
        dbname="amocrm",
        user="postgres",
        password="",
        schema="public",
    ),
    accounts=[
        AmoCRMAccount(
            id=30019651,
            name="bneginskogo",
            base_url="https://bneginskogo.amocrm.ru",
            token_path=Path("token.json"),
            mybi_account_id=53859,  # Внутренний ID из mybi.ru
            pipeline_ids=[5987164, 6241334],
            cache_dir=Path(".cache"),
        ),
        # Добавьте остальные аккаунты здесь
    ],
    batch_size=100,
    window_minutes=120,
)


def get_config(env_path: Optional[Union[str, Path]] = None) -> ETLConfig:
    """
    Получает конфигурацию ETL.

    Если указан env_path, загружает настройки из файла.
    Иначе использует переменные окружения или DEFAULT_CONFIG.
    """
    if env_path:
        return ETLConfig.from_env(Path(env_path))

    # Проверяем наличие .env в текущей директории
    default_env = Path(".env")
    if default_env.exists():
        return ETLConfig.from_env(default_env)

    # Проверяем наличие переменных окружения
    if os.environ.get("ETL_DB_HOST") or os.environ.get("AMO_ACCOUNT_1_ID"):
        return ETLConfig.from_env()

    return DEFAULT_CONFIG

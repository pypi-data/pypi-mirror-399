import os
import time
import json
import requests
import logging
from datetime import datetime
from typing import Iterator, List, Optional, Sequence, Union
# ratelimit больше не используется - rate limiting реализован вручную через self.rate_limit

# Создаём базовый логгер
logger = logging.getLogger(__name__)
if not logger.handlers:
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

DEFAULT_RATE_LIMIT = 7  # Максимум запросов в секунду по умолчанию

class Deal(dict):
    """
    Объект сделки расширяет стандартный словарь данными из custom_fields_values.

    Обеспечивает два способа доступа к кастомным полям:
      1. get(key): при обращении по названию (строкой) или по ID поля (integer)
         возвращает текстовое значение поля (например, «Дурина Юлия»).
      2. get_id(key): возвращает идентификатор выбранного варианта (enum_id) для полей типа select.
         Если в данных enum_id отсутствует, производится поиск в переданной конфигурации полей,
         сравнение выполняется без учёта регистра и лишних пробелов.

    Параметр custom_fields_config – словарь, где ключи – ID полей, а значения – модели полей.
    """
    def __init__(self, data, custom_fields_config=None, logger=None):
        super().__init__(data)
        self._custom = {}
        self._custom_config = custom_fields_config  # сохраняем конфигурацию кастомных полей
        self._logger = logger or logging.getLogger(__name__)
        custom = data.get("custom_fields_values") or []
        self._logger.debug(f"Processing custom_fields_values: {custom}")
        for field in custom:
            if isinstance(field, dict):
                field_name = field.get("field_name")
                values = field.get("values")
                if field_name and values and isinstance(values, list) and len(values) > 0:
                    key_name = field_name.lower().strip()
                    stored_value = values[0].get("value")
                    stored_enum_id = values[0].get("enum_id")  # может быть None для некоторых полей
                    # Сохраняем полную информацию (и для get() и для get_id())
                    self._custom[key_name] = {"value": stored_value, "enum_id": stored_enum_id}
                    self._logger.debug(f"Set custom field '{key_name}' = {{'value': {stored_value}, 'enum_id': {stored_enum_id}}}")
                field_id = field.get("field_id")
                if field_id is not None and values and isinstance(values, list) and len(values) > 0:
                    stored_value = values[0].get("value")
                    stored_enum_id = values[0].get("enum_id")  # может быть None для некоторых полей
                    self._custom[int(field_id)] = {"value": stored_value, "enum_id": stored_enum_id}
                    self._logger.debug(f"Set custom field id {field_id} = {{'value': {stored_value}, 'enum_id': {stored_enum_id}}}")
        if custom_fields_config:
            for cid, field_obj in custom_fields_config.items():
                key = field_obj.get("name", "").lower().strip() if isinstance(field_obj, dict) else str(field_obj).lower().strip()
                if key not in self._custom:
                    self._custom[key] = None
                    self._logger.debug(f"Field '{key}' not found in deal data; set to None")

    def __getitem__(self, key):
        if key in super().keys():
            return super().__getitem__(key)
        if isinstance(key, str):
            lower_key = key.lower().strip()
            if lower_key in self._custom:
                stored = self._custom[lower_key]
                return stored.get("value") if isinstance(stored, dict) else stored
        if isinstance(key, int):
            if key in self._custom:
                stored = self._custom[key]
                return stored.get("value") if isinstance(stored, dict) else stored
        raise KeyError(key)

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def get_field_type(self, key):
        """
        Определяет тип кастомного поля.
        
        :param key: Название поля (строка) или ID поля (integer).
        :return: Строка с типом поля ('text', 'select', 'numeric', 'checkbox', и т.д.) 
                 или None, если поле не найдено или тип не определён.
        """
        field_def = None
        
        # Получаем определение поля из конфигурации
        if self._custom_config:
            if isinstance(key, int):
                field_def = self._custom_config.get(key)
            else:
                for fid, fdef in self._custom_config.items():
                    if isinstance(fdef, dict) and fdef.get("name", "").lower().strip() == key.lower().strip():
                        field_def = fdef
                        break
        
        # Если нашли определение, возвращаем его тип
        if field_def and isinstance(field_def, dict):
            return field_def.get("type")
        
        # Если конфигурации нет или поле не найдено, пробуем определить тип по данным
        stored = None
        if isinstance(key, str):
            lower_key = key.lower().strip()
            if lower_key in self._custom:
                stored = self._custom[lower_key]
        elif isinstance(key, int):
            if key in self._custom:
                stored = self._custom[key]
                
        if isinstance(stored, dict) and "enum_id" in stored:
            return "select"
        
        return None

    def get_id(self, key, default=None):
        """
        Возвращает идентификатор выбранного варианта (enum_id) для кастомного поля типа select.
        Для полей других типов возвращает их значение, как метод get().
        
        Если значение enum_id отсутствует в данных, производится поиск в конфигурации кастомных полей,
        сравнение значения выполняется без учёта регистра и пробелов.

        :param key: Название поля (строка) или ID поля (integer).
        :param default: Значение по умолчанию, если enum_id не найден.
        :return: Для полей типа select - идентификатор варианта (целое число).
                 Для других типов полей - значение поля. 
                 Если поле не найдено - default.
        """
        field_type = self.get_field_type(key)
        
        # Если это не поле списка, возвращаем значение как get()
        if field_type is not None and field_type != "select":
            return self.get(key, default)
            
        stored = None
        if isinstance(key, str):
            lower_key = key.lower().strip()
            if lower_key in self._custom:
                stored = self._custom[lower_key]
        elif isinstance(key, int):
            if key in self._custom:
                stored = self._custom[key]
        if isinstance(stored, dict):
            enum_id = stored.get("enum_id")
            if enum_id is not None:
                return enum_id
            if self._custom_config:
                field_def = None
                if isinstance(key, int):
                    field_def = self._custom_config.get(key)
                else:
                    for fid, fdef in self._custom_config.items():
                        if fdef.get("name", "").lower().strip() == key.lower().strip():
                            field_def = fdef
                            break
                if field_def:
                    enums = field_def.get("enums") or []
                    for enum in enums:
                        if enum.get("value", "").lower().strip() == stored.get("value", "").lower().strip():
                            return enum.get("id", default)
        
        # Если это не поле типа select или не удалось найти enum_id, 
        # возвращаем значение поля
        return self.get(key, default)

class CacheConfig:
    """
    Конфигурация кэширования для AmoCRMClient.

    Параметры:
        enabled (bool): Включено ли кэширование
        storage (str): Тип хранилища ('file' или 'memory')
        base_dir (str): Базовая директория для кэша (по умолчанию ~/.amocrm/cache/)
        file (str): Путь к файлу кэша (устаревший, для обратной совместимости)
        lifetime_hours (int|dict|None): Время жизни кэша в часах
            - int: одинаковое время для всех типов данных
            - dict: разное время для каждого типа (например, {'pipelines': 168, 'users': 24})
            - None: бесконечный кэш
    """
    DEFAULT_LIFETIMES = {
        'custom_fields': 24,
        'pipelines': 168,  # 7 дней
        'users': 24,
    }

    def __init__(self, enabled=True, storage='file', base_dir=None, file=None, lifetime_hours='default'):
        self.enabled = enabled
        self.storage = storage.lower()
        self.base_dir = base_dir or os.path.join(os.path.expanduser('~'), '.amocrm', 'cache')
        self.file = file  # Для обратной совместимости с custom fields

        # Обработка lifetime_hours: может быть int, dict, None, или 'default'
        if lifetime_hours == 'default':
            # Используем дефолтные значения
            self.lifetime_hours = self.DEFAULT_LIFETIMES.copy()
        elif isinstance(lifetime_hours, dict):
            # Объединяем дефолтные значения с пользовательскими
            self.lifetime_hours = {**self.DEFAULT_LIFETIMES, **lifetime_hours}
        elif lifetime_hours is None:
            # Бесконечный кэш для всех типов
            self.lifetime_hours = None
        elif isinstance(lifetime_hours, (int, float)):
            # Одинаковое время для всех типов
            self.lifetime_hours = {
                'custom_fields': lifetime_hours,
                'pipelines': lifetime_hours,
                'users': lifetime_hours,
            }
        else:
            # Fallback на дефолтные значения
            self.lifetime_hours = self.DEFAULT_LIFETIMES.copy()

    def get_lifetime(self, data_type):
        """
        Получает время жизни кэша для указанного типа данных.

        :param data_type: Тип данных ('custom_fields', 'pipelines', 'users')
        :return: Время жизни в часах или None для бесконечного кэша
        """
        if self.lifetime_hours is None:
            return None
        if isinstance(self.lifetime_hours, dict):
            return self.lifetime_hours.get(data_type, 24)
        return self.lifetime_hours

    @classmethod
    def disabled(cls):
        """Создает конфигурацию с отключенным кэшированием"""
        return cls(enabled=False)

    @classmethod
    def memory_only(cls, lifetime_hours=24):
        """Создает конфигурацию с кэшированием только в памяти"""
        return cls(enabled=True, storage='memory', lifetime_hours=lifetime_hours)

    @classmethod
    def file_cache(cls, file=None, base_dir=None, lifetime_hours='default'):
        """Создает конфигурацию с файловым кэшированием"""
        return cls(enabled=True, storage='file', base_dir=base_dir, file=file, lifetime_hours=lifetime_hours)

class AmoCRMClient:
    """
    Клиент для работы с API amoCRM.

    Основные функции:
      - load_token: Загружает и проверяет токен авторизации.
      - _make_request: Выполняет HTTP-запрос с учетом ограничения по скорости.
      - get_deal_by_id: Получает данные сделки по ID и возвращает объект Deal.
      - get_custom_fields_mapping: Загружает и кэширует список кастомных полей.
      - find_custom_field_id: Ищет кастомное поле по его названию.
      - update_lead: Обновляет сделку, включая стандартные и кастомные поля.

    Дополнительно можно задать уровень логирования через параметр log_level,
    либо полностью отключить логирование, установив disable_logging=True.
    """
    def __init__(
        self,
        base_url,
        token_file=None,
        cache_config=None,
        log_level=logging.INFO,
        disable_logging=False,
        rate_limit: Optional[int] = None,
        *,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        redirect_uri: Optional[str] = None,
    ):
        """
        Инициализирует клиента, задавая базовый URL, токен авторизации и настройки кэша для кастомных полей.

        :param base_url: Базовый URL API amoCRM.
        :param token_file: Файл, содержащий токен авторизации.
        :param cache_config: Конфигурация кэширования (объект CacheConfig или None для значений по умолчанию)
        :param log_level: Уровень логирования (например, logging.DEBUG, logging.INFO).
        :param disable_logging: Если True, логирование будет отключено.
        :param rate_limit: Максимальное количество запросов в секунду (по умолчанию 7).
        """
        self.base_url = base_url.rstrip('/')
        self.rate_limit = rate_limit if rate_limit is not None else DEFAULT_RATE_LIMIT
        self._request_times: List[float] = []  # Для отслеживания времени запросов
        domain = self.base_url.split("//")[-1].split(".")[0]
        self.domain = domain
        self.token_file = token_file or os.path.join(os.path.expanduser('~'), '.amocrm_token.json')

        # OAuth2 credentials (используются для авто‑refresh токена)
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        
        # Создаем логгер для конкретного экземпляра клиента
        self.logger = logging.getLogger(f"{__name__}.{self.domain}")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.propagate = False  # Отключаем передачу логов в родительский логгер
        
        if disable_logging:
            self.logger.setLevel(logging.CRITICAL + 1)  # Выше, чем любой стандартный уровень
        else:
            self.logger.setLevel(log_level)
        
        # Настройка кэширования
        if cache_config is None:
            self.cache_config = CacheConfig()
        else:
            self.cache_config = cache_config
            
        # Установка файла кэша, если используется файловое хранилище
        if self.cache_config.enabled and self.cache_config.storage == 'file':
            if not self.cache_config.file:
                self.cache_config.file = f"custom_fields_cache_{self.domain}.json"
        
        self.logger.debug(f"AmoCRMClient initialized for domain {self.domain}")

        self.token = None
        self.refresh_token = None
        self.expires_at = None
        self.load_token()

        # Memory caches для разных типов данных
        self._custom_fields_mapping = None
        self._pipelines_cache = None
        self._users_cache = None

    def load_token(self):
        """
        Загружает токен авторизации из файла или строки, проверяет его срок действия.
        При наличии refresh_token и учётных данных пробует обновить токен.

        :return: Действительный access_token.
        :raises Exception: Если токен не найден или истёк и нет возможности обновить.
        """
        data = None
        if os.path.exists(self.token_file):
            with open(self.token_file, 'r') as f:
                data = json.load(f)
            self.logger.debug(f"Token loaded from file: {self.token_file}")
        else:
            try:
                data = json.loads(self.token_file)
                self.logger.debug("Token parsed from provided string.")
            except Exception as e:
                raise Exception("Токен не найден и не удалось распарсить переданное содержимое.") from e

        self.refresh_token = data.get('refresh_token', self.refresh_token)
        self.client_id = data.get('client_id', self.client_id)
        self.client_secret = data.get('client_secret', self.client_secret)
        self.redirect_uri = data.get('redirect_uri', self.redirect_uri)

        expires_at_str = data.get('expires_at')
        expires_at = None
        if expires_at_str:
            try:
                expires_at = datetime.fromisoformat(expires_at_str).timestamp()
            except Exception:
                try:
                    expires_at = float(expires_at_str)
                except Exception:
                    expires_at = None
        self.expires_at = expires_at

        access_token = data.get('access_token')
        if access_token and expires_at and time.time() < expires_at:
            self.logger.debug("Token is valid.")
            self.token = access_token
            return access_token

        if self.refresh_token and self.client_id and self.client_secret and self.redirect_uri:
            self.logger.info("Access token истёк, пробую обновить через refresh_token…")
            return self._refresh_access_token()

        raise Exception("Токен истёк или некорректен, и нет данных для refresh_token. Обновите токен.")

    def _wait_for_rate_limit(self):
        """Ожидает, если превышен лимит запросов в секунду."""
        now = time.time()
        # Удаляем запросы старше 1 секунды
        self._request_times = [t for t in self._request_times if now - t < 1.0]

        if len(self._request_times) >= self.rate_limit:
            # Ждём до освобождения слота
            sleep_time = 1.0 - (now - self._request_times[0])
            if sleep_time > 0:
                self.logger.debug(f"Rate limit: ожидание {sleep_time:.3f}с (лимит {self.rate_limit} req/s)")
                time.sleep(sleep_time)
            # Очищаем старые записи после ожидания
            now = time.time()
            self._request_times = [t for t in self._request_times if now - t < 1.0]

        self._request_times.append(time.time())

    def _make_request(self, method, endpoint, params=None, data=None, timeout=10):
        """
        Выполняет HTTP-запрос к API amoCRM с учетом ограничения по скорости (rate limit).

        :param method: HTTP-метод (GET, PATCH, POST, DELETE и т.д.).
        :param endpoint: Конечная точка API (начинается с /api/v4/).
        :param params: GET-параметры запроса.
        :param data: Данные, отправляемые в JSON-формате.
        :param timeout: Тайм‑аут запроса в секундах (по умолчанию 10).
        :return: Ответ в формате JSON или None (если статус 204).
        :raises Exception: При получении кода ошибки, отличного от 200/204.
        """
        # Ручной rate limiting
        self._wait_for_rate_limit()

        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        self.logger.debug(f"Making {method} request to {url} with params {params} and data {data}")
        response = requests.request(method, url, headers=headers, params=params, json=data, timeout=timeout)

        if response.status_code == 401 and self.refresh_token:
            self.logger.info("Получен 401, пробую обновить токен и повторить запрос…")
            self._refresh_access_token()
            headers["Authorization"] = f"Bearer {self.token}"
            response = requests.request(method, url, headers=headers, params=params, json=data, timeout=timeout)

        if response.status_code not in (200, 204):
            self.logger.error(f"Request error {response.status_code}: {response.text}")
            raise Exception(f"Ошибка запроса: {response.status_code}, {response.text}")
        if response.status_code == 204:
            return None
        return response.json()

    def _refresh_access_token(self):
        """Обновляет access_token по refresh_token и сохраняет его в token_file."""
        if not all([self.refresh_token, self.client_id, self.client_secret, self.redirect_uri]):
            raise Exception("Нельзя обновить токен: отсутствует refresh_token или client_id/client_secret/redirect_uri")

        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "redirect_uri": self.redirect_uri,
        }
        token_url = f"{self.base_url}/oauth2/access_token"
        self.logger.debug(f"Refreshing token via {token_url}")
        resp = requests.post(token_url, json=payload, timeout=10)
        if resp.status_code != 200:
            self.logger.error(f"Не удалось обновить токен: {resp.status_code} {resp.text}")
            raise Exception(f"Не удалось обновить токен: {resp.status_code}")

        data = resp.json() or {}
        access_token = data.get("access_token")
        refresh_token = data.get("refresh_token", self.refresh_token)
        expires_in = data.get("expires_in")
        if not access_token:
            raise Exception("Ответ на refresh не содержит access_token")

        expires_at = None
        if expires_in:
            expires_at = time.time() + int(expires_in)

        self.token = access_token
        self.refresh_token = refresh_token
        self.expires_at = expires_at

        if self.token_file:
            try:
                with open(self.token_file, "w") as f:
                    json.dump({
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "expires_at": datetime.fromtimestamp(expires_at).isoformat() if expires_at else None,
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "redirect_uri": self.redirect_uri,
                    }, f)
                self.logger.debug(f"Новый токен сохранён в {self.token_file}")
            except Exception as exc:
                self.logger.error(f"Не удалось сохранить обновлённый токен: {exc}")

        return access_token

    def _extract_account_name(self):
        """
        Извлекает имя аккаунта из пути к файлу токена.

        Примеры:
            ~/.amocrm/accounts/bneginskogo.json -> default
            ~/.amocrm/accounts/bneginskogo_eng.json -> eng
            ~/.amocrm/accounts/bneginskogo_thai.json -> thai

        :return: Имя аккаунта или 'default'
        """
        if not self.token_file:
            return 'default'

        # Получаем имя файла без расширения
        filename = os.path.splitext(os.path.basename(self.token_file))[0]

        # Проверяем паттерн: base_name или base_name_account
        parts = filename.split('_')
        if len(parts) > 1:
            # Последняя часть - это имя аккаунта (eng, thai и т.д.)
            return parts[-1]

        return 'default'

    def _get_cache_file_path(self, data_type):
        """
        Получает путь к файлу кэша для указанного типа данных.

        :param data_type: Тип данных ('custom_fields', 'pipelines', 'users')
        :return: Путь к файлу кэша
        """
        # Для custom_fields используем старый путь, если указан (обратная совместимость)
        if data_type == 'custom_fields' and self.cache_config.file:
            return self.cache_config.file

        # Создаем директорию кэша, если не существует
        os.makedirs(self.cache_config.base_dir, exist_ok=True)

        # Формируем имя файла: {account}_{data_type}.json
        account_name = self._extract_account_name()
        cache_filename = f"{account_name}_{data_type}.json"
        return os.path.join(self.cache_config.base_dir, cache_filename)

    def _is_cache_valid(self, data_type, last_updated):
        """
        Проверяет, валиден ли кэш на основе времени последнего обновления.

        :param data_type: Тип данных ('custom_fields', 'pipelines', 'users')
        :param last_updated: Время последнего обновления (timestamp)
        :return: True если кэш валиден, False если устарел
        """
        lifetime = self.cache_config.get_lifetime(data_type)

        if lifetime is None:
            # Бесконечный кэш
            return True

        # Проверяем срок жизни
        return time.time() - last_updated < lifetime * 3600

    def _save_cache(self, data_type, data):
        """
        Сохраняет данные в кэш.

        :param data_type: Тип данных ('custom_fields', 'pipelines', 'users')
        :param data: Данные для сохранения
        """
        if not self.cache_config.enabled:
            self.logger.debug(f"Caching disabled; {data_type} cache not saved.")
            return

        if self.cache_config.storage != 'file':
            self.logger.debug(f"Using memory caching; {data_type} cache not saved to file.")
            return

        cache_file = self._get_cache_file_path(data_type)
        cache_data = {
            "last_updated": time.time(),
            "data": data
        }

        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            self.logger.debug(f"{data_type} cache saved to {cache_file}")
        except Exception as e:
            self.logger.error(f"Failed to save {data_type} cache: {e}")

    def _load_cache(self, data_type):
        """
        Загружает данные из кэша.

        :param data_type: Тип данных ('custom_fields', 'pipelines', 'users')
        :return: Кэшированные данные или None
        """
        if not self.cache_config.enabled:
            self.logger.debug(f"Caching disabled; no {data_type} cache loaded.")
            return None

        if self.cache_config.storage != 'file':
            self.logger.debug(f"Using memory caching; {data_type} cache kept in memory only.")
            return None

        cache_file = self._get_cache_file_path(data_type)

        if not os.path.exists(cache_file):
            self.logger.debug(f"{data_type} cache file not found: {cache_file}")
            return None

        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            last_updated = cache_data.get("last_updated", 0)

            if not self._is_cache_valid(data_type, last_updated):
                self.logger.debug(f"{data_type} cache expired.")
                return None

            self.logger.debug(f"{data_type} cache loaded from {cache_file}")
            return cache_data.get("data")

        except Exception as e:
            self.logger.error(f"Error loading {data_type} cache: {e}")
            return None

    def _to_timestamp(self, value: Optional[Union[int, float, str, datetime]]) -> Optional[int]:
        """
        Преобразует значение даты/времени в Unix timestamp.
        Возвращает None, если значение не указано.
        """
        if value is None:
            return None
        if isinstance(value, datetime):
            return int(value.timestamp())
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str):
            try:
                return int(datetime.fromisoformat(value).timestamp())
            except ValueError as exc:
                raise ValueError(f"Не удалось преобразовать '{value}' в timestamp") from exc
        raise TypeError(f"Неподдерживаемый тип для timestamp: {type(value)}")

    def _format_filter_values(self, values: Optional[Union[int, Sequence[Union[int, str]], str]]) -> Optional[Union[str, Sequence[Union[int, str]]]]:
        """
        Преобразует значение или последовательность значений для передачи в запрос.
        """
        if values is None:
            return None
        if isinstance(values, (list, tuple, set)):
            return [str(v) for v in values]
        return str(values)

    def _extract_collection(self, response: dict, data_path: Sequence[str]) -> list:
        """
        Извлекает коллекцию элементов из ответа API по указанному пути ключей.
        """
        data = response or {}
        for key in data_path:
            if not isinstance(data, dict):
                return []
            data = data.get(key)
            if data is None:
                return []
        if isinstance(data, list):
            return data
        return []

    def _iterate_paginated(
        self,
        endpoint: str,
        params: Optional[dict] = None,
        data_path: Sequence[str] = ("_embedded",),
    ) -> Iterator[dict]:
        """
        Возвращает генератор, проходящий по всем страницам ответа API и
        yielding элементы коллекции.
        """
        query = dict(params or {})
        query.setdefault("page", 1)
        query.setdefault("limit", 250)

        while True:
            response = self._make_request("GET", endpoint, params=query)
            if not response:
                break
            items = self._extract_collection(response, data_path)
            if not items:
                break
            for item in items:
                yield item

            total_pages = response.get("_page_count")
            if total_pages is not None:
                has_next = query["page"] < total_pages
            else:
                links = response.get("_links") or {}
                next_link = links.get("next") if isinstance(links, dict) else None
                has_next = bool(next_link)
            if not has_next:
                break
            query["page"] += 1

    def iter_leads(
        self,
        updated_from: Optional[Union[int, float, str, datetime]] = None,
        updated_to: Optional[Union[int, float, str, datetime]] = None,
        pipeline_ids: Optional[Union[int, Sequence[Union[int, str]]]] = None,
        include_contacts: bool = False,
        include: Optional[Union[str, Sequence[str]]] = None,
        limit: int = 250,
        extra_params: Optional[dict] = None,
    ) -> Iterator[dict]:
        """
        Итератор сделок с фильтрацией по диапазону обновления и воронкам.
        """
        params = {"limit": limit, "page": 1}
        start_ts = self._to_timestamp(updated_from)
        end_ts = self._to_timestamp(updated_to)
        if start_ts is not None:
            params["filter[updated_at][from]"] = start_ts
        if end_ts is not None:
            params["filter[updated_at][to]"] = end_ts
        pipeline_param = self._format_filter_values(pipeline_ids)
        if pipeline_param:
            params["filter[pipeline_id]"] = pipeline_param

        include_parts: List[str] = []
        if include_contacts:
            include_parts.append("contacts")
        if include:
            if isinstance(include, str):
                include_parts.append(include)
            else:
                include_parts.extend([str(item) for item in include])
        if include_parts:
            params["with"] = ",".join(sorted(set(include_parts)))
        if extra_params:
            params.update(extra_params)

        yield from self._iterate_paginated(
            "/api/v4/leads", params=params, data_path=("_embedded", "leads")
        )

    def fetch_leads(self, *args, **kwargs) -> List[dict]:
        """
        Возвращает список сделок. Обёртка над iter_leads.
        """
        return list(self.iter_leads(*args, **kwargs))

    def iter_contacts(
        self,
        updated_from: Optional[Union[int, float, str, datetime]] = None,
        updated_to: Optional[Union[int, float, str, datetime]] = None,
        contact_ids: Optional[Union[int, Sequence[Union[int, str]]]] = None,
        limit: int = 250,
        extra_params: Optional[dict] = None,
    ) -> Iterator[dict]:
        """
        Итератор контактов с фильтрацией по диапазону обновления или списку ID.
        """
        params = {"limit": limit, "page": 1}
        start_ts = self._to_timestamp(updated_from)
        end_ts = self._to_timestamp(updated_to)
        if start_ts is not None:
            params["filter[updated_at][from]"] = start_ts
        if end_ts is not None:
            params["filter[updated_at][to]"] = end_ts
        contact_param = self._format_filter_values(contact_ids)
        if contact_param:
            params["filter[id][]"] = contact_param
        if extra_params:
            params.update(extra_params)

        yield from self._iterate_paginated(
            "/api/v4/contacts", params=params, data_path=("_embedded", "contacts")
        )

    def fetch_contacts(self, *args, **kwargs) -> List[dict]:
        """
        Возвращает список контактов. Обёртка над iter_contacts.
        """
        return list(self.iter_contacts(*args, **kwargs))

    def get_contact_by_id(self, contact_id: Union[int, str], include: Optional[Union[str, Sequence[str]]] = None) -> dict:
        """
        Получает данные контакта по его ID.
        """
        endpoint = f"/api/v4/contacts/{contact_id}"
        params = {}
        if include:
            if isinstance(include, str):
                params["with"] = include
            else:
                params["with"] = ",".join(str(item) for item in include)
        data = self._make_request("GET", endpoint, params=params)
        if not data or not isinstance(data, dict) or "id" not in data:
            raise Exception(f"Contact {contact_id} not found or invalid response.")
        return data

    def iter_notes(
        self,
        entity: str = "lead",
        updated_from: Optional[Union[int, float, str, datetime]] = None,
        updated_to: Optional[Union[int, float, str, datetime]] = None,
        note_type: Optional[Union[str, Sequence[str]]] = None,
        entity_ids: Optional[Union[int, Sequence[Union[int, str]]]] = None,
        limit: int = 250,
        extra_params: Optional[dict] = None,
    ) -> Iterator[dict]:
        """
        Итератор примечаний для заданной сущности.
        """
        mapping = {
            "lead": "leads",
            "contact": "contacts",
            "company": "companies",
            "customer": "customers",
        }
        plural = mapping.get(entity.lower(), entity.lower() + "s")
        endpoint = f"/api/v4/{plural}/notes"

        params = {"limit": limit, "page": 1}
        start_ts = self._to_timestamp(updated_from)
        end_ts = self._to_timestamp(updated_to)
        if start_ts is not None:
            params["filter[updated_at][from]"] = start_ts
        if end_ts is not None:
            params["filter[updated_at][to]"] = end_ts
        note_type_param = self._format_filter_values(note_type)
        if note_type_param:
            params["filter[note_type]"] = note_type_param
        entity_param = self._format_filter_values(entity_ids)
        if entity_param:
            params["filter[entity_id]"] = entity_param
        if extra_params:
            params.update(extra_params)

        yield from self._iterate_paginated(
            endpoint, params=params, data_path=("_embedded", "notes")
        )

    def fetch_notes(self, *args, **kwargs) -> List[dict]:
        """
        Возвращает список примечаний. Обёртка над iter_notes.
        """
        return list(self.iter_notes(*args, **kwargs))

    def iter_events(
        self,
        entity: Optional[str] = None,
        entity_ids: Optional[Union[int, Sequence[Union[int, str]]]] = None,
        event_type: Optional[Union[str, Sequence[str]]] = None,
        created_from: Optional[Union[int, float, str, datetime]] = None,
        created_to: Optional[Union[int, float, str, datetime]] = None,
        limit: int = 250,
        extra_params: Optional[dict] = None,
    ) -> Iterator[dict]:
        """
        Итератор событий с фильтрацией по сущности, типам и диапазону дат.
        """
        params = {"limit": limit, "page": 1}
        if entity:
            params["filter[entity]"] = entity
        entity_param = self._format_filter_values(entity_ids)
        if entity_param:
            params["filter[entity_id]"] = entity_param
        event_type_param = self._format_filter_values(event_type)
        if event_type_param:
            params["filter[type]"] = event_type_param
        start_ts = self._to_timestamp(created_from)
        end_ts = self._to_timestamp(created_to)
        if start_ts is not None:
            params["filter[created_at][from]"] = start_ts
        if end_ts is not None:
            params["filter[created_at][to]"] = end_ts
        if extra_params:
            params.update(extra_params)

        yield from self._iterate_paginated(
            "/api/v4/events", params=params, data_path=("_embedded", "events")
        )

    def fetch_events(self, *args, **kwargs) -> List[dict]:
        """
        Возвращает список событий. Обёртка над iter_events.
        """
        return list(self.iter_events(*args, **kwargs))

    def iter_users(
        self,
        limit: int = 250,
        extra_params: Optional[dict] = None,
    ) -> Iterator[dict]:
        """
        Итератор пользователей аккаунта.
        """
        params = {"limit": limit, "page": 1}
        if extra_params:
            params.update(extra_params)
        yield from self._iterate_paginated(
            "/api/v4/users", params=params, data_path=("_embedded", "users")
        )

    def fetch_users(self, *args, **kwargs) -> List[dict]:
        """
        Возвращает список пользователей. Обёртка над iter_users.
        """
        return list(self.iter_users(*args, **kwargs))

    def get_users_cached(self, force_update=False):
        """
        Возвращает список пользователей с кэшированием (по умолчанию 24 часа).

        Использует трехуровневое кэширование:
        1. Memory cache (самый быстрый)
        2. File cache (персистентный)
        3. API request (если кэш устарел или отсутствует)

        :param force_update: Если True, игнорирует кэш и загружает данные из API
        :return: Список пользователей
        """
        # 1. Проверяем memory cache
        if not force_update and self._users_cache is not None:
            self.logger.debug("Using memory-cached users.")
            return self._users_cache

        # 2. Проверяем file cache
        if not force_update and self.cache_config.enabled:
            cached_data = self._load_cache('users')
            if cached_data is not None:
                self._users_cache = cached_data
                self.logger.debug("Users loaded from file cache.")
                return cached_data

        # 3. Загружаем из API
        self.logger.debug("Fetching users from API...")
        users = self.fetch_users()

        # Сохраняем в memory cache
        self._users_cache = users

        # Сохраняем в file cache
        if self.cache_config.enabled:
            self._save_cache('users', users)

        self.logger.debug(f"Fetched {len(users)} users from API.")
        return users

    def iter_pipelines(
        self,
        limit: int = 250,
        extra_params: Optional[dict] = None,
    ) -> Iterator[dict]:
        """
        Итератор воронок со статусами.
        """
        params = {"limit": limit, "page": 1}
        if extra_params:
            params.update(extra_params)
        yield from self._iterate_paginated(
            "/api/v4/leads/pipelines", params=params, data_path=("_embedded", "pipelines")
        )

    def fetch_pipelines(self, *args, **kwargs) -> List[dict]:
        """
        Возвращает список воронок. Обёртка над iter_pipelines.
        """
        return list(self.iter_pipelines(*args, **kwargs))

    def get_deal_by_id(self, deal_id, skip_fields_mapping=False):
        """
        Получает данные сделки по её ID и возвращает объект Deal.
        Если данные отсутствуют или имеют неверную структуру, выбрасывается исключение.
        
        :param deal_id: ID сделки для получения
        :param skip_fields_mapping: Если True, не загружает справочник кастомных полей
                                   (используйте для работы только с ID полей)
        :return: Объект Deal с данными сделки
        """
        endpoint = f"/api/v4/leads/{deal_id}"
        params = {'with': 'contacts,companies,catalog_elements,loss_reason,tags'}
        data = self._make_request("GET", endpoint, params=params)
        
        # Проверяем, что получили данные и что они содержат ключ "id"
        if not data or not isinstance(data, dict) or "id" not in data:
            self.logger.error(f"Deal {deal_id} not found or invalid response: {data}")
            raise Exception(f"Deal {deal_id} not found or invalid response.")

        custom_config = None if skip_fields_mapping else self.get_custom_fields_mapping()
        self.logger.debug(f"Deal {deal_id} data received (содержимое полей не выводится полностью).")
        return Deal(data, custom_fields_config=custom_config, logger=self.logger)

    def _save_custom_fields_cache(self, mapping):
        """
        Сохраняет кэш кастомных полей в файл, если используется файловый кэш.
        Если кэширование отключено или выбран кэш в памяти, операция пропускается.
        """
        if not self.cache_config.enabled:
            self.logger.debug("Caching disabled; cache not saved.")
            return
        if self.cache_config.storage != 'file':
            self.logger.debug("Using memory caching; no file cache saved.")
            return
        cache_data = {"last_updated": time.time(), "mapping": mapping}
        with open(self.cache_config.file, "w") as f:
            json.dump(cache_data, f)
        self.logger.debug(f"Custom fields cache saved to {self.cache_config.file}")

    def _load_custom_fields_cache(self):
        """
        Загружает кэш кастомных полей из файла, если используется файловый кэш.
        Если кэширование отключено или выбран кэш в памяти, возвращает None.
        """
        if not self.cache_config.enabled:
            self.logger.debug("Caching disabled; no cache loaded.")
            return None
        if self.cache_config.storage != 'file':
            self.logger.debug("Using memory caching; cache will be kept in memory only.")
            return None
        if os.path.exists(self.cache_config.file):
            with open(self.cache_config.file, "r") as f:
                try:
                    cache_data = json.load(f)
                    self.logger.debug("Custom fields cache loaded successfully.")
                    return cache_data
                except Exception as e:
                    self.logger.error(f"Error loading cache: {e}")
                    return None
        return None

    def get_custom_fields_mapping(self, force_update=False):
        """
        Возвращает словарь отображения кастомных полей для сделок с кэшированием (по умолчанию 24 часа).

        Использует трехуровневое кэширование:
        1. Memory cache (самый быстрый)
        2. File cache (персистентный)
        3. API request (если кэш устарел или отсутствует)

        :param force_update: Если True, игнорирует кэш и загружает данные из API
        :return: Словарь с кастомными полями (ключ - field_id, значение - объект поля)
        """
        # 1. Проверяем memory cache
        if not force_update and self._custom_fields_mapping is not None:
            self.logger.debug("Using memory-cached custom fields mapping.")
            return self._custom_fields_mapping

        # 2. Проверяем file cache (с поддержкой старого формата)
        if not force_update and self.cache_config.enabled:
            # Пробуем новый формат
            cached_data = self._load_cache('custom_fields')
            if cached_data is not None:
                self._custom_fields_mapping = cached_data
                self.logger.debug("Custom fields loaded from file cache (new format).")
                return cached_data

            # Пробуем старый формат для обратной совместимости
            legacy_cache = self._load_custom_fields_cache()
            if legacy_cache:
                mapping = legacy_cache.get("mapping")
                if mapping:
                    self._custom_fields_mapping = mapping
                    self.logger.debug("Custom fields loaded from legacy cache format.")
                    # Мигрируем в новый формат
                    self._save_cache('custom_fields', mapping)
                    return mapping

        # 3. Загружаем из API
        self.logger.debug("Fetching custom fields from API...")
        mapping = {}
        page = 1
        total_pages = 1
        while page <= total_pages:
            endpoint = f"/api/v4/leads/custom_fields?limit=250&page={page}"
            response = self._make_request("GET", endpoint)
            if response and "_embedded" in response and "custom_fields" in response["_embedded"]:
                for field in response["_embedded"]["custom_fields"]:
                    mapping[field["id"]] = field
                total_pages = response.get("_page_count", page)
                self.logger.debug(f"Fetched page {page} of {total_pages}")
                page += 1
            else:
                break

        # Сохраняем в memory cache
        self._custom_fields_mapping = mapping

        # Сохраняем в file cache (новый формат)
        if self.cache_config.enabled:
            self._save_cache('custom_fields', mapping)

        self.logger.debug(f"Fetched {len(mapping)} custom fields from API.")
        return mapping

    def find_custom_field_id(self, search_term):
        """
        Ищет кастомное поле по заданному названию (или части названия).

        :param search_term: Строка для поиска по имени поля.
        :return: Кортеж (field_id, field_obj) если найдено, иначе (None, None).
        """
        mapping = self.get_custom_fields_mapping()
        search_term_lower = search_term.lower().strip()
        for key, field_obj in mapping.items():
            if isinstance(field_obj, dict):
                name = field_obj.get("name", "").lower().strip()
            else:
                name = str(field_obj).lower().strip()
            if search_term_lower == name or search_term_lower in name:
                self.logger.debug(f"Found custom field '{name}' with id {key}")
                return int(key), field_obj
        self.logger.debug(f"Custom field containing '{search_term}' not found.")
        return None, None

    def update_lead(self, lead_id, update_fields: dict, tags_to_add: list = None, tags_to_delete: list = None):
        """
        Обновляет сделку, задавая новые значения для стандартных и кастомных полей.

        Для кастомных полей:
          - Если значение передается как целое число, оно интерпретируется как идентификатор варианта (enum_id)
            для полей типа select.
          - Если значение передается как строка, используется ключ "value".

        :param lead_id: ID сделки, которую нужно обновить.
        :param update_fields: Словарь с полями для обновления. Ключи могут быть стандартными или названием кастомного поля.
        :param tags_to_add: Список тегов для добавления к сделке.
        :param tags_to_delete: Список тегов для удаления из сделки.
        :return: Ответ API в формате JSON.
        :raises Exception: Если одно из кастомных полей не найдено.
        """
        payload = {}
        standard_fields = {
            "name", "price", "status_id", "pipeline_id", "created_by", "updated_by",
            "closed_at", "created_at", "updated_at", "loss_reason_id", "responsible_user_id"
        }
        custom_fields = []
        for key, value in update_fields.items():
            if key in standard_fields:
                payload[key] = value
                self.logger.debug(f"Standard field {key} set to {value}")
            else:
                if isinstance(value, int):
                    field_value_dict = {"enum_id": value}
                else:
                    field_value_dict = {"value": value}
                try:
                    field_id = int(key)
                    custom_fields.append({"field_id": field_id, "values": [field_value_dict]})
                    self.logger.debug(f"Custom field by id {field_id} set to {value}")
                except ValueError:
                    field_id, field_obj = self.find_custom_field_id(key)
                    if field_id is not None:
                        custom_fields.append({"field_id": field_id, "values": [field_value_dict]})
                        self.logger.debug(f"Custom field '{key}' found with id {field_id} set to {value}")
                    else:
                        raise Exception(f"Custom field '{key}' не найден.")
        if custom_fields:
            payload["custom_fields_values"] = custom_fields
        if tags_to_add:
            payload["tags_to_add"] = tags_to_add
        if tags_to_delete:
            payload["tags_to_delete"] = tags_to_delete
        self.logger.debug("Update payload for lead {} prepared (содержимое payload не выводится полностью).".format(lead_id))
        endpoint = f"/api/v4/leads/{lead_id}"
        response = self._make_request("PATCH", endpoint, data=payload)
        self.logger.debug("Update response received.")
        return response
    
    def get_entity_notes(self, entity, entity_id, get_all=False, note_type=None, extra_params=None):
        """
        Получает список примечаний для указанной сущности и её ID.

        Используется эндпоинт:
        GET /api/v4/{entity_plural}/{entity_id}/notes

        :param entity: Тип сущности (например, 'lead', 'contact', 'company', 'customer' и т.д.).
                    Передаётся в единственном числе, для формирования конечной точки будет использована
                    таблица преобразования (например, 'lead' -> 'leads').
        :param entity_id: ID сущности.
        :param get_all: Если True, метод автоматически проходит по всем страницам пагинации.
        :param note_type: Фильтр по типу примечания. Может быть строкой (например, 'common') или списком строк.
        :param extra_params: Словарь дополнительных GET-параметров, если требуется.
        :return: Список примечаний (каждый элемент – словарь с данными примечания).
        """
        # Преобразуем тип сущности в форму во множественном числе (для известных типов)
        mapping = {
            'lead': 'leads',
            'contact': 'contacts',
            'company': 'companies',
            'customer': 'customers'
        }
        plural = mapping.get(entity.lower(), entity.lower() + "s")
        
        endpoint = f"/api/v4/{plural}/{entity_id}/notes"
        params = {
            "page": 1,
            "limit": 250
        }
        if note_type is not None:
            params["filter[note_type]"] = note_type
        if extra_params:
            params.update(extra_params)
        
        notes = []
        while True:
            response = self._make_request("GET", endpoint, params=params)
            if response and "_embedded" in response and "notes" in response["_embedded"]:
                notes.extend(response["_embedded"]["notes"])
            if not get_all:
                break
            total_pages = response.get("_page_count", params["page"])
            if params["page"] >= total_pages:
                break
            params["page"] += 1
        self.logger.debug(f"Retrieved {len(notes)} notes for {entity} {entity_id}")
        return notes

    def get_entity_note(self, entity, entity_id, note_id):
        """
        Получает расширенную информацию по конкретному примечанию для указанной сущности.

        Используется эндпоинт:
        GET /api/v4/{entity_plural}/{entity_id}/notes/{note_id}

        :param entity: Тип сущности (например, 'lead', 'contact', 'company', 'customer' и т.д.).
        :param entity_id: ID сущности.
        :param note_id: ID примечания.
        :return: Словарь с полной информацией о примечании.
        :raises Exception: При ошибке запроса.
        """
        mapping = {
            'lead': 'leads',
            'contact': 'contacts',
            'company': 'companies',
            'customer': 'customers'
        }
        plural = mapping.get(entity.lower(), entity.lower() + "s")
        endpoint = f"/api/v4/{plural}/{entity_id}/notes/{note_id}"
        self.logger.debug(f"Fetching note {note_id} for {entity} {entity_id}")
        note_data = self._make_request("GET", endpoint)
        self.logger.debug(f"Note {note_id} for {entity} {entity_id} fetched successfully.")
        return note_data

    # Удобные обёртки для сделок и контактов:
    def get_deal_notes(self, deal_id, **kwargs):
        return self.get_entity_notes("lead", deal_id, **kwargs)

    def get_deal_note(self, deal_id, note_id):
        return self.get_entity_note("lead", deal_id, note_id)

    def get_contact_notes(self, contact_id, **kwargs):
        return self.get_entity_notes("contact", contact_id, **kwargs)

    def get_contact_note(self, contact_id, note_id):
        return self.get_entity_note("contact", contact_id, note_id)
    
    def get_entity_events(self, entity, entity_id=None, get_all=False, event_type=None, extra_params=None):
        """
        Получает список событий для указанной сущности.
        Если entity_id не указан (None), возвращает события для всех сущностей данного типа.

        :param entity: Тип сущности (например, 'lead', 'contact', 'company' и т.д.).
        :param entity_id: ID сущности или None для получения событий по всем сущностям данного типа.
        :param get_all: Если True, автоматически проходит по всем страницам пагинации.
        :param event_type: Фильтр по типу события. Может быть строкой или списком строк.
        :param extra_params: Словарь дополнительных GET-параметров.
        :return: Список событий (каждый элемент – словарь с данными события).
        """
        params = {
            'page': 1,
            'limit': 100,
            'filter[entity]': entity,
        }
        # Добавляем фильтр по ID, если он указан
        if entity_id is not None:
            params['filter[entity_id]'] = entity_id
        # Фильтр по типу события
        if event_type is not None:
            params['filter[type]'] = event_type
        if extra_params:
            params.update(extra_params)

        events = []
        while True:
            response = self._make_request("GET", "/api/v4/events", params=params)
            if response and "_embedded" in response and "events" in response["_embedded"]:
                events.extend(response["_embedded"]["events"])
            # Если не нужно получать все страницы, выходим
            if not get_all:
                break
            total_pages = response.get("_page_count", params['page'])
            if params['page'] >= total_pages:
                break
            params['page'] += 1
        return events

    # Удобные обёртки:
    def get_deal_events(self, deal_id, **kwargs):
        return self.get_entity_events("lead", deal_id, **kwargs)

    def get_contact_events(self, contact_id, **kwargs):
        return self.get_entity_events("contact", contact_id, **kwargs)

    def fetch_updated_leads_raw(
        self,
        pipeline_id,
        updated_from,
        updated_to=None,
        save_to_file=None,
        limit=250,
        include_contacts=False,
    ):
        """Возвращает сделки из указанной воронки, обновленные в заданный период.

        :param pipeline_id: ID воронки.
        :param updated_from: datetime, начиная с которого искать изменения.
        :param updated_to: datetime окончания диапазона (опционально).
        :param save_to_file: путь к файлу для сохранения результатов в формате JSON.
        :param limit: количество элементов на страницу (максимум 250).
        :param include_contacts: если True, в ответ будут включены данные контактов.
        :return: список словарей со сделками.
        """

        all_leads = self.fetch_leads(
            updated_from=updated_from,
            updated_to=updated_to,
            pipeline_ids=pipeline_id,
            include_contacts=include_contacts,
            limit=limit,
        )
        if save_to_file:
            with open(save_to_file, "w", encoding="utf-8") as f:
                json.dump(all_leads, f, ensure_ascii=False, indent=2)

        self.logger.debug(f"Fetched {len(all_leads)} leads from pipeline {pipeline_id}")
        return all_leads

    def get_event(self, event_id):
        """
        Получает подробную информацию по конкретному событию по его ID.
        
        Используется эндпоинт:
          GET /api/v4/events/{event_id}
        
        :param event_id: ID события.
        :return: Словарь с подробной информацией о событии.
        :raises Exception: При ошибке запроса.
        """
        endpoint = f"/api/v4/events/{event_id}"
        self.logger.debug(f"Fetching event with ID {event_id}")
        event_data = self._make_request("GET", endpoint)
        self.logger.debug(f"Event {event_id} details fetched successfully.")
        return event_data
    
    def get_pipelines(self):
        """
        Получает список всех воронок и их статусов из amoCRM.

        :return: Список словарей, где каждый словарь содержит данные воронки, а также, если присутствует, вложенные статусы.
        :raises Exception: Если данные не получены или структура ответа неверна.
        """
        pipelines = self.fetch_pipelines()
        if pipelines:
            self.logger.debug(f"Получено {len(pipelines)} воронок")
            return pipelines
        self.logger.error("Не удалось получить воронки из amoCRM")
        raise Exception("Ошибка получения воронок из amoCRM")

    def get_pipelines_cached(self, force_update=False):
        """
        Возвращает список воронок с кэшированием (по умолчанию 7 дней).

        Использует трехуровневое кэширование:
        1. Memory cache (самый быстрый)
        2. File cache (персистентный)
        3. API request (если кэш устарел или отсутствует)

        :param force_update: Если True, игнорирует кэш и загружает данные из API
        :return: Список воронок со статусами
        """
        # 1. Проверяем memory cache
        if not force_update and self._pipelines_cache is not None:
            self.logger.debug("Using memory-cached pipelines.")
            return self._pipelines_cache

        # 2. Проверяем file cache
        if not force_update and self.cache_config.enabled:
            cached_data = self._load_cache('pipelines')
            if cached_data is not None:
                self._pipelines_cache = cached_data
                self.logger.debug("Pipelines loaded from file cache.")
                return cached_data

        # 3. Загружаем из API
        self.logger.debug("Fetching pipelines from API...")
        pipelines = self.fetch_pipelines()

        # Сохраняем в memory cache
        self._pipelines_cache = pipelines

        # Сохраняем в file cache
        if self.cache_config.enabled:
            self._save_cache('pipelines', pipelines)

        self.logger.debug(f"Fetched {len(pipelines)} pipelines from API.")
        return pipelines

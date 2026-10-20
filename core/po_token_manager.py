# в этом файле использовано больше ИИ чем в других, могут быть ошибки, если что-то не так то пожалуйста сообщите мне об этом

import logging
import os
import platform
import stat
import subprocess

import requests
from path_utils import get_root_dir

# create a logger with the same name as the file (proxy_rotator)
logger = logging.getLogger(__name__)


class PotBinaryManager:
    """Отвечает за скачивание, запуск, остановку бинарников POT провайдера"""

    def __init__(self, port=4416):
        # сохранить параметры
        self._port = port

        # подготовка директории для кэша
        self._cache_dir = get_root_dir() / "cache" / "pot_bin"
        self._cache_dir.mkdir(parents=True, exist_ok=True)

        # путь к бинарнику
        self._binary_path = self._cache_dir / self._get_binary_name()

        # ссылка на запущенный процесс
        self._process = None

    def start(self) -> None:
        """Запустить bgutil-ytdlp-pot-provider в режиме HTTP-сервера"""
        logger.info("Starting bgutil-ytdlp-pot-provider on port %s", self._port)
        # убедится в том что перед запуском процесса точно будет существовать бинарник
        self._ensure_binary()
        # запустить процесс
        self._process = subprocess.Popen(
            [str(self._binary_path), "--port", str(self._port)]
        )

    def stop(self) -> None:
        """Корректно останавливает bgutil-ytdlp-pot-provider"""
        logger.info("Stopping bgutil-ytdlp-pot-provider")
        # если процесс не был запущен то просто выйти из метода
        if self._process is None:
            return
        # на Linux будет правильное завершение, на windows то же самое что просто kill
        self._process.terminate()
        # попробовать подождать 5 секунд до завершения дочернего процесса
        try:
            self._process.wait(timeout=5)
        # если время вышло то просто kill и ждать завершения процесса
        except subprocess.TimeoutExpired:
            self._process.kill()
            self._process.wait()
        # на всякий случай сделать None
        self._process = None

    def is_running(self) -> bool:
        """Проверяет запущен ли бинарник в данный момент"""
        return self._process is not None and self._process.poll() is None

    def _get_binary_name(self) -> str:
        """Возвращает имя подходящего бинарника для текущей OS и архитектуры"""
        # система (всегда нижний регистр)
        system = platform.system().lower()
        # архитектура (всегда нижний регистр)
        machine = platform.machine().lower()

        # карта для определения того какой бинарник нужен
        mapping = {
            ("linux", "x86_64"): "bgutil-pot-linux-x86_64",
            ("linux", "aarch64"): "bgutil-pot-linux-aarch64",
            ("windows", "amd64"): "bgutil-pot-windows-x86_64.exe",
            ("darwin", "x86_64"): "bgutil-pot-macos-x86_64",
            ("darwin", "arm64"): "bgutil-pot-macos-aarch64",
        }

        # получить имя с помощью карты на основе системы и архитектуры
        name = mapping.get((system, machine))
        # вывести в лог информацию о том какая платформа была обнаружена и какое имя бинарника было выбрано
        logger.debug("Detected platform: %s %s, binary name: %s", system, machine, name)
        # если имя не найдено то платформа не поддерживается и следует вернуть ошибку
        if name is None:
            raise RuntimeError(f"Unsupported platform: {system} {machine}")
        # если имя найдено то следует его вернуть
        return name

    def _get_download_url(self) -> str:
        """Возвращает url для скачивания последней версии бинарника"""
        # часть ссылки которая не меняется
        base = "https://github.com/jim60105/bgutil-ytdlp-pot-provider-rs/releases/latest/download"
        # добавить к base имя бинарника который зависит от OS и архитектуры и вернуть
        return f"{base}/{self._get_binary_name()}"

    def _ensure_binary(self) -> None:
        """Скачать бинарник если еще нет"""
        if not self._binary_path.exists():
            self._download_binary()

    def _download_binary(self) -> None:
        """Скачать бинарник а потом сделать исполняемым"""
        url = self._get_download_url()
        logger.info("Downloading a binary from: %s", url)

        # попытаться скачать бинарник
        try:
            # stream=True нужен для загрузки файла по частям
            response = requests.get(url, stream=True, timeout=120)
            # не позволяет продолжить если скачалось с ошибкой
            response.raise_for_status()

            # w - режим записи, wb - режим бинарной записи (используется тут)
            with open(self._binary_path, "wb") as f:
                # iter_content по кусочкам отдает файл
                f.writelines(response.iter_content(chunk_size=8192))

            # если не windows то разрешить выполнение файла
            if platform.system() != "Windows":
                # st содержит информацию о файле, st.st_mode содержит информацию о правах доступа
                st = os.stat(self._binary_path)
                # разрешить исполнять владельцу
                os.chmod(self._binary_path, st.st_mode | stat.S_IEXEC)
        # если не получилось скачать то:
        except (requests.RequestException, OSError) as e:
            # вывести ошибку
            logger.error("Failed to download binary file: %s", e)
            # удалить неполный файл если есть
            if self._binary_path.exists():
                self._binary_path.unlink()
            raise RuntimeError("Failed to download POT provider") from e


class PotClient:
    """HTTP-взаимодействие с запущенным сервером-провайдером."""

    def __init__(self, url="http://127.0.0.1:4416"):
        self._url = url
        # если в конце ссылки есть слэш то убрать его, чтобы не было двойного слэша при формировании url для ping
        self._url = self._url.rstrip("/")

    def ping(self) -> bool:
        """Проверяет доступность сервера-провайдера, возвращает True если доступен, иначе False"""
        try:
            # сделать GET-запрос на {ссылка}/ping с таймаутом 5 секунд
            response = requests.get(f"{self._url}/ping", timeout=5)
            # логгировать статус-код ответа
            logger.info("Ping response: %s", response.status_code)
            # если статус 200 то вернуть True, иначе False
            return response.status_code == 200
        except requests.RequestException as e:
            # логгировать ошибку (url и текст ошибки) и вернуть False
            logger.error("Failed to ping POT provider: %s, Error: %s", self._url, e)
            return False

    def invalidate_caches(self) -> bool:
        """Отправляет запрос на сервер-провайдер для очистки кэшей, возвращает True если успешно, иначе False"""
        try:
            # сделать POST-запрос на {ссылка}/invalidate_caches с таймаутом 5 секунд
            response = requests.post(f"{self._url}/invalidate_caches", timeout=5)
            # логгировать статус-код ответа
            logger.info("Invalidate caches response: %s", response.status_code)
            # если статус 200 то вернуть True, иначе False
            return response.status_code == 200
        except requests.RequestException as e:
            # логгировать ошибку (url и текст ошибки) и вернуть False
            logger.error(
                "Failed to invalidate caches on POT provider: %s, Error: %s",
                self._url,
                e,
            )
            return False

    def get_pot(
        self, content_binding: str, proxy: str, bypass_cache: bool = False
    ) -> str:
        """Отправляет запрос на сервер-провайдер для получения POT токена, возвращает токен если успешно, иначе None.
        Так как программа работает с прокси то это стоит тоже учитывать.

        Вот список аргументов и того за что они отвечают:
        * content_binding: str - Советую передавать video_id, но можно передавать и другие уникальные идентификаторы
        * proxy: str - URL прокси-сервера для использования при запросе
        * bypass_cache: bool - Флаг, указывающий на необходимость обхода кэша
        """
        # сформировать url для запроса
        url = f"{self._url}/get_pot"
        # сформировать тело запроса для POST-запроса
        payload = {
            "content_binding": content_binding,
            "proxy": proxy,
            "bypass_cache": bypass_cache,
        }
        try:
            # сделать POST-запрос на {ссылка}/get_pot с телом запроса payload и таймаутом 60 секунд
            response = requests.post(url, json=payload, timeout=60)
            # проверить статус-код ответа, если не 200 то вызвать исключение
            response.raise_for_status()
            # получить JSON-ответ и извлечь poToken
            data = response.json()
            token = data.get("poToken")
            # если токен есть то вывести в лог информацию о том что токен сгенерирован и когда он истекает, а потом вернуть токен
            if token:
                logger.info("POT token generated, expires at %s", data.get("expiresAt"))
                return token
            # если токена нет то вывести в лог предупреждение и вернуть None
            logger.warning("POT provider returned no poToken: %s", data)
            return None
        except requests.RequestException as e:
            # вывести в лог ошибку RequestException (url и текст ошибки) и вернуть None
            logger.error("Failed to get POT token: %s, Error: %s", self._url, e)
            return None
        except ValueError as e:  # ошибка парсинга JSON
            # вывести в лог ошибку ValueError (url и текст ошибки) и вернуть None
            logger.error("Failed to parse POT response as JSON: %s", e)
            return None

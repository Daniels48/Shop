import asyncio
import threading
import json
from datetime import datetime
from aiohttp import web, ClientSession

from PyQt5.QtCore import QObject, pyqtSignal


class PyQtHttpServer(QObject):
    """HTTP сервер для взаимодействия с 1С и другими клиентами"""
    request_received = pyqtSignal(str, dict)  # (endpoint, data)
    log_message = pyqtSignal(str)  # Лог сервера для GUI

    def __init__(self, host='localhost', port=8081, ip_target="localhost", port_target=8081):
        super().__init__()
        self.host = host
        self.port = port
        self.ip_target = ip_target
        self.port_target = port_target
        self.runner = None
        self.site = None
        self.is_running = False
        self.server_thread = None
        self._loop = None
        self._stop_event = None
        self.app = None  # Добавляем атрибут app

    # --- Основные endpoint'ы ---

    async def handle_add_product(self, request):
        """Получить товар от 1С"""
        try:
            data = await request.json()
        except Exception:
            data = {}
        msg = f"📦 /add_product -> {data}"
        self.log_message.emit(msg)  # Добавлен лог
        self.request_received.emit("/add_product", data)
        text_response = {"result": "ok", "message": "Product received"}
        self.log_message.emit(f"Ответ -> {text_response}")  # Добавлен лог
        return web.json_response(text_response)

    async def handle_pay(self, request):
        """Получить команду оплаты"""
        try:
            data = await request.json()
        except Exception:
            data = {}
        msg = f"💳 /pay -> {data}"
        self.log_message.emit(msg)
        self.request_received.emit("/pay", data)
        return web.json_response({"result": "ok", "message": "Payment started"})

    async def _post_json(self, url: str, data: dict):
        """Асинхронная отправка JSON POST-запроса"""
        async with ClientSession() as session:
            try:
                async with session.post(url, json=data, timeout=5) as resp:
                    reply = await resp.json()
                    msh = f"📤 POST -> {url} | ответ: {reply}"
                    self.log_message.emit(msh)
                    return reply
            except Exception as e:
                msge = f"⚠️ Ошибка при POST {url}: {e}"
                self.log_message.emit(msge)
                return None

    def send_post(self, data: dict):
        """Отправка JSON POST-запроса из любого потока"""
        if not self._loop or not self._loop.is_running():
            msg = "⚠️ Нельзя отправить — сервер не запущен (нет event loop)"
            self.log_message.emit(msg)  # Добавлен лог
            return
        url = f"http://{self.ip_target}:{self.port_target}/pay"
        asyncio.run_coroutine_threadsafe(self._post_json(url, data), self._loop)

    async def handle_status(self, request):
        """Проверить статус сервера"""
        info = {
            "status": "running",
            "timestamp": datetime.now().isoformat()
        }
        msg = "📡 /status -> OK"
        self.log_message.emit(msg)  # Заменен print на лог
        self.request_received.emit("/status", info)
        return web.json_response(info)

    # --- Запуск и остановка сервера ---
    async def _start_server(self):
        try:
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            self.site = web.TCPSite(self.runner, self.host, self.port)
            await self.site.start()
            self.is_running = True
            self.log_message.emit(f"🚀 HTTP сервер запущен на {self.host}:{self.port}")

            self._stop_event = asyncio.Event()
            await self._stop_event.wait()  # ждём сигнала остановки

        except asyncio.CancelledError:
            pass  # игнорируем отмену
        except Exception as e:
            self.log_message.emit(f"❌ Ошибка при запуске сервера: {e}")
        finally:
            await self._cleanup_async()
            self.is_running = False
            self.log_message.emit("✅ Сервер полностью остановлен")

    def stop_server(self):
        """Остановка сервера"""
        if not self.is_running:
            return
        self.log_message.emit("🛑 Останавливаем сервер...")
        if hasattr(self, '_stop_event') and self._stop_event:
            if self._loop and self._loop.is_running():
                self._loop.call_soon_threadsafe(self._stop_event.set)

    def _run_server(self):
        """Запуск сервера в отдельном потоке"""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        try:
            # Запускаем сервер и держим loop активным
            self._loop.run_until_complete(self._start_server())
        except Exception as e:
            msg = f"❌ Ошибка сервера: {e}"
            self.log_message.emit(msg)
        finally:
            # Аккуратно закрываем loop
            if self._loop.is_running():
                self._loop.stop()

            # Ждём завершения всех задач
            pending = asyncio.all_tasks(self._loop)
            if pending:
                self._loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))

            self._loop.close()
            self._loop = None  # Обнуляем loop
            self.is_running = False

    async def _cleanup_async(self):
        """Асинхронная очистка ресурсов"""
        try:
            if hasattr(self, 'site') and self.site:
                await self.site.stop()
            if hasattr(self, 'runner') and self.runner:
                await self.runner.cleanup()
        except Exception as e:
            self.log_message.emit(f"⚠️ Ошибка при очистке: {e}")
        finally:
            self.runner = None
            self.site = None
            self._stop_event = None

    def start(self):
        """Запуск сервера"""
        # Если сервер уже запущен, сначала останавливаем
        if self.is_running:
            self.stop_server()
            # Даём время на остановку
            import time
            time.sleep(0.5)
            # Ждём завершения потока
            if self.server_thread and self.server_thread.is_alive():
                self.server_thread.join(timeout=2.0)

        # Создаём новое приложение для каждого запуска
        self.app = web.Application()

        self.app.add_routes([
            web.post('/add_product', self.handle_add_product),
            web.post('/pay', self.handle_pay),
            web.post('/status', self.handle_status)
        ])

        # Запускаем в новом потоке
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()

    def update_config(self, host=None, port=None, ip_target=None, port_target=None):
        """Обновление конфигурации сервера"""
        if host:
            self.host = host
        if port:
            self.port = port
        if ip_target:
            self.ip_target = ip_target
        if port_target:
            self.port_target = port_target
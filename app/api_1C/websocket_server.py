import asyncio
import websockets
import json
import threading
from PyQt5.QtCore import QObject, pyqtSignal


class WebSocketServer(QObject):
    message_received = pyqtSignal(str)  # Сообщение от клиента в GUI

    def __init__(self, host='0.0.0.0', port=8765):
        super().__init__()
        self.host = host
        self.port = port
        self.server = None
        self.current_client = None
        self._is_running = False
        self._thread = None
        self._loop = None

    def _create_message_server(self, msg_client=None, msg_server=None, error=None):
        data_dict = {"type_msg": "server"}
        if msg_client: data_dict["client"] = msg_client
        if msg_server: data_dict["server"] = msg_server
        if error: data_dict["error"] = error
        return json.dumps(data_dict, ensure_ascii=False)

    async def handler(self, websocket, path):
        self.current_client = websocket
        msg_for_GUI = self._create_message_server(msg_client="add")
        self.message_received.emit(msg_for_GUI)

        try:
            async for message in websocket:
                if not self._is_running:
                    break
                self.message_received.emit(message)
        except Exception as e:
            if self._is_running:
                msg_for_GUI = self._create_message_server(error=f"error;handler; {e}")
                self.message_received.emit(msg_for_GUI)
        finally:
            self.current_client = None
            if self._is_running:
                msg_for_GUI = self._create_message_server(msg_client="off")
                self.message_received.emit(msg_for_GUI)

    async def start_server(self):
        self.server = await websockets.serve(self.handler, self.host, self.port)
        msg_for_GUI = self._create_message_server(msg_server="on")
        self.message_received.emit(msg_for_GUI)
        print(f"🚀 WebSocket сервер запущен на {self.host}:{self.port}")

    def _run_server(self):
        """Запуск сервера в отдельном потоке"""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        try:
            self._loop.run_until_complete(self.start_server())
            print("⏳ Сервер ожидает подключений...")

            # Бесконечный цикл asyncio
            self._loop.run_forever()

        except Exception as e:
            if self._is_running:
                msg_for_GUI = self._create_message_server(error=f"error;run; {e}")
                self.message_received.emit(msg_for_GUI)
                print(f"❌ Ошибка сервера: {e}")
        finally:
            self._cleanup()

    def _cleanup(self):
        """Очистка ресурсов"""
        print("🧹 Очистка ресурсов сервера...")
        try:
            if self.server:
                self.server.close()
                if self._loop and not self._loop.is_closed():
                    self._loop.run_until_complete(self.server.wait_closed())

            if self._loop and not self._loop.is_closed():
                self._loop.close()
        except Exception as e:
            print(f"⚠️ Ошибка при cleanup: {e}")

    def start(self):
        """Запуск сервера"""
        if self._is_running:
            return

        self._is_running = True
        self._thread = threading.Thread(target=self._run_server, daemon=True)
        self._thread.start()
        print("✅ WebSocket сервер запущен в отдельном потоке")

    def send_to_client(self, message):
        """Отправка сообщения клиенту из GUI"""
        if not self._is_running or not self._loop or self._loop.is_closed():
            msg_for_GUI = self._create_message_server(error="not server")
            self.message_received.emit(msg_for_GUI)
            return False

        if self.current_client is not None:
            try:
                asyncio.run_coroutine_threadsafe(
                    self.current_client.send(message),
                    self._loop
                )
                msg_for_GUI = self._create_message_server(msg_client="send message")
                self.message_received.emit(msg_for_GUI)
                return True
            except Exception as e:
                msg_for_GUI = self._create_message_server(error=f"send error: {e}")
                self.message_received.emit(msg_for_GUI)
                return False
        else:
            msg_for_GUI = self._create_message_server(error="not client")
            self.message_received.emit(msg_for_GUI)
            return False

    def stop_server(self):
        """Остановка сервера"""
        if not self._is_running:
            return

        print("🛑 Останавливаем сервер...")
        self._is_running = False

        # Останавливаем asyncio loop
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)

        # Ждем завершения потока
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3.0)
            if self._thread.is_alive():
                print("⚠️ Поток сервера не остановился, принудительное завершение")
            else:
                print("✅ Сервер полностью остановлен")
import asyncio
import websockets
import json
import random
import socket
from datetime import datetime
import logging


class Mock1CServer:
    """Сервер-имитатор 1С для отправки команд по имени ПК в сети"""

    def __init__(self, target_computer_name, port=8765):
        self.target_computer_name = target_computer_name
        self.port = port
        self.websocket = None
        self.is_connected = False

    def resolve_computer_name(self):
        """Разрешение имени компьютера в IP адрес"""
        try:
            print(f"🔍 Поиск IP адреса для компьютера: {self.target_computer_name}")

            # Пробуем разные методы разрешения имени
            try:
                # Метод 1: стандартное разрешение
                ip_address = socket.gethostbyname(self.target_computer_name)
                print(f"✅ Найден IP: {ip_address}")
                return ip_address
            except socket.gaierror:
                # Метод 2: добавляем .local для mDNS (Apple Bonjour/Avahi)
                ip_address = socket.gethostbyname(f"{self.target_computer_name}.local")
                print(f"✅ Найден IP через .local: {ip_address}")
                return ip_address

        except Exception as e:
            print(f"❌ Не удалось найти компьютер '{self.target_computer_name}': {e}")
            return None

    async def connect_to_pyqt_server(self):
        """Подключение к PyQt серверу по имени компьютера"""
        try:
            # Получаем IP адрес по имени компьютера
            ip_address = self.resolve_computer_name()
            if not ip_address:
                return False

            uri = f"ws://{ip_address}:{self.port}"
            print(f"🔗 Подключаемся к: {uri}")

            self.websocket = await websockets.connect(
                uri,
                ping_interval=20,
                ping_timeout=10
            )
            self.is_connected = True

            print("✅ Успешное подключение к PyQt серверу!")

            # Отправляем приветственное сообщение
            await self.websocket.send(json.dumps({
                "ТипСообщения": "connection",
                "Статус": "connected",
                "client": "mock_1c_server",
                "timestamp": datetime.now().isoformat()
            }))

            return True

        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            return False

    async def send_product(self, barcode=None, name=None, price=None, quantity=None):
        """Отправка товара в PyQt приложение"""
        if not self.is_connected:
            print("❌ Нет подключения к PyQt серверу")
            return False

        product_data = {
            "ТипСообщения": "товар",
            "Данные": {
                "штрихкод": barcode or f"2000000{random.randint(1000, 9999)}",
                "наименование": name or f"Тестовый товар {random.randint(1, 100)}",
                "цена": price or round(random.uniform(50, 5000), 2),
                "количество": quantity or random.randint(1, 5),
                "единица": "шт"
            },
            "timestamp": datetime.now().isoformat()
        }

        try:
            await self.websocket.send(json.dumps(product_data, ensure_ascii=False))
            print(f"📤 Отправлен товар: {product_data['Данные']['наименование']}")
            print(f"   💰 Цена: {product_data['Данные']['цена']} руб.")
            print(f"   📦 Количество: {product_data['Данные']['количество']}")
            return True
        except Exception as e:
            print(f"❌ Ошибка отправки товара: {e}")
            return False

    async def send_payment(self, payment_type=None, amount=None):
        """Отправка команды оплаты"""
        if not self.is_connected:
            print("❌ Нет подключения к PyQt серверу")
            return False

        payment_types = ["cash", "card", "combined"]
        payment_data = {
            "ТипСообщения": "оплата",
            "ТипОплаты": payment_type or random.choice(payment_types),
            "Сумма": amount or round(random.uniform(100, 5000), 2),
            "timestamp": datetime.now().isoformat()
        }

        try:
            await self.websocket.send(json.dumps(payment_data, ensure_ascii=False))
            print(f"📤 Отправлена оплата: {payment_data['ТипОплаты']}")
            print(f"   💵 Сумма: {payment_data['Сумма']} руб.")
            return True
        except Exception as e:
            print(f"❌ Ошибка отправки оплаты: {e}")
            return False

    async def send_clear_cart(self):
        """Очистка корзины"""
        if not self.is_connected:
            print("❌ Нет подключения к PyQt серверу")
            return False

        clear_data = {
            "ТипСообщения": "очистка",
            "Действие": "очистить_корзину",
            "timestamp": datetime.now().isoformat()
        }

        try:
            await self.websocket.send(json.dumps(clear_data, ensure_ascii=False))
            print("📤 Отправлена команда очистки корзины")
            return True
        except Exception as e:
            print(f"❌ Ошибка отправки команды очистки: {e}")
            return False

    async def listen_for_responses(self):
        """Прослушивание ответов от PyQt сервера"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                print(f"📨 Ответ от PyQt сервера:")
                print(f"   🏷️  Тип: {data.get('ТипСообщения', 'unknown')}")
                print(f"   📊 Статус: {data.get('Статус', 'unknown')}")
                if 'Ошибка' in data:
                    print(f"   ❌ Ошибка: {data['Ошибка']}")
                print()
        except Exception as e:
            print(f"❌ Ошибка прослушивания: {e}")
            self.is_connected = False

    async def automated_test_sequence(self):
        """Автоматическая последовательность тестовых команд"""
        print("🚀 Запуск автоматического теста...")

        commands = [
            ("📦", "Случайный товар 1", self.send_product),
            ("📦", "Случайный товар 2", self.send_product),
            ("💳", "Оплата картой", lambda: self.send_payment("card", 500)),
            ("📦", "Случайный товар 3", self.send_product),
            ("💵", "Оплата наличными", lambda: self.send_payment("cash", 750)),
            ("🔄", "Очистка корзины", self.send_clear_cart),
        ]

        for emoji, description, command_func in commands:
            print(f"\n{emoji} {description}")
            await command_func()
            await asyncio.sleep(2)  # Пауза между командами

        print("✅ Автоматический тест завершен!")

    async def interactive_mode(self):
        """Интерактивный режим отправки команд"""
        print("\n" + "=" * 60)
        print("🎮 MOCK 1C SERVER - Интерактивный режим")
        print("=" * 60)
        print("Доступные команды:")
        print("  1 - 📦 Отправить случайный товар")
        print("  2 - 📦 Отправить товар с параметрами")
        print("  3 - 💳 Отправить оплату картой")
        print("  4 - 💵 Отправить оплату наличными")
        print("  5 - 🔄 Очистить корзину")
        print("  6 - 🚀 Автоматический тест (последовательность)")
        print("  0 - ❌ Выход")
        print("=" * 60)

        while self.is_connected:
            try:
                command = await asyncio.get_event_loop().run_in_executor(
                    None, input, "\nВведите команду (1-6, 0-выход): "
                )

                if command == '0':
                    break
                elif command == '1':
                    await self.send_product()
                elif command == '2':
                    print("Введите параметры товара (Enter для случайных):")
                    barcode = input("Штрихкод: ").strip() or None
                    name = input("Наименование: ").strip() or None
                    try:
                        price = float(input("Цена: ").strip()) if input("Цена: ").strip() else None
                    except:
                        price = None
                    try:
                        quantity = int(input("Количество: ").strip()) if input("Количество: ").strip() else None
                    except:
                        quantity = None
                    await self.send_product(barcode, name, price, quantity)
                elif command == '3':
                    try:
                        amount = float(input("Сумма оплаты: ").strip()) if input("Сумма оплаты: ").strip() else None
                    except:
                        amount = None
                    await self.send_payment("card", amount)
                elif command == '4':
                    try:
                        amount = float(input("Сумма оплаты: ").strip()) if input("Сумма оплаты: ").strip() else None
                    except:
                        amount = None
                    await self.send_payment("cash", amount)
                elif command == '5':
                    await self.send_clear_cart()
                elif command == '6':
                    await self.automated_test_sequence()
                else:
                    print("❌ Неизвестная команда")

            except (KeyboardInterrupt, EOFError):
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")

    async def start(self):
        """Запуск mock сервера"""
        print(f"🖥️  Mock 1C Server запущен")
        print(f"🎯 Целевой компьютер: {self.target_computer_name}")
        print(f"🔌 Порт: {self.port}")

        # Подключаемся к PyQt серверу
        if not await self.connect_to_pyqt_server():
            print("❌ Не удалось подключиться к PyQt серверу")
            return

        # Запускаем прослушивание ответов в фоне
        listen_task = asyncio.create_task(self.listen_for_responses())

        # Запускаем интерактивный режим
        await self.interactive_mode()

        # Завершаем работу
        if self.websocket:
            await self.websocket.close()
        print("🔌 Mock 1C Server остановлен")




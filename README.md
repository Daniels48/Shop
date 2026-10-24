# Shop 

Shop — настольное приложение для автоматизации работы магазина, управления товарами, учёта продаж и контроля складских операций.

Приложение позволяет вести каталог товаров, обрабатывать продажи, учитывать различные способы оплаты, отслеживать изменения остатков и просматривать статистику работы магазина.

## Возможности
- Управление товарами и их характеристиками
- Учёт штрихкодов товаров
- Поиск товаров по штрихкоду
- Оформление продаж
- Поддержка оплаты наличными, банковской картой и комбинированной оплаты
- Учёт продаж и способов оплаты
- Управление складскими остатками
- Добавление и списание товаров
- Создание и объединение товарных позиций
- История изменений товаров и складских операций
- Просмотр статистики продаж за день и месяц
- Учёт выручки и количества проданных товаров
- Учёт обедов и дополнительных операций
- Работа с базой данных PostgreSQL
- Логирование ошибок


## Технологии
- Python
- PyQt5
- PostgreSQL
- SQLAlchemy
- Alembic
- SQL

## Запуск проекта

### 1️⃣ Клонировать репозиторий

```bash
git clone https://github.com/Daniels48/Shop.git
```
```bash
cd Shop
```


### 2️⃣ Создать файл `.env`

Скопируйте `.env.example` и переименуйте его в `.env`:

```bash
cp .env.example .env
```

После этого при необходимости измените значения переменных в файле `.env`.

### 3️⃣ Запустить контейнеры


```bash
docker compose up -d --build
```

### 4️⃣ Применить миграции
```bash
docker alembic upgrade head
```

### 5️⃣ Загрузить тестовые данные

**Linux / macOS:**

```bash
pyinstaller --clean --onefile --windowed --name Shop \
  --paths . --collect-submodules app \
  --add-data "app/view/resources:app/view/resources" \
  app/main.py
```

**Windows:**

```bash
docker compose exec api python -m scripts.seed
```

### 6️⃣ Открыть приложение

```text
http://localhost
```

### 7️⃣ API документация

```text
http://localhost/docs
```


## 🧪 Тесты

Запустить все backend-тесты:

```bash
docker compose exec api pytest -v
```

## Тестовые пользователи

Пароль для всех пользователей:

```text
DemoPass123!
```

| Email | Роль | Логин |
|---|---|---|
| `demo_admin@example.com` | Администратор | demo_admin |
| `demo_developer@example.com` | Разработчик | demo_developer |
| `demo_qa@example.com` | QA-тестировщик | demo_qa |
| `demo_manager@example.com` | Менеджер | demo_manager |
| `demo_reporter@example.com` | Автор задач | demo_reporter |
| `demo_developer2@example.com` | Второй разработчик | demo_developer2 |
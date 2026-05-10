# Birthday API

## 1. Создание виртуального окружения
```bash
python3 -m venv .venv
```

## 2. Активация виртуального окружения
```bash
source .venv/bin/activate
```

## Установка зависимостей
```bash
pip install -r dependencies.txt
```

## Запуск сервера
```bash
cd src && uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

## Тестирование API

### Подготовка тестовой базы данных
Если база данных не инициализирована, выполните SQL-запросы для создания тестовых данных в `src/my_database.db`:

```bash
sqlite3 api/my_database.db <<EOF
INSERT OR IGNORE INTO users(username,email,password) VALUES('testuser','test@mail.ru','secret123');
DELETE FROM user_contacts; -- Очистить контакты перед тестами (опционально)
EOF
```

### Запуск тестовых сценариев

**Способ 1: Использование готового скрипта**

```bash
cd .. && bash test_contacts.sh
```

Этот скрипт автоматически тестирует все маршруты contacts и contact:
- Регистрация пользователя (POST /auth)
- Получение списка контактов (GET /contacts)  
- Создание контакта (POST /contact)
- Чтение контакта по ID (GET /contact/{id})
- Обновление контакта (PUT /contact)
- Удаление контакта (DELETE /contact/{id})

**Способ 2: Индивидуальные тесты через curl**

```bash
# Регистрация и получение токена
TOKEN=$(curl -s http://localhost:8001/auth \
    -H "Content-Type: application/json" \
    -d '{"name":"testuser","password":"secret123"}' | jq -r '.token')

# Создание контакта
curl -X POST http://localhost:8001/contact \
    -H "Content-Type: application/json" \
    -H "X-Token: $TOKEN" \
    -d '{"name":"Иван Иванов","phone_number":"+7 (900) 123-45-67","date_of_birth":"1990-05-15"}'

# Получение списка контактов
curl http://localhost:8001/contacts \
    -H "X-Token: $TOKEN" | jq .

# Удаление контакта (замените ID на реальный)
curl -X DELETE http://localhost:8001/contact/1 \
    -H "X-Token: $TOKEN"
```

## Структура API

### Маршруты аутентификации (не защищены токеном)
- `POST /auth` — Авторизация пользователя, возвращает токен

### Защищённые маршруты (требуют валидный токен в заголовке X-Token)
- `GET /contacts` — Получить все контакты текущего пользователя  
- `GET /contact/{id}` — Получить конкретный контакт по ID
- `POST /contact` — Создать новый контакт
- `PUT /contact` — Обновить существующий контакт (требует указать id в теле запроса)
- `DELETE /contact/{id}` — Удалить контакт

### Примеры ответов

**Успешная регистрация:**
```json
{"token": "abc123def456..."}
```

**Список контактов:**
```json
[{"id":1,"name":"Иван Иванов","phone_number":"+7 (900) 123-45-67","date_of_birth":"1990-05-15","notes":null}]
```

## Структура данных Contact

| Поле | Тип | Описание |
|------|-----|----------|
| id | int | Уникальный идентификатор контакта (автоматически генерируется) |
| name | str Имя контакта, обязательное поле. Максимальная длина 255 символов. Не может быть пустым или содержать только пробелы. phone_number VARCHAR(50) Номер телефона в международном формате без + и кодах страны (например: "79001234567"). date_of_birth DATE Дата рождения в формате YYYY-MM-DD. notes TEXT Примечания к контакту, опциональное поле. |
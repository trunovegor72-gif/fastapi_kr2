# Контрольная работа №2 — FastAPI

Технологии разработки серверных приложений.

## Запуск

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

Документация: http://localhost:8000/docs

Проверить всё разом: `python test_endpoints.py`

## Маршруты

**Задание 3.1**
- `POST /create_user` — создание пользователя с валидацией (email, age > 0).

**Задание 3.2**
- `GET /product/{product_id}` — продукт по id.
- `GET /products/search?keyword=...&category=...&limit=...` — поиск по товарам.
  Маршрут `/products/search` объявлен раньше `/product/{id}`, чтобы не было конфликта.

**Задание 5.1 / 5.2**
- `POST /login` — логин (`user123` / `password123`), ставит подписанную куку `session_token`.
- `GET /user` — профиль, требует валидную куку. Без неё или с битой — 401.
- `GET /profile` — то же самое (по тексту 5.2).

**Задание 5.3** — сессия с динамическим временем жизни
- `POST /login_dynamic` — кука вида `<user_id>.<timestamp>.<подпись>`, `max_age=300`.
- `GET /profile_dynamic` — проверяет подпись и время:
  - прошло меньше 3 минут — кука не обновляется;
  - от 3 до 5 минут — кука обновляется с новым временем;
  - больше 5 минут — 401 `Session expired`;
  - подделанные данные — 401 `Invalid session`.

**Задание 5.4**
- `GET /headers` — возвращает `User-Agent` и `Accept-Language`. Если их нет — 400.

**Задание 5.5**
- Модель `CommonHeaders` в `models.py`.
- `GET /headers_v2` — возвращает заголовки через модель.
- `GET /info` — то же + поле `message` и HTTP-заголовок `X-Server-Time`.
- При неверном формате `Accept-Language` — 400.

## Проверка через curl

```bash
curl -c cookies.txt -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user123","password":"password123"}'

curl -b cookies.txt http://localhost:8000/user
```

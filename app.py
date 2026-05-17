import time
import uuid

from fastapi import Cookie, FastAPI, Header, HTTPException, Request, Response
from itsdangerous import BadSignature, Signer
from pydantic import ValidationError

from models import CommonHeaders, LoginData, UserCreate

app = FastAPI(title="Контрольная работа 2")

SECRET_KEY = "my-secret-key-12345"
signer = Signer(SECRET_KEY)

# простая "база" пользователей
USERS = {"user123": "password123"}

sample_product_1 = {"product_id": 123, "name": "Smartphone", "category": "Electronics", "price": 599.99}
sample_product_2 = {"product_id": 456, "name": "Phone Case", "category": "Accessories", "price": 19.99}
sample_product_3 = {"product_id": 789, "name": "Iphone", "category": "Electronics", "price": 1299.99}
sample_product_4 = {"product_id": 101, "name": "Headphones", "category": "Accessories", "price": 99.99}
sample_product_5 = {"product_id": 202, "name": "Smartwatch", "category": "Electronics", "price": 299.99}
sample_products = [sample_product_1, sample_product_2, sample_product_3, sample_product_4, sample_product_5]


#Задание 3.1 ----------
@app.post("/create_user")
def create_user(user: UserCreate):
    return user


#Задание 3.2 ----------

@app.get("/products/search")
def search_products(keyword: str, category: str | None = None, limit: int = 10):
    result = [p for p in sample_products if keyword.lower() in p["name"].lower()]
    if category:
        result = [p for p in result if p["category"].lower() == category.lower()]
    return result[:limit]


@app.get("/product/{product_id}")
def get_product(product_id: int):
    for p in sample_products:
        if p["product_id"] == product_id:
            return p
    raise HTTPException(status_code=404, detail="Продукт не найден")


#Задание 5.1 / 5.2 ----------
@app.post("/login")
def login(data: LoginData, response: Response):
    if USERS.get(data.username) != data.password:
        raise HTTPException(status_code=401, detail="Неверные данные")

    user_id = str(uuid.uuid4())
    token = signer.sign(user_id).decode()
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        max_age=300,
    )
    return {"message": "Вы вошли в систему", "username": data.username}


@app.get("/user")
def get_user(session_token: str | None = Cookie(default=None)):
    if session_token is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        user_id = signer.unsign(session_token).decode()
    except BadSignature:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"user_id": user_id, "name": "Egor Trunov", "email": "egor@example.com"}


@app.get("/profile")
def profile(session_token: str | None = Cookie(default=None)):
    if session_token is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        user_id = signer.unsign(session_token).decode()
    except BadSignature:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"user_id": user_id, "name": "Egor Trunov"}


# Задание 5.3 ----------

SESSION_TTL = 300
RENEW_AFTER = 180


def make_session_token(user_id: str, ts: int) -> str:
    return signer.sign(f"{user_id}.{ts}").decode()


@app.post("/login_dynamic")
def login_dynamic(data: LoginData, response: Response):
    if USERS.get(data.username) != data.password:
        raise HTTPException(status_code=401, detail="Неверные данные")

    user_id = str(uuid.uuid4())
    now = int(time.time())
    token = make_session_token(user_id, now)
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=False,
        max_age=SESSION_TTL,
    )
    return {"message": "Вы вошли в систему", "username": data.username}


@app.get("/profile_dynamic")
def profile_dynamic(response: Response, session_token: str | None = Cookie(default=None)):
    if session_token is None:
        response.status_code = 401
        return {"message": "Unauthorized"}

    try:
        raw = signer.unsign(session_token).decode()
        user_id, ts_str = raw.rsplit(".", 1)
        last_active = int(ts_str)
    except (BadSignature, ValueError):
        response.status_code = 401
        return {"message": "Invalid session"}

    now = int(time.time())
    elapsed = now - last_active

    if elapsed > SESSION_TTL:
        response.status_code = 401
        return {"message": "Session expired"}

    # продлеваем, только если прошло от 3 до 5 минут
    if RENEW_AFTER <= elapsed <= SESSION_TTL:
        new_token = make_session_token(user_id, now)
        response.set_cookie(
            key="session_token",
            value=new_token,
            httponly=True,
            secure=False,
            max_age=SESSION_TTL,
        )

    return {"user_id": user_id, "name": "Egor Trunov", "last_active": last_active}


#Задание 5.4 ----------
@app.get("/headers")
def read_headers(request: Request):
    user_agent = request.headers.get("user-agent")
    accept_language = request.headers.get("accept-language")
    if not user_agent or not accept_language:
        raise HTTPException(status_code=400, detail="Отсутствуют обязательные заголовки")
    return {"User-Agent": user_agent, "Accept-Language": accept_language}


#Задание 5.5 ----------
def get_common_headers(user_agent: str, accept_language: str) -> CommonHeaders:
    try:
        return CommonHeaders.model_validate(
            {"User-Agent": user_agent, "Accept-Language": accept_language}
        )
    except ValidationError:
        raise HTTPException(status_code=400, detail="Неверный формат Accept-Language")


@app.get("/headers_v2")
def headers_v2(
    user_agent: str = Header(...),
    accept_language: str = Header(...),
):
    h = get_common_headers(user_agent, accept_language)
    return {"User-Agent": h.user_agent, "Accept-Language": h.accept_language}


@app.get("/info")
def info(
    response: Response,
    user_agent: str = Header(...),
    accept_language: str = Header(...),
):
    h = get_common_headers(user_agent, accept_language)
    from datetime import datetime

    response.headers["X-Server-Time"] = datetime.now().isoformat(timespec="seconds")
    return {
        "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
        "headers": {
            "User-Agent": h.user_agent,
            "Accept-Language": h.accept_language,
        },
    }

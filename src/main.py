from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, APIRouter, Depends
from fastapi.responses import JSONResponse
from init_db import init_db
from datetime import date

import models.user as user
import models.contacts as contacts

DB_NAME = "my_database.db"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.db = await init_db(DB_NAME)
    print("Соединение с базой данных установлено")

    yield  # Здесь приложение "живет" и принимает запросы

    # --- КОД ПРИ ОСТАНОВКЕ ---
    await app.db.close()
    print("Соединение с базой данных закрыто")

app = FastAPI(lifespan=lifespan)

# Зависимость для проверки
async def verify_token(request: Request):
    token = request.headers.get("X-Token")
    if token is None:
        raise HTTPException(status_code=401)

    user_id = await user.check_user(request.app.db, token)
    if user_id == 0:
        raise HTTPException(status_code=403)

    request.state.user_id = user_id

@app.post("/auth")
async def route_auth(request: Request, user_model: user.User):
    db = request.app.db
    token = await user.auth(db, user_model.username, user_model.password)
    if token is None:
        raise HTTPException(status_code=404, detail="User not found")

    return JSONResponse(status_code=200, content={'token': token})

protected_router = APIRouter(
    dependencies=[Depends(verify_token)]
)

@protected_router.get("/contacts")
async def route_get_contacts(request: Request):
    return await contacts.get_contacts(request.app.db, request.state.user_id)

# получение ближайших ДР пользователей
@protected_router.get("/contacts/birthdays")
async def route_get_contacts(request: Request):
    return await contacts.get_contacts_birthdays(request.app.db, request.state.user_id)

@protected_router.get("/contact/{contact_id}", response_model=contacts.Contact, status_code=200)
async def route_get_contact(request: Request, contact_id: int):
    contact = await contacts.get_one_contact(request.app.db, request.state.user_id, contact_id)
    if contact is None:
        raise HTTPException(status_code=404, detail="User not found")
    return contact

@protected_router.post("/contact", response_model=contacts.Contact, status_code=201)
async def route_create_contact(request: Request, model: contacts.AddContact):
    contact_id = await contacts.add_contact(request.app.db, request.state.user_id, model)
    if contact_id == 0:
        raise HTTPException(status_code=409, detail="User exists")
    
    contact = await contacts.get_one_contact(request.app.db, request.state.user_id, contact_id)
    if contact is None:
        raise HTTPException(status_code=404, detail="User not found")

    return contact

@protected_router.delete("/contact/{contact_id}")
async def route_delete_contact(request: Request, contact_id: int):
    db = request.app.db
    contact = await contacts.get_one_contact(db, request.state.user_id, contact_id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact don`t exist for deleting")

    await contacts.delete_contact(db, request.state.user_id, contact_id)
    return JSONResponse(status_code=204, content=None)

@protected_router.put("/contact", response_model=contacts.Contact, status_code=200)
async def route_update_contact(request: Request, contact: contacts.Contact):
    db = request.app.db
    contact_in_db = await contacts.get_one_contact(db, request.state.user_id, contact.id)
    if contact_in_db is None:
        raise HTTPException(status_code=404, detail="Contact don`t exist for update")

    await contacts.update_contact(request.app.db, request.state.user_id, contact)
                                #    contact.id, contact.name, contact.phone_number, contact.date_of_birth, contact.notes)
    contact = await contacts.get_one_contact(db, request.state.user_id, contact.id)
    
    return contact

app.include_router(protected_router)

import hashlib
import os
import time
from pydantic import BaseModel

class User(BaseModel):
    username: str
    password: str

def create_token():
    seed = os.urandom(32) + str(time.time()).encode()
    return hashlib.md5(seed).hexdigest()


async def check_user(db, token):
    async with db.execute('SELECT id FROM users WHERE token = ?', (token,)) as cursor:
        user = await cursor.fetchone()
        return user[0] if user else 0

async def auth(db, username, password):
    async with db.execute('SELECT id FROM users WHERE username = ? AND password = ?', (username, password)) as cursor:
        user = await cursor.fetchone()
    if user:
        user_id = user[0]
        new_token = create_token()
        await db.execute('UPDATE users SET token = ? WHERE id = ?', (new_token, user_id))
        await db.commit()
        return new_token
    return None

import aiosqlite
from pydantic import BaseModel
from datetime import date

class Contact(BaseModel):
    id: int
    name: str
    phone_number: str
    date_of_birth: date
    notes: str | None = None

class AddContact(BaseModel):
    name: str
    phone_number: str
    date_of_birth: date
    notes: str | None = None

async def get_contacts(db, user_id):
    db.row_factory = aiosqlite.Row 
    async with db.execute('SELECT * FROM user_contacts WHERE user_id = ? ORDER BY name ASC', (user_id,)) as cursor:
        rows = await cursor.fetchall()
        contacts = [Contact(**dict(row)) for row in rows]
        return contacts


async def get_one_contact(db, user_id, contact_id):
    db.row_factory = aiosqlite.Row 
    async with db.execute('SELECT * FROM user_contacts WHERE user_id = ? AND id = ?', (user_id, contact_id)) as cursor:
        row = await cursor.fetchone()
        if row is None:
            return None
        return Contact(**dict(row))


async def delete_contact(db, user_id, contact_id):
    async with db.execute('DELETE FROM user_contacts WHERE user_id = ? AND id = ?', (user_id, contact_id)) as cursor:
        if cursor.rowcount == 0:
            return False
    await db.commit()
    return True


async def add_contact(db, user_id, model: AddContact):
    try:
        async with db.execute(
            'INSERT INTO user_contacts (user_id,name,phone_number,date_of_birth,notes) VALUES (?, ? , ? , ? , ?)',
            (user_id, model.name, model.phone_number, model.date_of_birth, model.notes)) as cursor:
            await cursor.fetchone()
            await db.commit()
            return cursor.lastrowid
    except Exception:
        return 0


async def update_contact(db, user_id, model: Contact):
    async with db.execute(
            'UPDATE user_contacts SET name = ? , phone_number = ?,date_of_birth = ?,notes = ? WHERE user_id = ? AND id = ?',
            (model.name, model.phone_number, model.date_of_birth, model.notes, user_id, model.id)) as cursor:
        await cursor.fetchone()
        await db.commit()

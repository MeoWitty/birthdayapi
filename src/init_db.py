import aiosqlite


async def init_db(db_name):
    conn = await aiosqlite.connect(db_name)
    await conn.execute('PRAGMA foreign_keys = ON')
    await conn.commit()
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            token TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
            """)
    await conn.commit()

    await conn.execute("""
        INSERT OR IGNORE INTO 
        users(username,email,password) 
        VALUES(?,?,?)
        """, ('user','user@mail.ru','pass'))
    await conn.commit()

    await conn.execute('PRAGMA foreign_keys = ON')
    await conn.commit()
    await conn.execute("""
            CREATE TABLE IF NOT EXISTS user_contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,      -- Имя пользователя (контакта)
            phone_number VARCHAR(50),         -- Номер телефона
            date_of_birth DATE,               -- Дата рождения
            notes TEXT,                       -- Примечания
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
    """)
    await conn.execute('PRAGMA foreign_keys = ON')
    await conn.commit()
    await conn.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_user_contacts ON user_contacts(user_id, phone_number);
    """)
    await conn.commit()
    return conn

import sqlite3
from typing import List, Tuple, Optional

DB_NAME = "spese.db"

class DatabaseManager:
    def __init__(self, db_name: str = DB_NAME):
        self.db_name = db_name
        self._create_table()

    def _create_table(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT CHECK(tipo IN ('entrata','uscita')) NOT NULL,
                categoria TEXT NOT NULL,
                importo REAL NOT NULL,
                giorno INTEGER NOT NULL,
                mese INTEGER NOT NULL,
                anno INTEGER NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def add_transaction(self, tipo: str, categoria: str, importo: float,
                        giorno: int, mese: int, anno: int):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("""
            INSERT INTO transactions (tipo, categoria, importo, giorno, mese, anno)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (tipo, categoria, importo, giorno, mese, anno))
        conn.commit()
        conn.close()

    def get_transactions(self, mese: Optional[int] = None, anno: Optional[int] = None) -> List[Tuple]:
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        if mese and anno:
            c.execute("SELECT * FROM transactions WHERE mese=? AND anno=?", (mese, anno))
        elif anno:
            c.execute("SELECT * FROM transactions WHERE anno=?", (anno,))
        else:
            c.execute("SELECT * FROM transactions")
        results = c.fetchall()
        conn.close()
        return results

    def reset_transactions(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("DELETE FROM transactions")
        conn.commit()
        conn.close()

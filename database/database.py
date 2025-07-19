import sqlite3
import os
from pathlib import Path
from typing import Optional, List, Tuple

class Database:
    def __init__(self, path_to_db: str = 'data/main.db'):
        base_dir = Path(__file__).parent.parent
        self.path_to_db = str(base_dir / path_to_db)
        os.makedirs(os.path.dirname(self.path_to_db), exist_ok=True)
        self._ensure_table_exists()

    def _ensure_table_exists(self):
        """Jadval mavjudligini ta'minlash"""
        with sqlite3.connect(self.path_to_db) as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                link TEXT NOT NULL,
                media_file_id TEXT,
                media_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            conn.commit()

    async def add_template(self, user_id: int, name: str, category: str, 
                         description: str, link: str, 
                         media_file_id: Optional[str] = None, 
                         media_type: Optional[str] = None) -> None:
        """Yangi shablon qo'shish"""
        with sqlite3.connect(self.path_to_db) as conn:
            conn.execute(
                "INSERT INTO templates(user_id, name, category, description, link, media_file_id, media_type) "
                "VALUES(?, ?, ?, ?, ?, ?, ?)",
                (user_id, name, category, description, link, media_file_id, media_type)
            )
            conn.commit()

    async def get_templates(self, category: Optional[str] = None) -> List[Tuple]:
        """Shablonlarni olish"""
        with sqlite3.connect(self.path_to_db) as conn:
            cursor = conn.cursor()
            if category:
                cursor.execute("SELECT * FROM templates WHERE category=?", (category,))
            else:
                cursor.execute("SELECT * FROM templates")
            return cursor.fetchall()

# Global database obyekti
db = Database()
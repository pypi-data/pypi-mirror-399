import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class HistoryManager:
    def __init__(self):
        self.data_dir = Path.home() / ".debugbuddy"
        self.data_dir.mkdir(exist_ok=True)
        self.db_file = self.data_dir / "history.db"
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                error_type TEXT,
                message TEXT,
                file TEXT,
                line INTEGER,
                language TEXT,
                simple TEXT,
                fix TEXT
            )
            """
        )
        conn.commit()
        conn.close()

    def add(self, error: Dict, explanation: Dict):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO history (
                timestamp, error_type, message, file, line, language, simple, fix
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now().isoformat(),
                error.get("type", "Unknown"),
                error.get("message", "")[:200],
                error.get("file"),
                error.get("line"),
                error.get("language", "unknown"),
                explanation.get("simple", "")[:100],
                explanation.get("fix", "")[:200],
            ),
        )
        conn.commit()
        conn.close()

    def get_recent(self, limit: int = 10) -> List[Dict]:
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM history ORDER BY id DESC LIMIT ?", (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        return self._rows_to_dicts(rows)

    def find_similar(self, error: Dict) -> Optional[Dict]:
        error_type = error.get("type", "").lower()
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM history
            WHERE LOWER(error_type) = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (error_type,),
        )
        row = cursor.fetchone()
        conn.close()
        return self._row_to_dict(row) if row else None

    def search(self, keyword: str) -> List[Dict]:
        keyword_lower = keyword.lower()
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT * FROM history
            WHERE
                LOWER(error_type) LIKE ? OR
                LOWER(REPLACE(error_type, ' ', '')) LIKE ? OR
                LOWER(message) LIKE ? OR
                LOWER(simple) LIKE ?
            ORDER BY id DESC
            """,
            (f"%{keyword_lower}%", f"%{keyword_lower}%", f"%{keyword_lower}%", f"%{keyword_lower}%"),
        )
        rows = cursor.fetchall()
        conn.close()
        return self._rows_to_dicts(rows)

    def clear(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM history")
        conn.commit()
        conn.close()

    def get_stats(self) -> Dict:
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM history")
        total = cursor.fetchone()[0]

        cursor.execute(
            "SELECT error_type, COUNT(*) FROM history GROUP BY error_type"
        )
        by_type = dict(cursor.fetchall())

        cursor.execute(
            "SELECT language, COUNT(*) FROM history GROUP BY language"
        )
        by_language = dict(cursor.fetchall())

        conn.close()

        return {
            "total": total,
            "by_type": by_type,
            "by_language": by_language,
        }

    def _rows_to_dicts(self, rows: List[tuple]) -> List[Dict]:
        return [self._row_to_dict(row) for row in rows]

    def _row_to_dict(self, row: tuple) -> Dict:
        return {
            "id": row[0],
            "timestamp": row[1],
            "error_type": row[2],
            "message": row[3],
            "file": row[4],
            "line": row[5],
            "language": row[6],
            "simple": row[7],
            "fix": row[8],
        }
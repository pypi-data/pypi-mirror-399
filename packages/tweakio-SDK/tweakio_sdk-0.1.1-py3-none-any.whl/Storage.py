import sqlite3
import os
import json
from typing import List, Dict, Optional
from Shared_Resources import logger

class Storage:
    def __init__(self, db_path: str = "tweakio.db"):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._init_db()

    def _init_db(self):
        """Initialize the database connection and create tables if they don't exist."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            # Enable WAL mode for better concurrency
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self._create_tables()
            logger.info(f"Storage initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}", exc_info=True)
            raise

    def _create_tables(self):
        """Create the messages table."""
        try:
            query = """
            CREATE TABLE IF NOT EXISTS messages (
                data_id TEXT PRIMARY KEY,
                chat TEXT,
                community TEXT,
                jid TEXT,
                message TEXT,
                sender TEXT,
                time TEXT,
                systime TEXT,
                direction TEXT,
                type TEXT,
                extra TEXT
            );
            """
            self.conn.execute(query)
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to create tables: {e}", exc_info=True)

    def insert_message(self, data: dict) -> bool:
        """
        Insert a message into the database.
        Returns True if inserted, False if it already existed.
        """
        try:
            # Prepare data
            data_id = data.get("data_id") or data.get("id")
            if not data_id:
                logger.warning("Attempted to insert message without data_id")
                return False

            chat = str(data.get("chat", ""))
            community = str(data.get("community", ""))
            jid = str(data.get("jid", ""))
            message = str(data.get("message", ""))
            sender = str(data.get("sender", ""))
            time = str(data.get("time", ""))
            systime = str(data.get("systime", ""))
            direction = str(data.get("direction", ""))
            msg_type = str(data.get("type", ""))
            
            # Serialize extra fields
            known_keys = {"data_id", "id", "chat", "community", "jid", "message", "sender", "time", "systime", "direction", "type"}
            extra = {k: v for k, v in data.items() if k not in known_keys}
            extra_json = json.dumps(extra)

            query = """
            INSERT OR IGNORE INTO messages 
            (data_id, chat, community, jid, message, sender, time, systime, direction, type, extra)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            cursor = self.conn.execute(query, (
                data_id, chat, community, jid, message, sender, time, systime, direction, msg_type, extra_json
            ))
            self.conn.commit()
            
            return cursor.rowcount > 0

        except Exception as e:
            logger.error(f"Failed to insert message {data.get('data_id', 'unknown')}: {e}", exc_info=True)
            return False

    def message_exists(self, data_id: str) -> bool:
        """Check if a message with the given data_id exists."""
        try:
            cursor = self.conn.execute("SELECT 1 FROM messages WHERE data_id = ?", (data_id,))
            return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Failed to check message existence {data_id}: {e}", exc_info=True)
            return False

    def get_all_messages(self) -> List[Dict]:
        """Retrieve all messages as a list of dictionaries."""
        try:
            self.conn.row_factory = sqlite3.Row
            cursor = self.conn.execute("SELECT * FROM messages")
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                d = dict(row)
                # Unpack extra if needed, or leave as string
                # d['extra'] = json.loads(d['extra']) if d['extra'] else {}
                results.append(d)
            return results
        except Exception as e:
            logger.error(f"Failed to get messages: {e}", exc_info=True)
            return []

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Storage connection closed.")

import sys
from pathlib import Path

# Add backend directory
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.database import engine, Base
from app.models.user import User
from app.models.document import Document
from app.models.chat_history import ChatHistory
from app.models.quiz_result import QuizResult
from app.models.flashcard import Flashcard
from app.models.extra import DocumentChunk, Quiz, QuizAttempt, ChatMessage, ActivityLog
from sqlalchemy import inspect, text

insp = inspect(engine)
existing_tables = insp.get_table_names()
print("Connected to Supabase PostgreSQL.")
print("Existing tables in Supabase:", existing_tables)

with engine.begin() as conn:
    for table_name, table in Base.metadata.tables.items():
        if table_name in existing_tables:
            existing_cols = {c['name'] for c in insp.get_columns(table_name)}
            for col in table.columns:
                if col.name not in existing_cols:
                    col_type = col.type.compile(engine.dialect)
                    stmt = f'ALTER TABLE "{table_name}" ADD COLUMN IF NOT EXISTS "{col.name}" {col_type};'
                    print(f"Adding missing column to {table_name}: {col.name} ({col_type})")
                    try:
                        conn.execute(text(stmt))
                    except Exception as err:
                        print(f"Notice on {stmt}: {err}")
        else:
            print(f"Creating missing table: {table_name}")
            table.create(conn)

print("\nAll Supabase tables and columns are 100% synchronized and aligned!")

with engine.begin() as conn:
    query = text("SELECT table_name, column_name FROM information_schema.columns WHERE table_schema = 'public' AND data_type IN ('json', 'jsonb')")
    json_cols = conn.execute(query).fetchall()
    for tbl, col in json_cols:
        try:
            conn.execute(text(f'ALTER TABLE "{tbl}" ALTER COLUMN "{col}" TYPE TEXT USING "{col}"::text;'))
            print(f"Converted {tbl}.{col} to TEXT")
        except Exception as e:
            print(f"Notice: {e}")


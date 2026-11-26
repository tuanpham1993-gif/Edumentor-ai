import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import engine
from sqlalchemy import text

def run_migration():
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE learning_paths ADD COLUMN IF NOT EXISTS is_shared BOOLEAN NOT NULL DEFAULT FALSE;"))
        conn.execute(text("ALTER TABLE learning_paths ADD COLUMN IF NOT EXISTS share_code VARCHAR(50) UNIQUE;"))
        conn.execute(text("ALTER TABLE learning_paths ADD COLUMN IF NOT EXISTS shared_at TIMESTAMP WITH TIME ZONE;"))
        conn.execute(text("ALTER TABLE learning_paths ADD COLUMN IF NOT EXISTS clone_count INTEGER NOT NULL DEFAULT 0;"))
        conn.execute(text("ALTER TABLE learning_paths ADD COLUMN IF NOT EXISTS cloned_from_id INTEGER REFERENCES learning_paths(record_id) ON DELETE SET NULL;"))
    print("Database migration successful!")

if __name__ == "__main__":
    run_migration()

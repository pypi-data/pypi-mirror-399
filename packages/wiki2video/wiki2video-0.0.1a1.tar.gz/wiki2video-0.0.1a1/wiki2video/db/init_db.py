import sqlite3
from pathlib import Path
import importlib.resources as pkg_resources

from wiki2video.core.paths import get_db_path


def init_database_if_needed():
    db_path = get_db_path()

    if db_path.exists():
        return

    # 读取 package 内 schema
    with pkg_resources.files("wiki2video").joinpath(
        "db/schema/working_blocks.sql"
    ).open("r") as f:
        schema_sql = f.read()

    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(schema_sql)
        conn.commit()
    finally:
        conn.close()

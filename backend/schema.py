import sqlite3

def get_schema(db_path):

    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)  # read-only
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")

    tables = [r[0] for r in cur.fetchall()]
    desc = []
    for t in tables:
        cur.execute(f"PRAGMA table_info({t});")
        cols = [r[1] + ':' + r[2] for r in cur.fetchall()]  # name:type
        desc.append(f"{t}({', '.join(cols)})")

    con.close()

    return "\n".join(desc)
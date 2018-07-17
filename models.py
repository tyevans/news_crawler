import sqlite3


def get_connection():
    return sqlite3.connect('articles.sqlite3')


def insert_page(url, content, conn=None):
    _conn = conn or get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO pages (url, content) VALUES (?, ?)",
                   (url, content))
    _conn.commit()
    if conn is None:
        _conn.close()


if __name__ == "__main__":
    conn = get_connection()
    conn.execute("""
        CREATE TABLE pages (
          url text,
          content text,
          crawled boolean default false,
          processed boolean default false
        )
    """)
    conn.commit()
    conn.close()

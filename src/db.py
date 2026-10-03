import os
import re
import sqlite3
from typing import List, Tuple, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

# Si DATABASE_URL está definida en el entorno o .env, usamos Postgres (Neon).
# Si no, recurrimos a SQLite local (ideal para desarrollo offline).
DATABASE_URL = os.getenv("DATABASE_URL")
SQLITE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "history.db")

def is_postgres() -> bool:
    return bool(DATABASE_URL and DATABASE_URL.startswith(("postgres://", "postgresql://")))

def get_connection():
    if is_postgres():
        import psycopg2
        # Compatibilidad: psycopg2 requiere 'postgresql://' en lugar de 'postgres://'
        url = DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        conn = psycopg2.connect(url)
        return conn
    else:
        os.makedirs(os.path.dirname(SQLITE_PATH), exist_ok=True)
        conn = sqlite3.connect(SQLITE_PATH, timeout=30.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

def clean_emojis(text: str) -> str:
    """Elimina emojis y símbolos de redes de un texto de manera determinista."""
    if not text:
        return ""
    emoji_pattern = re.compile(
        r'[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U00002300-\U000023FF\U00002B50-\U00002B55\U0000FE00-\U0000FE0F]+'
    )
    cleaned = emoji_pattern.sub('', str(text))
    cleaned = re.sub(r'[ \t]{2,}', ' ', cleaned)
    return cleaned.strip()

def init_db():
    """Inicializa el esquema de tablas tanto en SQLite como en Postgres."""
    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            if is_postgres():
                # Esquema PostgreSQL (Neon)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS posts (
                        id SERIAL PRIMARY KEY,
                        topic TEXT,
                        tone TEXT,
                        content TEXT,
                        approved INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS authors (
                        id SERIAL PRIMARY KEY,
                        name TEXT UNIQUE,
                        topics TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS books_metadata (
                        id SERIAL PRIMARY KEY,
                        title TEXT UNIQUE,
                        author TEXT,
                        summary TEXT,
                        topics TEXT,
                        file_hash TEXT DEFAULT '',
                        chunk_count INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                ''')
            else:
                # Esquema SQLite
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS posts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        topic TEXT,
                        tone TEXT,
                        content TEXT,
                        approved INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS authors (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE,
                        topics TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS books_metadata (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT UNIQUE,
                        author TEXT,
                        summary TEXT,
                        topics TEXT,
                        file_hash TEXT DEFAULT '',
                        chunk_count INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                ''')
    finally:
        conn.close()

# ── Posts & Cola de Publicación ──

def insert_post(topic: str, tone: str, content: str) -> int:
    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            c_topic = clean_emojis(topic)
            c_tone = clean_emojis(tone)
            c_content = clean_emojis(content)
            if is_postgres():
                cursor.execute('''
                    INSERT INTO posts (topic, tone, content)
                    VALUES (%s, %s, %s) RETURNING id
                ''', (c_topic, c_tone, c_content))
                post_id = cursor.fetchone()[0]
            else:
                cursor.execute('''
                    INSERT INTO posts (topic, tone, content)
                    VALUES (?, ?, ?)
                ''', (c_topic, c_tone, c_content))
                post_id = cursor.lastrowid
            return post_id
    finally:
        conn.close()

def get_all_posts() -> List[Tuple]:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT id, topic, tone, content, approved, created_at FROM posts ORDER BY created_at DESC')
        rows = cursor.fetchall()
        return [(r[0], clean_emojis(r[1]), clean_emojis(r[2]), clean_emojis(r[3]), r[4], str(r[5])) for r in rows]
    finally:
        conn.close()

def toggle_approval(post_id: int, current_status: int):
    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            new_status = 1 if current_status == 0 else 0
            param = "%s" if is_postgres() else "?"
            cursor.execute(f'UPDATE posts SET approved = {param} WHERE id = {param}', (new_status, post_id))
    finally:
        conn.close()

def delete_post(post_id: int):
    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            param = "%s" if is_postgres() else "?"
            cursor.execute(f'DELETE FROM posts WHERE id = {param}', (post_id,))
    finally:
        conn.close()

# ── Catálogo de Libros y Metadatos ──

def upsert_book_metadata(title: str, author: str, summary: str, topics: str, file_hash: str = "", chunk_count: int = 0):
    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            c_title = clean_emojis(title)
            c_author = clean_emojis(author)
            c_summary = clean_emojis(summary)
            c_topics = clean_emojis(topics)
            
            if is_postgres():
                cursor.execute('''
                    INSERT INTO books_metadata (title, author, summary, topics, file_hash, chunk_count)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT(title) DO UPDATE SET
                        author = EXCLUDED.author,
                        summary = EXCLUDED.summary,
                        topics = EXCLUDED.topics,
                        file_hash = EXCLUDED.file_hash,
                        chunk_count = EXCLUDED.chunk_count
                ''', (c_title, c_author, c_summary, c_topics, file_hash, chunk_count))
            else:
                cursor.execute('''
                    INSERT INTO books_metadata (title, author, summary, topics, file_hash, chunk_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(title) DO UPDATE SET
                        author = excluded.author,
                        summary = excluded.summary,
                        topics = excluded.topics,
                        file_hash = excluded.file_hash,
                        chunk_count = excluded.chunk_count
                ''', (c_title, c_author, c_summary, c_topics, file_hash, chunk_count))
    finally:
        conn.close()

def get_all_books_metadata() -> List[Tuple]:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT title, author, summary, topics FROM books_metadata ORDER BY author, title')
        rows = cursor.fetchall()
        return [(clean_emojis(r[0]), clean_emojis(r[1]), clean_emojis(r[2]), clean_emojis(r[3])) for r in rows]
    finally:
        conn.close()

def is_book_ingested(file_hash: str) -> bool:
    """Verifica por hash SHA256 si el libro ya fue indexado."""
    if not file_hash:
        return False
    conn = get_connection()
    try:
        cursor = conn.cursor()
        param = "%s" if is_postgres() else "?"
        cursor.execute(f'SELECT id FROM books_metadata WHERE file_hash = {param}', (file_hash,))
        row = cursor.fetchone()
        return bool(row)
    finally:
        conn.close()

# ── Gestión Dinámica de Autores y Temas Clave ──

def upsert_author(name: str, topics: str):
    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            c_name = clean_emojis(name)
            c_topics = clean_emojis(topics)
            if is_postgres():
                cursor.execute('''
                    INSERT INTO authors (name, topics)
                    VALUES (%s, %s)
                    ON CONFLICT(name) DO UPDATE SET topics = EXCLUDED.topics
                ''', (c_name, c_topics))
            else:
                cursor.execute('''
                    INSERT INTO authors (name, topics)
                    VALUES (?, ?)
                    ON CONFLICT(name) DO UPDATE SET topics = excluded.topics
                ''', (c_name, c_topics))
    finally:
        conn.close()

def get_all_authors_with_topics() -> Dict[str, List[str]]:
    """Retorna un diccionario {nombre_autor: [tema1, tema2, ...]} desde la base de datos."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT name, topics FROM authors ORDER BY name')
        rows = cursor.fetchall()
        result = {}
        for r in rows:
            name = clean_emojis(r[0])
            topics_raw = clean_emojis(r[1])
            topic_list = [t.strip() for t in topics_raw.split(',') if t.strip()]
            result[name] = topic_list
        return result
    finally:
        conn.close()

# ── Búsqueda Semántica Vectorial (Neon pgvector) ──

def search_chunks_pgvector(query_embedding: List[float], n_results: int = 3, author: Optional[str] = None, title: Optional[str] = None) -> List[Tuple]:
    """Ejecuta una búsqueda de similitud coseno ultrarrápida usando el índice HNSW de pgvector en Neon."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        emb_str = "[" + ",".join(f"{x:.6f}" for x in query_embedding) + "]"
        conditions = []
        params = []
        if author and author != "Todos":
            if isinstance(author, (list, tuple, set)):
                conditions.append("author = ANY(%s)")
                params.append(list(author))
            elif isinstance(author, dict) and "$in" in author:
                conditions.append("author = ANY(%s)")
                params.append(list(author["$in"]))
            else:
                conditions.append("author = %s")
                params.append(str(author))
        if title and title != "Todos":
            conditions.append("title = %s")
            params.append(title)
        
        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        # Si hay filtros específicos (autor o libro), deshabilitamos temporalmente el indexscan de HNSW
        # para que PostgreSQL filtre primero por autor/título y ordene los chunks coincidentes,
        # evitando que el grafo HNSW descarte resultados por cutoff de post-filtrado.
        if conditions:
            cursor.execute("SET LOCAL enable_indexscan = off;")

        query = f"""
            SELECT id, title, author, content
            FROM book_chunks
            {where_clause}
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """
        params.extend([emb_str, n_results])
        cursor.execute(query, tuple(params))
        return cursor.fetchall()
    finally:
        conn.close()


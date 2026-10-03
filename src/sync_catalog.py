"""
Script de Sincronización y Mantenimiento del Catálogo — Club de la Libertad

Este script:
1. Normaliza los autores y títulos en 'book_chunks' en Neon PostgreSQL (pgvector).
2. Asegura que la tabla 'books_metadata' contenga los 27 libros con sus resúmenes y temas.
3. Actualiza el conteo exacto de chunks por libro directamente desde la base vectorial.
4. Registra todos los autores y sus tópicos en la tabla 'authors'.
5. Genera o actualiza el archivo 'data/catalog_manifest.json' para ingestas con CERO consumo de API.

Uso:
    python src/sync_catalog.py
"""

import os
import sys
import json

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(base_dir, 'src'))
import db

def main():
    manifest_path = os.path.join(base_dir, "data", "catalog_manifest.json")
    if not os.path.exists(manifest_path):
        print(f"Error: No se encontró '{manifest_path}'.")
        return

    with open(manifest_path, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    conn = db.get_connection()
    conn.autocommit = True
    cur = conn.cursor()

    print(f"Sincronizando {len(catalog)} libros con la base de datos Neon PostgreSQL...")

    # 1. Asegurar constraint compuesta (title, author)
    if db.is_postgres():
        try:
            cur.execute("ALTER TABLE books_metadata DROP CONSTRAINT IF EXISTS books_metadata_title_key;")
            cur.execute("ALTER TABLE books_metadata DROP CONSTRAINT IF EXISTS books_metadata_title_author_key;")
            cur.execute("ALTER TABLE books_metadata ADD CONSTRAINT books_metadata_title_author_key UNIQUE (title, author);")
        except Exception as e:
            print(f"Aviso de constraint: {e}")

    # 2. Normalizar chunks existentes
    for item in catalog:
        old_a = item.get("old_author")
        old_t = item.get("old_title")
        new_a = item["author"]
        new_t = item["title"]

        if old_a and old_t and (old_a != new_a or old_t != new_t):
            cur.execute("""
                UPDATE book_chunks 
                SET author = %s, title = %s
                WHERE author = %s AND title = %s
            """, (new_a, new_t, old_a, old_t))

    # 3. Eliminar filas obsoletas con 0 chunks si existen
    if db.is_postgres():
        cur.execute("DELETE FROM books_metadata WHERE chunk_count = 0;")

    # 4. Upsert de libros en books_metadata con conteo real de chunks
    for item in catalog:
        a = item["author"]
        t = item["title"]
        s = item["summary"]
        top = item["topics"]

        cur.execute("SELECT COUNT(*) FROM book_chunks WHERE author = %s AND title = %s", (a, t))
        chunk_row = cur.fetchone()
        chunk_count = chunk_row[0] if chunk_row else 0

        if db.is_postgres():
            cur.execute("""
                INSERT INTO books_metadata (title, author, summary, topics, chunk_count)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (title, author) DO UPDATE SET
                    summary = EXCLUDED.summary,
                    topics = EXCLUDED.topics,
                    chunk_count = EXCLUDED.chunk_count;
            """, (t, a, s, top, chunk_count))
        else:
            cur.execute("""
                INSERT INTO books_metadata (title, author, summary, topics, chunk_count)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT (title, author) DO UPDATE SET
                    summary = excluded.summary,
                    topics = excluded.topics,
                    chunk_count = excluded.chunk_count;
            """, (t, a, s, top, chunk_count))

        print(f" -> Catálogo: '{t}' de {a} ({chunk_count} chunks)")

    # 5. Registrar autores y temas
    autores_dict = {}
    for item in catalog:
        auth = item["author"]
        if auth not in autores_dict:
            autores_dict[auth] = set()
        for topic in item["topics"].split(","):
            autores_dict[auth].add(topic.strip())

    for auth, topics_set in autores_dict.items():
        topics_str = ", ".join(sorted(list(topics_set)))
        db.upsert_author(auth, topics_str)

    conn.close()
    print("\n¡Catálogo sincronizado exitosamente con cero tokens consumidos!")

if __name__ == "__main__":
    main()

"""
Script de Migración a Neon PostgreSQL con pgvector — Club de la Libertad

Este script transfiere:
1. Todos los posteos (borradores y aprobados) desde 'data/history.db' a Neon.
2. Todo el catálogo de libros y metadatos a Neon.
3. Los 17.226 fragmentos y sus embeddings vectoriales desde 'data/chroma_db' directamente
   a la tabla 'book_chunks' en Neon usando la extensión 'pgvector'.

Uso:
1. Configura DATABASE_URL en tu archivo .env con la URL de tu proyecto de Neon.
2. Ejecuta:
   python src/migrate_to_neon.py
"""

import os
import sys
import sqlite3
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL or not DATABASE_URL.startswith(("postgres://", "postgresql://")):
    print("ERROR: Debes definir DATABASE_URL en tu archivo .env con la URL de Neon.")
    print("Ejemplo: DATABASE_URL=postgresql://usuario:password@ep-xyz.us-east-2.aws.neon.tech/neondb?sslmode=require")
    sys.exit(1)

import psycopg2
from psycopg2.extras import execute_values

# Normalizar URL para psycopg2
db_url = DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

print(" Conectando a Neon PostgreSQL...")
conn = psycopg2.connect(db_url)
conn.autocommit = True
cursor = conn.cursor()

print(" Habilitando extensión 'vector' (pgvector) en Neon...")
cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")

print(" Creando tablas relacionales y vectoriales...")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id SERIAL PRIMARY KEY,
        topic TEXT,
        tone TEXT,
        content TEXT,
        approved INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS authors (
        id SERIAL PRIMARY KEY,
        name TEXT UNIQUE,
        topics TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")

cursor.execute("""
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
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS book_chunks (
        id TEXT PRIMARY KEY,
        title TEXT,
        author TEXT,
        content TEXT,
        embedding vector(384)
    );
""")

# Crear índice vectorial HNSW para búsquedas ultrarrápidas por distancia coseno
cursor.execute("""
    CREATE INDEX IF NOT EXISTS book_chunks_embedding_idx 
    ON book_chunks USING hnsw (embedding vector_cosine_ops);
""")

# 1. Migrar autores iniciales
DEFAULT_AUTHORS = [
    ("Ludwig von Mises", "Praxeología, Acción Humana, Cálculo Económico, Intervencionismo, Inflación"),
    ("Friedrich Hayek", "Orden Espontáneo, Sistema de Precios, Conocimiento Disperso, Camino de Servidumbre, Socialismo"),
    ("Adam Smith", "Mano Invisible, División del Trabajo, Libre Comercio, Simpatía"),
    ("Frederic Bastiat", "Lo que se ve y no se ve, La Ley, Saqueo Legal, Falacia de la Ventana Rota, Estado"),
    ("Murray Rothbard", "Anarcocapitalismo, Derechos Naturales, Abolición del Estado, Banca Libre, Estado"),
    ("Juan Bautista Alberdi", "Constitución, Inmigración, Libre Navegación, Gobierno Limitado"),
    ("Milton Friedman", "Libertad de Elegir, Monetarismo, Impuesto Negativo, Libre Mercado"),
    ("Ayn Rand", "Objetivismo, Egoísmo Racional, Virtud del Egoísmo, Capitalismo"),
    ("Lysander Spooner", "Anarquismo Individualista, Contrato Social, Ley Natural, Vicios no son Delitos")
]

for auth_name, auth_topics in DEFAULT_AUTHORS:
    cursor.execute("""
        INSERT INTO authors (name, topics) VALUES (%s, %s)
        ON CONFLICT(name) DO UPDATE SET topics = EXCLUDED.topics;
    """, (auth_name, auth_topics))
print(" Autores base registrados.")

# 2. Migrar SQLite local (history.db) si existe
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sqlite_path = os.path.join(base_dir, "data", "history.db")

if os.path.exists(sqlite_path):
    print(f" Leyendo datos desde SQLite local ({sqlite_path})...")
    s_conn = sqlite3.connect(sqlite_path)
    s_cur = s_conn.cursor()

    # Migrar posts
    try:
        s_cur.execute("SELECT topic, tone, content, approved, created_at FROM posts")
        posts = s_cur.fetchall()
        for p in posts:
            cursor.execute("""
                INSERT INTO posts (topic, tone, content, approved, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """, p)
        print(f" Se migraron {len(posts)} posteos a Neon.")
    except Exception as e:
        print(f" Aviso en migración de posts: {e}")

    # Migrar books_metadata
    try:
        s_cur.execute("SELECT title, author, summary, topics FROM books_metadata")
        books = s_cur.fetchall()
        for b in books:
            cursor.execute("""
                INSERT INTO books_metadata (title, author, summary, topics)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT(title) DO NOTHING;
            """, b)
        print(f" Se migraron {len(books)} libros de catálogo a Neon.")
    except Exception as e:
        print(f" Aviso en migración de catálogo: {e}")

    s_conn.close()

# 3. Migrar ChromaDB a Neon pgvector
chroma_path = os.path.join(base_dir, "data", "chroma_db")
if os.path.exists(chroma_path):
    print("\n Conectando a ChromaDB local para migrar vectores...")
    try:
        import chromadb
        client = chromadb.PersistentClient(path=chroma_path)
        col = client.get_collection("textos_clasicos")
        total_vectors = col.count()
        print(f" Total de fragmentos vectorizados a transferir: {total_vectors}")

        batch_size = 500
        migrated = 0

        # Obtener todos los IDs
        all_ids = col.get(limit=total_vectors, include=[])["ids"]

        for i in range(0, len(all_ids), batch_size):
            chunk_ids = all_ids[i:i + batch_size]
            data = col.get(ids=chunk_ids, include=["documents", "metadatas", "embeddings"])
            
            rows = []
            for j in range(len(data["ids"])):
                cid = data["ids"][j]
                doc = data["documents"][j]
                meta = data["metadatas"][j] if data["metadatas"] else {}
                title = meta.get("title", "")
                author = meta.get("author", "")
                emb_str = "[" + ",".join(f"{float(x):.6f}" for x in data["embeddings"][j]) + "]"
                rows.append((cid, title, author, doc, emb_str))

            execute_values(
                cursor,
                """
                INSERT INTO book_chunks (id, title, author, content, embedding)
                VALUES %s
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    author = EXCLUDED.author,
                    content = EXCLUDED.content,
                    embedding = EXCLUDED.embedding;
                """,
                rows,
                template="(%s, %s, %s, %s, %s::vector)"
            )
            migrated += len(rows)
            print(f" Migrados: {migrated}/{total_vectors} fragmentos ({int(migrated/total_vectors*100)}%)...", end="\r")

        print(f"\n ¡Migración vectorial a Neon pgvector completada exitosamente! ({migrated} vectores)")
    except Exception as e:
        print(f"\n Error durante la migración de ChromaDB: {e}")

conn.close()
print("\n Proceso completado. La base de datos Neon está lista para producción.")

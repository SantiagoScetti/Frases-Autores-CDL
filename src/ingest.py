import os
import re
import hashlib
from typing import Optional, Callable, Dict, Any
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter
import db

load_dotenv()

def compute_file_hash(filepath: str) -> str:
    """Calcula el hash SHA256 del contenido del archivo para control incremental."""
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def process_file_content(filepath: str) -> str:
    """Extrae el contenido limpio de un archivo de texto, removiendo cabeceras comunes de ebooks."""
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()

    start_marker = "*** START OF THE PROJECT GUTENBERG EBOOK"
    end_marker = "*** END OF THE PROJECT GUTENBERG EBOOK"
    
    start_idx = text.find(start_marker)
    if start_idx != -1:
        start_idx = text.find('\n', start_idx)
        if start_idx != -1:
            start_idx += 1
    else:
        start_idx = 0
        
    end_idx = text.find(end_marker)
    if end_idx == -1:
        end_idx = len(text)
        
    return text[start_idx:end_idx].strip()

def chunk_text(text: str, max_length: int = 1500):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=max_length,
        chunk_overlap=150,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    return splitter.split_text(text)

def parse_filename_metadata(filename: str) -> Dict[str, str]:
    clean_name = filename.replace('.txt', '').strip()
    if " - " in clean_name:
        parts = clean_name.split(" - ", 1)
        titulo = parts[0].strip()
        autor = parts[1].strip()
        return {"author": autor, "title": titulo, "category": "Biblioteca RAG"}
    else:
        return {"author": "Varios Autores", "title": clean_name, "category": "General"}

def extract_book_summary(raw_text: str) -> str:
    """Extrae una muestra representativa del texto para el resumen editorial."""
    texto_limpio = raw_text.replace('\n', ' ').replace('\r', ' ')
    texto_limpio = re.sub(r'\s+', ' ', texto_limpio).strip()
    if len(texto_limpio) > 350:
        return texto_limpio[:350] + "..."
    return texto_limpio

def get_chroma_collection(db_dir: Optional[str] = None):
    if not db_dir:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_dir = os.path.join(base_dir, "data", "chroma_db")
    os.makedirs(db_dir, exist_ok=True)
    client = chromadb.PersistentClient(path=db_dir)
    local_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    collection = client.get_or_create_collection(
        name="textos_clasicos",
        embedding_function=local_ef
    )
    return collection

def ingest_single_book(
    filepath: str,
    custom_title: Optional[str] = None,
    custom_author: Optional[str] = None,
    custom_topics: Optional[str] = None,
    progress_callback: Optional[Callable[[float, str], None]] = None,
    force_reindex: bool = False
) -> Dict[str, Any]:
    """
    Ingesta incremental de un único libro.
    Calcula SHA256 para evitar duplicar procesamiento de archivos ya indexados.
    """
    if not os.path.exists(filepath):
        return {"status": "error", "message": f"El archivo no existe: {filepath}"}

    file_name = os.path.basename(filepath)
    file_hash = compute_file_hash(filepath)
    
    db.init_db()

    # Comprobación incremental
    if not force_reindex and db.is_book_ingested(file_hash):
        if progress_callback:
            progress_callback(1.0, f"'{file_name}' ya se encuentra indexado.")
        return {"status": "skipped", "message": f"El libro '{file_name}' ya fue indexado previamente.", "file_hash": file_hash}

    meta = parse_filename_metadata(file_name)
    title = (custom_title or meta["title"]).strip()
    author = (custom_author or meta["author"]).strip()
    topics = (custom_topics or "Filosofía, Economía, Libertad, Sociedad").strip()

    if progress_callback:
        progress_callback(0.1, f"Extrayendo texto de '{title}'...")

    raw_text = process_file_content(filepath)
    if not raw_text:
        return {"status": "error", "message": "El archivo de texto está vacío."}

    chunks = chunk_text(raw_text, max_length=1500)
    total_chunks = len(chunks)
    if total_chunks == 0:
        return {"status": "error", "message": "No se pudieron generar fragmentos de texto."}

    if progress_callback:
        progress_callback(0.3, f"Conectando a base vectorial ({total_chunks} fragmentos)...")

    collection = get_chroma_collection()

    summary = extract_book_summary(raw_text)
    book_prefix = hashlib.md5(title.encode('utf-8')).hexdigest()[:8]
    metadata_item = {"author": author, "title": title, "category": "Biblioteca RAG"}

    batch_size = 100
    total_batches = (total_chunks + batch_size - 1) // batch_size

    for b_idx in range(total_batches):
        start = b_idx * batch_size
        end = min(start + batch_size, total_chunks)
        batch_chunks = chunks[start:end]
        batch_ids = [f"{book_prefix}_{str(j + 1).zfill(5)}" for j in range(start, end)]
        batch_metadatas = [metadata_item for _ in range(len(batch_chunks))]

        collection.upsert(
            documents=batch_chunks,
            metadatas=batch_metadatas,
            ids=batch_ids
        )

        if progress_callback:
            pct = 0.3 + 0.6 * ((b_idx + 1) / total_batches)
            progress_callback(pct, f"Indexando lote {b_idx + 1} de {total_batches}...")

    # Guardar metadatos en base relacional (Postgres o SQLite)
    db.upsert_book_metadata(title, author, summary, topics, file_hash=file_hash, chunk_count=total_chunks)
    db.upsert_author(author, topics)

    if progress_callback:
        progress_callback(1.0, f"¡'{title}' de {author} indexado exitosamente!")

    return {
        "status": "success",
        "title": title,
        "author": author,
        "chunks": total_chunks,
        "file_hash": file_hash
    }

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_dir = os.path.join(base_dir, "data", "raw")
    
    if not os.path.exists(raw_dir) or not os.listdir(raw_dir):
        print(f"Error: El directorio {raw_dir} está vacío.")
        return

    db.init_db()
    files = [f for f in os.listdir(raw_dir) if f.endswith('.txt')]
    print(f"Total de archivos .txt encontrados: {len(files)}")

    ingested_count = 0
    skipped_count = 0

    for idx, file_name in enumerate(files, 1):
        file_path = os.path.join(raw_dir, file_name)
        print(f"\n[{idx}/{len(files)}] Evaluando: {file_name}")
        
        result = ingest_single_book(file_path)
        if result["status"] == "success":
            print(f" -> Indexado: {result['title']} ({result['chunks']} chunks)")
            ingested_count += 1
        elif result["status"] == "skipped":
            print(f" -> Omitido (ya indexado): {file_name}")
            skipped_count += 1
        else:
            print(f" -> Error: {result.get('message')}")

    print(f"\nProceso finalizado. Nuevos indexados: {ingested_count}, Previamente indexados: {skipped_count}.")

if __name__ == "__main__":
    main()

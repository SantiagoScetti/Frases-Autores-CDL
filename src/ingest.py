import os
import re
import chromadb
from chromadb.utils import embedding_functions

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
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
        
    return text[start_idx:end_idx]

def chunk_text(text, max_length=1500):
    paragraphs = text.split('\n\n')
    
    cleaned_paragraphs = []
    for p in paragraphs:
        if len(p) >= 100:
            cleaned_p = p.replace('\n', ' ').strip()
            cleaned_p = re.sub(r'\s+', ' ', cleaned_p)
            cleaned_paragraphs.append(cleaned_p)
            
    chunks = []
    current_chunk = ""
    for p in cleaned_paragraphs:
        if len(current_chunk) + len(p) <= max_length:
            current_chunk += " " + p if current_chunk else p
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = p
    if current_chunk:
        chunks.append(current_chunk.strip())
        
    return chunks

def get_metadata(filename):
    clean_name = filename.replace('.txt', '')
    if " - " in clean_name:
        parts = clean_name.split(" - ")
        titulo = parts[0].strip()
        autor = parts[1].strip()
        return {"author": autor, "title": titulo, "category": "Biblioteca RAG"}
    else:
        return {"author": "Desconocido", "title": clean_name, "category": "General"}

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_dir = os.path.join(base_dir, "data", "raw")
    db_dir = os.path.join(base_dir, "data", "chroma_db")
    
    if not os.path.exists(raw_dir) or not os.listdir(raw_dir):
        print(f"Error: El directorio {raw_dir} está vacío.")
        return

    print("Inicializando ChromaDB y configurando Embeddings Locales (gratis y sin límites)...")
    client = chromadb.PersistentClient(path=db_dir)
    
    # Usamos embeddings locales con SentenceTransformers (all-MiniLM-L6-v2)
    # Esto evita cualquier problema de rate limit o cuotas de API de Gemini.
    local_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    
    collection = client.get_or_create_collection(
        name="textos_clasicos",
        embedding_function=local_ef
    )
    
    files = [f for f in os.listdir(raw_dir) if f.endswith('.txt')]
    print(f"Se encontraron {len(files)} libros para procesar.")
    
    for file_name in files:
        file_path = os.path.join(raw_dir, file_name)
        print(f"\n--- Procesando: {file_name} ---")
        
        raw_text = process_file(file_path)
        chunks = chunk_text(raw_text, max_length=1500)
        print(f"Total de fragmentos generados: {len(chunks)}")
        
        if not chunks:
            print("No hay chunks válidos, pasando al siguiente.")
            continue
            
        metadata = get_metadata(file_name)
        
        batch_size = 100
        total_chunks = len(chunks)
        import hashlib
        book_prefix = hashlib.md5(file_name.encode()).hexdigest()[:8]
        
        print(f"Ingestando en la base de datos...")
        for i in range(0, total_chunks, batch_size):
            batch_chunks = chunks[i:i + batch_size]
            batch_ids = [f"{book_prefix}_{str(j + 1).zfill(4)}" for j in range(i, i + len(batch_chunks))]
            batch_metadatas = [metadata for _ in range(len(batch_chunks))]
            
            collection.upsert(
                documents=batch_chunks,
                metadatas=batch_metadatas,
                ids=batch_ids
            )
            print(f" Lote {i // batch_size + 1}/{(total_chunks + batch_size - 1) // batch_size} completado.", end="\r")
        print("\nIngesta del libro completada.")

    print("\n¡Proceso de ingesta total finalizado exitosamente!")

if __name__ == "__main__":
    main()

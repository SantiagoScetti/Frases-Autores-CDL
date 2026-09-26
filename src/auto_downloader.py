import requests
import time
import os
import re
import sys

def main():
    busquedas = [
        "No Treason Lysander Spooner",
        "Second Treatise of Government John Locke",
        "The Law Frederic Bastiat",
        "Essay on the Nature of Trade Cantillon"
    ]

    os.makedirs('data/raw', exist_ok=True)

    for query in busquedas:
        print(f"\nBuscando: {query}")
        sys.stdout.flush()
        try:
            url = f"https://gutendex.com/books/?search={requests.utils.quote(query)}"
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('results'):
                print(f"No encontrado en Gutendex: {query}")
                sys.stdout.flush()
                continue
                
            first_result = data['results'][0]
            book_id = first_result['id']
            title = first_result['title']
            
            text_url = None
            for mime_type, file_url in first_result.get('formats', {}).items():
                if 'text/plain' in mime_type:
                    text_url = file_url
                    break
                    
            if text_url:
                clean_title = re.sub(r'[^a-zA-Z0-9\s]', '', title).replace(' ', '_').lower()
                clean_title = clean_title[:50]
                
                file_path = f"data/raw/{book_id}_{clean_title}.txt"
                
                print(f"Descargando: {title} (ID: {book_id})")
                sys.stdout.flush()
                
                text_response = requests.get(text_url, timeout=30)
                text_response.raise_for_status()
                
                with open(file_path, 'wb') as f:
                    f.write(text_response.content)
                print(f"Guardado exitosamente en {file_path}")
            else:
                print(f"Formato de texto plano (.txt) no disponible para el libro '{title}'.")
            
            sys.stdout.flush()
            time.sleep(2)
            
        except Exception as e:
            print(f"Error en la búsqueda o descarga de '{query}': {e}")
            sys.stdout.flush()

if __name__ == "__main__":
    main()

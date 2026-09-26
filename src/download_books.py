import urllib.request
import os

def main():
    # Diccionario inicial con los libros a descargar (ID de Gutenberg)
    libros = {
        "smith_riqueza_naciones": 3300,
        "locke_tratado_gobierno": 7370,
        "mill_sobre_la_libertad": 34901,
        "bastiat_the_law": 44800,
        "spooner_no_treason": 36184
    }

    # Asegurarnos de que el directorio existe
    os.makedirs('data/raw', exist_ok=True)

    for nombre, libro_id in libros.items():
        url = f"https://www.gutenberg.org/cache/epub/{libro_id}/pg{libro_id}.txt"
        file_path = f"data/raw/{nombre}.txt"
        print(f"Descargando {nombre} desde {url}...")
        
        try:
            urllib.request.urlretrieve(url, file_path)
            print(f"Éxito: {nombre}.txt guardado en data/raw/.\n")
        except Exception as e:
            print(f"Error descargando {nombre}: {e}\n")

if __name__ == "__main__":
    main()

import os
import glob
import shutil
from thefuzz import process, fuzz
from PyPDF2 import PdfReader

# 1. Configuración de rutas
biblioteca_path = r"G:\.shortcut-targets-by-id\0B3hQ30qOLR8bOG9oTHVLRjVEM3M\BIBLIOTECA"
dest_pdfs = r"data\raw\pdfs"
dest_txts = r"data\raw"

os.makedirs(dest_pdfs, exist_ok=True)
os.makedirs(dest_txts, exist_ok=True)

# 2. Diccionario de libros pendientes. 
# La key es el nombre final en el TXT, el valor es una lista de palabras clave para ayudar al match.
libros_pendientes = {
    "Libertario en 30 días - VVAA.txt": ["Libertario en 30 dias", "VVAA"],
    "Individualismo y orden económico - Friedrich A. Hayek.txt": ["Individualismo y orden economico", "Hayek"],
    "Estados pequeños grandes posibilidades - Marquart Andreas & Bagus Philipp.txt": ["Estados pequenos grandes posibilidades"],
    "Lo que debemos saber sobre la inflación - Hazlitt Henry.txt": ["Lo que debemos saber sobre la inflacion", "Hazlitt"],
    "Los Impuestos son un Robo - Chodorov Frank.txt": ["Los impuestos son un robo", "Chodorov"],
    "Más prosperidad menos incertidumbre - Lopez Murphy Ricardo.txt": ["Mas prosperidad menos incertidumbre", "Lopez Murphy"],
    "Libertad, Patria y Vida - Lopez Murphy Ricardo.txt": ["Libertad Patria y Vida", "Lopez Murphy"],
    "Como los países salen de la pobreza - Zitelmann Rainer.txt": ["Como los paises salen de la pobreza", "Zitelmann"],
    "Mirando al Futuro - Barros Marta Ferreres Orlando.txt": ["Mirando al Futuro"],
    "Economía Sociedad e Historia - Hans-Hermann Hoppe.txt": ["Economia Sociedad e Historia", "Hoppe"],
    "Que le hizo el Gobierno a nuestro Dinero - Rothbard Murray.txt": ["Que le hizo el Gobierno a nuestro Dinero", "Rothbard"],
    "El estado - De Jasay Anthony.txt": ["El estado De Jasay", "Jasay"],
    "El mercado para la libertad - Tannehill Morris y Linda.txt": ["El mercado para la libertad", "Tannehill"],
    "Anatomía del Estado - Rothbard Murray N.txt": ["Anatomia del Estado", "Rothbard"],
    "Nosotros la gente - Alejandro Cabrera.txt": ["Nosotros la gente", "Alejandro Cabrera"],
    "Ensayos en Homenaje a Krause - VVAA.txt": ["Ensayos en Homenaje de Krause"],
    "Los enemigos del comercio 1 - Escohotado Antonio.txt": ["Los enemigos del comercio 1", "Escohotado"],
    "Los enemigos del comercio 2 - Escohotado Antonio.txt": ["Los enemigos del comercio 2", "Escohotado"],
    "Los enemigos del comercio 3 - Escohotado Antonio.txt": ["Los enemigos del comercio 3", "Escohotado"],
    "El Uso del conocimiento - Friedrich Hayek.txt": ["El uso del conocimiento en la sociedad", "Hayek"],
    "Lo esencial - Ludwig von Mises.txt": ["Lo esencial", "Mises"],
    "Crítica de la razón idiota.txt": ["Critica de la razon idiota"],
    "El Gerente Sustentable.txt": ["El Gerente Sustentable"],
    "100 Recomendaciones para Dirigentes políticos.txt": ["100 Recomendaciones para Dirigentes politicos"],
    "Las zonas oscuras de la democracia.txt": ["Las zonas oscuras de la democracia"],
    "A Dios lo que es del césar y viceversa.txt": ["A Dios lo que es del cesar y viceversa"],
    "Lobizón.txt": ["Lobizon"],
    "Amor - Editorial Grito Sagrado.txt": ["Amor Grito Sagrado"],
    "Amistad - Editorial Grito Sagrado.txt": ["Amistad Grito Sagrado"],
    "Dignidad - Editorial Grito Sagrado.txt": ["Dignidad Grito Sagrado"],
    "Libertad - Editorial Grito Sagrado.txt": ["Libertad Grito Sagrado"],
    "El Derecho Ambiental y sus aportes al derecho Positivo Argentino.txt": ["El Derecho Ambiental y sus aportes"],
    "Ciudades Modelo.txt": ["Ciudades Modelo"],
    "El estado, la lógica del poder político.txt": ["El estado la logica del poder politico"],
    "La recova de Miguel Angel Morra.txt": ["La recova de Miguel Angel Morra"],
    "La neo Izquierda.txt": ["La neo Izquierda"],
    "Dadme Libertad.txt": ["Dadme Libertad"],
    "El Socialismo - Ludwig von Mises.txt": ["El Socialismo", "Mises"],
    "El libre Mercado y sus Enemigos.txt": ["El libre Mercado y sus Enemigos"],
    "El Hombre, la economía y el Estado Vol 1 - Rothbard.txt": ["El Hombre la economia y el Estado 1", "Man Economy and State"],
    "El Hombre, la economía y el Estado Vol 2 - Rothbard.txt": ["El Hombre la economia y el Estado 2"],
    "Ensayo sobre la naturaleza del comercio en general - Cantillon.txt": ["Ensayo sobre la naturaleza del comercio en general", "Cantillon"],
    "En defensa del Capitalismo Global.txt": ["En defensa del Capitalismo Global"],
    "La Acción Humana - Ludwig von Mises.txt": ["La Accion Humana", "Mises"],
    "Tiempo y Dinero.txt": ["Tiempo y Dinero"],
    "Protocolos en Empresas de Familia.txt": ["Protocolos en Empresas de Familia"],
    "Nación, estado y economía - Mises.txt": ["Nacion estado y economia", "Mises"]
}

import re

def clean_text(text):
    # Remove standalone numbers (likely page numbers)
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
    # Remove multiple spaces
    text = re.sub(r' +', ' ', text)
    # Remove multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def extract_text_from_pdf(pdf_path, txt_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t: text += t + "\n"
        
        text = clean_text(text)
        
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)
        return True
    except Exception as e:
        print(f"Error procesando PDF {pdf_path}: {e}")
        return False

def main():
    print("Escaneando todos los PDFs en la biblioteca de Google Drive...")
    # Recopilar todos los PDFs. Ignoramos EPUBs por ahora porque PyPDF2 solo lee PDFs.
    todos_los_pdfs = []
    for root, dirs, files in os.walk(biblioteca_path):
        for file in files:
            if file.lower().endswith('.pdf'):
                # Guardamos una tupla: (nombre_del_archivo_limpio, ruta_completa)
                nombre_limpio = os.path.splitext(file)[0].replace('_', ' ').replace('-', ' ')
                # Para mejorar el match, agregamos el nombre de la carpeta (suele ser el autor)
                carpeta_autor = os.path.basename(root)
                contexto_busqueda = f"{nombre_limpio} {carpeta_autor}"
                todos_los_pdfs.append((contexto_busqueda, os.path.join(root, file)))
                
    if not todos_los_pdfs:
        print("No se encontraron PDFs. Verifica la ruta o asegúrate de que el Drive esté sincronizado y conectado.")
        return
        
    print(f"Se encontraron {len(todos_los_pdfs)} PDFs. Iniciando el cruce inteligente...")
    
    # Solo los nombres para usar thefuzz extractOne
    nombres_para_buscar = [item[0] for item in todos_los_pdfs]
    rutas_map = {item[0]: item[1] for item in todos_los_pdfs}
    
    encontrados = 0
    
    for final_name, keywords in libros_pendientes.items():
        # Tomamos la primer keyword como principal (el titulo)
        query = keywords[0]
        # Hacemos fuzzy match contra todos los PDFs
        mejor_coincidencia, score = process.extractOne(query, nombres_para_buscar, scorer=fuzz.token_set_ratio)
        
        # Si el score es mayor a 85, lo consideramos un match
        if score > 85:
            ruta_pdf = rutas_map[mejor_coincidencia]
            print(f"MATCH: '{query}' encontrado como '{os.path.basename(ruta_pdf)}' (Score: {score})")
            
            # 1. Copiar el PDF
            dest_pdf_path = os.path.join(dest_pdfs, os.path.basename(ruta_pdf))
            if not os.path.exists(dest_pdf_path):
                shutil.copy2(ruta_pdf, dest_pdf_path)
            
            # 2. Convertir a TXT
            dest_txt_path = os.path.join(dest_txts, final_name)
            if not os.path.exists(dest_txt_path):
                import PyPDF2 # import inside to avoid error if missing
                print(f"   -> Extrayendo texto a {final_name}...")
                exito = extract_text_from_pdf(dest_pdf_path, dest_txt_path)
                if exito:
                    encontrados += 1
            else:
                print(f"   -> Ya extraído anteriormente ({final_name})")
        else:
            print(f"NO MATCH: Para '{query}'. Mejor candidato fue '{mejor_coincidencia}' con Score: {score}")
            
    print(f"\n¡Proceso finalizado! Se encontraron y procesaron {encontrados} libros nuevos.")

if __name__ == "__main__":
    main()
